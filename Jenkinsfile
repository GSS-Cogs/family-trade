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
                        sh "jupyter-nbconvert --to python --stdout '${notebooks[i].name}' | ipython"
                    }
                    sh "jupyter-nbconvert --to python --stdout update_metadata.ipynb | ipython"
                }
            }
        }
        stage('Upload draftset') {
            steps {
                script {
                    def csvs = []
                    for (def file : findFiles(glob: 'out/*.csv')) {
                        csvs.add("out/${file.name}")
                    }
                    uploadDraftset('ONS Pink Book Chapter 3', csvs)
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
                    publishDraftset()
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
