#!/usr/bin/env python3
# ai_code_analyzer.py

import json
import requests
import xml.etree.ElementTree as ET
from pathlib import Path
import subprocess
import sys

class AICodeAnalyzer:
    def __init__(self, ollama_host="http://localhost:11434"):
        self.ollama_host = ollama_host
        self.models = {
            "security": "deepseek-coder:6.7b",
            "quality": "deepseek-coder:6.7b",
            "general": "deepseek-coder:6.7b"
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
    
    def parse_sonarqube_results(self):
        """Parse SonarQube results"""
        return {"status": "SonarQube results found but not parsed yet"}
    
    def parse_owasp_results(self):
        """Parse OWASP results"""
        return {"status": "OWASP results found but not parsed yet"}
    
    def parse_spotbugs_results(self):
        """Parse SpotBugs results"""
        return {"status": "SpotBugs results found but not parsed yet"}
    
    def analyze_with_ai(self, code_content, analysis_type="security"):
        """Send code to Ollama for AI analysis"""
        model = self.models.get(analysis_type, self.models["general"])
        
        prompt = self.build_analysis_prompt(code_content, analysis_type)
        
        try:
            print(f"Analizando con AI (tipo: {analysis_type})...")
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
                },
                timeout=120  # Timeout de 2 minutos
            )
            
            if response.status_code == 200:
                result = response.json().get('response', '')
                print(f"Análisis {analysis_type} completado.")
                return result
            else:
                error_msg = f"Ollama API error: {response.status_code}: {response.text}"
                print(error_msg)
                return f"Error en análisis {analysis_type}: {error_msg}"
                
        except requests.exceptions.RequestException as e:
            error_msg = f"Error de conexión con Ollama: {str(e)}"
            print(error_msg)
            return f"Error de conexión en análisis {analysis_type}: {error_msg}"
        except Exception as e:
            error_msg = f"Error inesperado: {str(e)}"
            print(error_msg)
            return f"Error inesperado en análisis {analysis_type}: {error_msg}"
    
    def build_analysis_prompt(self, code_content, analysis_type):
        """Build specialized prompts for different analysis types"""
        base_prompts = {
            "security": """
            Como experto en seguridad, analiza este código Java buscando vulnerabilidades:
            - Riesgos de inyección SQL
            - Vulnerabilidades XSS
            - Problemas de autenticación/autorización
            - Problemas de validación de entrada
            - Debilidades criptográficas
            
            Proporciona números de línea específicos y pasos de remediación.
            """,
            "quality": """
            Como experto en calidad de código, analiza este código Java buscando:
            - Code smells y anti-patrones
            - Problemas de rendimiento
            - Problemas de mantenibilidad
            - Violaciones de mejores prácticas
            - Mal uso de patrones de diseño
            
            Sugiere mejoras específicas con ejemplos.
            """,
            "general": """
            Realiza una revisión integral del código enfocándote en:
            - Arquitectura general
            - Manejo de errores
            - Calidad de documentación
            - Gaps en cobertura de pruebas
            """
        }
        
        return f"{base_prompts.get(analysis_type, base_prompts['general'])}\n\nCódigo:\n```java\n{code_content}\n```"
    
    def generate_comprehensive_report(self, static_results, ai_results):
        """Generate HTML report combining static analysis and AI insights"""

        # Crear el directorio si no existe
        Path("scan-results").mkdir(parents=True, exist_ok=True)

        # Generar contenido dinámico
        static_content = self.format_static_results(static_results)
        ai_content = self.format_ai_results(ai_results)
        summary_content = self.generate_summary(static_results, ai_results)

        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>AI-Powered Code Analysis Report</title>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }}
                .severity-high {{ color: #d32f2f; font-weight: bold; }}
                .severity-medium {{ color: #f57c00; font-weight: bold; }}
                .severity-low {{ color: #388e3c; }}
                .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
                .ai-insight {{ background-color: #e3f2fd; padding: 15px; margin: 10px 0; border-radius: 5px; }}
                .file-analysis {{ background-color: #f5f5f5; padding: 10px; margin: 10px 0; border-radius: 3px; }}
                .analysis-type {{ font-weight: bold; color: #1976d2; margin-top: 15px; }}
                pre {{ background-color: #f8f8f8; padding: 10px; border-radius: 3px; overflow-x: auto; }}
                h1 {{ color: #1976d2; }}
                h2 {{ color: #424242; border-bottom: 2px solid #ddd; padding-bottom: 5px; }}
                h3 {{ color: #666; }}
            </style>
        </head>
        <body>
            <h1>🤖 AI-Powered Security & Quality Analysis Report</h1>
            
            <div class="section">
                <h2>📊 Executive Summary</h2>
                {summary_content}
            </div>
            
            <div class="section">
                <h2>🔍 Static Analysis Results</h2>
                {static_content}
            </div>
            
            <div class="section">
                <h2>🧠 AI-Enhanced Insights</h2>
                {ai_content}
            </div>
            
            <div class="section">
                <h2>💡 Recommendations</h2>
                <div class="ai-insight">
                    <h3>Próximos Pasos Recomendados:</h3>
                    <ul>
                        <li>Implementar herramientas de análisis estático (SonarQube, SpotBugs, OWASP Dependency Check)</li>
                        <li>Revisar y aplicar las sugerencias de seguridad identificadas por AI</li>
                        <li>Mejorar la calidad del código según las recomendaciones de AI</li>
                        <li>Establecer un pipeline de CI/CD con análisis automatizado</li>
                    </ul>
                </div>
            </div>
            
            <div class="section">
                <h2>📈 Métricas del Análisis</h2>
                <p><strong>Archivos analizados:</strong> {len(ai_results)}</p>
                <p><strong>Tipos de análisis realizados:</strong> Seguridad, Calidad de Código</p>
                <p><strong>Herramientas de análisis estático encontradas:</strong> {len(static_results)}</p>
                <p><strong>Fecha del análisis:</strong> {self.get_current_timestamp()}</p>
            </div>
        </body>
        </html>
        """
        
        # Generate and save report
        report_path = "scan-results/ai-analysis-report.html"
        with open(report_path, "w", encoding='utf-8') as f:
            f.write(html_template)
        
        print(f"\n✅ Reporte generado exitosamente: {report_path}")
        return report_path

    def format_static_results(self, static_results):
        """Format static analysis results for HTML"""
        if not static_results:
            return "<p>⚠️ No se encontraron resultados de herramientas de análisis estático.</p><p>Considera ejecutar: SonarQube, OWASP Dependency Check, o SpotBugs.</p>"
        
        content = "<ul>"
        for tool, results in static_results.items():
            content += f"<li><strong>{tool.upper()}:</strong> {results}</li>"
        content += "</ul>"
        return content

    def format_ai_results(self, ai_results):
        """Format AI analysis results for HTML"""
        if not ai_results:
            return "<p>❌ No se pudieron obtener resultados del análisis con AI.</p>"
        
        content = ""
        for file_path, analyses in ai_results.items():
            content += f'<div class="file-analysis"><h3>📄 {file_path}</h3>'
            
            for analysis_type, result in analyses.items():
                content += f'<div class="analysis-type">🔍 Análisis de {analysis_type.capitalize()}:</div>'
                # Escapar caracteres HTML y formatear el resultado
                formatted_result = result.replace('<', '&lt;').replace('>', '&gt;').replace('\n', '<br>')
                content += f'<div class="ai-insight"><pre>{formatted_result}</pre></div>'
            
            content += '</div>'
        
        return content

    def generate_summary(self, static_results, ai_results):
        """Generate executive summary"""
        files_analyzed = len(ai_results)
        static_tools = len(static_results)
        
        summary = f"""
        <p>Se analizaron <strong>{files_analyzed}</strong> archivos Java utilizando análisis potenciado por IA.</p>
        <p>Se encontraron <strong>{static_tools}</strong> herramientas de análisis estático configuradas.</p>
        """
        
        if files_analyzed > 0:
            summary += "<p class='severity-medium'>✅ El análisis con IA se completó exitosamente.</p>"
        else:
            summary += "<p class='severity-high'>❌ No se pudieron analizar archivos con IA.</p>"
            
        return summary

    def get_current_timestamp(self):
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

if __name__ == "__main__":
    print("🚀 Iniciando AI Code Analyzer...")
    
    analyzer = AICodeAnalyzer()
    
    # Collect static analysis results
    print("\n📊 Recolectando resultados de análisis estático...")
    static_results = analyzer.collect_static_analysis_results()
    print(f"Herramientas encontradas: {len(static_results)}")
    
    # Analyze source code with AI
    print("\n🔍 Buscando archivos Java...")
    java_files = list(Path("my-app/src").rglob("*.java"))
    print(f"Archivos Java encontrados: {len(java_files)}")
    
    if not java_files:
        print("❌ No se encontraron archivos Java en my-app/src")
        print("Estructura esperada: my-app/src/**/*.java")
        sys.exit(1)
    
    ai_results = {}
    
    for i, java_file in enumerate(java_files, 1):
        print(f"\n📝 Analizando archivo {i}/{len(java_files)}: {java_file}")
        
        try:
            with open(java_file, 'r', encoding='utf-8') as f:
                code_content = f.read()
            
            print(f"Contenido del archivo ({len(code_content)} caracteres):")
            print("=" * 50)
            print(code_content[:200] + "..." if len(code_content) > 200 else code_content)
            print("=" * 50)
            
            # Perform different types of AI analysis
            ai_results[str(java_file)] = {
                'security': analyzer.analyze_with_ai(code_content, 'security'),
                'quality': analyzer.analyze_with_ai(code_content, 'quality')
            }
            
        except Exception as e:
            print(f"❌ Error procesando {java_file}: {str(e)}")
            ai_results[str(java_file)] = {
                'security': f'Error: {str(e)}',
                'quality': f'Error: {str(e)}'
            }
    
    # Generate comprehensive report
    print(f"\n📄 Generando reporte comprensivo...")
    print(f"Resultados estáticos: {len(static_results)} herramientas")
    print(f"Resultados AI: {len(ai_results)} archivos")
    
    report_path = analyzer.generate_comprehensive_report(static_results, ai_results)
    
    print(f"\n🎉 Análisis completado!")
    print(f"📂 Reporte disponible en: {report_path}")