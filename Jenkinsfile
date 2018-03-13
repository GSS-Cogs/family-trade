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
        sh 'jupyter-nbconvert --to python --stdout Prepare_sources.ipynb | python'
      }
    }
  }
  post {
    always {
      archiveArtifacts 'out/*'
    }
  }
}