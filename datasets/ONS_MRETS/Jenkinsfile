pipeline {
    agent {
        label 'master'
    }
    triggers {
        upstream(upstreamProjects: '../Reference/ref_trade',
                 threshold: hudson.model.Result.SUCCESS)
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
                sh "jupyter-nbconvert --output-dir=out --ExecutePreprocessor.timeout=None --execute tidy.ipynb"
            }
        }
        stage('Test') {
            agent {
                docker {
                    image 'cloudfluff/csvlint'
                    reuseNode true
                }
            }
            steps {
                script {
                    ansiColor('xterm') {
                        sh "csvlint -s schema.json"
                    }
                }
            }
        }
        stage('Upload draftset') {
            steps {
                script {
                    jobDraft.replace()
                    uploadTidy(['out/bop_observations.csv'],
                               'https://github.com/ONS-OpenData/ref_trade/raw/master/columns.csv')
                }
            }
        }
        stage('Upload reference data') {
            steps {
                script {
                    def pmd = pmdConfig("pmd")
                    String draftId = pmd.drafter.findDraftset(env.JOB_NAME).id
                    String graph = "http://gss-data.org.uk/def/cdid"
                    pmd.drafter.deleteGraph(draftId, graph)
                    pmd.drafter.addData(draftId, "${WORKSPACE}/out/cdids.ttl", 'text/turtle', 'UTF-8', graph)
                }
            }
        }
        stage('Publish') {
            steps {
                script {
                    jobDraft.publish()
                }
            }
        }
    }
    post {
        always {
            script {
                archiveArtifacts 'out/*'
                updateCard '5b471c67f6af3eb0df95c06b'
            }
        }
        success {
            build job: '../GDP-tests', wait: false
        }
    }
}
