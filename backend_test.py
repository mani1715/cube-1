#!/usr/bin/env python3
"""
Backend Testing Script for Phase 12 User Authentication and Phase 9 Endpoints
Tests user signup, login, token refresh, profile retrieval, dashboard overview,
production health checks, SEO endpoints, GDPR compliance, and security headers
"""

import requests
import json
import sys
from datetime import datetime
import xml.etree.ElementTree as ET

# Backend URL from frontend .env
BACKEND_URL = "https://cubecraft-438.preview.emergentagent.com"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_success(message):
    print(f"{Colors.GREEN}✅ {message}{Colors.ENDC}")

def print_error(message):
    print(f"{Colors.RED}❌ {message}{Colors.ENDC}")

def print_warning(message):
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.ENDC}")

def print_info(message):
    print(f"{Colors.BLUE}ℹ️  {message}{Colors.ENDC}")

def print_header(message):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{message}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.ENDC}")

def check_security_headers(response, endpoint_name):
    """Check if security headers are present in response"""
    print_info(f"Checking security headers for {endpoint_name}")
    
    expected_headers = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'Referrer-Policy': 'strict-origin-when-cross-origin',
        'Permissions-Policy': 'geolocation=(), microphone=(), camera=()',
        'Content-Security-Policy': None  # Just check if exists
    }
    
    headers_ok = True
    for header, expected_value in expected_headers.items():
        if header in response.headers:
            actual_value = response.headers[header]
            if expected_value and actual_value != expected_value:
                print_warning(f"  {header}: Expected '{expected_value}', got '{actual_value}'")
            else:
                print_success(f"  {header}: ✓")
        else:
            print_error(f"  {header}: Missing")
            headers_ok = False
    
    return headers_ok

def test_production_health_endpoints():
    """Test Phase 9.1 - Production Health Check Endpoints"""
    print_header("PHASE 9.1 - PRODUCTION HEALTH CHECK ENDPOINTS")
    
    endpoints = [
        ("/api/phase9/production/health", "Detailed Health Check"),
        ("/api/phase9/production/health/ready", "Readiness Probe"),
        ("/api/phase9/production/health/live", "Liveness Probe"),
        ("/api/phase9/production/environment", "Environment Info"),
        ("/api/phase9/production/metrics", "Application Metrics")
    ]
    
    results = {}
    
    for endpoint, description in endpoints:
        print_info(f"Testing {description}: {endpoint}")
        try:
            response = requests.get(f"{BACKEND_URL}{endpoint}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print_success(f"{description} - Status: 200")
                
                # Check specific response content
                if endpoint == "/api/phase9/production/health":
                    if data.get('status') in ['healthy', 'degraded']:
                        print_success(f"  Health status: {data.get('status')}")
                    if 'components' in data and 'database' in data['components']:
                        db_status = data['components']['database']['status']
                        print_success(f"  Database status: {db_status}")
                    if 'service' in data:
                        print_success(f"  Service: {data['service']}")
                
                elif endpoint == "/api/phase9/production/health/ready":
                    if data.get('ready') is True:
                        print_success(f"  Service ready: {data.get('ready')}")
                
                elif endpoint == "/api/phase9/production/health/live":
                    if data.get('alive') is True:
                        print_success(f"  Service alive: {data.get('alive')}")
                
                elif endpoint == "/api/phase9/production/environment":
                    if 'environment' in data:
                        print_success(f"  Environment: {data.get('environment')}")
                    if 'features' in data:
                        print_success(f"  Features configured: {len(data['features'])}")
                
                elif endpoint == "/api/phase9/production/metrics":
                    if 'collections' in data:
                        print_success(f"  Collections monitored: {len(data['collections'])}")
                        for collection, count in data['collections'].items():
                            print_info(f"    {collection}: {count} records")
                
                # Check security headers
                check_security_headers(response, description)
                results[endpoint] = True
                
            else:
                print_error(f"{description} - Status: {response.status_code}")
                print_error(f"  Response: {response.text}")
                results[endpoint] = False
                
        except Exception as e:
            print_error(f"{description} - Error: {str(e)}")
            results[endpoint] = False
    
    return results

def test_seo_endpoints():
    """Test Phase 9.2 - SEO Endpoints"""
    print_header("PHASE 9.2 - SEO ENDPOINTS")
    
    results = {}
    
    # Test sitemap.xml
    print_info("Testing Sitemap Generation: /api/phase9/seo/sitemap.xml")
    try:
        response = requests.get(f"{BACKEND_URL}/api/phase9/seo/sitemap.xml", timeout=10)
        
        if response.status_code == 200:
            print_success("Sitemap - Status: 200")
            
            # Check content type
            content_type = response.headers.get('content-type', '')
            if 'xml' in content_type.lower():
                print_success(f"  Content-Type: {content_type}")
            else:
                print_warning(f"  Content-Type: {content_type} (expected XML)")
            
            # Validate XML structure
            try:
                root = ET.fromstring(response.text)
                if root.tag.endswith('urlset'):
                    print_success("  Valid XML sitemap structure")
                    
                    # Count URLs
                    urls = root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}url')
                    print_success(f"  URLs in sitemap: {len(urls)}")
                    
                    # Check for required elements
                    for url in urls[:3]:  # Check first 3 URLs
                        loc = url.find('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
                        if loc is not None:
                            print_info(f"    URL: {loc.text}")
                else:
                    print_error("  Invalid sitemap XML structure")
            except ET.ParseError as e:
                print_error(f"  XML parsing error: {str(e)}")
            
            # Check security headers
            check_security_headers(response, "Sitemap")
            results['/api/phase9/seo/sitemap.xml'] = True
            
        else:
            print_error(f"Sitemap - Status: {response.status_code}")
            results['/api/phase9/seo/sitemap.xml'] = False
            
    except Exception as e:
        print_error(f"Sitemap - Error: {str(e)}")
        results['/api/phase9/seo/sitemap.xml'] = False
    
    # Test robots.txt
    print_info("Testing Robots.txt: /api/phase9/seo/robots.txt")
    try:
        response = requests.get(f"{BACKEND_URL}/api/phase9/seo/robots.txt", timeout=10)
        
        if response.status_code == 200:
            print_success("Robots.txt - Status: 200")
            
            # Check content type
            content_type = response.headers.get('content-type', '')
            if 'text/plain' in content_type:
                print_success(f"  Content-Type: {content_type}")
            else:
                print_warning(f"  Content-Type: {content_type} (expected text/plain)")
            
            # Check content
            content = response.text
            if 'User-agent:' in content:
                print_success("  Contains User-agent directive")
            if 'Disallow:' in content:
                print_success("  Contains Disallow directive")
            if 'Sitemap:' in content:
                print_success("  Contains Sitemap reference")
            
            print_info(f"  Content preview: {content[:100]}...")
            
            # Check security headers
            check_security_headers(response, "Robots.txt")
            results['/api/phase9/seo/robots.txt'] = True
            
        else:
            print_error(f"Robots.txt - Status: {response.status_code}")
            results['/api/phase9/seo/robots.txt'] = False
            
    except Exception as e:
        print_error(f"Robots.txt - Error: {str(e)}")
        results['/api/phase9/seo/robots.txt'] = False
    
    return results

def test_gdpr_compliance_endpoints():
    """Test Phase 9.5 - GDPR Compliance Endpoints"""
    print_header("PHASE 9.5 - GDPR COMPLIANCE ENDPOINTS")
    
    results = {}
    
    # Test cookie settings
    print_info("Testing Cookie Settings: /api/phase9/compliance/cookie-settings")
    try:
        response = requests.get(f"{BACKEND_URL}/api/phase9/compliance/cookie-settings", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print_success("Cookie Settings - Status: 200")
            
            if 'cookie_policy' in data:
                policy = data['cookie_policy']
                print_success(f"  Cookie categories: {len(policy)}")
                
                # Check required categories
                required_categories = ['essential', 'analytics', 'preferences']
                for category in required_categories:
                    if category in policy:
                        print_success(f"    {category}: ✓")
                    else:
                        print_error(f"    {category}: Missing")
            
            check_security_headers(response, "Cookie Settings")
            results['/api/phase9/compliance/cookie-settings'] = True
            
        else:
            print_error(f"Cookie Settings - Status: {response.status_code}")
            results['/api/phase9/compliance/cookie-settings'] = False
            
    except Exception as e:
        print_error(f"Cookie Settings - Error: {str(e)}")
        results['/api/phase9/compliance/cookie-settings'] = False
    
    # Test cookie consent
    print_info("Testing Cookie Consent: /api/phase9/compliance/cookie-consent")
    try:
        consent_data = {
            "essential": True,
            "analytics": True,
            "preferences": False
        }
        
        response = requests.post(
            f"{BACKEND_URL}/api/phase9/compliance/cookie-consent",
            json=consent_data,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("Cookie Consent - Status: 200")
            
            if data.get('success') is True:
                print_success("  Consent saved successfully")
            if 'consent' in data:
                print_success(f"  Consent preferences: {data['consent']}")
            
            check_security_headers(response, "Cookie Consent")
            results['/api/phase9/compliance/cookie-consent'] = True
            
        else:
            print_error(f"Cookie Consent - Status: {response.status_code}")
            results['/api/phase9/compliance/cookie-consent'] = False
            
    except Exception as e:
        print_error(f"Cookie Consent - Error: {str(e)}")
        results['/api/phase9/compliance/cookie-consent'] = False
    
    # Test data export
    print_info("Testing Data Export: /api/phase9/compliance/data-export")
    try:
        export_data = {
            "email": "test@example.com",
            "data_types": ["all"]
        }
        
        response = requests.post(
            f"{BACKEND_URL}/api/phase9/compliance/data-export",
            json=export_data,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("Data Export - Status: 200")
            
            if data.get('success') is True:
                print_success("  Export generated successfully")
            if 'total_records' in data:
                print_success(f"  Total records: {data['total_records']}")
            if 'export_data' in data:
                print_success("  Export data structure present")
            
            check_security_headers(response, "Data Export")
            results['/api/phase9/compliance/data-export'] = True
            
        else:
            print_error(f"Data Export - Status: {response.status_code}")
            print_error(f"  Response: {response.text}")
            results['/api/phase9/compliance/data-export'] = False
            
    except Exception as e:
        print_error(f"Data Export - Error: {str(e)}")
        results['/api/phase9/compliance/data-export'] = False
    
    # Test account deletion
    print_info("Testing Account Deletion: /api/phase9/compliance/account-deletion")
    try:
        deletion_data = {
            "email": "test@example.com",
            "confirmation": True,
            "reason": "Testing GDPR compliance"
        }
        
        response = requests.post(
            f"{BACKEND_URL}/api/phase9/compliance/account-deletion",
            json=deletion_data,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("Account Deletion - Status: 200")
            
            if data.get('success') is True:
                print_success("  Deletion request processed")
            if 'deleted_records' in data:
                print_success(f"  Collections processed: {len(data['deleted_records'])}")
            if 'total_deleted' in data:
                print_success(f"  Total records deleted: {data['total_deleted']}")
            
            check_security_headers(response, "Account Deletion")
            results['/api/phase9/compliance/account-deletion'] = True
            
        else:
            print_error(f"Account Deletion - Status: {response.status_code}")
            print_error(f"  Response: {response.text}")
            results['/api/phase9/compliance/account-deletion'] = False
            
    except Exception as e:
        print_error(f"Account Deletion - Error: {str(e)}")
        results['/api/phase9/compliance/account-deletion'] = False
    
    return results

def test_security_headers_comprehensive():
    """Test security headers on a sample of endpoints"""
    print_header("PHASE 9.7 - SECURITY HEADERS COMPREHENSIVE TEST")
    
    # Test security headers on various endpoints
    test_endpoints = [
        "/api/health",
        "/api/phase9/production/health",
        "/api/phase9/seo/sitemap.xml",
        "/api/phase9/compliance/cookie-settings"
    ]
    
    all_headers_ok = True
    
    for endpoint in test_endpoints:
        print_info(f"Testing security headers on: {endpoint}")
        try:
            response = requests.get(f"{BACKEND_URL}{endpoint}", timeout=10)
            if response.status_code == 200:
                headers_ok = check_security_headers(response, endpoint)
                if not headers_ok:
                    all_headers_ok = False
            else:
                print_warning(f"  Endpoint returned {response.status_code}, skipping header check")
        except Exception as e:
            print_error(f"  Error testing {endpoint}: {str(e)}")
            all_headers_ok = False
    
    return all_headers_ok

def test_phase12_user_authentication():
    """Test Phase 12 User Authentication System"""
    print_header("PHASE 12 - USER AUTHENTICATION SYSTEM")
    
    results = {}
    tokens = {}  # Store tokens for subsequent tests
    
    # Test 1: User Signup
    print_info("Testing User Signup: /api/phase12/users/signup")
    try:
        signup_data = {
            "email": "testuser@example.com",
            "password": "TestPass123",
            "name": "Test User",
            "phone": "1234567890"
        }
        
        response = requests.post(
            f"{BACKEND_URL}/api/phase12/users/signup",
            json=signup_data,
            timeout=10
        )
        
        if response.status_code == 201:
            data = response.json()
            print_success("User Signup - Status: 201")
            
            if data.get('success') is True:
                print_success("  Signup successful")
            if 'user' in data and data['user'].get('email') == signup_data['email']:
                print_success(f"  User created: {data['user']['email']}")
            if 'access_token' in data and 'refresh_token' in data:
                print_success("  JWT tokens generated")
                tokens['access_token'] = data['access_token']
                tokens['refresh_token'] = data['refresh_token']
            if 'password' not in str(data):
                print_success("  Password not exposed in response")
            
            check_security_headers(response, "User Signup")
            results['/api/phase12/users/signup'] = True
            
        else:
            print_error(f"User Signup - Status: {response.status_code}")
            print_error(f"  Response: {response.text}")
            results['/api/phase12/users/signup'] = False
            
    except Exception as e:
        print_error(f"User Signup - Error: {str(e)}")
        results['/api/phase12/users/signup'] = False
    
    # Test 2: User Login
    print_info("Testing User Login: /api/phase12/users/login")
    try:
        login_data = {
            "email": "testuser@example.com",
            "password": "TestPass123"
        }
        
        response = requests.post(
            f"{BACKEND_URL}/api/phase12/users/login",
            json=login_data,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("User Login - Status: 200")
            
            if data.get('success') is True:
                print_success("  Login successful")
            if 'user' in data and data['user'].get('email') == login_data['email']:
                print_success(f"  User authenticated: {data['user']['email']}")
            if 'access_token' in data and 'refresh_token' in data:
                print_success("  JWT tokens generated")
                # Update tokens from login
                tokens['access_token'] = data['access_token']
                tokens['refresh_token'] = data['refresh_token']
            if 'last_login' in data['user']:
                print_success("  Last login timestamp updated")
            
            check_security_headers(response, "User Login")
            results['/api/phase12/users/login'] = True
            
        else:
            print_error(f"User Login - Status: {response.status_code}")
            print_error(f"  Response: {response.text}")
            results['/api/phase12/users/login'] = False
            
    except Exception as e:
        print_error(f"User Login - Error: {str(e)}")
        results['/api/phase12/users/login'] = False
    
    # Test 3: Get Profile (with auth token)
    if tokens.get('access_token'):
        print_info("Testing Get Profile: /api/phase12/users/profile")
        try:
            headers = {"Authorization": f"Bearer {tokens['access_token']}"}
            
            response = requests.get(
                f"{BACKEND_URL}/api/phase12/users/profile",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print_success("Get Profile - Status: 200")
                
                if data.get('success') is True:
                    print_success("  Profile retrieved successfully")
                if 'user' in data and data['user'].get('email') == "testuser@example.com":
                    print_success(f"  Profile data: {data['user']['name']}")
                if 'password' not in str(data):
                    print_success("  Password not exposed in profile")
                
                check_security_headers(response, "Get Profile")
                results['/api/phase12/users/profile'] = True
                
            else:
                print_error(f"Get Profile - Status: {response.status_code}")
                print_error(f"  Response: {response.text}")
                results['/api/phase12/users/profile'] = False
                
        except Exception as e:
            print_error(f"Get Profile - Error: {str(e)}")
            results['/api/phase12/users/profile'] = False
    else:
        print_warning("Skipping profile test - no access token available")
        results['/api/phase12/users/profile'] = False
    
    # Test 4: Token Refresh
    if tokens.get('refresh_token'):
        print_info("Testing Token Refresh: /api/phase12/users/refresh")
        try:
            refresh_data = {"refresh_token": tokens['refresh_token']}
            
            response = requests.post(
                f"{BACKEND_URL}/api/phase12/users/refresh",
                json=refresh_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print_success("Token Refresh - Status: 200")
                
                if data.get('success') is True:
                    print_success("  Token refresh successful")
                if 'access_token' in data:
                    print_success("  New access token generated")
                    # Update access token
                    tokens['access_token'] = data['access_token']
                if data.get('token_type') == 'bearer':
                    print_success("  Token type: bearer")
                
                check_security_headers(response, "Token Refresh")
                results['/api/phase12/users/refresh'] = True
                
            else:
                print_error(f"Token Refresh - Status: {response.status_code}")
                print_error(f"  Response: {response.text}")
                results['/api/phase12/users/refresh'] = False
                
        except Exception as e:
            print_error(f"Token Refresh - Error: {str(e)}")
            results['/api/phase12/users/refresh'] = False
    else:
        print_warning("Skipping token refresh test - no refresh token available")
        results['/api/phase12/users/refresh'] = False
    
    # Test 5: Dashboard Overview
    if tokens.get('access_token'):
        print_info("Testing Dashboard Overview: /api/phase12/dashboard/overview")
        try:
            headers = {"Authorization": f"Bearer {tokens['access_token']}"}
            
            response = requests.get(
                f"{BACKEND_URL}/api/phase12/dashboard/overview",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print_success("Dashboard Overview - Status: 200")
                
                if data.get('success') is True:
                    print_success("  Dashboard data retrieved")
                if 'overview' in data:
                    overview = data['overview']
                    print_success(f"  Total sessions: {overview.get('total_sessions', 0)}")
                    print_success(f"  Total events: {overview.get('total_events', 0)}")
                    print_success(f"  Total payments: {overview.get('total_payments', 0)}")
                    print_success(f"  Saved blogs: {overview.get('saved_blogs', 0)}")
                
                check_security_headers(response, "Dashboard Overview")
                results['/api/phase12/dashboard/overview'] = True
                
            else:
                print_error(f"Dashboard Overview - Status: {response.status_code}")
                print_error(f"  Response: {response.text}")
                results['/api/phase12/dashboard/overview'] = False
                
        except Exception as e:
            print_error(f"Dashboard Overview - Error: {str(e)}")
            results['/api/phase12/dashboard/overview'] = False
    else:
        print_warning("Skipping dashboard test - no access token available")
        results['/api/phase12/dashboard/overview'] = False
    
    return results


def main():
    """Main testing function"""
    print_header("PHASE 12 USER AUTHENTICATION TESTING")
    print_info(f"Testing backend at: {BACKEND_URL}")
    print_info(f"Test started at: {datetime.now().isoformat()}")
    
    all_results = {}
    
    # Run all tests
    try:
        # Test Phase 12 User Authentication
        phase12_results = test_phase12_user_authentication()
        all_results.update(phase12_results)
        
        # Test production health endpoints
        health_results = test_production_health_endpoints()
        all_results.update(health_results)
        
        # Test SEO endpoints
        seo_results = test_seo_endpoints()
        all_results.update(seo_results)
        
        # Test GDPR compliance endpoints
        gdpr_results = test_gdpr_compliance_endpoints()
        all_results.update(gdpr_results)
        
        # Test security headers comprehensively
        security_headers_ok = test_security_headers_comprehensive()
        
    except KeyboardInterrupt:
        print_error("\nTesting interrupted by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error during testing: {str(e)}")
        sys.exit(1)
    
    # Summary
    print_header("TEST SUMMARY")
    
    passed = sum(1 for result in all_results.values() if result)
    total = len(all_results)
    
    print_info(f"Total endpoints tested: {total}")
    print_success(f"Passed: {passed}")
    print_error(f"Failed: {total - passed}")
    
    if security_headers_ok:
        print_success("Security headers: ✓")
    else:
        print_error("Security headers: Some issues found")
    
    # Detailed results
    print_info("\nDetailed Results:")
    for endpoint, result in all_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {endpoint}: {status}")
    
    # Exit code
    if passed == total and security_headers_ok:
        print_success("\n🎉 All Phase 12 User Authentication and Phase 9 backend tests passed!")
        sys.exit(0)
    else:
        print_error(f"\n💥 {total - passed} tests failed. Please check the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main()