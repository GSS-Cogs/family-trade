pipeline {
  agent {
      label 'master'
  }
  stages {
    stage('Prepare CSVW') {
      agent {
        docker {
          image 'cloudfluff/databaker'
          reuseNode true
        }
      }
      steps {
        sh 'jupyter-nbconvert --to python --stdout Prepare_sources.ipynb | python'
      }
    }
    stage('Fetch countries') {
      agent {
        docker {
          image 'cloudfluff/databaker'
          reuseNode true
        }
      }
      steps {
        sh 'jupyter-nbconvert --to python --stdout Fetch_countries.ipynb | python'
      }
    }
    stage('CSV2RDF') {
      agent {
        docker {
          image 'cloudfluff/rdf-tabular'
          reuseNode true
        }
      }
      steps {
        sh 'rdf serialize --input-format tabular --output-format ttl --stream out/cn8_2012.csv > out/cn8_2012.ttl'
        sh 'rdf serialize --input-format tabular --output-format ttl --stream out/cn8_2013.csv > out/cn8_2013.ttl'
        sh 'rdf serialize --input-format tabular --output-format ttl --stream out/cn8_2014.csv > out/cn8_2014.ttl'
        sh 'rdf serialize --input-format tabular --output-format ttl --stream out/cn8_2015.csv > out/cn8_2015.ttl'
        sh 'rdf serialize --input-format tabular --output-format ttl --stream out/cn8_2016.csv > out/cn8_2016.ttl'
      }
    }
    stage('Normalize Cube') {
      steps {
        sh 'java -cp bin/sparql uk.org.floop.updateInPlace.Run -q sparql-normalize out/cn8_2012.ttl'
        sh 'java -cp bin/sparql uk.org.floop.updateInPlace.Run -q sparql-normalize out/cn8_2013.ttl'
        sh 'java -cp bin/sparql uk.org.floop.updateInPlace.Run -q sparql-normalize out/cn8_2014.ttl'
        sh 'java -cp bin/sparql uk.org.floop.updateInPlace.Run -q sparql-normalize out/cn8_2015.ttl'
        sh 'java -cp bin/sparql uk.org.floop.updateInPlace.Run -q sparql-normalize out/cn8_2016.ttl'
      }
    }
    stage('Test') {
      steps {
        sh 'java -cp bin/sparql uk.org.floop.sparqlTestRunner.Run -i -t tests/qb -r reports/TESTS-qb-2012.xml out/cn8_2012.ttl'
        sh 'java -cp bin/sparql uk.org.floop.sparqlTestRunner.Run -i -t tests/qb -r reports/TESTS-qb-2013.xml out/cn8_2013.ttl'
        sh 'java -cp bin/sparql uk.org.floop.sparqlTestRunner.Run -i -t tests/qb -r reports/TESTS-qb-2014.xml out/cn8_2014.ttl'
        sh 'java -cp bin/sparql uk.org.floop.sparqlTestRunner.Run -i -t tests/qb -r reports/TESTS-qb-2015.xml out/cn8_2015.ttl'
        sh 'java -cp bin/sparql uk.org.floop.sparqlTestRunner.Run -i -t tests/qb -r reports/TESTS-qb-2016.xml out/cn8_2016.ttl'
       }
    }
  }
  post {
    always {
      archiveArtifacts 'out/*'
    }
  }
}