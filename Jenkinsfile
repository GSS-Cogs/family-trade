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
                sh 'jupyter-nbconvert --output-dir=out --ExecutePreprocessor.timeout=None --execute Balanceofpayments2017q3_TabF.ipynb'
                sh 'jupyter-nbconvert --to python --stdout update_metadata.ipynb | ipython'
            }
        }
        stage('Upload draftset') {
            steps {
                script {
                    uploadDraftset('ONS Balance of Payments', ['out/balanceofpayments2017q3.csv'])
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
