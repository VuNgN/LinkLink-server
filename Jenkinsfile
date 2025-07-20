pipeline {
    agent { label 'python node' }

    environment {
        // Backend
        BACKEND_DIR = 'app'
        PYTHON_VERSION = '3.10'
        // Frontend
        FRONTEND_DIR = 'frontend'
        NODE_VERSION = '18'
        // Docker
        DOCKER_IMAGE = 'linklink-app'
    }

    options {
        timestamps()
        skipDefaultCheckout()
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Backend: Lint & Test') {
            steps {
                dir("${BACKEND_DIR}") {
                    sh 'python3 -m venv venv'
                    sh '. venv/bin/activate && pip install --upgrade pip'
                    sh '. venv/bin/activate && pip install -r ../requirements.txt'
                    sh '. venv/bin/activate && pip install flake8'
                    sh '. venv/bin/activate && flake8 .'
                    sh '. venv/bin/activate && pip install pytest pytest-asyncio pytest-cov'
                    sh '. venv/bin/activate && pytest --cov=app --cov-report=xml --cov-report=html'
                }
            }
            post {
                always {
                    junit 'app/htmlcov/*.xml'
                    archiveArtifacts artifacts: 'app/htmlcov/**', allowEmptyArchive: true
                }
            }
        }

        stage('Frontend: Lint & Build') {
            steps {
                dir("${FRONTEND_DIR}") {
                    sh 'npm ci'
                    sh 'npm run lint'
                    sh 'npm run build'
                }
            }
            post {
                always {
                    archiveArtifacts artifacts: 'frontend/dist/**', allowEmptyArchive: true
                }
            }
        }

        stage('Docker Build') {
            steps {
                script {
                    sh 'docker build -t ${DOCKER_IMAGE}:latest .'
                }
            }
        }

        stage('Deploy') {
            steps {
                script {
                    sh 'sudo systemctl restart linklink-dev.service'
                }
            }
        }
    }

    post {
        always {
            cleanWs()
        }
    }
} 