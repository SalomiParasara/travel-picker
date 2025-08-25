pipeline {
  agent any
  options { skipDefaultCheckout(true) }

  environment {
    REGISTRY       = "salomiparasara"                 
    REPO           = "https://github.com/SalomiParasara/travel-picker.git"
    IMAGE          = "${env.REGISTRY}/${env.REPO}"    // e.g., salomiparasara/travel-picker
    TAG            = "v${env.BUILD_NUMBER}"
    HOST_PORT      = "8081"
    CNAME          = "travel_picker_${env.BUILD_NUMBER}"
    REGISTRY_CRED  = "DOCKERHUB"                      // Jenkins creds id (Username+Token)
    COMPOSE_PROJECT_NAME = "travel_picker"            // isolates stack
  }

  stages {
    stage('Checkout') {
      steps {
        git branch: 'main', url: 'https://github.com/SalomiParasara/travel-picker.git'
      }
    }

    stage('Test (docker compose)') {
      steps {
        sh '''
          export IMAGE=${IMAGE} TAG=${TAG} HOST_PORT=${HOST_PORT}
          docker compose run --rm test
        '''
      }
    }

    stage('Build (docker compose)') {
      steps {
        sh '''
          export IMAGE=${IMAGE} TAG=${TAG} HOST_PORT=${HOST_PORT}
          docker compose build app
        '''
      }
    }

    stage('Push to Docker Hub') {
      steps {
        script {
          docker.withRegistry('https://index.docker.io/v1/', REGISTRY_CRED) {
            sh 'docker push ${IMAGE}:${TAG}'
          }
        }
      }
    }

    stage('Deploy (docker compose up)') {
      steps {
        sh '''
          export IMAGE=${IMAGE} TAG=${TAG} HOST_PORT=${HOST_PORT}
          # stop any previous stack by project name (optional safety)
          docker compose down || true
          docker compose up -d app
          
          # simple smoke check
          sleep 5
          curl -fsS http://localhost:${HOST_PORT}/healthz | grep '"ok"'
        '''
      }
    }
  }

  post {
    always {
      echo "Deployed ${IMAGE}:${TAG} on port ${HOST_PORT}"
    }
  }
}
