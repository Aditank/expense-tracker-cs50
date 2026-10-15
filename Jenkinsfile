
pipeline {
    agent any

    environment {
        APP_IMAGE = 'expense-tracker'
        TEST_IMAGE = 'expense-tracker-test'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Test') {
            steps {
                sh '''
                    docker build -f Dockerfile.test \
                        -t ${TEST_IMAGE}:${BUILD_NUMBER} .
                    docker run --rm ${TEST_IMAGE}:${BUILD_NUMBER}
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                    docker build -t ${APP_IMAGE}:${BUILD_NUMBER} .
                    docker tag ${APP_IMAGE}:${BUILD_NUMBER} \
                        ${APP_IMAGE}:latest
                '''
            }
        }
    }

    post {
        success {
            echo 'Tests passed and Docker image built successfully.'
        }
        failure {
            echo 'Pipeline failed. Check the console output.'
        }
    }
}
