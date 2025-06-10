#!/usr/bin/env python3
"""
Authentication Helper Module - Cloud Version
Provides user registration, login and other functionality for testing
"""

import requests
import json
import uuid
import random
import string
import time
from datetime import datetime

# Cloud deployment URL
BASE_URL = "http://coughoverflow-alb-1348614147.us-east-1.elb.amazonaws.com"

class AuthHelper:
    def __init__(self):
        self.session = requests.Session()
        self.current_user = None
        self.last_username = None
    
    def generate_username(self, prefix="testuser"):
        """Generate a valid username (3-20 characters)"""
        # Generate 6-character random string
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        username = f"{prefix}_{random_suffix}"
        
        # Ensure username is within 3-20 character range
        if len(username) > 20:
            username = username[:20]
        elif len(username) < 3:
            username = f"usr_{random_suffix}"
        
        return username
    
    def generate_password(self, length=8):
        """Generate a valid password (at least 6 characters)"""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    
    def register_user(self, username=None, password=None):
        """Register user"""
        if not username:
            username = self.generate_username()
        if not password:
            password = self.generate_password()
        
        data = {
            "username": username,
            "password": password
        }
        
        try:
            response = self.session.post(f"{BASE_URL}/api/v1/register", json=data, timeout=10)
            if response.status_code == 201:
                result = response.json()
                return {
                    "success": True,
                    "username": username,
                    "password": password,
                    "response": result
                }
            else:
                return {
                    "success": False,
                    "error": f"{response.status_code} - {response.text}",
                    "username": username
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "username": username
            }
    
    def login_user(self, username, password):
        """User login"""
        data = {
            "username": username,
            "password": password
        }
        
        try:
            response = self.session.post(f"{BASE_URL}/api/v1/login", json=data, timeout=10)
            if response.status_code == 200:
                result = response.json()
                self.current_user = {
                    "username": username,
                    "password": password
                }
                return {
                    "success": True,
                    "response": result
                }
            else:
                return {
                    "success": False,
                    "error": f"{response.status_code} - {response.text}"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def logout_user(self):
        """User logout"""
        try:
            response = self.session.post(f"{BASE_URL}/api/v1/logout", timeout=5)
            self.current_user = None
            return {
                "success": True,
                "status_code": response.status_code
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_current_user(self):
        """Get current user information"""
        try:
            response = self.session.get(f"{BASE_URL}/api/v1/me", timeout=5)
            if response.status_code == 200:
                return {
                    "success": True,
                    "user": response.json()
                }
            else:
                return {
                    "success": False,
                    "error": f"{response.status_code} - {response.text}"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def make_authenticated_request(self, method, endpoint, **kwargs):
        """Send authenticated request"""
        url = f"{BASE_URL}{endpoint}"
        
        if method.upper() == "GET":
            return self.session.get(url, **kwargs)
        elif method.upper() == "POST":
            return self.session.post(url, **kwargs)
        elif method.upper() == "PUT":
            return self.session.put(url, **kwargs)
        elif method.upper() == "DELETE":
            return self.session.delete(url, **kwargs)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
    
    def create_test_user(self, prefix="testuser"):
        """Create and login test user"""
        # Register user
        register_result = self.register_user(username=self.generate_username(prefix))
        if not register_result["success"]:
            return register_result
        
        # Login user
        login_result = self.login_user(
            register_result["username"], 
            register_result["password"]
        )
        
        if login_result["success"]:
            self.last_username = register_result["username"]
            return {
                "success": True,
                "username": register_result["username"],
                "password": register_result["password"]
            }
        else:
            return {
                "success": False,
                "error": f"Login failed: {login_result['error']}"
            }

def test_auth_system():
    """Test authentication system"""
    print("🧪 Testing Authentication System...")
    
    auth = AuthHelper()
    
    # 1. Test registration
    print("\n1. Testing user registration...")
    register_result = auth.register_user()
    if register_result["success"]:
        print(f"   ✅ User registered: {register_result['username']}")
        username = register_result["username"]
        password = register_result["password"]
    else:
        print(f"   ❌ Registration failed: {register_result['error']}")
        return False
    
    # 2. Test login
    print("\n2. Testing user login...")
    login_result = auth.login_user(username, password)
    if login_result["success"]:
        print("   ✅ User logged in successfully")
    else:
        print(f"   ❌ Login failed: {login_result['error']}")
        return False
    
    # 3. Test get user information
    print("\n3. Testing get current user...")
    user_result = auth.get_current_user()
    if user_result["success"]:
        print(f"   ✅ Current user: {user_result['user']}")
    else:
        print(f"   ❌ Get user failed: {user_result['error']}")
        return False
    
    # 4. Test authenticated request
    print("\n4. Testing authenticated request...")
    data = {"problem_id": "1", "code": "print('hello auth')"}
    response = auth.make_authenticated_request("POST", "/api/v1/judge", json=data)
    if response.status_code == 201:
        print("   ✅ Authenticated request successful")
    else:
        print(f"   ❌ Authenticated request failed: {response.status_code}")
        return False
    
    # 5. Test logout
    print("\n5. Testing user logout...")
    logout_result = auth.logout_user()
    if logout_result["success"]:
        print("   ✅ User logged out successfully")
    else:
        print(f"   ❌ Logout failed: {logout_result['error']}")
        return False
    
    print("\n🎉 All authentication tests passed!")
    return True

if __name__ == "__main__":
    test_auth_system() 