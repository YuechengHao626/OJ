#!/bin/bash

# OpenJudge Performance Test Runner
# This script runs k6 performance tests against the OpenJudge submission API

echo "🚀 OpenJudge Performance Test Runner"
echo "======================================"

# Check if k6 is installed
if ! command -v k6 &> /dev/null; then
    echo "❌ k6 is not installed. Please install k6 first:"
    echo "   macOS: brew install k6"
    echo "   Ubuntu: sudo apt-get install k6"
    echo "   Windows: choco install k6"
    echo "   Or visit: https://k6.io/docs/getting-started/installation/"
    exit 1
fi

echo "✅ k6 is installed"

# Check if the test script exists
if [ ! -f "k6_performance_test.js" ]; then
    echo "❌ k6_performance_test.js not found in current directory"
    exit 1
fi

echo "✅ Test script found"

# Create output directory for results
mkdir -p performance_results
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
OUTPUT_FILE="performance_results/openjudge_performance_${TIMESTAMP}.json"

echo "📊 Starting performance test..."
echo "📁 Results will be saved to: $OUTPUT_FILE"
echo ""

# Run the k6 test with JSON output for detailed analysis
k6 run \
    --out json=$OUTPUT_FILE \
    --summary-trend-stats="avg,min,med,max,p(90),p(95),p(99)" \
    k6_performance_test.js

# Check if test completed successfully
if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Performance test completed successfully!"
    echo "📊 Results saved to: $OUTPUT_FILE"
    echo ""
    echo "💡 Quick Analysis Tips:"
    echo "   - Check 'http_req_duration' for response times"
    echo "   - Monitor 'http_req_failed' for error rates"
    echo "   - Review 'submission_success_rate' for API reliability"
    echo "   - Examine 'submission_duration' for processing times"
    echo ""
    echo "🔍 For detailed analysis, you can:"
    echo "   1. Import the JSON file into k6 Cloud or Grafana"
    echo "   2. Use jq to query specific metrics: jq '.metrics' $OUTPUT_FILE"
    echo "   3. Generate HTML reports with k6-reporter"
else
    echo ""
    echo "❌ Performance test failed!"
    echo "🔍 Check the output above for error details"
    exit 1
fi 