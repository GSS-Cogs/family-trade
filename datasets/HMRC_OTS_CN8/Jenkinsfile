transformPipeline {
    refFamily = 'ref_trade'
    trelloCard = ''
}
"""
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
                      ansiColor('xterm') {
                          if (fileExists('main.py')) {
                              sh "jupytext --to notebook *.py"
                          }
                          sh "jupyter-nbconvert --output-dir=out --ExecutePreprocessor.timeout=None --execute 'main.ipynb'"
                      }
              }
            }
        }
        stage('Upload draftset') {
            steps {
                script {
		    jobDraft.replace()
                    def csvs = []
                    for (def file : findFiles(glob: 'out/*.csv')) {
                        csvs.add("out/${///file.name}")
                    }
                    uploadTidy(csvs, 'https://gss-cogs.github.io/ref_trade/columns.csv')
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
                archiveArtifacts 'out/**'
	    }
        }
    }
}
"""
