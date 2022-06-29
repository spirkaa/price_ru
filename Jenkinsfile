pipeline {
  agent any

  options {
    buildDiscarder(logRotator(numToKeepStr: '10', daysToKeepStr: '60'))
    parallelsAlwaysFailFast()
    disableConcurrentBuilds()
    skipDefaultCheckout true
  }

  environment {
    GOOGLE_SA_KEYFILE_CREDS_ID = 'priceru-google-sa-keyfile'
    TABLE_ID = credentials('priceru-table-id')
    SHEET_TITLE = "Диски"
    TITLE_ROWS_COUNT = "1"
    URL_COL_NUM = "2"
    PRICE_COL_LTR = "F"
    PYTHON_IMAGE = 'python:3.10-slim-bullseye'
  }

  stages {
    stage('Checkout') {
      when {
        branch 'main'
        beforeAgent true
        anyOf {
          triggeredBy cause: 'UserIdCause'
          triggeredBy 'TimerTrigger'
        }
      }
      steps {
        checkout scm
      }
    }

    stage('Run python script') {
      when {
        branch 'main'
        beforeAgent true
        anyOf {
          triggeredBy 'TimerTrigger'
          triggeredBy cause: 'UserIdCause'
        }
      }
      agent {
        docker {
          image env.PYTHON_IMAGE
          alwaysPull true
          reuseNode true
        }
      }
      steps {
        script {
          withCredentials([
            file(credentialsId: "${GOOGLE_SA_KEYFILE_CREDS_ID}", variable: 'GOOGLE_SA_KEYFILE')
            ]) {
            sh '''#!/bin/bash
              cp $GOOGLE_SA_KEYFILE price_ru/cred.json
              python --version
              python -m venv venv
              source venv/bin/activate
              pip install -r requirements.txt
              python -m price_ru
            '''
          }
        }
      }
      post {
        always {
          emailext(
            to: '$DEFAULT_RECIPIENTS',
            subject: '$DEFAULT_SUBJECT',
            body: '$DEFAULT_CONTENT'
          )
        }
      }
    }
  }
}
