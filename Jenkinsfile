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
      }
    }
    stage('Publish') {
      steps {
        script {
          def PMD = 'https://production-drafter-ons-alpha.publishmydata.com'
          def drafts = readJSON(text: httpRequest(acceptType: 'APPLICATION_JSON',
            authentication: 'onspmd',
            httpMode: 'GET',
            url: "${PMD}/v1/draftsets").content)
          def jobDraft = drafts.find  { it['display-name'] == env.JOB_NAME }
          if (jobDraft) {
            def rmDraftResponse = httpRequest(acceptType: 'APPLICATION_JSON',
              authentication: 'onspmd', httpMode: 'DELETE', url: "${PMD}/v1/draftset/${jobDraft.id}")
            if (rmDraftResponse.status == 202) {
              def rmDraftJob = readJSON(text: rmDraftResponse.content)
              def running = true
              def success = false
              while (running) {
                jobResponse = httpRequest(acceptType: 'APPLICATION_JSON', authentication: 'onspmd',
                  httpMode: 'GET', url: "${PMD}/${rmDraftJob['finished-job']}")
                if (jobResponse.status == 404) {
                  if (readJSON(text: jobResponse.content)['restart-id'] != rmDraftJob['restart-id']) {
                    running = false
                  } else {
                    sleep 10
                  }
                } else if (jobResponse.status == 200) {
                  running = false
                  if (readJSON(text: jobResponse.content)['restart-id'] == rmDraftJob['restart-id']) {
                    success = true
                  }
                }
              }
            }
          }
          def newDraftResponse = httpRequest(acceptType: 'APPLICATION_JSON', authentication: 'onspmd',
            httpMode: 'POST', url: "${PMD}/v1/draftsets?display-name=${env.JOB_NAME}")
          if (newDraftResponse.status == 200) {
            drafts = readJSON(text: httpRequest(acceptType: 'APPLICATION_JSON',
              authentication: 'onspmd',
              httpMode: 'GET',
              url: "${PMD}/v1/draftsets").content)
            jobDraft = drafts.find { it['display-name'] == env.JOB_NAME }
          }
        }
      }
    }
  }
  post {
    always {
      archiveArtifacts 'out/*'
    }
  }
}
