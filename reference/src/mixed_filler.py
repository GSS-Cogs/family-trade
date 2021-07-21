#!/usr/bin/env python3

import argparse
import csv

from rdflib import Graph, URIRef, RDFS
from rdflib.namespace import SKOS

parser = argparse.ArgumentParser(description='Fill labels & check parents of mixed codelists')
parser.add_argument('codelist', type=argparse.FileType('r+'))
args = parser.parse_args()

reader = csv.DictReader(args.codelist)
updated_rows = []
for row in reader:
    if row['Label'] is None or row['Label'] == '':
        uri = row['URI']
        g = Graph()
        g.parse(uri, format='application/rdf+xml')
        label = g.value(URIRef(uri), RDFS.label)
        if label is None:
            label = g.value(URIRef(uri), SKOS.prefLabel)
        row['Label'] = label
    updated_rows.append(row)

args.codelist.seek(0)
writer = csv.DictWriter(args.codelist, reader.fieldnames)
writer.writeheader()
for row in updated_rows:
    writer.writerow(row)

args.codelist.close()