pipeline {
    agent any
    stages {
        stage('deploy') {
            steps {
                git url: 'https://github.com/serfill/mkt-phone.git', branch: 'main'
            }
        }
        stage('ceheck') {
            steps {
                sh 'ls -la'
            }
        }
        stage('Run...') {
            steps {
                sh 'docker-compose up -d --build'                    
            }
        }
    }
}
