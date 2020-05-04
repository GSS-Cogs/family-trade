CSVLINT  := docker run -v $(CURDIR):/workspace -w /workspace gsscogs/csvlint csvlint
TABLE2QB := docker run -v $(CURDIR):/workspace -w /workspace cloudfluff/table2qb table2qb
CSV2RDF  := docker run -v $(CURDIR):/workspace -w /workspace gsscogs/csv2rdf csv2rdf

test:
	$(CSVLINT) -s codelists-metadata.json
	$(CSVLINT) -s columns.csv-metadata.json
	$(CSVLINT) -s components.csv-metadata.json

components-old.trig: components.csv
	$(TABLE2QB) exec components-pipeline --input-csv components.csv --base-uri http://gss-data.org.uk/ --output-file components-old.trig --graph http://gss-data.org.uk/graph/components

components-old.ttl: components.csv
	$(TABLE2QB) exec components-pipeline --input-csv components.csv --base-uri http://gss-data.org.uk/ --output-file components-old.ttl

components-new.ttl: components.csv components.csv-metadata.json
	$(CSV2RDF) -t components.csv -u components.csv-metadata.json -m annotated -o components-new.ttl
