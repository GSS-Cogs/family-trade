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
            url: "${PMD}/v1/draftsets?include=owned").content)
          def jobDraft = drafts.find  { it['display-name'] == env.JOB_NAME }
          if (jobDraft) {
            def rmDraftResponse = httpRequest(acceptType: 'APPLICATION_JSON',
              authentication: 'onspmd', httpMode: 'DELETE', url: "${PMD}/v1/draftset/${jobDraft.id}")
            if (rmDraftResponse.status == 202) {
              def rmDraftJob = readJSON(text: rmDraftResponse.content)
              if (!waitForJob("${PMD}/${rmDraftJob['finished-job']}", rmDraftJob['restart-id'])) {
                error "waiting to delete job draftset"
              }
            }
          }
          def newDraftResponse = httpRequest(acceptType: 'APPLICATION_JSON', authentication: 'onspmd',
            httpMode: 'POST', url: "${PMD}/v1/draftsets?display-name=${env.JOB_NAME}")
          if (newDraftResponse.status == 200) {
            newJobDraft = readJSON(text: newDraftResponse.content)
            def COMP = 'http://production-grafter-ons-alpha.publishmydata.com/v1/pipelines/ons-table2qb.core/components/import'
            withCredentials([usernameColonPassword(credentialsId: 'onspmd', variable: 'USERPASS')]) {
              String draftsetId = '399821a0-8106-4511-8362-77de7c0996c8'
              String endpointType = 'grafter-server.destination/draftset-update'
              String endpoint = groovy.json.JsonOutput.toJson([
                url: "http://localhost:3001/v1/draftset/${newJobDraft.id}/data",
                headers: [Authorization: "Basic ${USERPASS.bytes.encodeBase64()}"]
              ])
              String boundary = UUID.randomUUID().toString()
              String body = [
                  "--${boundary}", 'Content-Disposition: form-data; name="__endpoint-type"', '', endpointType,
                  "--${boundary}", 'Content-Disposition: form-data; name="__endpoint"', '', endpoint,
                  "--${boundary}", 'Content-Disposition: form-data; name="components-csv"; filename="components.csv"', 'Content-Type: text/csv', '', readFile('metadata/components.csv'),
                  "--${boundary}--"
              ].join('\r\n') + '\r\n'
              echo body
              def uploadComponents = httpRequest(acceptType: 'APPLICATION_JSON', authentication: 'onspmd',
                httpMode: 'POST', url: COMP, requestBody: body,
                customHeaders: [[name: 'Content-Type', value: 'multipart/form-data;boundary="' + boundary + '"']])
              if (uploadComponents.status == 202) {
                echo uploadComponents.content
                def uploadComponentsJob = readJSON(text: uploadComponents.content)
                if (!waitForJob("http://production-grafter-ons-alpha.publishmydata.com${uploadComponentsJob['finished-job']}", uploadComponentsJob['restart-id'])) {
                  error "Failed to upload components.csv"
                }
              }
            }
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

boolean waitForJob(pollUrl, restartId) {
  def running = true
  def success = false
  while (running) {
    jobResponse = httpRequest(acceptType: 'APPLICATION_JSON', authentication: 'onspmd',
                    httpMode: 'GET', url: pollUrl, validResponseCodes: '200:404')
    if (jobResponse.status == 404) {
      if (readJSON(text: jobResponse.content)['restart-id'] != restartId) {
        running = false
      } else {
        sleep 10
      }
    } else if (jobResponse.status == 200) {
      running = false
      def jobResponseObj = readJSON(text: jobResponse.content)
      if ((jobResponseObj.type == 'ok') && (jobResponseObj['restart-id'] == restartId)) {
        success = true
      }
    }
  }
  return success
}
