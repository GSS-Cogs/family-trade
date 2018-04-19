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
        sh "jupyter-nbconvert --to python --stdout 'CPA to Tidy data(Code Classification merge).ipynb' | ipython"
      }
    }
  }
  post {
    always {
      archiveArtifacts 'out/*'
    }
  }
}