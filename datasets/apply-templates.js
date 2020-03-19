const dataset = window.location.search.substring(1);
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
                var fetchDatasets;
                if (mainInfo.hasOwnProperty('pmd')) {
                    fetchDatasets = $.post({
                        url: mainInfo.pmd + '/sparql',
                        data: {
                            "query": `PREFIX dcat: <http://www.w3.org/ns/dcat#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT DISTINCT ?ds ?label WHERE { ?ds dcat:landingPage <${info.landingPage}>; rdfs:label ?label }`
                        },
                        dataType: 'json',
                        headers: {"Accept": "application/sparql-results+json"}
                    }).then(function(results) {
                        return results.results.bindings.map(binding => {
                                return {
                                    uri: binding.ds.value,
                                    label: binding.label.value
                                };
                            });
                    });
                } else {
                    fetchDatasets = $.Deferred();
                    fetchDatasets.resolve([]);
                }
                fetchDatasets.done(function(datasets) {
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
                const collected = info.pipelines.map(function (pipeline, i) {
                    return {
                        'directory': pipeline,
                        'number': i + 1,
                        'info': allInfo[i][0]
                    };
                });
                $("#body").html(template({
                    "family": info.family,
                    "github": info.github,
                    "jenkins_base": info.jenkins.base,
                    "jenkins_path": info.jenkins.path.map(function(p) {return 'job/' + p;}).join('/'),
                    "jenkins_buildicon": 'buildStatus/icon?job=' + encodeURIComponent(info.jenkins.path.join('/') + '/'),
                    "pipelines": collected
                }));
            });
        });
    });
}
