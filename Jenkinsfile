
pipeline {
    agent any

    environment {
        AWS_REGION = 'us-east-1'
        ECR_REPOSITORY = 'expense-tracker'
        AWS_ACCOUNT_ID = '454681118296'
        APP_INSTANCE_ID = 'i-0acb4c22193ec598c'
        APP_IMAGE = '454681118296.dkr.ecr.us-east-1.amazonaws.com/expense-tracker'
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
                '''
            }
        }

        stage('Push to Amazon ECR') {
            steps {
                sh '''
                    set -eu

                    aws ecr get-login-password --region "$AWS_REGION" |
                        docker login --username AWS --password-stdin \
                        "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"

                    docker push "${APP_IMAGE}:${BUILD_NUMBER}"
                '''
            }
        }

        stage('Deploy to Application EC2') {
            steps {
                sh '''
                    set -eu

                    COMMAND_ID=$(aws ssm send-command \
                        --region "$AWS_REGION" \
                        --instance-ids "$APP_INSTANCE_ID" \
                        --document-name AWS-RunShellScript \
                        --parameters "$(jq -nc \
                            --arg image "${APP_IMAGE}:${BUILD_NUMBER}" \
                            --arg region "$AWS_REGION" \
                            '{
                                commands: [
                                    "set -eu",
                                    "sudo systemctl enable --now docker",
                                    "sudo mkdir -p /opt/expense-tracker",
                                    "aws ecr get-login-password --region " + $region + " | sudo docker login --username AWS --password-stdin 454681118296.dkr.ecr.us-east-1.amazonaws.com",
                                    "sudo docker pull " + $image,
                                    "if ! sudo test -f /opt/expense-tracker/finance.db; then sudo touch /opt/expense-tracker/finance.db; fi",
                                    "sudo docker rm -f expense-tracker-app 2>/dev/null || true",
                                    "sudo docker run -d --name expense-tracker-app --restart unless-stopped -p 5000:5000 -e EXPENSE_DB=/app/finance.db -v /opt/expense-tracker/finance.db:/app/finance.db " + $image,
                                    "sudo docker ps --filter name=expense-tracker-app"
                                ]
                            }')" \
                        --comment "Deploy expense tracker build ${BUILD_NUMBER}" \
                        --query 'Command.CommandId' \
                        --output text)

                    echo "SSM Command ID: $COMMAND_ID"

                    for attempt in $(seq 1 30); do
                        STATUS=$(aws ssm get-command-invocation \
                            --region "$AWS_REGION" \
                            --command-id "$COMMAND_ID" \
                            --instance-id "$APP_INSTANCE_ID" \
                            --query 'Status' \
                            --output text 2>/dev/null || true)

                        echo "Deployment status: $STATUS"

                        case "$STATUS" in
                            Success)
                                aws ssm get-command-invocation \
                                    --region "$AWS_REGION" \
                                    --command-id "$COMMAND_ID" \
                                    --instance-id "$APP_INSTANCE_ID" \
                                    --query 'StandardOutputContent' \
                                    --output text
                                exit 0
                                ;;
                            Failed|Cancelled|TimedOut)
                                aws ssm get-command-invocation \
                                    --region "$AWS_REGION" \
                                    --command-id "$COMMAND_ID" \
                                    --instance-id "$APP_INSTANCE_ID" \
                                    --query '[StatusDetails,StandardOutputContent,StandardErrorContent]' \
                                    --output json
                                exit 1
                                ;;
                        esac

                        sleep 5
                    done

                    echo "Timed out waiting for deployment command."
                    exit 1
                '''
            }
        }
    }

    post {
        success {
            echo 'Tests passed, image pushed to ECR, and deployment command succeeded.'
        }
        failure {
            echo 'Pipeline failed. Check the Console Output for the failing stage.'
        }
    }
}
