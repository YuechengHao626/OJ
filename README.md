# 2025_P4_OpenJudge - Educational Online Judge Platform


## Project Overview

OpenJudge is an educational online judge platform designed to address a key limitation of existing competitive programming platforms. Unlike traditional online judges such as LeetCode or Codeforces that hide test cases to prevent students from exploiting test cases, our system is built specifically for educational purposes where **all test cases are fully visible** to students. Currently, this MVP version only supports solving problems using **Python**.

This transparency allows students to:
- **Learn from their mistakes** by seeing exactly which test cases fail
- **Debug more effectively** with complete visibility into expected vs. actual outputs  
- **Improve problem-solving skills** through iterative refinement based on clear feedback
- **Understand edge cases** that they might not have considered

The platform maintains the familiar Online Judge model while prioritizing learning and understanding over competitive assessment.

## 🚀 Live Demo

**Access the deployed platform**: [http://coughoverflow-alb-1348614147.us-east-1.elb.amazonaws.com/](http://coughoverflow-alb-1348614147.us-east-1.elb.amazonaws.com/)

**Default Login Credentials:**
- **Username**: `CSSE6400`
- **Password**: `qimojiayou`

Use these credentials to explore the platform's features, submit code solutions, and experience the educational-focused online judge environment.

## 📁 Repository Structure

```
2025_P4_OpenJudge/
├── OpenJudge/                    # Main application directory
│   ├── app/                      # Flask application core
│   │   ├── models/              # Database models (User, Problem, Submission)
│   │   ├── routes/              # API endpoints and route handlers
│   │   ├── tasks.py             # Celery task definitions for async judging
│   │   ├── utils/               # Helper functions and utilities
│   │   └── __init__.py          # Flask app factory
│   ├── test/                    # Comprehensive test suite
│   │   ├── test_basic.py        # Basic functionality tests
│   │   ├── test_judge_integration.py  # Judge system integration tests
│   │   ├── test_validation.py   # Parameter validation and security tests
│   │   ├── k6_performance_test.js     # k6 performance testing script
│   │   ├── run_performance_test.sh    # Performance test runner
│   │   ├── test.sh              # One-click test execution script
│   │   └── auth_helper.py       # Authentication test utilities
│   ├── instance/                # Instance-specific configuration
│   ├── *.tf                     # Terraform infrastructure files
│   │   ├── main.tf              # Core AWS infrastructure (ECS, ALB, VPC)
│   │   ├── rds.tf               # PostgreSQL database configuration
│   │   ├── sqs.tf               # SQS message queue setup
│   │   ├── celery.tf            # Celery worker infrastructure
│   │   └── autoscaling.tf       # Auto-scaling policies
│   ├── deploy.sh                # One-click deployment script
│   ├── dockerfile               # Container image definition
│   ├── docker-compose.yml       # Local development environment
│   ├── pyproject.toml           # Python dependencies and project metadata
│   └── credentials              # AWS credentials (create manually)
└── README.md                    # Project documentation (this file)
```

**Key Components:**
- **`app/`**: Core Flask application with MVC architecture
- **`test/`**: Comprehensive endpoint-level tests including validation and security testing for cloud deployment
- **`*.tf`**: Complete AWS infrastructure as code using Terraform
- **`deploy.sh`**: Automated deployment pipeline
- **`docker-compose.yml`**: Local development environment setup (don't use it in main branch,which is cloud version)

## Deployment

### Architecture Stack
- **Backend**: Flask (REST API)
- **Authentication**: JSON Web Token (JWT)
- **Task Queue**: Celery 
- **Message Broker**: AWS SQS
- **Database**: PostgreSQL (AWS RDS)
- **Load Balancing**: AWS Application Load Balancer (ALB)
- **Auto Scaling**: ECS Service Auto Scaling for API and Worker
- **Infrastructure**: Terraform, Docker, AWS services

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Flask Web     │    │  SQS Message    │    │ Celery Worker   │
│      API        │◄──►│     Broker      │◄──►│   (Async)       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                                              
         │                                              
         ▼                                              
┌─────────────────┐                          
│ PostgreSQL (RDS)│                          
│   (Database)    │                          
└─────────────────┘                          
```
**Sandbox Removal**: Unlike local version, we removed judge sandbox in cloud version. We originally planned to implement sandboxed containerized judging using ECS RunTask via boto3 to isolate user code execution. However, during implementation we discovered that launching a new container per submission introduced unacceptable latency in the cloud environment. As a result, we removed the sandbox component and now execute judging logic directly within the Celery worker process. The security and performance trade-offs of this decision are documented in detail in our final project report.

### Branch Structure
Due to configuration differences, I used the main branch to support the cloud-deployed version and endpoint testing, while the local branch is used for local development and internal testing.
- **`main` branch**: Cloud-deployed production version using AWS infrastructure (currently live at the URL above) with end-point and performance tests.
- **`local` branch**: Local development and internal testing environment

### Cloud Deployment (main branch)

1. **Navigate to the project directory:**
   ```bash
   cd OpenJudge/
   ```

2. **Configure AWS credentials:**
   Create a file named `credentials` with your AWS credentials:
   ```ini
   [default]
   aws_access_key_id=YOUR_KEY
   aws_secret_access_key=YOUR_SECRET
   aws_session_token=YOUR_SESSION_TOKEN
   ```

3. **Deploy the infrastructure:**
   ```bash
   ./deploy.sh
   ```

The deployment script will:
- Initialize and upgrade Terraform modules
- Apply the complete AWS infrastructure configuration
- Output the API endpoint URL upon successful completion

**Recommend you use Ubuntu to deploy it to AWS, just in case of some weird problem.** 

## Usage

### Usage Model

OpenJudge follows the traditional Online Judge paradigm similar to ACM/ICPC-style online judge model, which is different from leetcode mode
- Students submit source code solutions for predefined programming problems
- The system executes submissions against multiple test cases
- Each test case receives a verdict (PASS/FAIL/ERROR) with detailed output comparison
- **Submissions must read input from standard input and print output to standard output**
- **Only support python code**


### Example Problem

**Problem 1: Odd or Even**

**Description**: Given an integer, print 'even' if it is even, or 'odd' if it is odd.

**Sample Input:**
```
3
```

**Expected Output:**
```
odd
```

**Correct Submission (Python):**
```python
n = int(input())
print('even' if n % 2 == 0 else 'odd')
```
**Problem 2: Armstrong Number**

**Description**: Check whether a 3-digit number is an Armstrong number. Print 'yes' or 'no'.

**Sample Input:**
```
153
```

**Expected Output:**
```
yes
```

**Correct Submission (Python):**
```python
def is_armstrong_number(n):
    # Check if the number is a 3-digit number
    if not (100 <= n <= 999):
        return "no"

    # Convert the number to a string to easily access its digits
    s_n = str(n)

    # Calculate the sum of the cubes of its digits
    sum_of_cubes = int(s_n[0]) ** 3 + int(s_n[1]) ** 3 + int(
        s_n[2]) ** 3

    # Check if it's an Armstrong number
    if sum_of_cubes == n:
        return "yes"
    else:
        return "no"


# Read the input
n = int(input())

# Call the function and print the result
print(is_armstrong_number(n))
```

![Successful Test Result](/model/frontend_result.jpg)


## Testing Strategy

### Cloud Testing (main branch)
Endpoint-level integration tests, parameter validation tests, and performance tests(k6) are located in the `OpenJudge/test/` directory. These tests:
- API authentication and authorization
- Problem submission workflows  
- Judge execution and verdict reporting
- Database persistence and retrieval
- User isolation and access control
- Parameter validation and security testing
- Performance and load testing

**Test Files:**
- **`test_basic.py`**: Core functionality tests including health checks, authentication, and basic judge operations
- **`test_judge_integration.py`**: Comprehensive judge system integration tests with various code scenarios
- **`test_validation.py`**: Parameter validation and security tests including:
  - Authentication field validation (registration/login)
  - Missing required field detection
  - Invalid data type handling
  - Code length limit enforcement (50KB)
  - Dangerous code pattern detection (import os, eval, exec, etc.)
  - Malformed JSON handling
  - Unauthorized access prevention
- **`k6_performance_test.js`**: k6 performance testing script for load testing
- **`run_performance_test.sh`**: Performance test runner script
- **`test.sh`**: One-click test execution script that runs all three test suites (basic, integration, validation)
- **`auth_helper.py`**: Authentication utilities and helper functions for testing

**Three-Phase Testing Strategy:**
1. **Phase 1: Basic Functionality Tests** - Core system health and authentication
2. **Phase 2: System Integration Tests** - End-to-end judge workflow validation  
3. **Phase 3: Parameter Validation Tests** - Security and input validation verification

More information please refer to README.md in test folder. If want to test more, please switch to local branch and do internal tests.

#### Performance Testing with k6
We use k6 for comprehensive performance testing that simulates realistic academic workloads and validates system scalability under peak usage conditions.

**Running Performance Tests:**
```bash
cd OpenJudge/test

# Install k6 (if not already installed)
# macOS: brew install k6
# Ubuntu: sudo apt-get install k6
# Windows: choco install k6

# Run performance test with automatic result saving
./run_performance_test.sh
```

**Performance Test Features:**
- **Academic Scenario Simulation**: Models real classroom usage patterns with concurrent student submissions
- **Load Testing**: Tests system behavior under peak academic loads (assignment deadline scenarios)
- **Scalability Validation**: Confirms auto-scaling effectiveness and system stability
- **Comprehensive Metrics**: Tracks response times, throughput, success rates, and system performance

**Recent Performance Results:**
- **Peak Load**: 25 concurrent users sustained for 90 seconds
- **Submission Success Rate**: 100% (250 submissions processed)
- **Average Response Time**: 1.67 seconds
- **95th Percentile**: 3.22 seconds
- **Throughput**: 6.33 requests/second


**Running Endpoint Functional Tests:**
```bash
cd OpenJudge/test
./test.sh
```
If you choose to deploy the service yourself, replace the request URL with your own and install the requests library via pip.

The test script will automatically run both basic and integration test suites, providing comprehensive validation of the cloud deployment.

### Local Testing (local branch)
Due to differences in configuration between the local and cloud environments, I have separated the codebase into two branches: local and main. The local branch supports internal function testing during local development(Internal tests are far more comprehensive than endpoint tests!). For local development, internal function and unit tests can be executed using:
```bash
./build_and_test.sh
```
This command will automatically build the Docker image and run all internal unit and integration tests within the local development environment.

All test scripts with description are located in OpenJudge/localtest 
```bash
   cd OpenJudge/localtest 
```

This command runs the complete test suite including unit tests for core functionality and integration tests for the local development environment. It internally invokes the test scripts located in the OpenJudge/test/ directory.



---


## 🔒 Security Features

Our OpenJudge platform implements several security measures to protect user data and prevent common web vulnerabilities:

### Authentication & Session Management
- **HTTP-only Cookies**: JWT tokens are stored in HTTP-only cookies to prevent XSS attacks from accessing authentication tokens
- **Secure Cookie Configuration**: Cookies include `SameSite=Lax` protection against CSRF attacks
- **Password Security**: User passwords are hashed using bcrypt with individual salt values
- **JWT Token Expiration**: Authentication tokens automatically expire after 24 hours

### Code Execution Security
- **Input Sanitization**: All user inputs are validated and sanitized before processing
- **Dangerous Pattern Detection**: Code submissions are scanned for potentially unsafe patterns including:
  - File system operations (`import os`, `open()`, `file()`)
  - Network operations (`import socket`, `import requests`)
  - System operations (`import subprocess`, `eval()`, `exec()`)
  - Destructive operations (`rmdir`, `remove`, `delete`)

### API Security
- **Request Validation**: All API endpoints validate JSON payloads and parameter types
- **Authentication Required**: Protected endpoints require valid JWT tokens via HTTP-only cookies
- **Error Handling**: Secure error messages that don't expose sensitive system information

**Note**: While we removed containerized sandboxing for performance reasons, the direct execution approach includes comprehensive input validation and dangerous code pattern detection to maintain security.



