// keep your style: top-level var for the built image tag
def img

pipeline {
  agent any

  environment {
    registry           = "salomiparasara/travel-picker" // << change
    registryCredential = "DOCKERHUB"                              // << Jenkins creds ID (Username+Password)
    githubCredential   = "GITHUB"                                  // << or remove 'credentialsId' below if repo is public
    dockerImage        = ''
    PORT               = "8000"                                    // app's internal port (Flask sample uses 8000)
    HOST_PORT          = "8081"                                    // host port to expose; change if busy
    APP_NAME           = "${JOB_NAME}"
  }

  stages {

    stage('Checkout') {
      steps {
        // If public repo: remove 'credentialsId: githubCredential'
        git branch: 'main',
            credentialsId: githubCredential,
            url: 'https://github.com/YOUR_GH_USER/travel-picker.git' // << change
      }
    }

    stage('Test') {
      steps {
        sh '''
          python -m pip install --upgrade pip
          pip install -r requirements.txt pytest
          pytest -q
        '''
      }
    }

    stage('Clean Up') {
      steps {
        // safer cleanup: ignore errors if nothing exists
        sh 'docker rm -f ${APP_NAME} || true'
        sh 'docker rm -f ${APP_NAME}_smoke || true'
        // remove previous images of this repo (optional)
        sh 'docker image ls ${registry} --format "{{.ID}}" | xargs -r docker rmi -f || true'
      }
    }

    stage('Build Image') {
      steps {
        script {
          img = "${registry}:${env.BUILD_ID}"
          echo "Building image: ${img}"
          dockerImage = docker.build(img)
        }
      }
    }

    stage('Smoke Test') {
      steps {
        sh '''
          docker run -d --name ${APP_NAME}_smoke -p ${PORT}:${PORT} ${img}
          sleep 5
          curl -fsS http://localhost:${PORT}/healthz | grep -i '"ok"'
        '''
      }
      post {
        always { sh 'docker rm -f ${APP_NAME}_smoke || true' }
      }
    }

    stage('Push To DockerHub') {
      steps {
        script {
          docker.withRegistry('https://registry.hub.docker.com', registryCredential) {
            // push build-id tag
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
        sh '''
          docker rm -f ${APP_NAME} || true
          docker run -d --name ${APP_NAME} -p ${HOST_PORT}:${PORT} ${img}
        '''
      }
    }
  }

  post {
    always {
      // keep disk clean; safe to ignore errs
      sh 'docker image prune -f || true'
    }
  }
}
