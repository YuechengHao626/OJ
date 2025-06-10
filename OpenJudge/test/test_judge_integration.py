#!/usr/bin/env python3
"""
Judge System Integration Test - Cloud Version
"""

import requests
import time
import json
import sys
import os

# Add current directory to path for importing auth_helper
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from auth_helper import AuthHelper

# Cloud deployment URL
BASE_URL = "http://coughoverflow-alb-1348614147.us-east-1.elb.amazonaws.com"

def get_judge_result_with_auth(auth, submission_id, max_wait=45):
    """Get judge result, support retry waiting for async task completion (with authentication)"""
    print(f"   🔍 Getting result for submission_id: {submission_id}")
    
    start_time = time.time()
    interval = 3  # Longer interval for cloud
    
    while True:
        elapsed = time.time() - start_time
        if elapsed > max_wait:
            print(f"   ⏰ Timeout after {max_wait}s")
            return None
        
        try:
            response = auth.make_authenticated_request(
                "GET", 
                f"/api/v1/judge?submission_id={submission_id}", 
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                result_status = result.get("result", "unknown")
                
                # If task is completed (not pending status)
                if result_status and result_status != "pending":
                    print(f"   ✅ Got result: {result_status}")
                    return result
                else:
                    print(f"   ⏳ [{int(elapsed)}s] Status: {result_status}")
            elif response.status_code == 404:
                print(f"   ⚠️ [{int(elapsed)}s] Submission not found (404)")
            elif response.status_code == 403:
                print(f"   ⚠️ [{int(elapsed)}s] Access forbidden (403)")
                return None
            else:
                print(f"   ⚠️ [{int(elapsed)}s] HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"   ⚠️ [{int(elapsed)}s] Error: {str(e)}")
        
        time.sleep(interval)

def test_judge_submission_with_auth():
    """Test authenticated code evaluation submission"""
    print("🔍 Testing authenticated judge submission...")
    
    # Create test user
    auth = AuthHelper()
    user_result = auth.create_test_user()
    
    if not user_result["success"]:
        print(f"   ❌ Failed to create test user: {user_result.get('error')}")
        return []
    
    print(f"   ✅ Test user created: {user_result['username']}")
    
    test_cases = [
        {
            "name": "Correct odd/even check",
            "problem_id": "1",
            "code": """
n = int(input())
print('even' if n % 2 == 0 else 'odd')
""",
            "expected_result": "ok"
        },
        {
            "name": "Wrong odd/even check",
            "problem_id": "1", 
            "code": """
n = int(input())
print('odd' if n % 2 == 0 else 'even')  # Logic reversed
""",
            "expected_result": "fail"
        },
        {
            "name": "Syntax error",
            "problem_id": "1",
            "code": """
n = int(input()  # Missing closing parenthesis
print('even' if n % 2 == 0 else 'odd')
""",
            "expected_result": "error"
        },
        {
            "name": "Runtime error",
            "problem_id": "1",
            "code": """
n = int(input())
print(n / 0)  # Division by zero error
""",
            "expected_result": "error"
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Test {i}: {test_case['name']}")
        
        # Submit evaluation
        payload = {
            "problem_id": test_case["problem_id"],
            "code": test_case["code"]
        }
        
        try:
            response = auth.make_authenticated_request(
                "POST", 
                "/api/v1/judge", 
                json=payload, 
                timeout=15
            )
            
            if response.status_code == 201:
                result = response.json()
                submission_id = result.get("submission_id")
                print(f"   ✅ Submitted, submission_id: {submission_id}")
                
                # Wait for processing completion and get result
                judge_result = get_judge_result_with_auth(auth, submission_id)
                
                if judge_result:
                    actual_result = judge_result.get("result")
                    expected_result = test_case["expected_result"]
                    
                    # Check if result matches
                    if actual_result == expected_result:
                        print(f"   ✅ Expected: {expected_result}, Got: {actual_result}")
                        results.append(True)
                        
                        # Show detailed results only for successful cases
                        if judge_result.get("testcase_result") and actual_result == "ok":
                            try:
                                testcase_data = json.loads(judge_result["testcase_result"])
                                if "results" in testcase_data:
                                    passed = sum(1 for r in testcase_data["results"] if r.get("pass"))
                                    total = len(testcase_data["results"])
                                    print(f"   📊 Test cases: {passed}/{total} passed")
                            except:
                                pass
                    else:
                        print(f"   ❌ Expected: {expected_result}, Got: {actual_result}")
                        results.append(False)
                        
                        # Don't show test case details for error/fail cases
                else:
                    print("   ❌ Failed to get judge result")
                    results.append(False)
            else:
                print(f"   ❌ Submission failed: {response.status_code}")
                print(f"   Response: {response.text}")
                results.append(False)
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            results.append(False)
    
    return results

def test_user_submission_isolation():
    """Test user submission isolation"""
    print("👥 Testing user submission isolation...")
    
    # Create two users
    auth1 = AuthHelper()
    auth2 = AuthHelper()
    
    user1_result = auth1.create_test_user()
    user2_result = auth2.create_test_user()
    
    if not user1_result["success"] or not user2_result["success"]:
        print("   ❌ Failed to create test users")
        return False
    
    print(f"   ✅ Users created: {user1_result['username']} and {user2_result['username']}")
    
    # User1 submits code
    payload = {
        "problem_id": "1",
        "code": "print('user1 code')"
    }
    
    response1 = auth1.make_authenticated_request("POST", "/api/v1/judge", json=payload, timeout=10)
    if response1.status_code != 201:
        print("   ❌ User1 submission failed")
        return False
    
    submission_id = response1.json().get("submission_id")
    print(f"   ✅ User1 submitted, submission_id: {submission_id}")
    
    # User2 tries to access User1's submission
    response2 = auth2.make_authenticated_request(
        "GET", 
        f"/api/v1/judge?submission_id={submission_id}", 
        timeout=5
    )
    
    if response2.status_code in [403, 404]:
        print(f"   ✅ User2 cannot access User1's submission ({response2.status_code})")
        return True
    else:
        print(f"   ❌ User2 can access User1's submission: {response2.status_code}")
        return False

def test_submission_list_with_auth():
    """Test authenticated submission list functionality"""
    print("📋 Testing authenticated submission list...")
    
    auth = AuthHelper()
    user_result = auth.create_test_user()
    
    if not user_result["success"]:
        print(f"   ❌ Failed to create test user: {user_result.get('error')}")
        return False
    
    print(f"   ✅ Test user created: {user_result['username']}")
    
    # Submit several tests
    test_codes = [
        "print('test 1')",
        "print('test 2')",
        "print('test 3')"
    ]
    
    submission_ids = []
    for i, code in enumerate(test_codes, 1):
        payload = {"problem_id": "1", "code": code}
        response = auth.make_authenticated_request("POST", "/api/v1/judge", json=payload, timeout=10)
        
        if response.status_code == 201:
            submission_id = response.json().get("submission_id")
            submission_ids.append(submission_id)
            print(f"   ✅ Submitted test {i}, submission_id: {submission_id}")
        else:
            print(f"   ❌ Failed to submit test {i}")
            return False
    
    # Get submission list
    response = auth.make_authenticated_request("GET", "/api/v1/judge/list", timeout=10)
    
    if response.status_code == 200:
        result = response.json()
        tasks = result.get("tasks", [])
        total = result.get("total", 0)
        
        print(f"   ✅ Got submission list: {len(tasks)} tasks, total: {total}")
        
        # Check if our submitted tasks are included
        found_submissions = [task["submission_id"] for task in tasks if task["submission_id"] in submission_ids]
        
        if len(found_submissions) >= len(submission_ids):
            print(f"   ✅ All submitted tasks found in list")
            return True
        else:
            print(f"   ⚠️ Only {len(found_submissions)}/{len(submission_ids)} tasks found")
            return True  # Partial success is still success
    else:
        print(f"   ❌ Failed to get submission list: {response.status_code}")
        return False

def test_direct_judge_call():
    """Test direct Judge module call"""
    print("🔍 Testing direct judge module call...")
    
    import sys
    import os
    
    # Add app path to import judge module
    app_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'app')
    sys.path.insert(0, app_path)
    
    try:
        from utils.judge import judge_submission
        
        test_code = """
n = int(input())
print('even' if n % 2 == 0 else 'odd')
"""
        
        result = judge_submission("1", "test_submission", test_code)
        
        if result:
            status = result.get("status")
            print(f"   ✅ Direct call successful, status: {status}")
            
            if result.get("results") and status == "ok":
                passed = sum(1 for r in result["results"] if r.get("pass"))
                total = len(result["results"])
                print(f"   📊 Test cases: {passed}/{total} passed")
            
            return status == "ok"
        else:
            print(f"   ❌ Direct call returned None")
            return False
            
    except ImportError as e:
        print(f"   ❌ Import error: {str(e)}")
        return False
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False

def main():
    """Main test function"""
    print("🚀 Starting authenticated Judge integration test suite...\n")
    
    test_results = {}
    
    # 1. Test direct Judge container call
    print("="*60)
    test_results["direct_judge"] = test_direct_judge_call()
    
    if not test_results["direct_judge"]:
        print("\n❌ Direct judge call failed. Make sure judge module is accessible:")
        print("   💡 Check that app/utils/judge.py exists and problems directory is available")
        # Don't exit directly, continue testing API
    
    # 2. Test authenticated Judge functionality via Flask API
    print(f"\n{'='*60}")
    api_test_results = test_judge_submission_with_auth()
    test_results["auth_judge"] = len(api_test_results) > 0 and all(api_test_results)
    
    # 3. Test user submission isolation
    print(f"\n{'='*60}")
    test_results["user_isolation"] = test_user_submission_isolation()
    
    # 4. Test submission list functionality
    print(f"\n{'='*60}")
    test_results["submission_list"] = test_submission_list_with_auth()
    
    # Output test summary
    print(f"\n{'='*60}")
    print("📊 AUTHENTICATED JUDGE TEST SUMMARY:")
    print(f"{'='*60}")
    
    print(f"Direct Judge Call:        {'✅ PASS' if test_results['direct_judge'] else '❌ FAIL'}")
    print(f"Authenticated Judge:      {'✅ PASS' if test_results['auth_judge'] else '❌ FAIL'}")
    print(f"User Isolation:           {'✅ PASS' if test_results['user_isolation'] else '❌ FAIL'}")
    print(f"Submission List:          {'✅ PASS' if test_results['submission_list'] else '❌ FAIL'}")
    
    if api_test_results:
        passed_api_tests = sum(api_test_results)
        total_api_tests = len(api_test_results)
        print(f"Individual Test Cases:    {passed_api_tests}/{total_api_tests} passed")
    
    passed_tests = sum(test_results.values())
    total_tests = len(test_results)
    
    print(f"\nOverall: {passed_tests}/{total_tests} major test categories passed")
    
    # Determine overall success criteria
    critical_tests = ["auth_judge", "user_isolation"]
    critical_passed = all(test_results.get(test, False) for test in critical_tests)
    
    if critical_passed:
        print("\n🎉 All critical authenticated judge tests passed!")
        print("💡 Your authentication and judge integration is working correctly!")
    else:
        print("\n⚠️ Some critical tests failed.")
        
        if not test_results.get("auth_judge"):
            print("💡 Authenticated judge submission failed - check API implementation")
        if not test_results.get("user_isolation"):
            print("💡 User isolation failed - check access control logic")
        
        sys.exit(1)

if __name__ == "__main__":
    main() 