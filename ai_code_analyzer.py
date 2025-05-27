#!/usr/bin/env python3
# ai_code_analyzer.py

import json
import requests
import xml.etree.ElementTree as ET
from pathlib import Path
import subprocess

class AICodeAnalyzer:
    def __init__(self, ollama_host="http://localhost:11434"):
        self.ollama_host = ollama_host
        self.models = {
            "security": "codellama:13b",
            "quality": "deepseek-coder:6.7b",
            "general": "mistral:7b"
        }
    
    def collect_static_analysis_results(self):
        """Collect results from various static analysis tools"""
        results = {}
        
        # SonarQube results
        if Path("target/sonar/report-task.txt").exists():
            results['sonarqube'] = self.parse_sonarqube_results()
        
        # OWASP Dependency Check
        if Path("target/dependency-check-report.json").exists():
            results['owasp'] = self.parse_owasp_results()
        
        # SpotBugs results
        if Path("target/spotbugsXml.xml").exists():
            results['spotbugs'] = self.parse_spotbugs_results()
        
        return results
    
    def analyze_with_ai(self, code_content, analysis_type="security"):
        """Send code to Ollama for AI analysis"""
        model = self.models.get(analysis_type, self.models["general"])
        
        prompt = self.build_analysis_prompt(code_content, analysis_type)
        
        response = requests.post(
            f"{self.ollama_host}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "top_p": 0.9,
                    "num_predict": 2048
                }
            }
        )
        
        if response.status_code == 200:
            return response.json().get('response', '')
        else:
            raise Exception(f"Ollama API error: {response.status_code}")
    
    def build_analysis_prompt(self, code_content, analysis_type):
        """Build specialized prompts for different analysis types"""
        base_prompts = {
            "security": """
            As a security expert, analyze this Java code for vulnerabilities:
            - SQL injection risks
            - XSS vulnerabilities
            - Authentication/authorization issues
            - Input validation problems
            - Cryptographic weaknesses
            
            Provide specific line numbers and remediation steps.
            """,
            "quality": """
            As a code quality expert, analyze this Java code for:
            - Code smells and anti-patterns
            - Performance issues
            - Maintainability concerns
            - Best practice violations
            - Design pattern misuse
            
            Suggest specific improvements with examples.
            """,
            "general": """
            Perform a comprehensive code review focusing on:
            - Overall architecture
            - Error handling
            - Documentation quality
            - Testing coverage gaps
            """
        }
        
        return f"{base_prompts.get(analysis_type, base_prompts['general'])}\n\nCode:\n{code_content}"
    
    def generate_comprehensive_report(self, static_results, ai_results):
        """Generate HTML report combining static analysis and AI insights"""
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>AI-Powered Code Analysis Report</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .severity-high { color: #d32f2f; font-weight: bold; }
                .severity-medium { color: #f57c00; font-weight: bold; }
                .severity-low { color: #388e3c; }
                .section { margin: 20px 0; padding: 15px; border: 1px solid #ddd; }
                .ai-insight { background-color: #e3f2fd; padding: 10px; margin: 10px 0; }
            </style>
        </head>
        <body>
            <h1>AI-Powered Security & Quality Analysis Report</h1>
            
            <div class="section">
                <h2>Executive Summary</h2>
                <p>Analysis completed with AI-enhanced insights</p>
                <!-- Summary content -->
            </div>
            
            <div class="section">
                <h2>Static Analysis Results</h2>
                <!-- Static analysis results -->
            </div>
            
            <div class="section">
                <h2>AI-Enhanced Insights</h2>
                <div class="ai-insight">
                    <!-- AI analysis results -->
                </div>
            </div>
            
            <div class="section">
                <h2>Recommendations</h2>
                <!-- Prioritized recommendations -->
            </div>
        </body>
        </html>
        """
        
        # Generate and save report
        with open("scan-results/ai-analysis-report.html", "w") as f:
            f.write(html_template)

if __name__ == "__main__":
    analyzer = AICodeAnalyzer()
    
    # Collect static analysis results
    static_results = analyzer.collect_static_analysis_results()
    
    # Analyze source code with AI
    java_files = Path("src").rglob("*.java")
    ai_results = {}
    
    for java_file in java_files:
        with open(java_file, 'r') as f:
            code_content = f.read()
        
        # Perform different types of AI analysis
        ai_results[str(java_file)] = {
            'security': analyzer.analyze_with_ai(code_content, 'security'),
            'quality': analyzer.analyze_with_ai(code_content, 'quality')
        }
    
    # Generate comprehensive report
    analyzer.generate_comprehensive_report(static_results, ai_results)