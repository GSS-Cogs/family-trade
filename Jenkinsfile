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
      }
    }
  }
  post {
    always {
      archiveArtifacts 'out/*'
    }
  }
}