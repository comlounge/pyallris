This folder should contain preread data for known cities as BSON export files so they can be imported easily to a streets collection in mongo.
pyallris only needs the streets at this moment and not the locations collection

aaachen-alsdorf-wuerselen-with-geo.bson also contains lat/lng for each street which is created by running scripts/get_street_geodata.py (or the console script generated from that)
