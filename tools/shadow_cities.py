"""

As input, takes the an urbanization prospects file and a recent shadow topology
to cross information.

Rob's topology contains cities from which Ripe Atlas probes were used to evaluate link latencies
between them. This script aims to cross this information with the United Nations's database to  offer
a finer-grained placement of Tor clients when generating a shadow-plugin-tor topology of Tor clients

"""

import sys, os
import argparse
import pandas as pd
import pdb
import json

class City:

    def __init__(self, citycode, country, population, lat, longit):
        self.citycode = citycode
        self.country = country
        self.population = population
        # geo coord 
        self.lat = lat
        self.long = longit

class RipeProbe:
    def __init__(self, ip, city):
        self.ip = ip
        self.city = city


parser = argparse.ArgumentParser()
parser.add_argument("--shadowtopology")
parser.add_argument("--cityinfo")

def main(args):
    
    cities = {}
    ripe_probes = {}
    pmatrix = {}
    with open(args.shadowtopology) as f:
        line = f.readline()
        while line:
            if "node id" in line: # start to parse a node!
                line = f.readline()
                ip =  line.split('<data key="d1">')[1].split("</data>")[0] # location info
                line = f.readline()
                if "d2" in line:
                    location = int(line.split('<data key="d2">')[1].split("</data>")[0]) # location info
                else:
                    continue
                countrycode = int(f.readline().split('<data key="d3">')[1].split("</data>")[0])
                city = City(location, countrycode, None, None, None)
                if location not in cities:
                    cities[location] = city 
                ripe_probes[ip] = RipeProbe(ip, city)
            elif "edge source" in line: #building the penalty matrix
		# first parse info
                tab = line.split(" ")
                source = tab[1].split("source=")[1]
                dest = tab[2].split("target=")[1]
                line = f.readline() #latency
                if "d6" in line:
                    latency = float(line.split('<data key="d6">')[1].split("</data>")[0])
                else:
                    print("No latency information for this edge?")
                line = f.readline() #loss
                if "d7" in line:
                    loss = float(line.split('<data key="d6">')[1].split("</data>")[0])	
		
                if source not in pmatrix:
                    pmatrix[source] = {dest: latency*loss}
                else:
                    pmatrix[source][dest] = latency*loss

            line = f.readline()
		
    
    ## Note: doesn't look like the city code match. What is shadow's city code?
    xls_population = pd.ExcelFile(args.cityinfo)
    cityinfo = xls_population.parse(0, header=16)
    #pdb.set_trace()
    for i in range(0, len(cityinfo['City Code'])):
        if int(cityinfo['City Code'][i]) in cities:
            cities[int(cityinfo['City Code'][i])] = cityinfo[2020][i]
            print("adding info for city {0}".format(cityinfo['City Code'][i]))

    with open('cityinfo_shadow.json', 'w') as jsonfile: 
        json.dump(cities, jsonfile)
    with open('pmatrix_shadow.json', 'w') as jsonfile:
        json.dump(pmatrix, jsonfile)

if __name__ == "__main__":
    sys.exit(main(parser.parse_args()))

