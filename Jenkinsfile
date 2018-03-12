pipeline {
  agent {
      label 'master'
  }
  stages {
    stage('Transform') {
      agent {
        docker {
          image 'cloudfluff/databaker'
          reuseNode true
        }
      }
      steps {
        sh 'jupyter-nbconvert --to python --stdout Transform_CN8_Non-EU_cod_XXXX_to_WDA.ipynb | python'
      }
    }
    stage('Grafter test') {
      agent {
        docker {
          image 'cloudfluff/ons-wda-grafter'
          reuseNode true
        }
      }
      steps {
        sh 'grafter run ons-graft.import.pipeline/data-baker data/out/CN8_Non-EU_cod_2012.csv data/out/CN8_Non-EU_cod_2013.csv data/out/CN8_Non-EU_cod_2014.csv data/out/CN8_Non-EU_cod_2015.csv data/out/CN8_Non-EU_cod_2016.csv "ONS_BoP" data/out/CN8_Non-EU_cod_20XX.nq'
      }
    }
  }
  post {
    always {
      archiveArtifacts 'out/*'
    }
  }
}