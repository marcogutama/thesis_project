pipeline {
    agent any
    
    tools {
        maven 'MAVEN'
    }
    
    environment {
        // Configurar la API key de OpenRouter como variable de entorno segura
        OPENROUTER_API_KEY = "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"
        SCAN_RESULTS_DIR = 'scan-results'
        PROJECT_NAME = 'my-app'
    }
    
    stages {
        stage('Checkout & Build') {
            steps {
                echo 'Starting AI-powered security and quality analysis pipeline'
                git branch: 'main', url: 'https://github.com/marcogutama/jenkins-pipeline-example.git'
                sh "java -version"
                sh "python3 --version"

                // Instalar dependencias Python si no están instaladas
                sh "pip3 install requests pathlib --break-system-packages || pip3 install requests pathlib || echo 'Dependencies already installed'"
                                
                // Crear directorio para resultados
                sh "mkdir -p ${SCAN_RESULTS_DIR}"
                
                dir('my-app') {
                    sh "mvn -Dmaven.test.failure.ignore=true clean package"
                }
            }
        }    
        
        stage('AI-Powered Analysis') {
            steps {
                script {
                    // 1. Copia el script a la raíz del workspace. 
                    //    Aquí, '.' es '/var/lib/jenkins/workspace/ai_analyzer/'.
                    //sh 'cp /opt/jenkins-scripts/ai_code_analyzer.py .'

                    // 2. Ahora, entra al directorio de los resultados.
                    dir(env.SCAN_RESULTS_DIR) {
                        sh 'cp /opt/jenkins-scripts/ai_code_analyzer.py .'
                        // 3. Ejecuta el script, que ahora está en el directorio padre ('../').
                        sh 'python3 ai_code_analyzer.py'
                    }
                }
            }
        }
        
        
    }
    
    post {
        always {
            // Publicar resultados de tests
            junit(
                allowEmptyResults: true,
                testResults: 'my-app/target/surefire-reports/*.xml'
            )
            
            // Publicar reporte HTML de análisis AI
            publishHTML([
                allowMissing: false,
                alwaysLinkToLastBuild: true,
                keepAll: true,
                reportDir: env.SCAN_RESULTS_DIR,
                reportFiles: 'ai-analysis-report.html',
                reportName: 'AI Security & Quality Report',
                reportTitles: 'AI-Powered Code Analysis'
            ])
            
            // Archivar resultados JSON
            archiveArtifacts artifacts: "*.json, *.html", 
                            allowEmptyArchive: true,
                            fingerprint: true
        }
        
        success {
            echo '🎉 Pipeline completed successfully!'
            // Aquí podrías agregar notificaciones de Slack/Teams
        }
        
        failure {
            echo '❌ Pipeline failed!'
            // Notificaciones de fallo
        }
        
        unstable {
            echo '⚠️ Pipeline completed with warnings!'
            // Notificaciones de advertencia
        }
    }
}
