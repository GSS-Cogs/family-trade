pipeline {
  agent {
      label 'master'
  }
  stages {
    stage('Transform') {
      agent {
        docker {
          image 'cloudfluff/databaker'
          args "-v '$env.WORKSPACE':/workspace"
          reuseNode true
        }
      }
      steps {
        sh 'jupyter-nbconvert --to python --stdout Balanceofpayments2017q3_TabA.ipynb | python'
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
        sh 'grafter run ons-graft.import.pipeline/data-baker data/out/balanceofpayments2017q3.csv "ONS_BoP" data/out/balanceofpayments2017q3.nq'
      }
    }

  }
  post {
    always {
      archiveArtifacts 'out/*'
    }
  }
}