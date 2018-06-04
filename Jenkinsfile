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
                    uploadDraftset('ONS ABS', ['out/ABS.csv'])
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
            archiveArtifacts 'out/**'
        }
    }
}
