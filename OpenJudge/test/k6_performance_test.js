/**
 * OpenJudge Performance Test Script using k6
 * 
 * This script simulates peak usage in an academic setting where students
 * submit code solutions to the OpenJudge platform. It tests the submission
 * API under realistic load conditions.
 * 
 * Usage: k6 run k6_performance_test.js
 * 
 * Requirements:
 * - k6 installed (https://k6.io/docs/getting-started/installation/)
 * - OpenJudge platform running and accessible
 */

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';

// =============================================================================
// CONFIGURATION
// =============================================================================

// Target URL - Replace with your OpenJudge deployment
const BASE_URL = 'http://coughoverflow-alb-1348614147.us-east-1.elb.amazonaws.com';

// Test configuration for academic peak usage simulation
export let options = {
  stages: [
    // Ramp up: Simulate students gradually joining the session
    { duration: '10s', target: 10 },   // Start with 10 concurrent users
    
    // Peak load: Simulate peak submission time (e.g., near assignment deadline)
    { duration: '30s', target: 25 },   // Increase to 25 concurrent users
    
    // Sustained load: Maintain peak usage
    { duration: '30s', target: 25 },   // Hold at 25 users for 30 seconds
    
    // Cool down: Students finishing their submissions
    { duration: '10s', target: 5 },    // Reduce to 5 users
    { duration: '10s', target: 0 },    // Ramp down to 0
  ],
  
  // Thresholds define our performance criteria
  thresholds: {
    // 95% of requests should complete within 2 seconds (good for academic use)
    http_req_duration: ['p(95)<2000'],
    
    // 99% of requests should complete within 5 seconds
    'http_req_duration{expected_response:true}': ['p(99)<5000'],
    
    // Error rate should be less than 1%
    http_req_failed: ['rate<0.01'],
    
    // Submission success rate should be above 95%
    submission_success_rate: ['rate>0.95'],
  },
};

// =============================================================================
// CUSTOM METRICS
// =============================================================================

// Track submission-specific metrics
const submissionSuccessRate = new Rate('submission_success_rate');
const submissionDuration = new Trend('submission_duration');
const authFailures = new Counter('auth_failures');

// =============================================================================
// TEST DATA - REALISTIC CODE SUBMISSIONS
// =============================================================================

// Simulate different types of code submissions students might make
const codeSubmissions = [
  // Correct solution
  {
    name: 'correct_solution',
    code: `n = int(input())
print('even' if n % 2 == 0 else 'odd')`,
    weight: 0.6  // 60% of submissions are correct
  },
  
  // Common mistake - reversed logic
  {
    name: 'logic_error',
    code: `n = int(input())
print('odd' if n % 2 == 0 else 'even')  # Oops, logic is reversed`,
    weight: 0.2  // 20% have logic errors
  },
  
  // Syntax error - missing parenthesis
  {
    name: 'syntax_error',
    code: `n = int(input()  # Missing closing parenthesis
print('even' if n % 2 == 0 else 'odd')`,
    weight: 0.1  // 10% have syntax errors
  },
  
  // Runtime error - division by zero
  {
    name: 'runtime_error',
    code: `n = int(input())
result = n / 0  # This will cause runtime error
print('even' if n % 2 == 0 else 'odd')`,
    weight: 0.05  // 5% have runtime errors
  },
  
  // More complex but correct solution
  {
    name: 'complex_solution',
    code: `def check_even_odd(number):
    """Check if a number is even or odd"""
    if number % 2 == 0:
        return 'even'
    else:
        return 'odd'

n = int(input())
result = check_even_odd(n)
print(result)`,
    weight: 0.05  // 5% write more complex solutions
  }
];

// Problem IDs that students might submit to
const problemIds = ['1', '2', '3'];

// =============================================================================
// HELPER FUNCTIONS
// =============================================================================

/**
 * Generate a random username for testing
 * Simulates different students submitting code
 */
function generateRandomUsername() {
  const prefixes = ['student', 'user', 'learner', 'coder'];
  const suffix = Math.random().toString(36).substring(2, 8);
  return `${prefixes[Math.floor(Math.random() * prefixes.length)]}_${suffix}`;
}

/**
 * Select a code submission based on weighted probability
 * This simulates realistic distribution of submission types
 */
function selectCodeSubmission() {
  const random = Math.random();
  let cumulativeWeight = 0;
  
  for (const submission of codeSubmissions) {
    cumulativeWeight += submission.weight;
    if (random <= cumulativeWeight) {
      return submission;
    }
  }
  
  // Fallback to first submission
  return codeSubmissions[0];
}

/**
 * Create a test user account
 * Each virtual user gets their own account to simulate real usage
 */
function createTestUser(username) {
  const registerPayload = {
    username: username,
    password: 'testpass123'  // Simple password for testing
  };
  
  const registerResponse = http.post(
    `${BASE_URL}/api/v1/register`,  // Fixed: correct API path
    JSON.stringify(registerPayload),
    {
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: '10s',
    }
  );
  
  return check(registerResponse, {
    'user registration successful': (r) => r.status === 201,
  });
}

/**
 * Authenticate user and get session cookies
 * Returns the response with authentication cookies
 */
function authenticateUser(username) {
  const loginPayload = {
    username: username,
    password: 'testpass123'
  };
  
  const loginResponse = http.post(
    `${BASE_URL}/api/v1/login`,  // Fixed: correct API path
    JSON.stringify(loginPayload),
    {
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: '10s',
    }
  );
  
  const authSuccess = check(loginResponse, {
    'authentication successful': (r) => r.status === 200,
    'auth token received': (r) => r.cookies.access_token !== undefined,
  });
  
  if (!authSuccess) {
    authFailures.add(1);
    console.log(`Authentication failed for ${username}: ${loginResponse.status}, cookies: ${JSON.stringify(loginResponse.cookies)}`);
    return null;
  }
  
  return loginResponse;
}

// =============================================================================
// MAIN TEST FUNCTION
// =============================================================================

export default function () {
  // Each virtual user represents a student
  const username = generateRandomUsername();
  
  // Step 1: Create user account (simulates student registration)
  console.log(`Creating user: ${username}`);
  const userCreated = createTestUser(username);
  
  if (!userCreated) {
    console.log(`Failed to create user: ${username}`);
    return;
  }
  
  // Step 2: Authenticate user (simulates student login)
  const authResponse = authenticateUser(username);
  
  if (!authResponse) {
    console.log(`Failed to authenticate user: ${username}`);
    return;
  }
  
  // Extract cookies for subsequent requests - Fixed cookie handling
  const accessToken = authResponse.cookies.access_token;
  if (!accessToken) {
    console.log(`No access token received for user: ${username}`);
    return;
  }
  
  // Format cookie header properly - Fix: k6 cookies are arrays of objects
  let tokenValue;
  if (Array.isArray(accessToken) && accessToken.length > 0) {
    tokenValue = accessToken[0].value;
  } else if (typeof accessToken === 'string') {
    tokenValue = accessToken;
  } else if (accessToken.value) {
    tokenValue = accessToken.value;
  } else {
    console.log(`❌ Could not extract token value for user: ${username}`);
    return;
  }
  
  const cookieHeader = `access_token=${tokenValue}`;
  console.log(`✅ User ${username} authenticated successfully`);
  
  // Step 3: Submit code solutions (main performance test)
  // Simulate a student making multiple submissions (common in academic settings)
  const submissionCount = Math.floor(Math.random() * 3) + 1; // 1-3 submissions per user
  
  for (let i = 0; i < submissionCount; i++) {
    // Select a random problem and code submission
    const problemId = problemIds[Math.floor(Math.random() * problemIds.length)];
    const selectedSubmission = selectCodeSubmission();
    
    // Add small variations to simulate real student behavior
    const codeVariations = [
      selectedSubmission.code,
      selectedSubmission.code + '\n# Student comment',
      selectedSubmission.code.replace('n = int(input())', 'n = int(input())  # Read input'),
    ];
    
    const finalCode = codeVariations[Math.floor(Math.random() * codeVariations.length)];
    
    // Prepare submission payload
    const submissionPayload = {
      problem_id: problemId,
      code: finalCode
    };
    
    console.log(`User ${username} submitting ${selectedSubmission.name} to problem ${problemId}`);
    
    // Record submission start time
    const submissionStart = Date.now();
    
    // Make the submission request
    const submissionResponse = http.post(
      `${BASE_URL}/api/v1/judge`,  // Fixed: correct API path
      JSON.stringify(submissionPayload),
      {
        headers: {
          'Content-Type': 'application/json',
          'Cookie': cookieHeader,
        },
        timeout: '15s',
      }
    );
    
    // Record submission duration
    const submissionEnd = Date.now();
    submissionDuration.add(submissionEnd - submissionStart);
    
    // Check submission success
    const submissionSuccess = check(submissionResponse, {
      'submission accepted': (r) => r.status === 201,
      'submission_id returned': (r) => {
        try {
          const body = JSON.parse(r.body);
          return body.submission_id !== undefined;
        } catch (e) {
          return false;
        }
      },
      'response time acceptable': (r) => r.timings.duration < 5000,
    });
    
    // Update custom metrics
    submissionSuccessRate.add(submissionSuccess);
    
    if (submissionSuccess) {
      console.log(`✅ Submission successful for ${username}`);
    } else {
      console.log(`❌ Submission failed for ${username}: ${submissionResponse.status}`);
    }
    
    // Simulate student thinking time between submissions (1-3 seconds)
    sleep(Math.random() * 2 + 1);
  }
  
  // Step 4: Check submission results (optional - simulates student checking results)
  // This adds realistic load to the result checking endpoint
  if (Math.random() < 0.7) { // 70% of students check their results
    const listResponse = http.get(
      `${BASE_URL}/api/v1/judge/list`,  // Fixed: correct API path
      {
        headers: {
          'Cookie': cookieHeader,
        },
        timeout: '10s',
      }
    );
    
    check(listResponse, {
      'submission list retrieved': (r) => r.status === 200,
    });
  }
  
  // Simulate time between user sessions
  sleep(Math.random() * 2);
}

// =============================================================================
// TEST LIFECYCLE HOOKS
// =============================================================================

export function setup() {
  console.log('🚀 Starting OpenJudge Performance Test');
  console.log(`📊 Target: ${BASE_URL}`);
  console.log('📈 Simulating academic peak usage scenario');
  console.log('👥 Virtual users represent students submitting code');
  
  // Verify the service is accessible
  const healthCheck = http.get(`${BASE_URL}/`);
  if (healthCheck.status !== 200 && healthCheck.status !== 302) {  // Accept both 200 and 302
    throw new Error(`Service not accessible at ${BASE_URL}`);
  }
  
  console.log('✅ Service health check passed');
  return {};
}

export function teardown(data) {
  console.log('📊 Performance test completed');
  console.log('💡 Check the summary report above for detailed metrics');
  console.log('🎯 Key metrics to review:');
  console.log('   - http_req_duration: Response times');
  console.log('   - http_req_failed: Error rate');
  console.log('   - submission_success_rate: Submission success rate');
  console.log('   - submission_duration: Time to process submissions');
} 