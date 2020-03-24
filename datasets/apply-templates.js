const dataset = window.location.search.substring(1);

function datasetFetcher(endpoint, landingPages) {
    return $.post({
        url: endpoint,
        data: {
            "query": `PREFIX dcat: <http://www.w3.org/ns/dcat#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT DISTINCT ?page ?ds ?label WHERE {
  ?ds dcat:landingPage ?page;
  rdfs:label ?label
} VALUES (?page) {
${landingPages.map(x => `(<${x}>)`).join(' ')}
}`
        },
        dataType: 'json',
        headers: {"Accept": "application/sparql-results+json"}
    }).then(function(results) {
        return results.results.bindings.map(binding => {
            return {
                landingPage: binding.page.value,
                uri: binding.ds.value,
                label: binding.label.value
            };
        });
    });
};

if (dataset) {
    Handlebars.registerHelper('ifObject', function(item, options) {
        if (typeof item === "object") {
            return options.fn(this);
        } else {
            return options.inverse(this);
        }
    });
    $.get({
        url: "etl.hbs",
        dataType: "html"
    }, function(source) {
        const template = Handlebars.compile(source);
        $.getJSON('info.json', function(mainInfo) {
            $.getJSON(dataset + "/info.json", function (info) {
                let fetchDatasets;
                if (mainInfo.hasOwnProperty('sparql')) {
                    fetchDatasets = datasetFetcher(mainInfo.sparql, [info.landingPage]);
                } else {
                    fetchDatasets = $.Deferred();
                    fetchDatasets.resolve([]);
                }
                fetchDatasets.done(function(datasets) {
                    if (mainInfo.hasOwnProperty('pmd')) {
                        datasets = datasets.map(function(ds) {
                            return {
                                uri: mainInfo.pmd + '/resource?uri=' + encodeURIComponent(ds.uri),
                                label: ds.label
                            }
                        });
                    }
                    $("#body").html(template({
                        "dataset_path": dataset,
                        "main": mainInfo,
                        "dataset": info,
                        "jenkins_path": mainInfo.jenkins.path.map(function (p) {
                            return 'job/' + p;
                        }).join('/'),
                        "jenkins_buildicon": 'buildStatus/icon?job=' + encodeURIComponent(mainInfo.jenkins.path.join('/') + '/'),
                        "datasets": datasets
                    }));
                });
                document.title = info.title;
            });
        });
    });
} else {
    Handlebars.registerHelper('rowClass', function(f, i) {
      if (i.hasOwnProperty('families') && !i.families.includes(f)) {
        return 'text-danger';
      } else if (i.hasOwnProperty('extract') && i.extract.hasOwnProperty('stage')) {
        if (i.extract.stage == 'Prioritized') {
          return 'text-body';
        } else {
          return 'text-muted';
        }
      } else {
        return 'text-body';
      }
    });
    $.get({
        url: "table.hbs",
        datatype: "html",
    }, function(source) {
        const template = Handlebars.compile(source);
        $.getJSON('info.json', function(info) {
            document.title = "Dataset family: " + info.family;
            const fetches = info.pipelines.map(function (pipeline) {
                return $.getJSON(pipeline + '/info.json');
            });
            $.when.apply($, fetches).then(function() {
                const allInfo = arguments;
                let collected = info.pipelines.map(function (pipeline, i) {
                    return {
                        'directory': pipeline,
                        'number': i + 1,
                        'info': allInfo[i][0]
                    };
                });
                let fetchDatasets;
                if (info.hasOwnProperty('sparql')) {
                    fetchDatasets = datasetFetcher(info.sparql, collected.map(p => p.info.landingPage));
                } else {
                    fetchDatasets = $.Deferred();
                    fetchDatasets.resolve([]);
                }
                fetchDatasets.done(function(datasets) {
                    collected = collected.map(p => {
                        p.datasets = datasets.filter(ds => ds.landingPage == p.info.landingPage);
                        return p;
                    });
                    $("#body").html(template({
                        "family": info.family,
                        "github": info.github,
                        "jenkins_base": info.jenkins.base,
                        "jenkins_path": info.jenkins.path.map(function (p) {
                            return 'job/' + p;
                        }).join('/'),
                        "jenkins_buildicon": 'buildStatus/icon?job=' + encodeURIComponent(info.jenkins.path.join('/') + '/'),
                        "pipelines": collected
                    }));
                });
            });
        });
    });
}
