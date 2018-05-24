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
                sh "jupyter-nbconvert --to python --stdout update_metadata.ipynb | ipython"
            }
        }
        stage('Upload draftset') {
            steps {
                script {
                    def PMD = 'https://production-drafter-ons-alpha.publishmydata.com'
                    def credentials = 'onspmd'
                    def drafts = drafter.listDraftsets(PMD, credentials, 'owned')
                    def jobDraft = drafts.find  { it['display-name'] == env.JOB_NAME }
                    if (jobDraft) {
                        drafter.deleteDraftset(PMD, credentials, jobDraft.id)
                    }
                    def newJobDraft = drafter.createDraftset(PMD, credentials, env.JOB_NAME)
                    drafter.deleteGraph(PMD, credentials, newJobDraft.id,
                                        "http://gss-data.org.uk/graph/hmrc-regional-trade-statistics/metadata")
                    drafter.addData(PMD, credentials, newJobDraft.id,
                                    readFile("out/dataset.trig"), "application/trig")
                    def PIPELINE = 'http://production-grafter-ons-alpha.publishmydata.com/v1/pipelines'
                    def observationFiles = findFiles(glob: 'out/*.csv')
                    for (int i = 0; i < observationFiles.size(); i++) {
                        runPipeline("${PIPELINE}/ons-table2qb.core/data-cube/import",
                                    newJobDraft.id, credentials, [[name: 'observations-csv',
                                                                   file: [name: "out/${observationFiles[i].name}", type: 'text/csv']],
                                                                  [name: 'dataset-name', value: 'HMRC Regional Trade Statistics']])
                    }
                }
            }
        }
        stage('Test Draftset') {
            steps {
                echo 'Placeholder for acceptance tests from e.g. GDP-205'
            }
        }
        stage('Publish') {
            steps {
                script {
                    def PMD = 'https://production-drafter-ons-alpha.publishmydata.com'
                    def credentials = 'onspmd'
                    def drafts = drafter.listDraftsets(PMD, credentials, 'owned')
                    def jobDraft = drafts.find  { it['display-name'] == env.JOB_NAME }
                    if (jobDraft) {
                        drafter.publishDraftset(PMD, credentials, jobDraft.id)
                    } else {
                        error "Expecting a draftset for this job."
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
