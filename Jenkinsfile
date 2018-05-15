pipeline {
    agent {
        label 'master'
    }
    stages {
        stage('Upload draftset') {
            steps {
                script {
                    List<String[]> codelists = readFile('codelists.csv').split('\n').tail().collect {
                        l -> l.split(',')
                    }
                    def PMD = 'https://production-drafter-ons-alpha.publishmydata.com'
                    def credentials = 'onspmd'
                    def drafts = drafter.listDraftsets(PMD, credentials, 'owned')
                    def jobDraft = drafts.find  { it['display-name'] == env.JOB_NAME }
                    if (jobDraft) {
                        drafter.deleteDraftset(PMD, credentials, jobDraft.id)
                    }
                    def newJobDraft = drafter.createDraftset(PMD, credentials, env.JOB_NAME)
                    def PIPELINE = 'http://production-grafter-ons-alpha.publishmydata.com/v1/pipelines'
                    for (String[] row : codelists) {
                        try {
                            echo "Uploading ${row[0]}"
                            runPipeline("${PIPELINE}/ons-table2qb.core/codelist/import",
                                        newJobDraft.id, credentials, [[name: 'codelist-csv',
                                                                       file: [name: "codelists/${row[1]}", type: 'text/csv']],
                                                                      [name: 'codelist-name', value: "${row[0]}"]])
                        } catch (Exception e) {
                            echo "Caught error: ${e.message}"
                        }
                    }
                }
            }
        }
    }
}
