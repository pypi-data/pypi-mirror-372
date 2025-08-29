# This script is used to fetch exon sequences per circle 
# using the REST API by ENSMBLE

import sys
import requests

class sequence(object):

    def __init__(self, species, coord) -> None:
        self.species = species
        self.coord = coord

    def fetch_sequence(self):

        chr = str(self.coord[0])
        start = str(self.coord[1])
        end = str(self.coord[2])

        server = "https://rest.ensembl.org"
        ext = "/sequence/region/" + self.species + "/" + chr + ":" + start + ".." + end + "?"
 
        try:
            r = requests.get(server+ext, headers={ "Content-Type" : "text/plain"})
        except requests.exceptions.RequestException as e:
            raise SystemExit(e)
 
        if not r.ok:
            r.raise_for_status()
            sys.exit()
        self.r = r
        print("WARNING! "+ r.headers["X-RateLimit-Remaining"] + " REST API requests remaining!")
        #print(r.text)

        return(r.text)

#obj = sequence("human", [1, 43829790, 43829804])
#obj.fetch_sequence()