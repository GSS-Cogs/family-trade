CSVLINT := docker run -v $(CURDIR):/workspace gsscogs/csvlint csvlint

test:
	$(CSVLINT) -s codelists-metadata.json
	$(CSVLINT) -s columns.csv-metadata.json
	$(CSVLINT) -s components.csv-metadata.json
