// quality-gates.groovy
def evaluateQualityGates() {
    def reportPath = "scan-results/ai-analysis-report.json"
    def report = readJSON file: reportPath
    
    def criticalIssues = report.issues.findAll { it.severity == 'CRITICAL' }
    def highIssues = report.issues.findAll { it.severity == 'HIGH' }
    
    // Define quality gates
    def gates = [
        criticalIssues: [threshold: 0, current: criticalIssues.size()],
        highIssues: [threshold: 5, current: highIssues.size()],
        aiScore: [threshold: 7.0, current: report.aiQualityScore]
    ]
    
    def failed = []
    gates.each { gate, values ->
        if (values.current > values.threshold) {
            failed.add("${gate}: ${values.current} > ${values.threshold}")
        }
    }
    
    if (failed) {
        error("Quality gates failed: ${failed.join(', ')}")
    } else {
        echo "All quality gates passed successfully"
    }
}