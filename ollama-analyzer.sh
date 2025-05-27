#!/bin/bash
# ollama-analyzer.sh

OLLAMA_MODEL="codellama:13b"
INPUT_FILE="$1"
OUTPUT_FILE="$2"

# Function to analyze code with Ollama
analyze_with_ollama() {
    local prompt="Analyze this Java code for security vulnerabilities and code quality issues. 
    Provide specific recommendations and severity ratings:
    
    $(cat $INPUT_FILE)"
    
    curl -X POST http://localhost:11434/api/generate \
        -H "Content-Type: application/json" \
        -d "{
            \"model\": \"$OLLAMA_MODEL\",
            \"prompt\": \"$prompt\",
            \"stream\": false,
            \"options\": {
                \"temperature\": 0.1,
                \"top_p\": 0.9
            }
        }" | jq -r '.response' > "$OUTPUT_FILE"
}

analyze_with_ollama