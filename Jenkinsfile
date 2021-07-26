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
                            def inFiles = findFiles(glob: '*.py') +
                                    findFiles(glob: 'codelists/*') +
                                    findFiles(glob: 'info.json')
                            def outFiles = findFiles(glob: 'out/*')
                            def newestIn = inFiles.max { it.lastModified }
                            def oldestOut = outFiles.min { it.lastModified }
                            if (oldestOut == null || (newestIn.lastModified > oldestOut.lastModified)) {
                                sh "rm -rf out"
                                warnError("Transform error for ${pipeline}.") {
                                    sh "jupytext --to notebook --use-source-timestamp '*.py'"
                                    sh "jupyter-nbconvert --to html --output-dir='out' --ExecutePreprocessor.timeout=None --execute 'main.ipynb'"
                                }
                            }
                        }
                    }
                }
            }
        }
        stage('Validate CSV-W') {
            agent {
                docker {
                    image 'gsscogs/csvlint'
                    reuseNode true
                    alwaysPull true
                }
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
                            sh "mkdir -p reports"
                            def schemas = findFiles(glob: 'out/*-metadata.json')
                            def results = findFiles(glob: 'reports/*-report.txt')
                            def newestIn = schemas.max { it.lastModified }
                            def oldestOut = results.min { it.lastModified }
                            if (oldestOut == null || (newestIn.lastModified > oldestOut.lastModified)) {
                                for (String schema : schemas) {
                                    String baseName = schema.name.substring(0, schema.name.lastIndexOf('-metadata.json'))
                                    sh(returnStatus: true, script: "csvlint --format junit --no-verbose -s ${schema} > reports/${baseName}-report.xml")
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    post {
        always {
            script {
                junit allowEmptyResults: true, testResults: 'datasets/*/reports/*-report.xml'
            }
        }
    }

}