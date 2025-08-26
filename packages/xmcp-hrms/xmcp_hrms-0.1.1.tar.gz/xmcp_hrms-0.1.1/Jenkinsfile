
pipeline {
    agent any
    options {
        timeout(time: 30, unit: 'MINUTES')
    }

    environment {
        REGISTRY = "harbor.cubastion.net"
        TARGET_IMAGE = "${params.target_image}"
        TAG = "${params.tag}"
        REGISTRY_CREDS_ID = "${params.registry_creds_id}"
        ARGOCD_SERVER = "${params.argocdServer}"
        ARGOCD_APP_NAME = "${params.argocdAppName}"
        ARGOCD_DEPLOY_ROLE = "${params.argocdDeployRole}"
    }

    stages {
        stage('Clone Repository') {
            steps {
                script {
                    cleanWs()
                    deleteDir()
                    checkout scm
                }
            }
        }

        stage('Build Image') {
            steps {
                script {
                    xagent_xnet_mcp = docker.build("${REGISTRY}/${TARGET_IMAGE}:${TAG}")
                }
            }
        }

        stage('Push Image') {
            steps {
                retry(2) {
                    script {
                        docker.withRegistry("https://${REGISTRY}", "${REGISTRY_CREDS_ID}") {
                            xagent_xnet_mcp.push()
                        }
                    }
                }
            }
        }

        stage('Sync ArgoCD') {
            steps {
                retry(2) {
                    script {
                        withCredentials([string(credentialsId: "${ARGOCD_DEPLOY_ROLE}", variable: 'ARGOCD_AUTH_TOKEN')]) {
                            sh """
                                # Sync the app
                                argocd app sync ${ARGOCD_APP_NAME} --auth-token \$ARGOCD_AUTH_TOKEN --server ${ARGOCD_SERVER} --insecure

                                # Restart the frontend StatefulSet
                                argocd app actions run ${ARGOCD_APP_NAME} restart \\
                                    --auth-token \$ARGOCD_AUTH_TOKEN \\
                                    --server ${ARGOCD_SERVER} \\
                                    --kind StatefulSet \\
                                    --resource-name xagent-ng \\
                                    --namespace xnet2 \\
                                    --insecure
                            """
                        }
                    }
                }
            }
        }
    }

    post {
        always {
            script {
                try {
                    sh "docker rmi ${REGISTRY}/${TARGET_IMAGE}:${TAG}"
                } catch (Exception e) {
                    echo "Image already removed or never built."
                }
            }
            cleanWs()
        }
    }
}
