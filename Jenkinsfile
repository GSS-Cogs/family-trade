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
                script {
                    def notebooks = findFiles(glob: 'Pinkbook2017chapter3_*.ipynb')
                    for (int i = 0; i < notebooks.size(); i++) {
                        sh "jupyter-nbconvert --to python --stdout '${notebook[i].name}' | ipython"
                    }
                }
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
                                        "http://gss-data.org.uk/graph/ons-pink-book-chapter-3/metadata")
                    drafter.addData(PMD, credentials, newJobDraft.id,
                                    readFile("metadata/dataset.trig"), "application/trig")
                    def PIPELINE = 'http://production-grafter-ons-alpha.publishmydata.com/v1/pipelines'
                    def observationFiles = findFiles(glob: 'out/*.csv')
                    for (int i = 0; i < observationFiles.size(); i++) {
                        runPipeline("${PIPELINE}/ons-table2qb.core/data-cube/import",
                                    newJobDraft.id, credentials, [[name: 'observations-csv',
                                                                   file: [name: "out/${observationFile[i].name}", type: 'text/csv']],
                                                                  [name: 'dataset-name', value: 'ONS Pink Book Chapter 3']])
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
