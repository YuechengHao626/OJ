# OpenJudge Test Suite

This directory contains comprehensive integration tests for the OpenJudge cloud deployment. The test suite validates core functionality, authentication systems, parameter validation, security measures, and judge execution workflows in the AWS production environment.

## 📁 Test Structure

```
test/
├── test_basic.py              # Core functionality and authentication tests
├── test_judge_integration.py  # Comprehensive judge system integration tests
├── test_validation.py         # Parameter validation and security tests
├── test.sh                    # One-click test execution script (3-phase testing)
├── auth_helper.py             # Authentication utilities and helper functions
├── k6_performance_test.js     # k6 performance testing script
├── run_performance_test.sh    # Performance test runner script
└── README.md                  # This documentation file
```

## 🧪 Test Files Overview

### `test_basic.py` - Core Functionality Tests
**Purpose**: Validates essential system functionality and user authentication workflows.

**Test Coverage**:
- **Health Check**: Verifies service availability and basic endpoint responses
- **Public Endpoints**: Tests publicly accessible routes and their responses
- **Authentication System**: Comprehensive user registration, login, and session management
- **Authenticated Submission**: Code submission workflow with proper authentication
- **Authenticated Result Query**: Result retrieval with user authentication
- **User Isolation**: Ensures users can only access their own submissions

### `test_judge_integration.py` - Judge System Integration Tests
**Purpose**: Comprehensive end-to-end testing of the judge system with various code scenarios.

**Test Coverage**:
1. **Direct Judge Module Test**: Direct function calls to the judge module
2. **Authenticated Judge Functionality**: Complete judge workflow via Flask API
3. **User Submission Isolation**: Cross-user access control validation
4. **Submission List Functionality**: Historical submission retrieval

**Code Test Scenarios**:
- ✅ **Correct Code**: Valid odd/even checker that passes all test cases
- ❌ **Incorrect Logic**: Code with reversed logic that fails test cases
- 🚫 **Syntax Error**: Code with Python syntax errors
- ⚠️ **Runtime Error**: Code that causes runtime exceptions (e.g., division by zero)

### `test_validation.py` - Parameter Validation and Security Tests ⭐ NEW
**Purpose**: Comprehensive validation of API parameter handling and security measures.

**Test Coverage**:
1. **Authentication Validation**: Registration and login field validation
   - Missing required fields (username, password)
   - Invalid username formats (too short/long, special characters)
   - Invalid password formats (too short/long, wrong data types)
   - Empty field handling

2. **Unauthorized Access Testing**: Security boundary validation
   - Protected endpoint access without authentication
   - Cross-user data access prevention
   - JWT token requirement enforcement

3. **Request Validation**: Input parameter validation
   - Missing required fields (code, problem_id)
   - Invalid data types (numbers, null, arrays instead of strings)
   - Invalid values (empty code, out-of-range problem_id)

4. **Security Pattern Detection**: Dangerous code prevention
   - File system operations (`import os`, `open()`)
   - Code execution functions (`eval()`, `exec()`)
   - Network operations (`import socket`, `subprocess`)
   - Dynamic imports (`__import__()`)

5. **Input Constraints**: System limits enforcement
   - Code length limits (50KB maximum)
   - Malformed JSON handling
   - Content-type validation

**Security Test Scenarios**:
- 🔐 **Authentication Bypass Attempts**: Unauthorized API access
- ⚠️ **Dangerous Code Injection**: Malicious code pattern detection
- 📏 **Resource Limit Testing**: Code size and format constraints
- 🔧 **Malformed Request Handling**: Invalid JSON and data types

### `auth_helper.py` - Authentication Utilities
**Purpose**: Provides reusable authentication functions for test scenarios.

**Key Features**:
- User registration and login automation
- JWT token management
- Authenticated HTTP request handling
- Session cleanup and logout functionality

### `test.sh` - Three-Phase Test Execution Script
**Purpose**: One-click execution of the complete test suite with comprehensive validation.

**Three-Phase Testing Strategy**:
1. **Phase 1: Basic Functionality Tests** - Core system health and authentication
2. **Phase 2: System Integration Tests** - End-to-end judge workflow validation  
3. **Phase 3: Parameter Validation Tests** - Security and input validation verification

**Features**:
- Automated test environment setup
- Sequential execution of all three test phases
- Comprehensive result reporting with phase-by-phase breakdown
- Color-coded output for easy result interpretation
- Total test duration tracking

### `k6_performance_test.js` - Performance Testing Script
**Purpose**: Load testing for the OpenJudge submission API using k6.

**Test Scenarios**:
- **Academic Peak Usage**: Simulates 10-30 concurrent students submitting code
- **Realistic Workload**: Mixed submission types (correct, errors, syntax issues)
- **Authentication Flow**: Complete user registration and login simulation
- **Multiple Submissions**: Students making 1-3 submissions per session

**Key Metrics Tracked**:
- **Response Time**: Average, P95, P99 percentiles
- **Throughput**: Requests per second
- **Error Rate**: Failed request percentage
- **Submission Success Rate**: API reliability metric

### `run_performance_test.sh` - Performance Test Runner
**Purpose**: Simplified script to execute k6 performance tests with proper setup.

**Features**:
- Automatic k6 installation check
- Result file management with timestamps
- Detailed metric reporting
- Analysis tips and recommendations

## 🚀 Running Tests

### Quick Start - Complete Test Suite (Recommended)
```bash
cd OpenJudge/test
./test.sh
```
This runs all three phases: Basic → Integration → Validation

### Individual Test Execution
```bash
# Run basic functionality tests (Phase 1)
python test_basic.py

# Run judge integration tests (Phase 2)
python test_judge_integration.py

# Run parameter validation tests (Phase 3)
python test_validation.py
```

### Performance Testing
```bash
# Install k6 first (if not already installed)
# macOS: brew install k6
# Ubuntu: sudo apt-get install k6

# Run performance tests
./run_performance_test.sh

# Or run k6 directly with custom options
k6 run k6_performance_test.js
```

## 📊 Test Results Interpretation

### Success Indicators
- ✅ **PASS**: Test completed successfully
- 📊 **Statistics**: Test case pass/fail ratios
- 🎉 **Summary**: Overall test suite completion
- 🔒 **Security**: Validation and security tests passed

### Failure Indicators
- ❌ **FAIL**: Test failed with specific error details
- ⚠️ **WARNING**: Partial success or non-critical issues
- 💡 **HINTS**: Troubleshooting suggestions for failed tests
- 🚫 **Security Issues**: Failed validation or security tests

### Three-Phase Test Results
The test suite provides detailed results for each phase:
- **Phase 1 Results**: Basic functionality status
- **Phase 2 Results**: Integration test outcomes  
- **Phase 3 Results**: Validation test summary with detailed security metrics

### Performance Metrics
- **Response Time**: Should be under 2s for 95% of requests
- **Error Rate**: Should be less than 1%
- **Submission Success Rate**: Should be above 95%
- **Throughput**: Requests per second during peak load

## 🔧 Test Environment Requirements

### Prerequisites
- **Python 3.8+** with required dependencies
- **Network Access** to deployed OpenJudge instance
- **AWS Infrastructure** properly deployed and accessible
- **k6** for performance testing (optional)

### Configuration
Tests automatically connect to the deployed OpenJudge instance. No additional configuration is required if the deployment was successful.

## 🎯 Test Philosophy

These tests follow an **endpoint-level integration testing** approach, validating the complete user journey from authentication to code submission and result retrieval. The three-phase approach ensures:

1. **Real-world Workflows** function correctly in the cloud environment
2. **Authentication Security** properly protects user data
3. **Parameter Validation** prevents malicious input and ensures data integrity
4. **Judge System** accurately evaluates various code scenarios
5. **User Isolation** maintains data privacy between different users
6. **System Reliability** handles both success and error cases gracefully
7. **Security Boundaries** protect against common web vulnerabilities
8. **Performance Standards** meet academic usage requirements under load

## 🔍 Debugging Failed Tests

If tests fail, check the following:

### General Issues
1. **Service Availability**: Ensure the OpenJudge deployment is running
2. **Network Connectivity**: Verify access to the deployed endpoint
3. **Database State**: Check if the PostgreSQL RDS instance is accessible
4. **Worker Status**: Confirm Celery workers are processing judge tasks
5. **Infrastructure Health**: Review AWS service status and logs

### Validation Test Issues
- **Authentication Failures**: Check JWT configuration and user registration limits
- **Parameter Validation Failures**: Verify API input validation logic
- **Security Test Failures**: Review dangerous code pattern detection
- **Unauthorized Access**: Confirm authentication middleware is working

### Performance Test Debugging
- **High Response Times**: Check AWS ECS scaling policies and database performance
- **High Error Rates**: Review application logs and database connection limits
- **Authentication Failures**: Verify JWT token configuration and session management
- **Submission Failures**: Check Celery worker status and SQS queue health

## 📈 Extending Tests

To add new test scenarios:

1. **Basic Tests**: Add new functions to `test_basic.py` for core functionality
2. **Judge Tests**: Extend `test_judge_integration.py` with additional code scenarios
3. **Validation Tests**: Add new security patterns or validation rules to `test_validation.py`
4. **Authentication**: Enhance `auth_helper.py` with new authentication patterns
5. **Execution**: Update `test.sh` to include new test files or phases
6. **Performance**: Modify `k6_performance_test.js` to add new load patterns or user behaviors

## 🎓 Academic Usage Notes

This test suite is specifically designed for educational environments:

- **Realistic Load Patterns**: Simulates actual student submission behavior
- **Academic Scenarios**: Tests common student coding mistakes and patterns
- **Security Validation**: Ensures safe code execution in educational settings
- **Scalability Validation**: Ensures the system can handle classroom-sized loads
- **Educational Metrics**: Focuses on response times and reliability important for learning
- **Input Validation**: Protects against common student input errors and malicious attempts

---

**Note**: These tests are specifically designed for the cloud deployment environment. For local development testing, refer to the `local` branch which contains additional unit tests and local environment configurations. 