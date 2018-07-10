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
                sh 'jupyter-nbconvert --to python --stdout "ABS To Tidydata.ipynb" | ipython'
                sh 'jupyter-nbconvert --to python --stdout update_metadata.ipynb | ipython'
            }
        }
        stage('Upload draftset') {
            steps {
                script {
                    uploadDraftset('ONS ABS', ['out/observations.csv'])
                }
            }
        }
        stage('Test Draftset') {
            steps {
                script {
                    configFileProvider([configFile(fileId: 'pmd', variable: 'configfile')]) {
                        def config = readJSON(text: readFile(file: configfile))
                        String PMD = config['pmd_api']
                        String credentials = config['credentials']
                        def drafts = drafter.listDraftsets(PMD, credentials, 'owned')
                        def jobDraft = drafts.find  { it['display-name'] == env.JOB_NAME }
                        if (jobDraft) {
                            withCredentials([usernameColonPassword(credentialsId: credentials, variable: 'USERPASS')]) {
                                sh "java -cp lib/sparql.jar uk.org.floop.sparqlTestRunner.Run -i -s ${PMD}/v1/draftset/${jobDraft.id}/query?union-with-live=true -a \'${USERPASS}\'"
                            }
                        } else {
                            error "Expecting a draftset for this job."
                        }
                    }
                }
            }
        }
        stage('Publish') {
            steps {
                script {
                    publishDraftset()
                }
            }
        }
    }
    post {
        always {
            archiveArtifacts 'out/**'
            junit 'reports/**/*.xml'
        }
    }
}
