pipeline {
    agent any
    
    environment {
        OLLAMA_HOST = 'http://localhost:11434'
        SCAN_RESULTS_DIR = 'scan-results'
    }
    
    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: '${GIT_URL}'
            }
        }
        
        stage('Static Analysis') {
            parallel {
                stage('SonarQube Scan') {
                    steps {
                        withSonarQubeEnv() {
                            sh 'mvn clean compile sonar:sonar'
                        }
                    }
                }
                stage('OWASP Dependency Check') {
                    steps {
                        dependencyCheck additionalArguments: '--format JSON --format HTML', odcInstallation: 'dependency-check'
                    }
                }
                stage('SpotBugs Analysis') {
                    steps {
                        sh 'mvn compile spotbugs:spotbugs'
                    }
                }
            }
        }
        
        stage('AI-Powered Analysis') {
            steps {
                script {
                    // Collect analysis results
                    def analysisData = collectAnalysisResults()
                    
                    // Send to AI model for enhanced analysis
                    def aiInsights = callOllamaAnalysis(analysisData)
                    
                    // Generate comprehensive report
                    generateAIReport(aiInsights)
                }
            }
        }
        
        stage('Quality Gates') {
            steps {
                script {
                    evaluateQualityGates()
                }
            }
        }
    }
    
    post {
        always {
            publishHTML([
                allowMissing: false,
                alwaysLinkToLastBuild: true,
                keepAll: true,
                reportDir: 'scan-results',
                reportFiles: 'ai-analysis-report.html',
                reportName: 'AI Security & Quality Report'
            ])
        }
    }
}