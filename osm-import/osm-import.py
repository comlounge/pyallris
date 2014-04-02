# encoding: utf-8

"""
Importiert Knoten und Strassen aus der angegebenen OSM-Datei in MongoDB.
Die Datenbank wird vorher geleert!

Copyright (c) 2012 Marian Steinbach

Hiermit wird unentgeltlich jeder Person, die eine Kopie der Software und
der zugehörigen Dokumentationen (die "Software") erhält, die Erlaubnis
erteilt, sie uneingeschränkt zu benutzen, inklusive und ohne Ausnahme, dem
Recht, sie zu verwenden, kopieren, ändern, fusionieren, verlegen,
verbreiten, unterlizenzieren und/oder zu verkaufen, und Personen, die diese
Software erhalten, diese Rechte zu geben, unter den folgenden Bedingungen:

Der obige Urheberrechtsvermerk und dieser Erlaubnisvermerk sind in allen
Kopien oder Teilkopien der Software beizulegen.

Die Software wird ohne jede ausdrückliche oder implizierte Garantie
bereitgestellt, einschließlich der Garantie zur Benutzung für den
vorgesehenen oder einen bestimmten Zweck sowie jeglicher Rechtsverletzung,
jedoch nicht darauf beschränkt. In keinem Fall sind die Autoren oder
Copyrightinhaber für jeglichen Schaden oder sonstige Ansprüche haftbar zu
machen, ob infolge der Erfüllung eines Vertrages, eines Delikts oder anders
im Zusammenhang mit der Software oder sonstiger Verwendung der Software
entstanden.
"""

import sys

sys.path.append('./')

import config
from imposm.parser import OSMParser
from pymongo import MongoClient
from bson.son import SON

import pprint
import re

pattern1 = re.compile(".*straße$")
pattern2 = re.compile(".*Straße$")
pattern3 = re.compile(".*platz$")
pattern4 = re.compile(".*Platz$")



# Wir legen alle nodes in diesem dict ab. Das bedeutet, dass wir
# ausreichend Arbeitsspeicher voraussetzen.
nodes = {}


class NodeCollector(object):
    def coords(self, coords):
        for osmid, lon, lat in coords:
            if osmid not in nodes:
                nodes[osmid] = {
                    'osmid': osmid,
                    'location': [lon, lat]
                }
            nodes[osmid]['lat'] = lat
            nodes[osmid]['lon'] = lat
    #def nodes(self, n):
    #    for osmid, tags, coords in n:
    #        nodes[osmid] = {
    #            'osmid': osmid,
    #            'location': [coords[0], coords[1]],
    #            'tags': tags
    #        }


class StreetCollector(object):
    wanted_nodes = {}
    streets = []
    #street_to_node = []

    def ways(self, ways):
        #global nodes
        for osmid, tags, refs in ways:
            if 'highway' not in tags or 'name' not in tags:
                # Wenn der way keinen "highway" tag hat oder keinen
                # Namen, ist er für uns nicht interessant.
                continue
            street = {
                'osmid': osmid,
                'name': tags['name'],
                'nodes': []
            }
            for ref in refs:
                if ref not in nodes:
                    continue
                self.wanted_nodes[ref] = True
                #self.street_to_node.append((osmid, ref))
                street['nodes'].append(ref)
            self.streets.append(street)

if __name__ == '__main__':
    
    filename = sys.argv[1]          # osm input file 
    city = sys.argv[2].lower()      # city name in lowercase
    rs = sys.argv[3]                # regionalschlüssel

    connection = MongoClient(config.DB_HOST, config.DB_PORT)
    db = connection[config.DB_NAME]
    db.locations.remove({'rs': rs})
    db.locations.ensure_index('osmid', unique=True)
    db.locations.ensure_index('name')
    db.locations.ensure_index([('nodes.location', '2dsphere')])
    db.streets.remove()

    print "Sammle nodes..."
    nodecollector = NodeCollector()
    p = OSMParser(concurrency=2, coords_callback=nodecollector.coords)
    p.parse(filename)

    print "Sammle Straßen..."
    streetcollector = StreetCollector()
    p = OSMParser(concurrency=2, ways_callback=streetcollector.ways)
    p.parse(filename)

    # Iteriere über alle gesammelten nodes und finde die,
    # welche von anderen Objekten referenziert werden.
    wanted_nodes = {}
    non_existing_nodes = 0
    for ref in streetcollector.wanted_nodes.keys():
        if ref in nodes:
            wanted_nodes[ref] = nodes[ref]
        else:
            non_existing_nodes += 1

    # reduziere das nodes dict auf das wesentliche
    wanted_nodes.values()  # TODO: Das ergibt keinen Sinn.

    unique_streets = {} # mapping name -> location ids
    for street in streetcollector.streets:
        for n in range(len(street['nodes'])):
            street['nodes'][n] = {
                'osmid': street['nodes'][n],
                'location': SON([
                    ('type', 'Point'),
                    ('coordinates', wanted_nodes[street['nodes'][n]]['location'])
                ])
            }

        street['rs'] = rs
        _id = db.locations.save(street)
        unique_streets.setdefault(street['name'], []).append(_id)

    # now we create records for searching for this street name which points
    # back to the location record of it. We also generate some alternative forms
    # also note that the locations collection can contain multiple entries for
    # a street (e.g. 'Am Tivoli' has 4 for Aachen, Germany)
    all_streets = {}

    for name, ids in unique_streets.items():

        all_streets[name.lower()] = {
            'name' : name.lower(),  # this we search for (we compare lowercase always)
            'city' : city,      # the city we are in
            'original' : name,      # this is the original and official name
            'locations' : ids,      # these are the ids referencing the osm entry in the locations collection
        }

        # compute alternatives
        alternatives = []
        if pattern1.match(name):
            alternatives.append(name.replace('straße', 'str.'))
            alternatives.append(name.replace('straße', 'str'))
            alternatives.append(name.replace('straße', ' straße'))
            alternatives.append(name.replace('straße', ' str.'))
            alternatives.append(name.replace('straße', ' str'))
        elif pattern2.match(name):
            alternatives.append(name.replace('Straße', 'Str.'))
            alternatives.append(name.replace('Straße', 'Str'))
            alternatives.append(name.replace(' Straße', 'straße'))
            alternatives.append(name.replace(' Straße', 'str.'))
            alternatives.append(name.replace(' Straße', 'str'))
        elif pattern3.match(name):
            alternatives.append(name.replace('platz', 'pl.'))
            alternatives.append(name.replace('platz', 'pl'))
        elif pattern4.match(name):
            alternatives.append(name.replace('Platz', 'Pl.'))
            alternatives.append(name.replace('Platz', 'Pl'))
        for alt in alternatives:
            all_streets[alt.lower()] = {
                'name' : alt.lower(),
                'original' : name,
                'city' : city,
                'locations' : ids,      # these are the ids referencing the osm entry in the locations collection
            }
    db.streets.remove({'city' : city})
    db.streets.insert(all_streets.values())
