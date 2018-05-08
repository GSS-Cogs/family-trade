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
                sh "jupyter-nbconvert --to python --stdout 'Business count by Age of Business.ipynb' | ipython"
                sh "jupyter-nbconvert --to python --stdout 'Business count by Employee Size.ipynb' | ipython"
                sh "jupyter-nbconvert --to python --stdout 'Business count by Industry Group.ipynb' | ipython"
                sh "jupyter-nbconvert --to python --stdout 'Employee count for Businesses by Age of Business.ipynb' | ipython"
                sh "jupyter-nbconvert --to python --stdout 'Employee count for Businesses by Employee Size.ipynb' | ipython"
                sh "jupyter-nbconvert --to python --stdout 'Employee count for Businesses by Industry Group.ipynb' | ipython"
                sh "jupyter-nbconvert --to python --stdout 'Total value of UK trade by Age of Business.ipynb' | ipython"
                sh "jupyter-nbconvert --to python --stdout 'Total value of UK trade by Employee Size.ipynb' | ipython"
                sh "jupyter-nbconvert --to python --stdout 'Total value of UK trade by Industry Group.ipynb' | ipython"
                sh "jupyter-nbconvert --to python --stdout 'TRADE IN GOODS STATISTICS -Business Count.ipynb' | ipython"
                sh "jupyter-nbconvert --to python --stdout 'TRADE IN GOODS STATISTICS -Employee Count and age business.ipynb' | ipython"
                sh "jupyter-nbconvert --to python --stdout 'TRADE IN GOODS STATISTICS -Employee Count and age employee count.ipynb' | ipython"
                sh "jupyter-nbconvert --to python --stdout 'TRADE IN GOODS STATISTICS -Employee Count and age.ipynb' | ipython"
                sh "jupyter-nbconvert --to python --stdout 'TRADE IN GOODS STATISTICS -Employee Count.ipynb' | ipython"
                sh "jupyter-nbconvert --to python --stdout 'TRADE IN GOODS STATISTICS_Employee size_Businesses.ipynb' | ipython"
                sh "jupyter-nbconvert --to python --stdout 'TRADE IN GOODS STATISTICS_Employee size_Employee count.ipynb' | ipython"
                sh "jupyter-nbconvert --to python --stdout 'TRADE IN GOODS STATISTICS_Employee size_value.ipynb' | ipython"
                sh "jupyter-nbconvert --to python --stdout 'TRADE IN GOODS STATISTICS -total value of UK Trade.ipynb' | ipython"
            }
        }
        stage('Upload draftset') {
            steps {
                error "Needs review"
            }
        }
        stage('Test Draftset') {
            steps {
                echo 'Placeholder for acceptance tests from e.g. GDP-205'
            }
        }
        stage('Publish') {
            steps {
                error 'Needs uploading first'
            }
        }
    }
    post {
        always {
            archiveArtifacts 'out/*'
        }
    }
}
