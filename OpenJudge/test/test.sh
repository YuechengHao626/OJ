#!/bin/bash

# OpenJudge Cloud Test Suite
# One-click execution of basic tests, integration tests, and validation tests

set -e  # Exit on error

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored messages
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_header() {
    echo -e "${BLUE}"
    echo "=================================================="
    echo "🚀 OpenJudge Cloud Test Suite"
    echo "=================================================="
    echo -e "${NC}"
    echo "Test Target: http://coughoverflow-alb-1348614147.us-east-1.elb.amazonaws.com"
    echo ""
}

# Check Python environment
check_python() {
    print_info "Checking Python environment..."
    
    if ! command -v python3 &> /dev/null; then
        print_error "Python3 not installed, please install Python3 first"
        exit 1
    fi
    
    python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
    print_success "Python version: $python_version"
    
    # Check required packages
    print_info "Checking required Python packages..."
    python3 -c "import requests, json, time, uuid, random, string" 2>/dev/null || {
        print_error "Missing required Python packages, please install: pip install requests"
        exit 1
    }
    print_success "Python package check passed"
}

# Run basic tests
run_basic_tests() {
    print_info "Starting basic tests..."
    echo ""
    
    if python3 test_basic.py; then
        print_success "Basic tests completed"
        return 0
    else
        print_error "Basic tests failed"
        return 1
    fi
}

# Run integration tests
run_integration_tests() {
    print_info "Starting integration tests..."
    echo ""
    
    if python3 test_judge_integration.py; then
        print_success "Integration tests completed"
        return 0
    else
        print_error "Integration tests failed"
        return 1
    fi
}

# Run validation tests
run_validation_tests() {
    print_info "Starting validation tests..."
    echo ""
    
    if python3 test_validation.py; then
        print_success "Validation tests completed"
        return 0
    else
        print_error "Validation tests failed"
        return 1
    fi
}

# Main function
main() {
    print_header
    
    # Check environment
    check_python
    echo ""
    
    # Record start time
    start_time=$(date +%s)
    
    # Run tests
    basic_result=0
    integration_result=0
    validation_result=0
    
    echo "🧪 Starting test process..."
    echo ""
    
    # Basic tests
    echo "📋 Phase 1: Basic Functionality Tests"
    echo "----------------------------------------"
    if run_basic_tests; then
        basic_result=1
    fi
    echo ""
    
    # Integration tests
    echo "🔗 Phase 2: System Integration Tests"
    echo "----------------------------------------"
    if run_integration_tests; then
        integration_result=1
    fi
    echo ""
    
    # Validation tests
    echo "🔍 Phase 3: Parameter Validation Tests"
    echo "----------------------------------------"
    if run_validation_tests; then
        validation_result=1
    fi
    echo ""
    
    # Calculate total duration
    end_time=$(date +%s)
    duration=$((end_time - start_time))
    
    # Output test result summary
    echo "=================================================="
    echo "📊 Test Result Summary"
    echo "=================================================="
    
    if [ $basic_result -eq 1 ]; then
        print_success "Basic Tests: PASSED"
    else
        print_error "Basic Tests: FAILED"
    fi
    
    if [ $integration_result -eq 1 ]; then
        print_success "Integration Tests: PASSED"
    else
        print_error "Integration Tests: FAILED"
    fi
    
    if [ $validation_result -eq 1 ]; then
        print_success "Validation Tests: PASSED"
    else
        print_error "Validation Tests: FAILED"
    fi
    
    echo ""
    print_info "Total Duration: ${duration} seconds"
    
    # Set exit code based on test results
    if [ $basic_result -eq 1 ] && [ $integration_result -eq 1 ] && [ $validation_result -eq 1 ]; then
        print_success "🎉 All tests passed! OpenJudge cloud system is running normally"
        exit 0
    else
        print_error "❌ Some tests failed, please check system status"
        exit 1
    fi
}

# Handle interrupt signal
trap 'print_warning "Tests interrupted by user"; exit 130' INT

# Check if running in correct directory
if [ ! -f "test_basic.py" ] || [ ! -f "test_judge_integration.py" ] || [ ! -f "test_validation.py" ]; then
    print_error "Please run this script in the test directory"
    print_info "Correct usage: cd OpenJudge/test && ./test.sh"
    exit 1
fi

# Run main function
main "$@" 