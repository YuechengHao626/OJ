/**
 * k6 Performance Test Configuration Examples
 * 
 * This file shows different configuration options for various testing scenarios.
 * Copy and modify these configurations in your k6_performance_test.js file.
 */

// =============================================================================
// SCENARIO 1: Small Class Testing (10-15 students)
// =============================================================================
export const smallClassConfig = {
  stages: [
    { duration: '5s', target: 5 },    // Warm up
    { duration: '20s', target: 10 },  // Peak usage
    { duration: '20s', target: 10 },  // Sustained
    { duration: '5s', target: 0 },    // Cool down
  ],
  thresholds: {
    http_req_duration: ['p(95)<1500'],
    http_req_failed: ['rate<0.005'],
    submission_success_rate: ['rate>0.98'],
  },
};

// =============================================================================
// SCENARIO 2: Large Class Testing (50-100 students)
// =============================================================================
export const largeClassConfig = {
  stages: [
    { duration: '15s', target: 20 },  // Gradual ramp up
    { duration: '30s', target: 50 },  // Peak load
    { duration: '60s', target: 50 },  // Sustained peak
    { duration: '15s', target: 10 },  // Wind down
    { duration: '10s', target: 0 },   // Complete
  ],
  thresholds: {
    http_req_duration: ['p(95)<3000'],
    http_req_failed: ['rate<0.02'],
    submission_success_rate: ['rate>0.95'],
  },
};

// =============================================================================
// SCENARIO 3: Exam/Assignment Deadline Rush
// =============================================================================
export const deadlineRushConfig = {
  stages: [
    { duration: '10s', target: 30 },  // Sudden spike
    { duration: '45s', target: 60 },  // High sustained load
    { duration: '30s', target: 60 },  // Peak continues
    { duration: '20s', target: 20 },  // Gradual decrease
    { duration: '15s', target: 0 },   // End
  ],
  thresholds: {
    http_req_duration: ['p(95)<5000'],  // More lenient during peak
    http_req_failed: ['rate<0.05'],
    submission_success_rate: ['rate>0.90'],
  },
};

// =============================================================================
// SCENARIO 4: Stress Testing (Find Breaking Point)
// =============================================================================
export const stressTestConfig = {
  stages: [
    { duration: '10s', target: 10 },   // Start normal
    { duration: '20s', target: 50 },   // Increase load
    { duration: '30s', target: 100 },  // High load
    { duration: '30s', target: 150 },  // Very high load
    { duration: '20s', target: 200 },  // Extreme load
    { duration: '10s', target: 0 },    // Stop
  ],
  thresholds: {
    // More lenient thresholds to see where system breaks
    http_req_duration: ['p(95)<10000'],
    http_req_failed: ['rate<0.10'],
  },
};

// =============================================================================
// CUSTOM BASE URLS FOR DIFFERENT ENVIRONMENTS
// =============================================================================
export const environments = {
  production: 'http://coughoverflow-alb-1348614147.us-east-1.elb.amazonaws.com',
  staging: 'http://staging.openjudge.example.com',
  local: 'http://localhost:5000',
  development: 'http://dev.openjudge.example.com',
};

// =============================================================================
// DIFFERENT CODE SUBMISSION PATTERNS
// =============================================================================

// Beginner class - more errors, simpler code
export const beginnerSubmissions = [
  {
    name: 'simple_correct',
    code: `n = int(input())\nif n % 2 == 0:\n    print('even')\nelse:\n    print('odd')`,
    weight: 0.4
  },
  {
    name: 'syntax_error',
    code: `n = int(input()\nprint('even' if n % 2 == 0 else 'odd')`,
    weight: 0.3
  },
  {
    name: 'logic_error',
    code: `n = int(input())\nprint('odd' if n % 2 == 0 else 'even')`,
    weight: 0.3
  }
];

// Advanced class - more complex solutions, fewer errors
export const advancedSubmissions = [
  {
    name: 'optimal_solution',
    code: `print('even' if int(input()) % 2 == 0 else 'odd')`,
    weight: 0.7
  },
  {
    name: 'function_based',
    code: `def check_parity(n): return 'even' if n % 2 == 0 else 'odd'\nprint(check_parity(int(input())))`,
    weight: 0.2
  },
  {
    name: 'minor_error',
    code: `n = int(input())\nresult = 'even' if n % 2 == 0 else 'odd'\nprint(result)`,
    weight: 0.1
  }
];

// =============================================================================
// USAGE EXAMPLES
// =============================================================================

/*
To use these configurations, replace the options export in k6_performance_test.js:

// For small class testing:
export let options = smallClassConfig;

// For large class testing:
export let options = largeClassConfig;

// For deadline rush simulation:
export let options = deadlineRushConfig;

// For stress testing:
export let options = stressTestConfig;

// To change the target URL:
const BASE_URL = environments.local;  // or environments.staging, etc.

// To use different submission patterns:
const codeSubmissions = beginnerSubmissions;  // or advancedSubmissions
*/

// =============================================================================
// CUSTOM METRICS EXAMPLES
// =============================================================================

/*
Add these custom metrics to track specific academic scenarios:

import { Rate, Trend, Counter } from 'k6/metrics';

// Track different types of submissions
const correctSubmissions = new Rate('correct_submissions');
const errorSubmissions = new Rate('error_submissions');
const syntaxErrors = new Rate('syntax_errors');

// Track student behavior patterns
const multipleAttempts = new Counter('multiple_attempts');
const quickResubmissions = new Counter('quick_resubmissions');

// Track system performance under academic load
const peakHourPerformance = new Trend('peak_hour_response_time');
const concurrentUserHandling = new Trend('concurrent_user_capacity');
*/ 