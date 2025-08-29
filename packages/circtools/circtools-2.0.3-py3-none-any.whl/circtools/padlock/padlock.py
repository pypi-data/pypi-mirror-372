#! /usr/bin/env python3

# Copyright (C) 2017 Tobias Jakobi
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either self.version 3 of the License, or
# (at your option) any later self.version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import circ_module.circ_template

import os
import circtools.scripts
import sys
import string
import random
import itertools
import subprocess

import pybedtools
from Bio.Blast import NCBIWWW
from Bio.Blast import NCBIXML

from Bio.SeqFeature import SeqFeature, FeatureLocation
from Bio.Graphics import GenomeDiagram

import primer3                  # for padlock probe designing

# var = os.system('module load blast/2.3.0+')       # for running blastn command-line
# print(var)
#cmd = subprocess.Popen('module load blast/2.3.0+', shell = True)
#exec(cmd)

#R file path
R_SCRIPT_PATH = os.path.join(
    circtools.scripts.__path__[0],
    "circtools_padlockprobe_formatter.R"
)

class Padlock(circ_module.circ_template.CircTemplate):
    def __init__(self, argparse_arguments, program_name, version):

        # get the user supplied options
        self.cli_params = argparse_arguments
        self.program_name = program_name
        self.version = version
        self.command = 'Rscript'
        self.temp_dir = self.cli_params.global_temp_dir
        self.gtf_file = self.cli_params.gtf_file
        self.fasta_file = self.cli_params.fasta_file
        self.detect_dir = self.cli_params.detect_dir
        self.output_dir = self.cli_params.output_dir
        self.organism = self.cli_params.organism
        self.id_list = self.cli_params.id_list
        #self.product_range = self.cli_params.product_size   # not required for probe designing
        #self.junction = self.cli_params.junction
        self.no_blast = self.cli_params.blast
        self.experiment_title = self.cli_params.experiment_title
        self.input_circRNA = self.cli_params.sequence_file
        self.num_pairs = self.cli_params.num_pairs
        self.rna_type = self.cli_params.rna_type            # flag for type of RNA for which you want to generate probes
        self.no_svg = self.cli_params.svg
        
        # gene_list file argument
        if (self.cli_params.gene_list):
            self.gene_list = self.cli_params.gene_list
        elif (self.cli_params.gene_list_file):
            gene_file = [line.rstrip() for line in open(self.cli_params.gene_list_file[0])]
            self.gene_list = gene_file
        else:
            print("Need to provide gene list by either -G or -GL options!")
            exit(-1)

        if self.id_list and self.gene_list:
            print("Please specify either host genes via -G/-GL or circRNA IDs via -i.")
            sys.exit(-1)

        # create a sub-directory for SVG files inside the self.output_dir directory
        # self.svg_dir = os.getcwd() + "/" + self.output_dir + "SVG/" 
        # if not os.path.isdir(self.svg_dir):
        #     os.mkdir(self.svg_dir)

        self.homo_sapiens_blast_db = "GPIPE/9606/current/rna"
        self.mus_musculus_blast_db = "GPIPE/10090/current/rna"
        self.rattus_norvegicus_blast_db = "GPIPE/10116/current/rna"
        self.sus_scrofa_blast_db = "GPIPE/9823/current/rna"

        self.other_blast_db = "nt"


    def module_name(self):
        """Return a string representing the name of the module."""
        return self.program_name

    # Register an handler for the timeout
    def handler(self, signum, frame):
        raise Exception("Maximum execution time for remote BLAST reached. Please try again later.")

    def call_blast(self, input_file, organism):

        blast_db = "nt"
        if organism == "mm":
            blast_db = self.mus_musculus_blast_db
        elif organism == "hs":
            blast_db = self.homo_sapiens_blast_db
        elif organism == "rn":
            blast_db = self.rattus_norvegicus_blast_db
        elif organism == "ss":
            blast_db = self.sus_scrofa_blast_db
        else:
            print("Organism not recognized. Make sure -O is supplied.")

        return_handle = NCBIWWW.qblast("blastn",
                                       blast_db,
                                       input_file,
                                       hitlist_size=10,
                                       expect=1000,
                                       word_size=7,
                                       gapcosts="5 2"
                                       )
        return return_handle



    @staticmethod
    def read_annotation_file(annotation_file, entity="gene", string=False):
        """Reads a GTF file
        Will halt the program if file not accessible
        Returns a BedTool object only containing gene sections
        """

        try:
            file_handle = open(annotation_file)
        except PermissionError:
            message = ("Input file " + str(annotation_file) + " cannot be read, exiting.")
            sys.exit(message)
        else:

            with file_handle:
                line_iterator = iter(file_handle)
                bed_content = ""
                print("Start parsing GTF file")
                for line in line_iterator:
                    # we skip any comment lines
                    if line.startswith("#"):
                        continue

                    # split up the annotation line
                    columns = line.split('\t')

                    if not (columns[2] == entity):
                        continue

                    # we do not want any 0-length intervals -> bedtools segfault
                    if int(columns[4]) - int(columns[3]) == 0:
                        continue

                    # extract chromosome, start, stop, score(0), name and strand
                    # we hopefully have a gene name now and use this one for the entry
                    
                    # added by Shubhada (to fetch the gene names)
                    s = str(columns[8])
                    news = s.strip("\n")[:-1].replace("; ", ";")          # removing trailing ; to form dictionary in next step
                    temp = [x for x in news.replace("\"", "").split(";")]
                    temp_keys = [x.split(" ")[0] for x in temp]
                    temp_values = ["_".join(x.split(" ")[1:]) for x in temp]
                    gene_dict = dict(zip(temp_keys,temp_values))
                    if ("gene_name" in gene_dict.keys()):
                        gene_name = gene_dict["gene_name"]
                    else:
                        gene_name = "name"
                    entry = [
                        columns[0],
                        columns[3],
                        columns[4],
                        gene_name,
                        str(0),
                        columns[6]
                        #columns[1]              # flag ensemble/havana
                    ]

                    # concatenate lines to one string
                    bed_content += '\t'.join(entry) + "\n"

            if not bed_content:
                exit(-1)

            if string:
                return bed_content
            else:
                return bed_content

    def run_module(self):

        def calc_GC(seq):
            # function to calculate GC content of a probe
            c=0
            g=0
            t=0
            a=0
            for x in str(seq):
                if x == "C":
                    c+=1    
                elif x == "G":
                    g+=1
                elif x == "A":
                    a+=1    
                elif x == "T":
                    t+=1

            gc_content=(g+c)*100/(a+t+g+c)
            return(gc_content)

        # function to call primer3 on given 40bp sequence
        def primer3_calling(scan_window, gene_string, junction, output_list):
            # argument 1 is 40bp sequence
            # argument 2 is the name with coordinate details to be printed in the output
            # argument 3 is junction type i.e. preferred or neutral
            # argument 4 is list to which the output line should be appended for BLAST
            rbd5 = scan_window[:20]
            rbd3 = scan_window[20:]
            if (('GGGGG' in rbd5) or ('GGGGG' in rbd3)):
                return None
            melt_tmp_5 = int(round(primer3.calc_tm(rbd5)))
            melt_tmp_3 = int(round(primer3.calc_tm(rbd3)))
            melt_tmp_full = int(round(primer3.calc_tm(scan_window)))
            gc_rbd5 = int(round(calc_GC(rbd5)))
            gc_rbd3 = int(round(calc_GC(rbd3)))
            gc_total = int(round(calc_GC(scan_window)))
            ## following part of code is commented for now so that all probes are present in the output. Some imp genes were getting missed because of this.
            #if ((melt_tmp_5 < 50) or (melt_tmp_3 < 50) or (melt_tmp_5 > 70) or (melt_tmp_3 > 70) or (melt_tmp_full < 68) or (melt_tmp_full > 82)) :
            #    print("Melting temperature outside range!", gene_string,  rbd5, rbd3, melt_tmp_5, melt_tmp_3, melt_tmp_full, junction)
            #    return None

            # checking for hairpin/homodimer/heterodimer possibilities
            warnings = []
            hairpin5 = primer3.calc_hairpin(rbd5)
            hairpin3 = primer3.calc_hairpin(rbd3)
            homo5 = primer3.calc_homodimer(rbd5)
            homo3 = primer3.calc_homodimer(rbd3) 
            hetero = primer3.calc_heterodimer(rbd5, rbd3)

            if ( (int(hairpin5.tm) > melt_tmp_5) or (int(hairpin3.tm) > melt_tmp_3)):
                warnings.append("Potential Hairpin")
            
            if ( (int(homo5.tm) > melt_tmp_5) or (int(homo3.tm) > melt_tmp_3)):
                warnings.append("Potential Homodimer")

            if (int(hetero.tm) > melt_tmp_5):
                warnings.append("Potential Heterodimer")

            # if len(warnings) == 0:
            #     print(gene_string, rbd5, rbd3, melt_tmp_5, melt_tmp_3, melt_tmp_full, gc_rbd5, gc_rbd3, junction)
            # else:
            #     print(gene_string, rbd5, rbd3, melt_tmp_5, melt_tmp_3, melt_tmp_full, gc_rbd5, gc_rbd3, junction, ",".join(warnings))
                
            output_list.append([gene_string, rbd5, rbd3, melt_tmp_5, melt_tmp_3, melt_tmp_full, gc_rbd5, gc_rbd3, junction])
            
            return output_list

        # function to run blast on every probe
        def probes_blast(probes_for_blast, blast_xml_tmp_file):
            # function that takes as an input the probes list 
            # with first three entries as id, rbd5 sequnces and rbd3 sequence respectively

            blast_object_cache = {}
            blast_result_cache = {}
            primer_to_circ_cache = {}

            blast_input_file = ""
            if circ_rna_number < 100:

                for entry in probes_for_blast:
                    circular_rna_id = entry[0].split('_')
                    
                    combined_seq = entry[1] + entry[2]      # because Xenium people BLAST both of them together
                    if entry[1] == "NA":
                        continue

                    # if not already BLASTed, add entry to the BLAST input file
                    elif not combined_seq in blast_object_cache:
                        blast_input_file += "\n>" + combined_seq + "\n" + combined_seq
                        blast_object_cache[combined_seq] = 1
                        primer_to_circ_cache[combined_seq] = circular_rna_id[0]

                    # seen already, skip
                    elif combined_seq in blast_object_cache:
                        continue

            else:
                print("Too many circRNAs selected, skipping BLAST step.")

            if self.no_blast:
                print("User disabled BLAST search, skipping.")
           
            #print(blast_input_file)            # this is a fasta file with primer sequences to BLAST

            run_blast = 0

            # check if we have to blast
            if not self.no_blast and blast_input_file:
                
                try:
                    print("Sending " + str(len(blast_object_cache)) + " primers to BLAST")
                    print("This may take a few minutes, please be patient.")
                    result_handle = self.call_blast(blast_input_file, self.organism)
                    run_blast = 1
                except Exception as exc:
                    print(exc)
                    exit(-1)
                with open(blast_xml_tmp_file, "w") as out_handle:
                    out_handle.write(result_handle.read())

                result_handle.close()
                '''
                ## this is the local installation running part for BLAST. Commented later for the release.
                
                # save the blast input fasta file into a temp file
                blast_fasta_file = blast_xml_tmp_file.replace("results.xml", "input.fa")
                with open(blast_fasta_file, "w") as out_handle:
                    out_handle.write(blast_input_file.strip())

                try:
                    print("Running BLAST command line")
                    if (self.organism == "mm"):
                        blastdb = "/beegfs/biodb/genomes/mus_musculus/GRCm38_102/GRCm38.cdna.all.fa"
                    else:
                        blastdb = "/beegfs/biodb/genomes/homo_sapiens/GRCh38_102/cDNA_slim.fa"
                    #cmd = "blastn -db " + blastdb + " -query " + blast_fasta_file + " -out " + blast_xml_tmp_file + " -task blastn -outfmt 5"
                    cmd = "blastn -word_size 7 -gapopen 5 -gapextend 2 -evalue 1000 -max_target_seqs 10 -db " + blastdb + " -query " + blast_fasta_file + " -out " + blast_xml_tmp_file + " -task blastn -outfmt 5"
                    cmd_out = os.system(cmd)

                except Exception as exc:
                    print(exc)
                    print(-1)
                '''

                result_handle = open(blast_xml_tmp_file)
                run_blast = 1

                blast_records = NCBIXML.parse(result_handle)

                for blast_record in blast_records:

                    if blast_record.query not in blast_result_cache:
                        blast_result_cache[blast_record.query] = []

                    for description in blast_record.descriptions:
                        # filter out the host gene we're in now
                        # also filter out all "PREDICTED" stuff
                        if description.title.find(primer_to_circ_cache[blast_record.query]) == -1 and\
                                description.title.find("PREDICTED") == -1:
                            blast_result_cache[blast_record.query].append(description.title)

            # if we encounter NAs nothing has been blasted, we manually set the values now

            blast_result_cache["NA"] = ["Not blasted, no primer pair found"]

            data_with_blast_results = ""

            for entry in probes_for_blast:
                #entry = line.split('\t')
                #print("BLAST CHECK", entry, len(entry))
                # split up the identifier for final plotting
                #entry[0] = "\t".join(entry[0].split("_")[:5])
                entry[0] = entry[0].replace("_", "\t")
                #print(entry)
                line = "\t".join(map(str, entry))
                #print(line)
                combined_seq = entry[1] + entry[2]      # because Xenium people BLAST both of them together

                if run_blast == 1:
                    left_result = "No hits"
                    right_result = "No hits"
                else:
                    left_result = "Not blasted, no off-targets found"
                    right_result = left_result

                if combined_seq in blast_result_cache:
                    left_result = ";".join(blast_result_cache[combined_seq])

                if combined_seq in blast_result_cache:
                    right_result = ";".join(blast_result_cache[combined_seq])

                # update line
                data_with_blast_results += line + "\t" + left_result + "\t" + right_result + "\n"

            return data_with_blast_results
        
        # function to create graphical representation of circular/linear RNAs
        def graphical_visualisation(blast_results, exon_cache_dict, flanking_exon_dict, output_dir, rna_type):
            for line in blast_results.splitlines():
                entry = line.split('\t')
                #print(entry)
                if entry[6] == "NA":            # no primers, no graphics
                    continue
                circular_rna_id = "_".join([entry[0], entry[1], entry[2], entry[3], entry[4]])
                circular_rna_id_isoform = "_".join([entry[0], entry[1], entry[2], entry[3], entry[4], entry[6]])       # entry[6] is the scanning sequence, saved to calculate forward/reverse primer start
                index = int(entry[5])
                #print(entry, circular_rna_id, circular_rna_id_isoform)
                if (rna_type == "circle"):
                    circrna_length = int(entry[3]) - int(entry[2])

                    exon1_length = len(exon_cache_dict[circular_rna_id][1])
                    exon2_length = len(exon_cache_dict[circular_rna_id][2])

                    exon2_colour = "#ffac68"
                    if exon2_length == 0:
                        exon1_length = int(len(exon_cache_dict[circular_rna_id][1])/2)+1
                        exon2_length = int(len(exon_cache_dict[circular_rna_id][1])/2)
                        exon2_colour = "#ff6877"
                    
                    # graphical design
                    gdd = GenomeDiagram.Diagram('Probe diagram')
                    gdt_features = gdd.new_track(1, greytrack=True, name="", )
                    gds_features = gdt_features.new_set()
                    # adding first exon
                    feature = SeqFeature(FeatureLocation(0, exon1_length))
                    feature.location.strand = +1
                    gds_features.add_feature(feature, name="Exon 1", label=False, color="#ff6877", label_size=22)
                    # adding second exon
                    feature = SeqFeature(FeatureLocation(circrna_length - exon2_length, circrna_length))
                    feature.location.strand = +1
                    gds_features.add_feature(feature, name="Exon 2", label=False, color=exon2_colour, label_size=22)

                    # adding the individual arm
                    flag = 0            # flag to keep track if start of RBD3 is before BSJ
                    rbd5_start = circrna_length-25+index 
                    rbd5_end = circrna_length-25+index+20
                    if (rbd5_end >= circrna_length):
                        feature = SeqFeature(FeatureLocation(rbd5_start, circrna_length)) 
                        gds_features.add_feature(feature, name="RBD5", label=False, color="red", label_size=22)
                        feature = SeqFeature(FeatureLocation(0, rbd5_end - circrna_length))
                        gds_features.add_feature(feature, name="RBD5", label=False, color="red", label_size=22)
                        rbd5_end = rbd5_end - circrna_length
                    else:
                        feature = SeqFeature(FeatureLocation(rbd5_start, rbd5_end))
                        gds_features.add_feature(feature, name="RBD5", label=False, color="red", label_size=22)
                        flag = 1
                    rbd3_start = rbd5_end + 1
                    #print(circular_rna_id_isoform, rbd5_end, rbd3_start, circrna_length, flag)
                    if (flag == 1):
                        feature = SeqFeature(FeatureLocation(rbd3_start, circrna_length)) 
                        gds_features.add_feature(feature, name="RBD3", label=False, color="green", label_size=22)
                        feature = SeqFeature(FeatureLocation(0, 20 - (circrna_length - rbd3_start)))
                        gds_features.add_feature(feature, name="RBD3", label=False, color="green", label_size=22)
                    else:
                        rbd3_end = rbd3_start + 20
                        feature = SeqFeature(FeatureLocation(rbd3_start, rbd3_end))
                        gds_features.add_feature(feature, name="RBD3", label=False, color="green", label_size=22)

                    feature = SeqFeature(FeatureLocation(0, 1))
                    gds_features.add_feature(feature, name="BSJ", label=True, color="white", label_size=22)
                    # adding flanking exons
                    if circular_rna_id in flanking_exon_dict:
                        for exon in flanking_exon_dict[circular_rna_id]:
                            exon_start, exon_stop = exon.split('_')

                            exon_start = int(exon_start) - int(entry[2])
                            exon_stop = int(exon_stop) - int(entry[2])

                            feature = SeqFeature(FeatureLocation(exon_start, exon_stop))
                            feature.location.strand = +1

                            gds_features.add_feature(feature, name="Exon", label=False, color="grey", label_size=22)
                        
                    gdd.draw(format='circular', pagesize=(600, 600), circle_core=0.25, track_size=0.2, tracklines=0, x=0.00, y=0.00, start=0, end=circrna_length-1)
                    gdd.write(output_dir + "/" + circular_rna_id_isoform + ".svg", "SVG")

                if (rna_type == "linear"):
                    exon1_length = len(exon_cache_dict[circular_rna_id][1])
                    exon2_length = len(exon_cache_dict[circular_rna_id][2])
                    circrna_length = exon1_length + exon2_length

                    # graphical design
                    gdd = GenomeDiagram.Diagram('Probe diagram')
                    gdt_features = gdd.new_track(1, greytrack=True, name="", )
                    gds_features = gdt_features.new_set()
                    # adding first exon
                    feature = SeqFeature(FeatureLocation(0, exon1_length))
                    feature.location.strand = +1
                    gds_features.add_feature(feature, name="Exon 1", label=False, color="#ff6877", label_size=22)
                    # adding second exon
                    feature = SeqFeature(FeatureLocation(circrna_length - exon2_length, circrna_length))
                    feature.location.strand = +1
                    gds_features.add_feature(feature, name="Exon 2", label=False, color="#ffac68", label_size=22)

                    # rbd5 
                    feature = SeqFeature(FeatureLocation(exon1_length-25+index+1, exon1_length-25+index+20+1))
                    gds_features.add_feature(feature, name="RBD5", label=False, color="red", label_size=22)
                    # rbd3
                    feature = SeqFeature(FeatureLocation(exon1_length-25+index+20+1, exon1_length-25+index+40)) 
                    gds_features.add_feature(feature, name="RBD3", label=False, color="green", label_size=22) 
                        
                    feature = SeqFeature(FeatureLocation(exon1_length, exon1_length))
                    gds_features.add_feature(feature, name="FSJ", label=True, color="white", label_size=22)
                    gdd.draw(format='linear', pagesize=(600, 600), circle_core=0.25, track_size=0.2, tracklines=0, x=0.00, y=0.00, 
                                 start=0, end=circrna_length-1, fragments = 1)
                    gdd.write(output_dir + "/" + circular_rna_id_isoform + ".svg", "SVG")

            return None
        
        if self.id_list and os.access(self.id_list[0], os.R_OK):
            print("Detected supplied circRNA ID file.")
            with open(self.id_list[0]) as f:
                lines = f.read().splitlines()
            self.id_list = lines

        # let's first check if the temporary directory exists
        if not (os.access(self.temp_dir, os.W_OK)):
            print("Temporary directory %s not writable." % self.temp_dir)
            # exit with -1 error if we can't use it
            exit(-1)

        # let's first check if the temporary directory exists
        if not (os.access(self.output_dir, os.W_OK)):
            print("Output directory %s not writable." % self.output_dir)
            # exit with -1 error if we can't use it
            exit(-1)

        '''
        ## this part is commented because product_range not required for padlock probe design
        # let's first check if the temporary directory exists
        if self.product_range and len(self.product_range) != 2:
            print("Please specify a qPCR product range as range, e.g. \"-p 140 150\".")
            # exit with -1 error if we can't use it
            exit(-1)

        if self.product_range[1] < self.product_range[0]:
            print("qPCR product range has to be > 0.")
            # exit with -1 error if we can't use it
            exit(-1)
        '''
        circ_rna_number = 0

        # define temporary files

        letters = string.ascii_letters
        tmp_prefix =  ''.join(random.choice(letters) for i in range(10))

        exon_storage_tmp = self.temp_dir + tmp_prefix + "_circtools_flanking_exons.tmp"
        exon_storage_linear_tmp = self.temp_dir + tmp_prefix + "_circtools_linear_exons.tmp" # file that will store ALL exons; for forward splice junctions
        blast_storage_tmp = self.temp_dir + tmp_prefix + "_circtools_blast_results.tmp"
        blast_storage_tmp_linear = self.temp_dir + tmp_prefix + "_circtools_blast_results_linear.tmp"
        blast_xml_tmp = self.temp_dir + tmp_prefix + "_circtools_blast_results.xml"
        blast_xml_tmp_linear = self.temp_dir + tmp_prefix + "_circtools_blast_linear_results.xml"

        output_html_file = self.output_dir + "/" + self.experiment_title.replace(" ", "_") + "_circles_BSJ.html"
        output_html_file_linear = self.output_dir + "/" + self.experiment_title.replace(" ", "_") + "_linear_FSJ.html"
        output_csv_file = self.output_dir + "/" + self.experiment_title.replace(" ", "_") + "_circles_BSJ.csv" # padlock probe output csv file 
        output_csv_file_linear = self.output_dir + "/" + self.experiment_title.replace(" ", "_") + "_linear_FSJ.csv" # padlock probe output csv file for linear RNA probes

        # fasta file with 50bp sequence for each junction; for Xenium 
        output_fasta_file = self.output_dir + "/" + self.experiment_title.replace(" ", "_") + "_BSJ.fa"
        output_fasta_file_linear = self.output_dir + "/" + self.experiment_title.replace(" ", "_") + "_FSJ.fa"
        
        # BED fole for genome browser
        bed_probes_circles = self.output_dir + "/" + self.experiment_title.replace(" ", "_") + "_probes_circles.bed"
        bed_probes_linear = self.output_dir + "/" + self.experiment_title.replace(" ", "_") + "_probes_linear.bed"
        # erase old contents
        open(exon_storage_tmp, 'w').close()
        open(exon_storage_linear_tmp, 'w').close()

        # define cache dicts
        exon_cache = {}
        flanking_exon_cache = {}
        primer_to_circ_cache = {}
        exon_dict_circle_bed12 = {}            # dictionary start stores first and last exons for every circle (needed for IGV bed file)
        
        # call the read_annotation_file and store exons in both bed and bedtools format for linear and circRNA
        exons_bed = self.read_annotation_file(self.gtf_file, entity="exon")
        exons_bed_list = [x.split("\t") for x in exons_bed.strip().split("\n")]
        #print(exons_bed_list)
        # create a "virtual" BED file for circular RNA bedtools intersect
        virtual_bed_file = pybedtools.BedTool(exons_bed, from_string=True)

        #virtual_bed_file.saveas('exons_hs.bed')
        # we trust that bedtools >= 2.27 is installed. Otherwise this merge will probably fail
        exons = virtual_bed_file.sort().merge(s=True,  # strand specific
                                                 c="4,5,6",  # copy columns 5 & 6
                                                 o="distinct,distinct,distinct")  # group
        #print(exons_bed_list[:5])
        exons_bed_list = [x.split("\t") for x in str(exons).splitlines()]
        #print(exons_bed_list[:5])
        #exons.saveas('exons_hs_merged.bed') 
        # define primer design parameters
        design_parameters = {
                'PRIMER_OPT_SIZE': 20,
                'PRIMER_MIN_SIZE': 20,
                'PRIMER_MAX_SIZE': 20,
                'PRIMER_MIN_TM': 50.0,
                'PRIMER_MAX_TM': 70.0,
                'PRIMER_MAX_NS_ACCEPTED': 0,
                'PRIMER_PRODUCT_SIZE_RANGE': [[20,20]]}

        # dictionary for ligation juntiond flag, taken from technical note Xenium
        dict_ligation_junction = {"AT":'preferred', "TA":'preferred', "GA":'preferred', "AG":'preferred',
                                      "TT":'neutral', "CT":'neutral', "CA":'neutral', "TC":'neutral', "AC":'neutral'
                                      , "CC":'neutral', "TG":'neutral', "AA":'neutral', "CG":'nonpreferred'
                                      , "GT":'nonpreferred', "GG":'nonpreferred', "GC":'nonpreferred'}
        # dictionary for RGB color values for BED tracks. One color per j index of scanning sequence (need 11 in total)
        track_color_dict = {0: "166,206,227", 1:"31,120,180", 2:"128,0,0", 3:"51,160,44", 4:"251,154,153", 5:"227,26,28",
                            6:"253,191,111", 7:"255,127,0", 8:"202,178,214", 9:"106,61,154", 10:"240,50,230"}
        
        if (self.rna_type == 1 or self.rna_type == 2):
            print("Finding probes for linear RNAs")
            # First for linear RNAs, store the exons per gene in the gene-list
            primex_data_with_blast_results_linear = []
            designed_probes_for_blast_linear = []
            fasta_xenium_linear_dict = {}
            fasta_xenium_linear = ""
            all_exon_cache = {}             # to store all exons for linear RNA splicing
            probe_bed_linear = []
            for each_gene in self.gene_list:
                list_exons_seq = []
                list_exons_pos = []
                all_exons = [x for x in exons_bed_list if x[3] == each_gene] # and x[6] == "ensembl_havana"]   # only take exons annotated by ensemble and havana both as these are confirmed both manually and automatically
                #print(all_exons)
                all_exons_unique = (list(map(list,set(map(tuple, all_exons)))))
                all_exons_unique.sort(key = lambda x: x[1])
                #print(all_exons_unique)
                fasta_bed_line = ""
                for each_element in all_exons_unique:
                    each_element[1] = str(int(each_element[1]) - 1)         # fix for sequence generation - 1 bp extra was getting added
                    virtual_bed_file = pybedtools.BedTool("\t".join(each_element), from_string=True)
                    virtual_bed_file = virtual_bed_file.sequence(fi=self.fasta_file, s=True)
                    seq = open(virtual_bed_file.seqfn).read().split("\n", 1)[1].rstrip()
                    list_exons_seq.append(seq)
                    each_line = "\t".join([each_element[i] for i in [0,1,2,5]])     # this entry is for final HTML report chr, start, end, gene
                    # print("Check each_line", each_line)
                    list_exons_pos.append(each_line)

                with open(exon_storage_linear_tmp, 'a') as data_store:
                    data_store.write(each_gene + "\t" + "\t".join(list_exons_seq) + "\n")
               
                # for every gene, extract from every exon, the first and last 25bp 
                for i in range(0, len(list_exons_seq)):
                    if i == len(list_exons_seq)-1:
                        break
                    # find out start and end of probes
                    pos = list_exons_pos[i]     # details about coordinates of these exons -> required for HTML output
                    temp_split = list_exons_pos[i].split("\t")      # exon1 coord
                    temp_split_2 = list_exons_pos[i+1].split("\t") # exon2 coord
                    #print(temp_split, [each_gene + "_" + "_".join(temp_split)])
                    all_exon_cache[each_gene + "_" + "_".join(temp_split)] = {1:list_exons_seq[i], 2:list_exons_seq[i+1]}
                    #print("Exon and exon+1 positions:", pos, temp_split, temp_split_2)
                    scan_coord_chr = temp_split[0]
                    scan_coord_strand = temp_split[3]

                    scan_sequence = list_exons_seq[i][-25:] + list_exons_seq[i+1][:25]
                    fasta_xenium_linear_dict[each_gene + "_" + "_".join(temp_split)] = scan_sequence 
                    fasta_xenium_linear += ">" + each_gene + "_" + "_".join(temp_split) + "\n" + scan_sequence + "\n"
                    for j in range(0,len(scan_sequence)):
                        scan_window = scan_sequence[j:j+40]
                        if (len(scan_window) < 40):
                            break
                        junction = dict_ligation_junction[scan_window[19:21]]
                        # filter criteria for padlock probes - accepted ligation junction preferences
                        if (junction == "nonpreferred" ):
                            #print("NONPREFERRED JUNCTION FOUND")
                            continue
                        else:
                            #primer3_calling(scan_window, each_gene+"_"+pos, junction, designed_probes_for_blast_linear)
                            primer3_calling(scan_window, each_gene+"_"+pos.replace("\t","_")+"_"+str(j), junction, designed_probes_for_blast_linear)
                            # coordinates for BED12 file and graphical visualisation
                            distance = int(temp_split_2[1]) - int(temp_split[2])  # distance between two exons i.e. length of intron 
                            primer_start = (int(temp_split[2]) - 25) + j
                            size1 = int(temp_split[2]) - primer_start
                            size2 = 15 + j
                            primer_end = primer_start + 40 + distance
                            block_start_2 = size1 + distance 
                            thick_start = primer_start
                            thick_end = primer_end
                            probe_bed_linear.append([scan_coord_chr, primer_start, primer_end, each_gene+"_"+scan_window, "0", scan_coord_strand, thick_start, thick_end,
                                                     track_color_dict[j], "2", str(size1)+","+str(size2), "0,"+str(block_start_2)])
                            #print(each_gene+"_"+pos, [scan_coord_chr, scan_coord_start, scan_coord_end, j], primer_start, primer_end, scan_window)
            
            primex_data_with_blast_results_linear = probes_blast(designed_probes_for_blast_linear, blast_xml_tmp_linear)

            # modify primex_data_with_blast_results for formatter script
            temp = primex_data_with_blast_results_linear.strip().split("\n")
            primex_data_with_blast_results_linear_storage = ""
            for each_element in temp:
                each_element = each_element.split("\t")
                each_element.pop(5)
                primex_data_with_blast_results_linear_storage = primex_data_with_blast_results_linear_storage + "\t".join(each_element) + "\n"

            #print(fasta_xenium_linear_dict.keys())
            with open(blast_storage_tmp_linear, 'w') as data_store:
                data_store.write(primex_data_with_blast_results_linear_storage)

            with open(bed_probes_linear, 'w') as f:
                for line in probe_bed_linear:
                    f.write("\t".join(map(str, line)))
                    f.write("\n")

            # visualisation
            if (self.no_svg):
                print("No graphical representations SVG will be generated")
            else:
                graphical_visualisation(primex_data_with_blast_results_linear, all_exon_cache, {}, self.output_dir, "linear")

        if (self.rna_type == 0 or self.rna_type == 2):
            ## part for circular RNAs
            print("Finding probes for circular RNAs")
            if self.detect_dir:
                fasta_xenium = ""
                #fasta_xenium_linear = ""
                with open(self.detect_dir) as fp:

                    for line in fp:

                        # make sure we remove the header
                        if line.startswith('Chr\t'):
                            continue

                        line = line.rstrip()
                        current_line = line.split('\t')
                        if current_line[3] == "not_annotated":
                            continue

                        if self.gene_list and not self.id_list and current_line[3] not in self.gene_list:
                            continue
                            
                        sep = "_"
                        name = sep.join([current_line[3],
                                         current_line[0],
                                         current_line[1],
                                         current_line[2],
                                         current_line[5]])

                        if self.id_list and not self.gene_list and name not in self.id_list:
                            continue

                        circrna_length = int(current_line[2]) - int(current_line[1])

                        if circrna_length < 50:
                            print("Padlock probe design length too large for circRNA \"%s\".\nCircRNA length:"
                                  " %d, padlock probes are 40bp long." %
                                  (name, circrna_length))
                            exit(-1)

                        sep = "\t"
                        bed_string = sep.join([current_line[0],
                                               current_line[1],
                                               current_line[2],
                                               current_line[3],
                                               str(0),
                                               current_line[5]])
                        virtual_bed_file = pybedtools.BedTool(bed_string, from_string=True)
                        result = exons.intersect(virtual_bed_file, s=True)
                        fasta_bed_line_start = ""
                        fasta_bed_line_stop = ""

                        start = 0
                        stop = 0
                        
                        # for every circular RNA, fetch the information about
                        # second and first exons
                        #print("Current line", current_line)
                        flanking_exon_cache[name] = {}
                        exon_dict_circle_bed12[name] = []
                        for result_line in str(result).splitlines():
                            bed_feature = result_line.split('\t')
                            # this is a single-exon circRNA
                            #print("bed feature", bed_feature)
                            if bed_feature[1] == current_line[1] and bed_feature[2] == current_line[2]:
                                #print("Single exon condition")
                                # remove 1 bp from start and end to correct for the gap 
                                temp_bed_feature = bed_feature 
                                temp_bed_feature[1] = str(int(temp_bed_feature[1]) - 1)
                                #temp_bed_feature[2] = str(int(temp_bed_feature[2]) + 1)
                                result_line = "\t".join(temp_bed_feature)
                                #print("Updated result line", result_line)
                                fasta_bed_line_start += result_line + "\n"
                                start = 1
                                stop = 1
                                exon_dict_circle_bed12[name].append(bed_feature)

                            if bed_feature[1] == current_line[1] and start == 0:
                                #print("Start zero condition")
                                temp_bed_feature = bed_feature
                                temp_bed_feature[1] = str(int(temp_bed_feature[1]) - 1)
                                result_line = "\t".join(temp_bed_feature) 
                                fasta_bed_line_start += result_line + "\n"
                                start = 1
                                exon_dict_circle_bed12[name].append(bed_feature)

                            if bed_feature[2] == current_line[2] and stop == 0:
                                #print("Stop zero condition")
                                temp_bed_feature = bed_feature
                                temp_bed_feature[1] = str(int(temp_bed_feature[1]) - 1)
                                result_line = "\t".join(temp_bed_feature) 
                                fasta_bed_line_stop += result_line + "\n"
                                stop = 1
                                exon_dict_circle_bed12[name].append(bed_feature)

                            # these exons are kept for correctly drawing the circRNAs later
                            # not used for primer design
                            if bed_feature[1] > current_line[1] and bed_feature[2] < current_line[2]:
                                flanking_exon_cache[name][bed_feature[1] + "_" + bed_feature[2]] = 1

                        #print("Exon dict for BED12 file:", exon_dict_circle_bed12[name], len(exon_dict_circle_bed12[name]))
                        # first and last exons
                        virtual_bed_file_start = pybedtools.BedTool(fasta_bed_line_start, from_string=True)
                        virtual_bed_file_stop = pybedtools.BedTool(fasta_bed_line_stop, from_string=True)

                        virtual_bed_file_start = virtual_bed_file_start.sequence(fi=self.fasta_file, s=True)
                        virtual_bed_file_stop = virtual_bed_file_stop.sequence(fi=self.fasta_file, s=True)

                        if stop == 0 or start == 0:
                            print("Could not identify the exact exon-border of the circRNA.")
                            print("Will continue with non-annotated, manually extracted sequence.")
                            # we have to manually reset the start position

                            fasta_bed_line = "\t".join([current_line[0],
                                                        current_line[1],
                                                        current_line[2],
                                                        current_line[5]])
                            
                            exon_dict_circle_bed12[name].append(current_line)
                            virtual_bed_file_start = pybedtools.BedTool(fasta_bed_line, from_string=True)
                            virtual_bed_file_start = virtual_bed_file_start.sequence(fi=self.fasta_file, s=True)
                            virtual_bed_file_stop = ""
                        exon1 = ""
                        exon2 = ""

                        if virtual_bed_file_start:
                            exon1 = open(virtual_bed_file_start.seqfn).read().split("\n", 1)[1].rstrip()

                        if virtual_bed_file_stop:
                            exon2 = open(virtual_bed_file_stop.seqfn).read().split("\n", 1)[1].rstrip()

                        circ_rna_number += 1
                        print("extracting flanking exons for circRNA #", circ_rna_number, name, end="\n", flush=True)

                        if exon2 and not exon1:
                            exon1 = exon2
                            exon2 = ""

                        if (current_line[5] == "+"):
                            exon_cache[name] = {1: exon1, 2: exon2}
                            with open(exon_storage_tmp, 'a') as data_store:
                                data_store.write("\t".join([name, exon1, exon2, "\n"]))
                        elif (current_line[5] == "-"):
                            exon_cache[name] = {1: exon2, 2: exon1}
                            with open(exon_storage_tmp, 'a') as data_store:
                                data_store.write("\t".join([name, exon2, exon1, "\n"]))
                        else:
                            print("Strand information not present. Assuming positive strand")
                            exon_cache[name] = {1: exon1, 2: exon2}
                            with open(exon_storage_tmp, 'a') as data_store:
                                data_store.write("\t".join([name, exon1, exon2, "\n"]))                            
                        
            
            else:
                print("Please provide Circtools detect output Coordinate file via option -d.")
                sys.exit(-1)
            
            if not exon_cache:
                print("Could not find any circRNAs matching your criteria, exiting.")
                exit(-1)
            
            else:
                designed_probes_for_blast = []
                probe_bed = []
                ## padlock probe design part starts here
                
                # circular RNA for loop
                #print(exon_cache)
                for each_circle in exon_cache:
                    if (exon_cache[each_circle][2]) == "":
                        # this is a single exon circle so take first 25 and last 25
                        # bases from its sequence to create a scan sequence
                        scan_sequence = exon_cache[each_circle][1][-25:] + exon_cache[each_circle][1][:25]
                        #print(each_circle, exon_cache[each_circle][1][-25:], exon_cache[each_circle][1][:25])
                    else:
                        # this is a multiple exon circular RNA. Take last 25 bases of
                        # last exon and first 25 bases of first exon as a scan sequence
                        scan_sequence = exon_cache[each_circle][2][-25:] + exon_cache[each_circle][1][:25]
                        #print(each_circle, exon_cache[each_circle][2][-25:], exon_cache[each_circle][1][:25])
                    if (len(exon_dict_circle_bed12[each_circle]) == 1):
                        #print("CHECK if SINGLE-EXON or SOMETHING ELSE", each_circle, exon_dict_circle_bed12[each_circle])
                        circle_exon = exon_dict_circle_bed12[each_circle][0]
                    else:
                        circle_exon = exon_dict_circle_bed12[each_circle][1]
                    circle_exon = "_".join([circle_exon[x] for x in [3,0,1,2,5]])
                    
                    print("ID for matching junctions: ", circle_exon)
                    #if ( circle_exon in fasta_xenium_linear_dict.keys()):
                    #   #print("FASTA ENTRY", circle_exon, scan_sequence, fasta_xenium_linear_dict[circle_exon])
                    fasta_xenium += ">" + circle_exon + "\n" + scan_sequence + "\n"                     
                    
                    # Scan a 40bp window over this scan_sequence and run primer3 on each 40bp sequence
                    for i in range(0,len(scan_sequence)):
                        scan_window = scan_sequence[i:i+40]
                        if (len(scan_window) < 40):
                            break

                        junction = dict_ligation_junction[scan_window[19:21]]
                        # filter criteria for padlock probes - accepted ligation junction preferences
                        if (junction == "nonpreferred" ):
                            #print("NON_PREFERRED JUNCTIONS", each_circle)
                            continue
                        else:
                            primer3_calling(scan_window, each_circle+"_"+str(i), junction, designed_probes_for_blast)
                            # coordinates for BED file generation for IGV browser
                            #print(each_circle, exon_dict_circle_bed12[each_circle])
                            scan_coord_chr = each_circle.split("_")[1]
                            scan_coord_strand = each_circle.split("_")[4]
                            if (len(exon_dict_circle_bed12[each_circle]) == 1):
                                start = int(exon_dict_circle_bed12[each_circle][0][1])
                                end = int(exon_dict_circle_bed12[each_circle][0][2])                                
                            else:
                                start = int(exon_dict_circle_bed12[each_circle][0][1])
                                end = int(exon_dict_circle_bed12[each_circle][1][2])
                            
                            thick_start = start
                            thick_end = end
                            distance = end - start
                            block_start_2 = (distance - 25) + i
                            size2 = 25 - i
                            size1 = 40 - size2
                            probe_bed.append([scan_coord_chr, thick_start, thick_end, each_circle+"_"+scan_window, "0", scan_coord_strand, thick_start, thick_end, 
                                              track_color_dict[i], "2", str(size1)+","+str(size2), "0,"+str(block_start_2)])

                # this is the first time we look through the input file
                # we collect the primer sequences and unify everything in one blast query
                # create a list for mapping that contains names with and without index (with index doesnt work with formatter script)
                #designed_probes_for_blast = [["_".join(i[0].split("_")[:5])]+i[1:] for i in designed_probes_for_blast]
                primex_data_with_blast_results = probes_blast(designed_probes_for_blast, blast_xml_tmp)
                #print(primex_data_with_blast_results)

                # modify primex_data_with_blast_results for formatter script
                temp = primex_data_with_blast_results.strip().split("\n")
                primex_data_with_blast_results_storage = ""
                for each_element in temp:
                    each_element = each_element.split("\t")
                    each_element.pop(5)
                    primex_data_with_blast_results_storage = primex_data_with_blast_results_storage + "\t".join(each_element) + "\n"
                
                with open(blast_storage_tmp, 'w') as data_store:
                    data_store.write(primex_data_with_blast_results_storage)
                with open(bed_probes_circles, 'w') as f:
                    for line in probe_bed:
                        f.write("\t".join(map(str, line)))
                        f.write("\n")
        
                #print(flanking_exon_cache)
                if (self.no_svg):
                    print("No graphical representations SVG will be generated")
                else:
                    graphical_visualisation(primex_data_with_blast_results, exon_cache, flanking_exon_cache, self.output_dir, "circle")
        
        if (self.rna_type == 1 or self.rna_type == 2):
            with open(output_fasta_file_linear, 'w') as data_store:
                data_store.write(fasta_xenium_linear)
        if (self.rna_type == 0 or self.rna_type == 2):
            with open(output_fasta_file, 'w') as data_store:
                data_store.write(fasta_xenium)
        
        
        # need to define path top R wrapper
        primer_script = 'circtools_primex_formatter'
        primer_script = R_SCRIPT_PATH

        # ------------------------------------ run formatter script and write output to various files -----------------------
        # for formatter command
        no_svg_flag = ""
        if not self.no_svg:
            no_svg_flag = "FALSE"
        else:
            no_svg_flag = "TRUE"

        # formatter script calling for circular RNA probes
        if (self.rna_type == 0 or self.rna_type == 2):    
            print("Formatting circular RNA probe outputs")
            primex_data_formatted = os.popen(primer_script + " " +
                                             blast_storage_tmp + " "
                                             + "\"" + self.experiment_title + "\"" + " "
                                             + "\"" + no_svg_flag + "\"" #+ " "
                                             #+ "\"" + self.svg_dir + "\"" 
                                             ).read()

            with open(output_html_file, 'w') as data_store:
                data_store.write(primex_data_formatted)
            print("Writing circular results to "+output_html_file)

            # writing output file to CSV -> the format recommended by Xenium technical note
            print("Writing probe results to "+output_csv_file)
            fout = open(output_csv_file, 'wb')
            fout.write("CircRNAID,RBD5,RBD3,Tm_RBD5,Tm_RBD3,Tm_Full,GC_RBD5,GC_RBD3,Ligation_Junction\n".encode())
            for eachline in primex_data_with_blast_results_storage.split("\n"):
                if (eachline == ""):    continue
                eachline = eachline.split("\t")
                tempstr = "_".join(eachline[:5])
                fout.write((tempstr + "," + ",".join(eachline[5:13]) + "\n").encode())
            fout.close()

        if (self.rna_type == 1 or self.rna_type == 2):
            print("Formatting linear RNA probe outputs")
            primex_data_formatted_linear = os.popen(primer_script + " " +
                                             blast_storage_tmp_linear + " "
                                             + "\"" + self.experiment_title + "\"" + " "
                                             + "\"" + no_svg_flag + "\"" #+ " "
                                             #+ "\"" + self.svg_dir + "\"" 
                                             ).read()

            with open(output_html_file_linear, 'w') as data_store:
                data_store.write(primex_data_formatted_linear)
            print("Writing linear results to "+output_html_file_linear)

            # writing output file to CSV for linear RNA probes
            print("Writing linear probe results to "+output_csv_file_linear)
            fout = open(output_csv_file_linear, 'wb')
            fout.write("Gene,RBD5,RBD3,Tm_RBD5,Tm_RBD3,Tm_Full,GC_RBD5,GC_RBD3,Ligation_Junction\n".encode())
            for eachline in primex_data_with_blast_results_linear_storage.split("\n"):
                if (eachline == ""):    continue
                eachline = eachline.split("\t")
                tempstr = "_".join(eachline[:5])
                fout.write((tempstr + "," + ",".join(eachline[5:13]) + "\n").encode())
            fout.close()
        print("Cleaning up")
        """      
        ## cleanup / delete tmp files
        os.remove(exon_storage_tmp)
        os.remove(blast_storage_tmp)
        os.remove(blast_xml_tmp)
        """
