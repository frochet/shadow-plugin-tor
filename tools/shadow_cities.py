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


parser = argparse.ArgumentParser()
parser.add_argument("--shadowtopology")
parser.add_argument("--cityinfo")

def main(args):
    
    cities = {}
    with open(args.shadowtopology) as f:
        line = f.readline()
        while line:
            if "node id" in line: # start to parse a node!
                f.readline() #skip ip
                line = f.readline()
                if "d2" in line:
                    location = int(line.strip('<data key="d2"/>\n')) # location info
                else:
                    continue
                countrycode = f.readline().strip('<data key="d3"/>\n')
                if location not in cities:
                    cities[location] = City(location, countrycode, None, None, None)
            line = f.readline()
    
    xls_population = pd.ExcelFile(args.cityinfo)
    cityinfo = xls_population.parse(0, header=16)
    pdb.set_trace()
    for i in range(0, len(cityinfo['City Code'])):
        if int(cityinfo['City Code'][i]) in cities:
            cities[int(cityinfo['City Code'][i])] = cityinfo[2020][i]
            print("adding info for city {0}".format(cityinfo['City Code'][i]))

    with open('cityinfo_shadow.json', 'w') as jsonfile:
        json.dump(cities, jsonfile)


if __name__ == "__main__":
    sys.exit(main(parser.parse_args()))

