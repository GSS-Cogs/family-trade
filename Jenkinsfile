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
            runPipeline(
              'http://production-grafter-ons-alpha.publishmydata.com/v1/pipelines/ons-table2qb.core/components/import',
              newJobDraft.id, 'onspmd',
              [[name: 'components-csv', file: [name: 'metadata/components.csv', type: 'text/csv']]]
            )
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

void runPipeline(pipelineUrl, draftsetId, credentials, params) {
  withCredentials([usernameColonPassword(credentialsId: credentials, variable: 'USERPASS')]) {
    String boundary = UUID.randomUUID().toString()
        allParams = [
            [name: '__endpoint-type', value: 'grafter-server.destination/draftset-update'],
            [name: '__endpoint', value: groovy.json.JsonOutput.toJson([
                url: "http://localhost:3001/v1/draftset/${draftsetId}/data",
                headers: [Authorization: "Basic ${USERPASS.bytes.encodeBase64()}"]
            ])]] + params
    String body = ""
    allParams.each { param ->
      body += "--${boundary}\r\n"
      body += 'Content-Disposition: form-data; name="' + param.name + '"'
      if (param.containsKey('file')) {
        body += '; filename="' + param.file.name + '"\r\nContent-Type: "' + param.file.type + '\r\n\r\n'
        body += readFile(param.file.name) + '\r\n'
      } else {
        body += "\r\n\r\n${param.value}\r\n"
      }
    }
    body += "--${boundary}--\r\n"
    def importRequest = httpRequest(acceptType: 'APPLICATION_JSON', authentication: credentials,
                                httpMode: 'POST', url: pipelineUrl, requestBody: body,
                                customHeaders: [[name: 'Content-Type', value: 'multipart/form-data;boundary="' + boundary + '"']])
    if (importRequest.status == 202) {
      def importJob = readJSON(text: importRequest.content)
      String jobUrl = new java.net.URI(pipelineUrl).resolve(importJob['finished-job']) as String
      if (!waitForJob(jobUrl, importJob['restart-id'])) {
        error "Failed import job"
      }
    } else {
      error "Failed import, ${importRequest.status} : {$importRequest.content}"
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
