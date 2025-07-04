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
        
        stage('Static Analysis') {
            parallel {
                stage('OWASP Dependency Check') {
                    steps {
                        dir('my-app') {
                            script {
                                try {
                                    // Ejecutar OWASP Dependency Check
                                    sh """
                                        mvn org.owasp:dependency-check-maven:check \
                                        -Dformat=JSON \
                                        -DfailBuildOnCVSS=0 \
                                        -DsuppressedVulnerabilityFiles=.dependency-check-suppressions.xml
                                    """
                                    
                                    // Copiar resultados al directorio de scan
                                    sh "cp target/dependency-check-report.json ../${SCAN_RESULTS_DIR}/ || echo 'No OWASP report found'"
                                } catch (Exception e) {
                                    echo "OWASP Dependency Check failed: ${e.getMessage()}"
                                    // Crear archivo vacío para que el análisis AI continue
                                    sh "echo '{}' > ../${SCAN_RESULTS_DIR}/dependency-check-report.json"
                                }
                            }
                        }
                    }
                }
                
                stage('SpotBugs Analysis') {
                    steps {
                        dir('my-app') {
                            script {
                                try {
                                    sh "mvn compile spotbugs:spotbugs"
                                    sh "cp target/spotbugsXml.xml ../${SCAN_RESULTS_DIR}/ || echo 'No SpotBugs report found'"
                                } catch (Exception e) {
                                    echo "SpotBugs analysis failed: ${e.getMessage()}"
                                    sh "echo '<BugCollection></BugCollection>' > ../${SCAN_RESULTS_DIR}/spotbugsXml.xml"
                                }
                            }
                        }
                    }
                }
                
                stage('Collect Source Files') {
                    steps {
                        script {
                            // Recopilar archivos Java para análisis AI
                            sh """
                                find my-app/src -name "*.java" -type f > ${SCAN_RESULTS_DIR}/java-files.txt
                                echo "Found Java files:"
                                cat ${SCAN_RESULTS_DIR}/java-files.txt
                            """
                        }
                    }
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
        
        stage('Quality Gates') {
            steps {
                script {
                    dir(env.SCAN_RESULTS_DIR) {
                        try {
                            def analysisResults = readJSON file: 'analysis-results.json'
                            
                            def criticalIssues = analysisResults.high_severity_vulnerabilities ?: 0
                            def totalVulns = analysisResults.total_vulnerabilities ?: 0
                            def qualityIssues = analysisResults.total_quality_issues ?: 0
                            
                            echo "=== QUALITY GATES EVALUATION ==="
                            echo "High Severity Vulnerabilities: ${criticalIssues}"
                            echo "Total Vulnerabilities: ${totalVulns}"
                            echo "Quality Issues: ${qualityIssues}"
                            
                            // Definir umbrales
                            def gates = [
                                'Critical Vulnerabilities': [threshold: 0, current: criticalIssues],
                                'Total Vulnerabilities': [threshold: 10, current: totalVulns],
                                'Quality Issues': [threshold: 20, current: qualityIssues]
                            ]
                            
                            def failed = []
                            gates.each { gateName, values ->
                                if (values.current > values.threshold) {
                                    failed.add("${gateName}: ${values.current} > ${values.threshold}")
                                } else {
                                    echo "✅ ${gateName}: ${values.current} <= ${values.threshold} (PASSED)"
                                }
                            }
                            
                            if (failed.size() > 0) {
                                echo "❌ Quality gates FAILED:"
                                failed.each { echo "  - ${it}" }
                                // Para testing, solo advertir en lugar de fallar
                                unstable("Quality gates failed: ${failed.join(', ')}")
                            } else {
                                echo "✅ All quality gates PASSED!"
                            }
                            
                        } catch (Exception e) {
                            echo "Warning: Could not evaluate quality gates: ${e.getMessage()}"
                            unstable("Quality gate evaluation failed")
                        }
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
            archiveArtifacts artifacts: "${env.SCAN_RESULTS_DIR}/*.json, ${env.SCAN_RESULTS_DIR}/*.html", 
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