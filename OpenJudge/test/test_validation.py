"""
Parameter Validation Test Script
Tests API endpoint parameter validation functionality with JWT authentication support
"""

import requests
import json
import uuid
import sys
import os

# Add current directory to path for importing auth_helper
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from auth_helper import AuthHelper

BASE_URL = "http://coughoverflow-alb-1348614147.us-east-1.elb.amazonaws.com"

class ValidationTest:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.test_results = {}
        self.auth = None

    def setup_auth(self):
        """Setup authenticated user"""
        if not self.auth:
            self.auth = AuthHelper()
            user_result = self.auth.create_test_user()
            if not user_result["success"]:
                raise Exception(f"Failed to create test user: {user_result.get('error')}")
            print(f"   ✅ Test user created: {user_result['username']}")

    def assert_status_code(self, response, expected_status, test_name):
        """Assert status code"""
        if response.status_code == expected_status:
            print(f"   ✅ {test_name} - Status: {response.status_code}")
            self.passed += 1
            self.test_results[test_name] = True
            return True
        else:
            print(f"   ❌ {test_name} - Expected: {expected_status}, Got: {response.status_code}")
            print(f"      Response: {response.text}")
            self.failed += 1
            self.test_results[test_name] = False
            return False

    def assert_error_message(self, response, expected_error, test_name):
        """Assert error message"""
        try:
            data = response.json()
            if "error" in data and expected_error in data["error"]:
                print(f"   ✅ {test_name} - Correct error message")
                return True
            else:
                print(f"   ❌ {test_name} - Unexpected error message: {data}")
                return False
        except:
            print(f"   ❌ {test_name} - Invalid JSON response: {response.text}")
            return False

def test_auth_validation(tester):
    """Test authentication-related validation"""
    print("🔐 Testing Authentication Validation...")
    
    # Test registration validation
    register_url = f"{BASE_URL}/api/v1/register"
    
    register_test_cases = [
        # Missing fields
        ({}, "Missing username and password"),
        ({"username": "test"}, "Missing password"),
        ({"password": "test123"}, "Missing username"),
        
        # Invalid username
        ({"username": "ab", "password": "test123"}, "Username too short"),
        ({"username": "a" * 21, "password": "test123"}, "Username too long"),
        ({"username": "test@user", "password": "test123"}, "Invalid username characters"),
        ({"username": "test user", "password": "test123"}, "Username with space"),
        
        # Invalid password
        ({"username": "testuser", "password": "123"}, "Password too short"),
        ({"username": "testuser", "password": "a" * 101}, "Password too long"),
        
        # Invalid data types
        ({"username": 123, "password": "test123"}, "Username as number"),
        ({"username": "testuser", "password": 123}, "Password as number"),
    ]
    
    for data, test_name in register_test_cases:
        try:
            response = requests.post(register_url, json=data, timeout=5)
            tester.assert_status_code(response, 400, f"Register - {test_name}")
        except Exception as e:
            print(f"   ❌ Register - {test_name} failed: {str(e)}")
            tester.test_results[f"Register - {test_name}"] = False
            tester.failed += 1
    
    # Test login validation
    login_url = f"{BASE_URL}/api/v1/login"
    
    login_test_cases = [
        ({}, "Missing credentials"),
        ({"username": "test"}, "Missing password"),
        ({"password": "test123"}, "Missing username"),
        ({"username": "", "password": "test123"}, "Empty username"),
        ({"username": "testuser", "password": ""}, "Empty password"),
    ]
    
    for data, test_name in login_test_cases:
        try:
            response = requests.post(login_url, json=data, timeout=5)
            tester.assert_status_code(response, 400, f"Login - {test_name}")
        except Exception as e:
            print(f"   ❌ Login - {test_name} failed: {str(e)}")
            tester.test_results[f"Login - {test_name}"] = False
            tester.failed += 1

def test_valid_requests(tester):
    """Test valid requests"""
    print("✅ Testing Valid Requests...")
    
    # Ensure authenticated user
    tester.setup_auth()
    
    # Test valid authenticated judge endpoint request
    valid_data = {
        "code": "print('hello world')",
        "problem_id": "1"
    }
    
    try:
        response = tester.auth.make_authenticated_request("POST", "/api/v1/judge", json=valid_data, timeout=10)
        tester.assert_status_code(response, 201, "Valid authenticated judge request")
        
        if response.status_code == 201:
            result = response.json()
            if "submission_id" in result:
                print("   ✅ Response contains submission_id")
            else:
                print("   ❌ Response missing submission_id")
                
    except Exception as e:
        print(f"   ❌ Valid authenticated request failed: {str(e)}")
        tester.test_results["Valid authenticated judge request"] = False
        tester.failed += 1

def test_missing_fields(tester):
    """Test missing required fields"""
    print("\n🚫 Testing Missing Required Fields...")
    
    # Ensure authenticated user
    tester.setup_auth()
    
    # Test authenticated judge endpoint
    test_cases = [
        ({}, "Missing all fields"),
        ({"code": "print('test')"}, "Missing problem_id"),
        ({"problem_id": "1"}, "Missing code"),
    ]
    
    for data, test_name in test_cases:
        try:
            response = tester.auth.make_authenticated_request("POST", "/api/v1/judge", json=data, timeout=5)
            if tester.assert_status_code(response, 400, f"Auth Judge - {test_name}"):
                tester.assert_error_message(response, "required", f"Auth Judge - {test_name} (error message)")
        except Exception as e:
            print(f"   ❌ Auth Judge - {test_name} failed: {str(e)}")
            tester.test_results[f"Auth Judge - {test_name}"] = False
            tester.failed += 1

def test_invalid_data_types(tester):
    """Test invalid data types"""
    print("\n🔢 Testing Invalid Data Types...")
    
    # Ensure authenticated user
    tester.setup_auth()
    
    test_cases = [
        ({"code": 123, "problem_id": "1"}, "Code as number"),
        ({"code": None, "problem_id": "1"}, "Code as null"),
        ({"code": [], "problem_id": "1"}, "Code as array"),
        ({"code": "print('test')", "problem_id": None}, "Problem_id as null"),
        ({"code": "print('test')", "problem_id": []}, "Problem_id as array"),
    ]
    
    for data, test_name in test_cases:
        try:
            response = tester.auth.make_authenticated_request("POST", "/api/v1/judge", json=data, timeout=5)
            tester.assert_status_code(response, 400, f"Auth Judge - {test_name}")
        except Exception as e:
            print(f"   ❌ Auth Judge - {test_name} failed: {str(e)}")
            tester.test_results[f"Auth Judge - {test_name}"] = False
            tester.failed += 1

def test_invalid_values(tester):
    """Test invalid values"""
    print("\n❌ Testing Invalid Values...")
    
    # Ensure authenticated user
    tester.setup_auth()
    
    test_cases = [
        ({"code": "", "problem_id": "1"}, "Empty code"),
        ({"code": "   ", "problem_id": "1"}, "Whitespace only code"),
        ({"code": "print('test')", "problem_id": "0"}, "Problem_id out of range (0)"),
        ({"code": "print('test')", "problem_id": "11"}, "Problem_id out of range (11)"),
        ({"code": "print('test')", "problem_id": "-1"}, "Negative problem_id"),
        ({"code": "print('test')", "problem_id": "abc"}, "Non-numeric problem_id"),
    ]
    
    for data, test_name in test_cases:
        try:
            response = tester.auth.make_authenticated_request("POST", "/api/v1/judge", json=data, timeout=5)
            tester.assert_status_code(response, 400, f"Auth Judge - {test_name}")
        except Exception as e:
            print(f"   ❌ Auth Judge - {test_name} failed: {str(e)}")
            tester.test_results[f"Auth Judge - {test_name}"] = False
            tester.failed += 1

def test_code_length_limits(tester):
    """Test code length limits"""
    print("\n📏 Testing Code Length Limits...")
    
    # Ensure authenticated user
    tester.setup_auth()
    
    # Test overly long code (>50KB)
    long_code = "print('hello')\n" * 5000  # About 75KB
    test_cases = [
        ({"code": long_code, "problem_id": "1"}, "Code too long (>50KB)"),
        ({"code": "a" * 51201, "problem_id": "1"}, "Code exactly over 50KB"),
    ]
    
    for data, test_name in test_cases:
        try:
            response = tester.auth.make_authenticated_request("POST", "/api/v1/judge", json=data, timeout=5)
            tester.assert_status_code(response, 400, f"Auth Judge - {test_name}")
        except Exception as e:
            print(f"   ❌ Auth Judge - {test_name} failed: {str(e)}")
            tester.test_results[f"Auth Judge - {test_name}"] = False
            tester.failed += 1

def test_dangerous_code_patterns(tester):
    """Test dangerous code pattern detection"""
    print("\n⚠️ Testing Dangerous Code Pattern Detection...")
    
    # Ensure authenticated user
    tester.setup_auth()
    
    dangerous_codes = [
        ("import os; os.system('rm -rf /')", "OS system call"),
        ("exec('malicious code')", "Exec function"),
        ("eval('1+1')", "Eval function"),
        ("import subprocess; subprocess.run(['ls'])", "Subprocess import"),
        ("open('/etc/passwd', 'r')", "File system access"),
        ("__import__('os')", "Dynamic import"),
    ]
    
    for code, test_name in dangerous_codes:
        data = {"code": code, "problem_id": "1"}
        try:
            response = tester.auth.make_authenticated_request("POST", "/api/v1/judge", json=data, timeout=5)
            tester.assert_status_code(response, 400, f"Auth Judge - Dangerous pattern: {test_name}")
        except Exception as e:
            print(f"   ❌ Auth Judge - {test_name} failed: {str(e)}")
            tester.test_results[f"Auth Judge - {test_name}"] = False
            tester.failed += 1

def test_unauthorized_requests(tester):
    """Test unauthorized requests"""
    print("\n🚫 Testing Unauthorized Requests...")
    
    # Test protected endpoints without authentication
    protected_endpoints = [
        ("POST", "/api/v1/judge", {"problem_id": "1", "code": "print('test')"}),
        ("GET", "/api/v1/judge?submission_id=test", None),
        ("GET", "/api/v1/judge/list", None),
        ("GET", "/api/v1/me", None),
    ]
    
    for method, endpoint, data in protected_endpoints:
        try:
            if method == "GET":
                response = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
            elif method == "POST":
                response = requests.post(f"{BASE_URL}{endpoint}", json=data, timeout=5)
            
            tester.assert_status_code(response, 401, f"Unauthorized {method} {endpoint}")
        except Exception as e:
            print(f"   ❌ Unauthorized {method} {endpoint} failed: {str(e)}")
            tester.test_results[f"Unauthorized {method} {endpoint}"] = False
            tester.failed += 1

def test_malformed_json(tester):
    """Test malformed JSON"""
    print("\n🔧 Testing Malformed JSON...")
    
    # Ensure authenticated user
    tester.setup_auth()
    
    url = f"{BASE_URL}/api/v1/judge"
    cookies = tester.auth.session.cookies
    
    test_cases = [
        ('{"code": "print(test)", "problem_id":', "Incomplete JSON"),
        ('{"code": "print(\'test\')", "problem_id": 1,}', "Trailing comma"),
        ('not json at all', "Not JSON"),
        ('', "Empty body"),
    ]
    
    for data, test_name in test_cases:
        try:
            response = requests.post(
                url, 
                data=data, 
                headers={"Content-Type": "application/json"}, 
                cookies=cookies,
                timeout=5
            )
            
            if response.status_code == 400:
                print(f"   ✅ Auth Judge - {test_name} - Status: 400")
                tester.passed += 1
                tester.test_results[f"Auth Judge - {test_name}"] = True
            else:
                print(f"   ❌ Auth Judge - {test_name} - Expected 400, Got: {response.status_code}")
                tester.failed += 1
                tester.test_results[f"Auth Judge - {test_name}"] = False
        except Exception as e:
            print(f"   ❌ Auth Judge - {test_name} failed: {str(e)}")
            tester.test_results[f"Auth Judge - {test_name}"] = False
            tester.failed += 1

def main():
    """Main test function"""
    print("🚀 Starting enhanced validation test suite with authentication...\n")
    
    tester = ValidationTest()
    
    # 1. Authentication validation tests
    print("="*60)
    test_auth_validation(tester)
    
    # 2. Unauthorized request tests
    print(f"\n{'='*60}")
    test_unauthorized_requests(tester)
    
    # 3. Valid request tests
    print(f"\n{'='*60}")
    test_valid_requests(tester)
    
    # 4. Missing field tests
    print(f"\n{'='*60}")
    test_missing_fields(tester)
    
    # 5. Invalid data type tests
    print(f"\n{'='*60}")
    test_invalid_data_types(tester)
    
    # 6. Invalid value tests
    print(f"\n{'='*60}")
    test_invalid_values(tester)
    
    # 7. Code length limit tests
    print(f"\n{'='*60}")
    test_code_length_limits(tester)
    
    # 8. Dangerous code pattern tests
    print(f"\n{'='*60}")
    test_dangerous_code_patterns(tester)
    
    # 9. Malformed JSON tests
    print(f"\n{'='*60}")
    test_malformed_json(tester)
    
    # Output test summary
    print(f"\n{'='*60}")
    print("📊 ENHANCED VALIDATION TEST SUMMARY:")
    print(f"{'='*60}")
    
    print(f"Total Tests:    {tester.passed + tester.failed}")
    print(f"Passed:         {tester.passed} ✅")
    print(f"Failed:         {tester.failed} ❌")
    print(f"Success Rate:   {(tester.passed / (tester.passed + tester.failed) * 100):.1f}%")
    
    if tester.failed == 0:
        print("\n🎉 All validation tests passed!")
        print("💡 Your API validation and authentication is working correctly!")
    else:
        print(f"\n⚠️ {tester.failed} validation tests failed.")
        print("💡 Check the failed tests above for details.")
        
        # Show failed test categories
        failed_tests = [name for name, result in tester.test_results.items() if not result]
        if failed_tests:
            print(f"\n❌ Failed tests:")
            for test in failed_tests[:10]:  # Only show first 10
                print(f"   - {test}")
            if len(failed_tests) > 10:
                print(f"   ... and {len(failed_tests) - 10} more")

if __name__ == "__main__":
    main() 