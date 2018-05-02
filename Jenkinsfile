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
        sh "jupyter-nbconvert --to python --stdout HMRC_RTS_Mass.ipynb | ipython"
        sh "jupyter-nbconvert --to python --stdout HMRC_RTS_Value.ipynb | ipython"
      }
    }
  }
  post {
    always {
      archiveArtifacts 'out/*'
    }
  }
}
