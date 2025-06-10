#!/usr/bin/env python3
"""
Basic Test Suite - Cloud Version
Test Flask application, authentication system and core functionality
"""

import requests
import json
import time
import sys
import os

# Add current directory to path for importing auth_helper
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from auth_helper import AuthHelper, test_auth_system

# Cloud deployment URL
BASE_URL = "http://coughoverflow-alb-1348614147.us-east-1.elb.amazonaws.com"

def test_health_check():
    """Test health check endpoint"""
    print("🏥 Testing health check...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/health", timeout=10)
        if response.status_code == 200:
            print("   ✅ Flask app is running")
            return True
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Health check error: {str(e)}")
        return False

def test_public_endpoints():
    """Test if public API endpoints exist"""
    print("🔗 Testing public API endpoints...")
    
    endpoints = [
        ("/", "GET", [200, 302, 404]),  # Homepage may redirect to login page
        ("/api/", "GET", [200, 404, 405]),
        ("/api/v1/", "GET", [200, 404, 405]),
        ("/login", "GET", [200]),  # Login page
        ("/register", "GET", [200]),  # Register page
    ]
    
    results = []
    for endpoint, method, expected_codes in endpoints:
        try:
            if method == "GET":
                response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
            else:
                response = requests.request(method, f"{BASE_URL}{endpoint}", timeout=10)
            
            if response.status_code in expected_codes:
                print(f"   ✅ {method} {endpoint} - Status: {response.status_code}")
                results.append(True)
            else:
                print(f"   ❌ {method} {endpoint} - Expected: {expected_codes}, Got: {response.status_code}")
                results.append(False)
        except Exception as e:
            print(f"   ❌ {method} {endpoint} - Error: {str(e)}")
            results.append(False)
    
    return all(results)

def test_authentication_system():
    """Test authentication system"""
    print("🔐 Testing authentication system...")
    return test_auth_system()

def test_submit_judge_with_auth():
    """Test judge submission with authentication"""
    print("📊 Testing authenticated judge submission...")
    
    # Create and login test user
    auth = AuthHelper()
    user_result = auth.create_test_user()
    
    if not user_result["success"]:
        print(f"   ❌ Failed to create test user: {user_result.get('error')}")
        return None
    
    print(f"   ✅ Test user created and logged in: {user_result['username']}")
    
    # Submit judge request
    data = {
        "code": """
n = int(input())
print('even' if n % 2 == 0 else 'odd')
""",
        "problem_id": "1"
    }
    
    try:
        response = auth.make_authenticated_request(
            "POST", 
            "/api/v1/judge", 
            json=data, 
            timeout=15
        )
        
        if response.status_code in [200, 201]:
            result = response.json()
            submission_id = result.get("submission_id")
            print(f"   ✅ Judge submission successful")
            print(f"   📝 Submission ID: {submission_id}")
            print(f"   📝 Response: {json.dumps(result, indent=2)}")
            return submission_id, auth
        else:
            print(f"   ❌ Judge submission failed: {response.status_code}")
            print(f"   📝 Response: {response.text}")
            return None, auth
            
    except Exception as e:
        print(f"   ❌ Judge submission error: {str(e)}")
        return None, auth

def test_get_judge_result_with_auth(submission_id, auth):
    """Test getting judge result with authentication"""
    if not submission_id:
        print("   ⏭️ Skipping result check (no submission_id)")
        return False
    
    print(f"🔍 Testing authenticated judge result retrieval for ID: {submission_id}")
    
    max_wait = 30  # Cloud may need longer time
    start_time = time.time()
    
    while True:
        elapsed = time.time() - start_time
        if elapsed > max_wait:
            print(f"   ⏰ Timeout after {max_wait}s")
            return False
        
        try:
            response = auth.make_authenticated_request(
                "GET", 
                f"/api/v1/judge?submission_id={submission_id}", 
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                status = result.get("result", "unknown")
                
                print(f"   ⏳ [{int(elapsed)}s] Status: {status}")
                
                if status in ["ok", "fail", "error", "accepted", "wrong_answer", "runtime_error"]:
                    print("   ✅ Judge processing completed")
                    print(f"   📝 Final result: {json.dumps(result, indent=2)}")
                    return True
                elif status in ["pending", "processing", "running"]:
                    time.sleep(3)  # Longer interval for cloud
                    continue
                else:
                    print(f"   ❓ Unknown status: {status}")
                    return False
                    
            elif response.status_code == 404:
                print(f"   ❌ Submission not found (404)")
                return False
            else:
                print(f"   ❌ Get result failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ⚠️ [{int(elapsed)}s] Error: {str(e)}")
            time.sleep(3)

def test_user_isolation():
    """Test user isolation functionality"""
    print("👥 Testing user isolation...")
    
    # Create two different users
    auth1 = AuthHelper()
    auth2 = AuthHelper()
    
    user1_result = auth1.create_test_user()
    user2_result = auth2.create_test_user()
    
    if not user1_result["success"] or not user2_result["success"]:
        print("   ❌ Failed to create test users")
        return False
    
    print(f"   ✅ Created users: {user1_result['username']} and {user2_result['username']}")
    
    # User1 submits code
    data = {
        "code": "print('user1 submission')",
        "problem_id": "1"
    }
    
    response1 = auth1.make_authenticated_request("POST", "/api/v1/judge", json=data, timeout=10)
    if response1.status_code not in [200, 201]:
        print("   ❌ User1 submission failed")
        return False
    
    submission_id = response1.json().get("submission_id")
    print(f"   ✅ User1 submitted code, submission_id: {submission_id}")
    
    # User2 tries to access User1's submission
    response2 = auth2.make_authenticated_request("GET", f"/api/v1/judge?submission_id={submission_id}", timeout=5)
    
    if response2.status_code == 403:
        print("   ✅ User2 cannot access User1's submission (403 Forbidden)")
        return True
    elif response2.status_code == 404:
        print("   ✅ User2 cannot find User1's submission (404 Not Found)")
        return True
    else:
        print(f"   ❌ User2 can access User1's submission: {response2.status_code}")
        return False

def main():
    """Main test function"""
    print("🚀 Starting enhanced basic test suite with authentication...\n")
    
    test_results = {}
    
    # 1. Health check
    print("="*60)
    test_results["health"] = test_health_check()
    
    if not test_results["health"]:
        print("\n❌ Flask app is not running. Please check:")
        print("   💡 Check cloud service status")
        sys.exit(1)
    
    # 2. Public endpoints test
    print(f"\n{'='*60}")
    test_results["public_endpoints"] = test_public_endpoints()
    
    # 3. Authentication system test
    print(f"\n{'='*60}")
    test_results["authentication"] = test_authentication_system()
    
    # 4. Authenticated judge submission test
    print(f"\n{'='*60}")
    submission_result = test_submit_judge_with_auth()
    if submission_result:
        submission_id, auth = submission_result
        test_results["auth_submit"] = True
        
        # 5. Authenticated judge result retrieval test
        print(f"\n{'='*60}")
        print("⏳ Waiting 3 seconds for processing...")
        time.sleep(3)
        test_results["auth_result"] = test_get_judge_result_with_auth(submission_id, auth)
    else:
        test_results["auth_submit"] = False
        test_results["auth_result"] = False
    
    # 6. User isolation test
    print(f"\n{'='*60}")
    test_results["user_isolation"] = test_user_isolation()
    
    # Output test summary
    print(f"\n{'='*60}")
    print("📊 ENHANCED BASIC TEST SUMMARY:")
    print(f"{'='*60}")
    
    print(f"Health Check:                {'✅ PASS' if test_results['health'] else '❌ FAIL'}")
    print(f"Public Endpoints:            {'✅ PASS' if test_results['public_endpoints'] else '❌ FAIL'}")
    print(f"Authentication System:       {'✅ PASS' if test_results['authentication'] else '❌ FAIL'}")
    print(f"Authenticated Submission:    {'✅ PASS' if test_results['auth_submit'] else '❌ FAIL'}")
    print(f"Authenticated Result Query:  {'✅ PASS' if test_results['auth_result'] else '❌ FAIL'}")
    print(f"User Isolation:              {'✅ PASS' if test_results['user_isolation'] else '❌ FAIL'}")
    
    passed_tests = sum(test_results.values())
    total_tests = len(test_results)
    
    print(f"\nOverall: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("\n🎉 All enhanced basic tests passed!")
        print("💡 Your authentication and judge services are working correctly!")
    else:
        print("\n⚠️ Some tests failed. Check the logs above for details.")
        
        if not test_results["authentication"]:
            print("💡 Authentication system failed - check your auth implementation")
        if not test_results["auth_submit"]:
            print("💡 Authenticated submission failed - check your API implementation")
        if not test_results["user_isolation"]:
            print("💡 User isolation failed - check your access control")

if __name__ == "__main__":
    main() 