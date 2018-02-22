pipeline {
  agent {
      label 'master'
  }
  stages {
    stage('Transform') {
      agent {
        docker {
          image 'cloudfluff/databaker'
          args "-v ${env.WORKSPACE}:/workspace"
          reuseNode true
        }
      }
      steps {
        sh 'jupyter-nbconvert --to python --stdout Transform_CN8_Non-EU_cod_XXXX_to_WDA.ipynb | python'
      }
    }
  }
  post {
    always {
      archiveArtifacts 'out/*'
    }
  }
}