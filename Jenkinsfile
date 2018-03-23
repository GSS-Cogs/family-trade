pipeline {
  agent {
      label 'master'
  }
  stages {
    stage('Clean') {
      steps {
        sh 'rm -rf out'
      }
    }
    stage('Transform') {
      agent {
        docker {
          image 'cloudfluff/databaker'
          reuseNode true
        }
      }
      steps {
        sh 'jupyter-nbconvert --to python --stdout Balanceofpayments2017q3_TabF.ipynb | ipython'
        sh 'jupyter-nbconvert --to python --stdout Pinkbook2017chapter3_3.1.ipynb | ipython'
        sh 'jupyter-nbconvert --to python --stdout Pinkbook2017chapter3_3.2.ipynb | ipython'
        sh 'jupyter-nbconvert --to python --stdout Pinkbook2017chapter3_3.3.ipynb | ipython'
        sh 'jupyter-nbconvert --to python --stdout Pinkbook2017chapter3_3.4.ipynb | ipython'
        sh 'jupyter-nbconvert --to python --stdout Pinkbook2017chapter3_3.5.ipynb | ipython'
        sh 'jupyter-nbconvert --to python --stdout Pinkbook2017chapter3_3.6.ipynb | ipython'
        sh 'jupyter-nbconvert --to python --stdout Pinkbook2017chapter3_3.7.ipynb | ipython'
        sh 'jupyter-nbconvert --to python --stdout Pinkbook2017chapter3_3.8.ipynb | ipython'
        sh 'jupyter-nbconvert --to python --stdout Pinkbook2017chapter3_3.9.ipynb | ipython'
        sh 'jupyter-nbconvert --to python --stdout Pinkbook2017chapter3_3.10.ipynb | ipython'
      }
    }
    state('Test') {
      agent {
        docker {
          image 'cloudfluff/rdf-tabular'
          reuseNode true
        }
      }
      steps {
        sh 'rdf validate --input-format=tabular metadata/balanceofpayments2017q3.csv-metadata.json'
      }
    }
  }
  post {
    always {
      archiveArtifacts 'out/*'
    }
  }
}