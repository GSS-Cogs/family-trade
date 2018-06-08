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
                sh "jupyter-nbconvert --to python --stdout 'Trade_merge.ipynb' | ipython"
                sh "jupyter-nbconvert --to python --stdout 'update_metadata.ipynb' | ipython"
            }
        }
        stage('Upload draftset') {
            steps {
                uploadDraftset('HMRC UK Trade in Goods Statistics by Business Characteristics 2015',
                               ['out/Businesscharacteristics.csv'])
            }
        }
        stage('Test Draftset') {
            steps {
                echo 'Placeholder for acceptance tests'
            }
        }
        stage('Publish') {
            steps {
                publishDraftset()
            }
        }
    }
    post {
        always {
            archiveArtifacts 'out/*'
        }
    }
}
