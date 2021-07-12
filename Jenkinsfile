pipeline {
    agent {
        label 'docker'
    }
    stages {
        stage('Generate CSV-W') {
            agent {
                docker {
                    image 'gsscogs/databaker'
                    reuseNode true
                    alwaysPull true
                }
            }
            environment {
                RECORD_MODE = 'none'
            }
            steps {
                script {
                    def pipelineInfo = readJSON(text: readFile(file: 'datasets/info.json'))
                    String [] testPipelines = pipelineInfo['pipelines']
                    if (pipelineInfo.containsKey('tests') && pipelineInfo['tests'].containsKey('skip')) {
                        testPipelines = testPipelines.minus(pipelineInfo['tests']['skip'])
                    }
                    for (String pipeline : testPipelines) {
                        dir("datasets/${pipeline}") {
                            def inFiles = findFiles(glob: '*.py') + findFiles(glob: 'codelists/*')
                            def outFiles = findFiles(glob: 'out/*')
                            def newestIn = inFiles.max { it.lastModified }
                            def oldestOut = outFiles.min { it.lastModified }
                            if (oldestOut == null || (newestIn.lastModified > oldestOut.lastModified)) {
                                sh "jupytext --to notebook '*.py'"
                                sh "jupyter-nbconvert --to html --output-dir='out' --ExecutePreprocessor.timeout=None --execute 'main.ipynb'"
                            }
                        }
                    }
                }
            }
        }
    }
}