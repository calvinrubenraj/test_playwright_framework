pipeline {
    agent any

    parameters {
        choice(name: 'ENV', choices: ['qa', 'stage'], description: 'Environment')
        choice(name: 'SUITE', choices: ['smoke', 'regression', 'all'], description: 'Suite')
        choice(name: 'BROWSER', choices: ['chromium', 'firefox', 'webkit'], description: 'Browser')
        booleanParam(name: 'SKIP_OPTIONAL', defaultValue: false, description: 'Skip optional tests')
    }

    stages {
        stage('Checkout') {
            steps { checkout scm }
        }
        stage('Setup') {
            steps {
                sh '''
                    python3 -m venv .venv
                    . .venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                    playwright install --with-deps chromium
                '''
            }
        }
        stage('Execute') {
            steps {
                script {
                    def marker = params.SUITE == 'all' ? '' : "-m ${params.SUITE}"
                    def skipOptional = params.SKIP_OPTIONAL ? '--skip-optional' : ''
                    sh """
                        . .venv/bin/activate
                        pytest --env=${params.ENV} --browser-name=${params.BROWSER} ${marker} ${skipOptional} -n auto --alluredir=allure-results --junitxml=junit.xml
                    """
                }
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'artifacts/**/*,allure-results/**/*', allowEmptyArchive: true
            junit testResults: 'junit.xml', allowEmptyResults: true
            allure includeProperties: false, jdk: '', results: [[path: 'allure-results']]
        }
        cleanup { cleanWs() }
    }
}
