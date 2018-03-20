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
        sh 'jupyter-nbconvert --to python --stdout Balanceofpayments2017q3_TabF.ipynb | python'
      }
    }
  }
  post {
    always {
      archiveArtifacts 'out/*'
    }
  }
}