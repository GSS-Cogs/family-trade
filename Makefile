csv2rdf:
	docker run -v "$(CURDIR)":/workspace:z cloudfluff/rdf-tabular rdf serialize --input-format tabular --output-format ttl --stream out/cn8_2012.csv > out/cn8_2012.ttl
	docker run -v "$(CURDIR)":/workspace:z cloudfluff/rdf-tabular rdf serialize --input-format tabular --output-format ttl --stream out/cn8_2013.csv > out/cn8_2013.ttl
	docker run -v "$(CURDIR)":/workspace:z cloudfluff/rdf-tabular rdf serialize --input-format tabular --output-format ttl --stream out/cn8_2014.csv > out/cn8_2014.ttl
	docker run -v "$(CURDIR)":/workspace:z cloudfluff/rdf-tabular rdf serialize --input-format tabular --output-format ttl --stream out/cn8_2015.csv > out/cn8_2015.ttl
	docker run -v "$(CURDIR)":/workspace:z cloudfluff/rdf-tabular rdf serialize --input-format tabular --output-format ttl --stream out/cn8_2016.csv > out/cn8_2016.ttl

normalize:
	java -cp bin/sparql uk.org.floop.updateInPlace.Run -q sparql-normalize out/cn8_2012.ttl

test:
	java -cp bin/sparql uk.org.floop.sparqlTestRunner.Run -i -t tests/qb -r reports/TESTS-qb.xml out/cn8_2012.ttl
