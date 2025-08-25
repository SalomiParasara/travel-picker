// top-level vars
def img
def dockerImage

pipeline {
  agent any

  options {
    skipDefaultCheckout(true)
    ansiColor('xterm')
    timestamps()
  }

  parameters {
    string(name: 'APP_NAME',   defaultValue: 'travel-picker', description: 'App/Container name')
    string(name: 'PORT',       defaultValue: '8000',          description: 'App internal port')
    string(name: 'HOST_PORT',  defaultValue: '8081',          description: 'Host port to expose')
    string(name: 'GITHUB_URL', defaultValue: 'https://github.com/SalomiParasara/travel-picker.git', description: 'Repo URL')
  }

  environment {
    // Docker Hub repo & creds
    registry           = "salomiparasara/travel-picker"
    registryCredential = "DOCKERHUB"

    // Set ONLY if your repo is private; leave blank for public
    githubCredential   = ""

    // Derived/env
    APP_NAME  = "${params.APP_NAME}"
    PORT      = "${params.PORT}"
    HOST_PORT = "${params.HOST_PORT}"

    IMAGE_TAG = "v${env.BUILD_NUMBER}"
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
      // Run tests in a Python container so the node doesn’t need system Python
      agent { docker { image 'python:3.11-slim'; args '-u'; reuseNode true } }
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
        // optional: clear older images from this repo
        sh """
          docker image ls ${registry} --format "{{.ID}}" | xargs -r docker rmi -f || true
        """
      }
    }

    stage('Build Image') {
      steps {
        script {
          img = "${env.registry}:${env.IMAGE_TAG}"
          echo "Building image: ${img}"
          // build context = workspace (.)
          dockerImage = docker.build(img)
        }
      }
    }

    stage('Smoke Test') {
      steps {
        // Run on internal port; don’t occupy HOST_PORT yet
        sh """
          docker run -d --name ${APP_NAME}_smoke -p ${PORT}:${PORT} ${img}
          for i in 1 2 3 4 5; do
            sleep 2
            if curl -fsS http://localhost:${PORT}/healthz | grep -i '"ok"' >/dev/null; then
              echo "Smoke OK"; exit 0
            fi
          done
          echo "Smoke test failed"; docker logs ${APP_NAME}_smoke || true; exit 1
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
            sh "docker push ${img}"
            sh "docker tag ${img} ${registry}:latest"
            sh "docker push ${registry}:latest"
          }
        }
      }
    }

    stage('Deploy') {
      steps {
        // Now expose on the chosen HOST_PORT
        sh """
          docker rm -f ${APP_NAME} || true
          docker run -d --name ${APP_NAME} -p ${HOST_PORT}:${PORT} ${img}
        """
      }
    }
  }

  post {
    always {
      // Don’t fail the build if Docker CLI isn’t present; ignore errors
      sh "docker image prune -f || true"
    }
    failure {
      echo "Build failed. Check earlier logs for details."
    }
  }
}
