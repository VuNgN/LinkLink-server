pipeline {
    agent { label 'python || node' }

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

        stage('Prepare .env') {
            steps {
                withCredentials([
                    string(credentialsId: 'DATABASE_URL', variable: 'DATABASE_URL'),
                    string(credentialsId: 'DB_ECHO', variable: 'DB_ECHO'),
                    string(credentialsId: 'SECRET_KEY', variable: 'SECRET_KEY'),
                    string(credentialsId: 'ALGORITHM', variable: 'ALGORITHM'),
                    string(credentialsId: 'ACCESS_TOKEN_EXPIRE_MINUTES', variable: 'ACCESS_TOKEN_EXPIRE_MINUTES'),
                    string(credentialsId: 'REFRESH_TOKEN_EXPIRE_DAYS', variable: 'REFRESH_TOKEN_EXPIRE_DAYS'),
                    string(credentialsId: 'MAIL_USERNAME', variable: 'MAIL_USERNAME'),
                    string(credentialsId: 'MAIL_PASSWORD', variable: 'MAIL_PASSWORD'),
                    string(credentialsId: 'MAIL_FROM', variable: 'MAIL_FROM'),
                    string(credentialsId: 'MAIL_PORT', variable: 'MAIL_PORT'),
                    string(credentialsId: 'MAIL_SERVER', variable: 'MAIL_SERVER'),
                    string(credentialsId: 'ADMIN_EMAIL', variable: 'ADMIN_EMAIL'),
                    string(credentialsId: 'HOST', variable: 'HOST'),
                    string(credentialsId: 'PORT', variable: 'PORT'),
                    string(credentialsId: 'UPLOAD_DIR', variable: 'UPLOAD_DIR'),
                    string(credentialsId: 'MAX_FILE_SIZE', variable: 'MAX_FILE_SIZE'),
                    string(credentialsId: 'ALLOWED_IMAGE_TYPES', variable: 'ALLOWED_IMAGE_TYPES'),
                    string(credentialsId: 'API_V1_STR', variable: 'API_V1_STR'),
                    string(credentialsId: 'PROJECT_NAME', variable: 'PROJECT_NAME'),
                    string(credentialsId: 'POSTGRES_HOST', variable: 'POSTGRES_HOST'),
                    string(credentialsId: 'POSTGRES_PORT', variable: 'POSTGRES_PORT'),
                    string(credentialsId: 'POSTGRES_DB', variable: 'POSTGRES_DB'),
                    string(credentialsId: 'POSTGRES_USER', variable: 'POSTGRES_USER'),
                    string(credentialsId: 'POSTGRES_PASSWORD', variable: 'POSTGRES_PASSWORD'),
                    string(credentialsId: 'LOG_LEVEL', variable: 'LOG_LEVEL'),
                    string(credentialsId: 'LOG_FILE', variable: 'LOG_FILE'),
                    string(credentialsId: 'DEBUG', variable: 'DEBUG'),
                    string(credentialsId: 'SERVICE_NAME', variable: 'SERVICE_NAME')
                ]) {
                    sh '''
                    cat > .env <<EOF
                    DATABASE_URL=$DATABASE_URL
                    DB_ECHO=$DB_ECHO
                    SECRET_KEY=$SECRET_KEY
                    ALGORITHM=$ALGORITHM
                    ACCESS_TOKEN_EXPIRE_MINUTES=$ACCESS_TOKEN_EXPIRE_MINUTES
                    REFRESH_TOKEN_EXPIRE_DAYS=$REFRESH_TOKEN_EXPIRE_DAYS
                    MAIL_USERNAME=$MAIL_USERNAME
                    MAIL_PASSWORD=$MAIL_PASSWORD
                    MAIL_FROM=$MAIL_FROM
                    MAIL_PORT=$MAIL_PORT
                    MAIL_SERVER=$MAIL_SERVER
                    ADMIN_EMAIL=$ADMIN_EMAIL
                    HOST=$HOST
                    PORT=$PORT
                    UPLOAD_DIR=$UPLOAD_DIR
                    MAX_FILE_SIZE=$MAX_FILE_SIZE
                    ALLOWED_IMAGE_TYPES=$ALLOWED_IMAGE_TYPES
                    API_V1_STR=$API_V1_STR
                    PROJECT_NAME=$PROJECT_NAME
                    POSTGRES_HOST=$POSTGRES_HOST
                    POSTGRES_PORT=$POSTGRES_PORT
                    POSTGRES_DB=$POSTGRES_DB
                    POSTGRES_USER=$POSTGRES_USER
                    POSTGRES_PASSWORD=$POSTGRES_PASSWORD
                    LOG_LEVEL=$LOG_LEVEL
                    LOG_FILE=$LOG_FILE
                    DEBUG=$DEBUG
                    EOF
                    '''
                }
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
                }
                sh '. app/venv/bin/activate && pytest tests --cov=app --cov-report=xml --cov-report=html --junitxml=pytest-report.xml'
            }
            post {
                always {
                    junit 'pytest-report.xml'
                    archiveArtifacts artifacts: 'htmlcov/**', allowEmptyArchive: true
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
                    sh 'sudo systemctl restart $SERVICE_NAME'
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