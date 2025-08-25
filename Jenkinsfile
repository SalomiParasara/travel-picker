// top-level var for the built image tag
def img
def dockerImage

pipeline {
  agent any

  parameters {
    string(name: 'APP_NAME',   defaultValue: 'travel-picker', description: 'App/Container name')
    string(name: 'PORT',       defaultValue: '8000',          description: 'App internal port')
    string(name: 'HOST_PORT',  defaultValue: '8081',          description: 'Host port to expose')
    string(name: 'GITHUB_URL', defaultValue: 'https://github.com/SalomiParasara/travel-picker.git', description: 'Repo URL')
  }

  environment {
    registry           = "salomiparasara/travel-picker" // Docker Hub repo
    registryCredential = "DOCKERHUB"                    // Jenkins creds ID (Username+Password or Token)
    githubCredential   = ""                             // If repo is private, set to Jenkins creds ID; else leave blank
    APP_NAME           = "${params.APP_NAME}"
    PORT               = "${params.PORT}"
    HOST_PORT          = "${params.HOST_PORT}"
  }

  stages {
    stage('Checkout') {
      steps {
        script {
          if (env.githubCredential?.trim()) {
            git branch: 'main',
                credentialsId: env.githubCredential,
                url: params.GITHUB_URL
          } else {
            git branch: 'main',
                url: params.GITHUB_URL
          }
        }
      }
    }

    stage('Test') {
      steps {
        sh """
          python -m pip install --upgrade pip
          pip install -r requirements.txt pytest
          pytest -q
        """
      }
    }

    stage('Clean Up') {
      steps {
        sh "docker rm -f ${APP_NAME} || true"
        sh "docker rm -f ${APP_NAME}_smoke || true"
        // remove previous images for this repo (optional)
        sh """
          docker image ls ${registry} --format "{{.ID}}" | xargs -r docker rmi -f || true
        """
      }
    }

    stage('Build Image') {
      steps {
        script {
          img = "${registry}:${env.BUILD_NUMBER}"
          echo "Building image: ${img}"
          dockerImage = docker.build(img)
        }
      }
    }

    stage('Smoke Test') {
      steps {
        sh """
          docker run -d --name ${APP_NAME}_smoke -p ${PORT}:${PORT} ${img}
          sleep 5
          curl -fsS http://localhost:${PORT}/healthz | grep -i '"ok"'
        """
      }
      post {
        always {
          sh "docker rm -f ${APP_NAME}_smoke || true"
        }
      }
    }

    stage('Push To DockerHub') {
      steps {
        script {
          docker.withRegistry('https://registry.hub.docker.com', registryCredential) {
            // push build-number tag
            sh "docker push ${img}"
            // also push :latest
            sh "docker tag ${img} ${registry}:latest"
            sh "docker push ${registry}:latest"
          }
        }
      }
    }

    stage('Deploy') {
      steps {
        sh """
          docker rm -f ${APP_NAME} || true
          docker run -d --name ${APP_NAME} -p ${HOST_PORT}:${PORT} ${img}
        """
      }
    }
  }

  post {
    always {
      sh "docker image prune -f || true"
    }
  }
}
