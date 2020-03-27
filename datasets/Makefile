datasets = $(sort $(dir $(wildcard */info.json)))
transforms = $(sort $(dir $(wildcard */main.py)))

%.ipynb : %.py
	jupytext --to notebook $<

mains = $(transforms:/=/main.ipynb)

$(mains): %.ipynb : %.py
	for pyfile in $(dir $<)*.py; do \
	  docker run -v $(CURDIR):/workspace -w /workspace gsscogs/databaker jupytext --to notebook "$$pyfile" ; \
	done

all_mains: $(mains)

outputs = $(transforms:/=/out)

$(outputs): $(mains)
	docker run -v $(CURDIR)/$(dir $@):/workspace -w /workspace gsscogs/databaker jupyter-nbconvert --output-dir=out --ExecutePreprocessor.timeout=None --execute main.ipynb

all_outputs: $(outputs)


.PHONY: csv_lints $(outputs)
csv_lints: $(outputs)
	for schema in $</*-schema.json; do \
	  docker run -v $(CURDIR)/$(dir $@):/workspace -w /workspace gsscogs/csvlint csvlint -s $$schema ; \
	done

print-%  : ; @echo $* = $($*)

clean:
	rm -f $(datasets:/=/*.ipynb)
	rm -rf $(datasets:/=/out)
