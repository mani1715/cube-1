#!/usr/bin/env python3
"""
Comprehensive Backend Testing Script for Phase 14 - All Sub-Phases
Tests all Phase 14 features: Scalability, Backup, Roles, Communication, Engagement, Power Tools, and Hardening
Also includes Phase 9 Production, SEO, GDPR endpoints, and Phase 12 User Authentication.
"""

import requests
import json
import sys
from datetime import datetime
import xml.etree.ElementTree as ET
import uuid

# Backend URL from frontend .env
BACKEND_URL = "https://rubiks-builder.preview.emergentagent.com"

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

def get_admin_token():
    """Get admin authentication token for testing"""
    try:
        login_data = {
            "email": "admin@acube.com",
            "password": "admin123"
        }
        
        response = requests.post(
            f"{BACKEND_URL}/api/admin/auth/login",
            json=login_data,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            admin_token = data.get('access_token')
            print_success("Admin authentication successful")
            return admin_token
        else:
            print_warning(f"Admin login failed with status {response.status_code}")
            return None
    except Exception as e:
        print_warning(f"Admin login error: {str(e)}")
        return None


def test_phase14_scalability_endpoints():
    """Test Phase 14.1 Scalability & Infrastructure Endpoints"""
    print_header("PHASE 14.1 - SCALABILITY & INFRASTRUCTURE ENDPOINTS")
    
    results = {}
    admin_token = get_admin_token()
    
    # Test 1: Public Health Check (no auth required)
    print_info("Testing Scalability Health Check: /api/phase14/scalability/health")
    try:
        response = requests.get(f"{BACKEND_URL}/api/phase14/scalability/health", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print_success("Scalability Health Check - Status: 200")
            
            if data.get('status') in ['healthy', 'degraded', 'unhealthy']:
                print_success(f"  Health status: {data.get('status')}")
            
            if 'components' in data:
                components = data['components']
                if 'database' in components:
                    db_status = components['database'].get('status')
                    print_success(f"  Database component: {db_status}")
                if 'cache' in components:
                    cache_status = components['cache'].get('status')
                    print_success(f"  Cache component: {cache_status}")
            
            check_security_headers(response, "Scalability Health Check")
            results['/api/phase14/scalability/health'] = True
            
        else:
            print_error(f"Scalability Health Check - Status: {response.status_code}")
            results['/api/phase14/scalability/health'] = False
            
    except Exception as e:
        print_error(f"Scalability Health Check - Error: {str(e)}")
        results['/api/phase14/scalability/health'] = False
    
    # Admin endpoints (require authentication)
    if admin_token:
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Test Connection Pool Health
        print_info("Testing Connection Pool Health: /api/phase14/scalability/connection-pool/health")
        try:
            response = requests.get(
                f"{BACKEND_URL}/api/phase14/scalability/connection-pool/health",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print_success("Connection Pool Health - Status: 200")
                
                if data.get('status') in ['healthy', 'unhealthy']:
                    print_success(f"  Pool status: {data.get('status')}")
                
                check_security_headers(response, "Connection Pool Health")
                results['/api/phase14/scalability/connection-pool/health'] = True
                
            else:
                print_error(f"Connection Pool Health - Status: {response.status_code}")
                results['/api/phase14/scalability/connection-pool/health'] = False
                
        except Exception as e:
            print_error(f"Connection Pool Health - Error: {str(e)}")
            results['/api/phase14/scalability/connection-pool/health'] = False
        
        # Test Cache Statistics
        print_info("Testing Cache Statistics: /api/phase14/scalability/cache/stats")
        try:
            response = requests.get(
                f"{BACKEND_URL}/api/phase14/scalability/cache/stats",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print_success("Cache Statistics - Status: 200")
                
                if 'cache_stats' in data:
                    cache_stats = data['cache_stats']
                    print_success(f"  Cache hit rate: {cache_stats.get('hit_rate', 0)}")
                
                check_security_headers(response, "Cache Statistics")
                results['/api/phase14/scalability/cache/stats'] = True
                
            else:
                print_error(f"Cache Statistics - Status: {response.status_code}")
                results['/api/phase14/scalability/cache/stats'] = False
                
        except Exception as e:
            print_error(f"Cache Statistics - Error: {str(e)}")
            results['/api/phase14/scalability/cache/stats'] = False
        
        # Test Performance Metrics
        print_info("Testing Performance Metrics: /api/phase14/scalability/performance/metrics")
        try:
            response = requests.get(
                f"{BACKEND_URL}/api/phase14/scalability/performance/metrics",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print_success("Performance Metrics - Status: 200")
                
                if 'total_requests' in data:
                    print_success(f"  Total requests: {data.get('total_requests')}")
                
                check_security_headers(response, "Performance Metrics")
                results['/api/phase14/scalability/performance/metrics'] = True
                
            else:
                print_error(f"Performance Metrics - Status: {response.status_code}")
                results['/api/phase14/scalability/performance/metrics'] = False
                
        except Exception as e:
            print_error(f"Performance Metrics - Error: {str(e)}")
            results['/api/phase14/scalability/performance/metrics'] = False
    
    else:
        print_warning("Skipping admin endpoints - no authentication token available")
        admin_endpoints = [
            '/api/phase14/scalability/connection-pool/health',
            '/api/phase14/scalability/cache/stats',
            '/api/phase14/scalability/performance/metrics'
        ]
        for endpoint in admin_endpoints:
            results[endpoint] = False
    
    return results


def test_phase14_backup_endpoints():
    """Test Phase 14.2 Backup & Disaster Recovery Endpoints"""
    print_header("PHASE 14.2 - BACKUP & DISASTER RECOVERY ENDPOINTS")
    
    results = {}
    admin_token = get_admin_token()
    
    if not admin_token:
        print_warning("Skipping backup tests - no authentication token available")
        return {}
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Test 1: Create Backup
    print_info("Testing Create Backup: /api/phase14/backup/create")
    try:
        backup_data = {
            "backup_type": "manual"
        }
        
        response = requests.post(
            f"{BACKEND_URL}/api/phase14/backup/create",
            json=backup_data,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("Create Backup - Status: 200")
            
            if 'backup' in data and 'backup_id' in data['backup']:
                backup_id = data['backup']['backup_id']
                print_success(f"  Backup ID: {backup_id}")
                # Store for later tests
                results['backup_id'] = backup_id
            
            check_security_headers(response, "Create Backup")
            results['/api/phase14/backup/create'] = True
            
        else:
            print_error(f"Create Backup - Status: {response.status_code}")
            print_error(f"  Response: {response.text}")
            results['/api/phase14/backup/create'] = False
            
    except Exception as e:
        print_error(f"Create Backup - Error: {str(e)}")
        results['/api/phase14/backup/create'] = False
    
    # Test 2: List Backups
    print_info("Testing List Backups: /api/phase14/backup/list")
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/phase14/backup/list",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("List Backups - Status: 200")
            
            if 'total_backups' in data:
                print_success(f"  Total backups: {data.get('total_backups')}")
            
            if 'backups' in data and len(data['backups']) > 0:
                print_success(f"  Backup entries: {len(data['backups'])}")
            
            check_security_headers(response, "List Backups")
            results['/api/phase14/backup/list'] = True
            
        else:
            print_error(f"List Backups - Status: {response.status_code}")
            results['/api/phase14/backup/list'] = False
            
    except Exception as e:
        print_error(f"List Backups - Error: {str(e)}")
        results['/api/phase14/backup/list'] = False
    
    # Test 3: Backup Statistics
    print_info("Testing Backup Statistics: /api/phase14/backup/statistics")
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/phase14/backup/statistics",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("Backup Statistics - Status: 200")
            
            if 'total_backups' in data:
                print_success(f"  Total backups: {data.get('total_backups')}")
            
            if 'storage_usage' in data:
                storage = data['storage_usage']
                print_success(f"  Storage usage: {storage.get('total_size_mb', 0)} MB")
            
            check_security_headers(response, "Backup Statistics")
            results['/api/phase14/backup/statistics'] = True
            
        else:
            print_error(f"Backup Statistics - Status: {response.status_code}")
            results['/api/phase14/backup/statistics'] = False
            
    except Exception as e:
        print_error(f"Backup Statistics - Error: {str(e)}")
        results['/api/phase14/backup/statistics'] = False
    
    return results


def test_phase14_roles_endpoints():
    """Test Phase 14.3 Role Expansion Endpoints"""
    print_header("PHASE 14.3 - ROLE EXPANSION ENDPOINTS")
    
    results = {}
    admin_token = get_admin_token()
    
    if not admin_token:
        print_warning("Skipping role tests - no authentication token available")
        return {}
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Test 1: List All Roles
    print_info("Testing List Roles: /api/phase14/roles")
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/phase14/roles",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("List Roles - Status: 200")
            
            if 'total_roles' in data:
                print_success(f"  Total roles: {data.get('total_roles')}")
            
            if 'roles' in data:
                roles = data['roles']
                print_success(f"  Role entries: {len(roles)}")
                
                # Check for expected roles
                role_names = [role.get('role') for role in roles]
                expected_roles = ['super_admin', 'admin', 'content_manager', 'moderator', 'analyst', 'viewer']
                
                for expected_role in expected_roles:
                    if expected_role in role_names:
                        print_success(f"    ✓ {expected_role}")
                    else:
                        print_error(f"    ✗ {expected_role} missing")
            
            check_security_headers(response, "List Roles")
            results['/api/phase14/roles'] = True
            
        else:
            print_error(f"List Roles - Status: {response.status_code}")
            results['/api/phase14/roles'] = False
            
    except Exception as e:
        print_error(f"List Roles - Error: {str(e)}")
        results['/api/phase14/roles'] = False
    
    # Test 2: Get Role Permissions
    print_info("Testing Role Permissions: /api/phase14/roles/content_manager/permissions")
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/phase14/roles/content_manager/permissions",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("Role Permissions - Status: 200")
            
            if data.get('role') == 'content_manager':
                print_success(f"  Role: {data.get('role')}")
            
            if 'permissions' in data:
                permissions = data['permissions']
                print_success(f"  Permissions: {len(permissions)}")
            
            check_security_headers(response, "Role Permissions")
            results['/api/phase14/roles/content_manager/permissions'] = True
            
        else:
            print_error(f"Role Permissions - Status: {response.status_code}")
            results['/api/phase14/roles/content_manager/permissions'] = False
            
    except Exception as e:
        print_error(f"Role Permissions - Error: {str(e)}")
        results['/api/phase14/roles/content_manager/permissions'] = False
    
    # Test 3: Permission Matrix
    print_info("Testing Permission Matrix: /api/phase14/roles/matrix")
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/phase14/roles/matrix",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("Permission Matrix - Status: 200")
            
            if 'roles' in data:
                print_success(f"  Roles in matrix: {len(data['roles'])}")
            
            if 'all_permissions' in data:
                print_success(f"  Total permissions: {len(data['all_permissions'])}")
            
            check_security_headers(response, "Permission Matrix")
            results['/api/phase14/roles/matrix'] = True
            
        else:
            print_error(f"Permission Matrix - Status: {response.status_code}")
            results['/api/phase14/roles/matrix'] = False
            
    except Exception as e:
        print_error(f"Permission Matrix - Error: {str(e)}")
        results['/api/phase14/roles/matrix'] = False
    
    # Test 4: Role Statistics
    print_info("Testing Role Statistics: /api/phase14/roles/statistics")
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/phase14/roles/statistics",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("Role Statistics - Status: 200")
            
            if 'total_admins' in data:
                print_success(f"  Total admins: {data.get('total_admins')}")
            
            if 'role_distribution' in data:
                print_success(f"  Role distribution entries: {len(data['role_distribution'])}")
            
            check_security_headers(response, "Role Statistics")
            results['/api/phase14/roles/statistics'] = True
            
        else:
            print_error(f"Role Statistics - Status: {response.status_code}")
            results['/api/phase14/roles/statistics'] = False
            
    except Exception as e:
        print_error(f"Role Statistics - Error: {str(e)}")
        results['/api/phase14/roles/statistics'] = False
    
    return results


def test_phase14_communication_endpoints():
    """Test Phase 14.4 Communication Enhancements Endpoints"""
    print_header("PHASE 14.4 - COMMUNICATION ENHANCEMENTS ENDPOINTS")
    
    results = {}
    admin_token = get_admin_token()
    
    if not admin_token:
        print_warning("Skipping communication tests - no authentication token available")
        return {}
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    template_id = None
    
    # Test 1: Create Email Template
    print_info("Testing Create Email Template: /api/phase14/communication/templates")
    try:
        template_data = {
            "name": "Welcome Email",
            "subject": "Welcome to A-Cube {{user_name}}",
            "body": "Hello {{user_name}}, welcome to our platform!",
            "category": "transactional",
            "variables": ["user_name"]
        }
        
        response = requests.post(
            f"{BACKEND_URL}/api/phase14/communication/templates",
            json=template_data,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("Create Email Template - Status: 200")
            
            if data.get('success') is True:
                print_success("  Template created successfully")
            
            if 'template_id' in data:
                template_id = data['template_id']
                print_success(f"  Template ID: {template_id}")
            
            check_security_headers(response, "Create Email Template")
            results['/api/phase14/communication/templates'] = True
            
        else:
            print_error(f"Create Email Template - Status: {response.status_code}")
            print_error(f"  Response: {response.text}")
            results['/api/phase14/communication/templates'] = False
            
    except Exception as e:
        print_error(f"Create Email Template - Error: {str(e)}")
        results['/api/phase14/communication/templates'] = False
    
    # Test 2: List Email Templates
    print_info("Testing List Email Templates: /api/phase14/communication/templates")
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/phase14/communication/templates",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("List Email Templates - Status: 200")
            
            if 'total' in data:
                print_success(f"  Total templates: {data.get('total')}")
            
            if 'templates' in data:
                templates = data['templates']
                print_success(f"  Template entries: {len(templates)}")
                
                # Use first template ID if we don't have one from creation
                if not template_id and templates:
                    template_id = templates[0].get('id')
            
            check_security_headers(response, "List Email Templates")
            results['/api/phase14/communication/templates_list'] = True
            
        else:
            print_error(f"List Email Templates - Status: {response.status_code}")
            results['/api/phase14/communication/templates_list'] = False
            
    except Exception as e:
        print_error(f"List Email Templates - Error: {str(e)}")
        results['/api/phase14/communication/templates_list'] = False
    
    # Test 3: Send Email (if we have a template)
    if template_id:
        print_info("Testing Send Email: /api/phase14/communication/send-email")
        try:
            email_data = {
                "template_id": template_id,
                "recipient": "test@example.com",
                "variables": {"user_name": "John Doe"},
                "priority": "normal"
            }
            
            response = requests.post(
                f"{BACKEND_URL}/api/phase14/communication/send-email",
                json=email_data,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print_success("Send Email - Status: 200")
                
                if data.get('success') is True:
                    print_success("  Email queued successfully")
                
                if 'email_id' in data:
                    print_success(f"  Email ID: {data['email_id']}")
                
                check_security_headers(response, "Send Email")
                results['/api/phase14/communication/send-email'] = True
                
            else:
                print_error(f"Send Email - Status: {response.status_code}")
                results['/api/phase14/communication/send-email'] = False
                
        except Exception as e:
            print_error(f"Send Email - Error: {str(e)}")
            results['/api/phase14/communication/send-email'] = False
    else:
        print_warning("Skipping send email test - no template ID available")
        results['/api/phase14/communication/send-email'] = False
    
    # Test 4: Email Queue
    print_info("Testing Email Queue: /api/phase14/communication/email-queue")
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/phase14/communication/email-queue",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("Email Queue - Status: 200")
            
            if 'total' in data:
                print_success(f"  Total emails in queue: {data.get('total')}")
            
            if 'emails' in data:
                print_success(f"  Email entries: {len(data['emails'])}")
            
            check_security_headers(response, "Email Queue")
            results['/api/phase14/communication/email-queue'] = True
            
        else:
            print_error(f"Email Queue - Status: {response.status_code}")
            results['/api/phase14/communication/email-queue'] = False
            
    except Exception as e:
        print_error(f"Email Queue - Error: {str(e)}")
        results['/api/phase14/communication/email-queue'] = False
    
    return results


def test_phase14_engagement_endpoints():
    """Test Phase 14.5 Engagement & Retention Endpoints"""
    print_header("PHASE 14.5 - ENGAGEMENT & RETENTION ENDPOINTS")
    
    results = {}
    admin_token = get_admin_token()
    
    if not admin_token:
        print_warning("Skipping engagement tests - no authentication token available")
        return {}
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Test 1: Track Activity
    print_info("Testing Track Activity: /api/phase14/engagement/track-activity")
    try:
        activity_data = {
            "user_id": "test-user-123",
            "activity_type": "login",
            "metadata": {"source": "web"}
        }
        
        response = requests.post(
            f"{BACKEND_URL}/api/phase14/engagement/track-activity",
            json=activity_data,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("Track Activity - Status: 200")
            
            if data.get('success') is True:
                print_success("  Activity tracked successfully")
            
            if data.get('activity_type') == 'login':
                print_success(f"  Activity type: {data.get('activity_type')}")
            
            check_security_headers(response, "Track Activity")
            results['/api/phase14/engagement/track-activity'] = True
            
        else:
            print_error(f"Track Activity - Status: {response.status_code}")
            print_error(f"  Response: {response.text}")
            results['/api/phase14/engagement/track-activity'] = False
            
    except Exception as e:
        print_error(f"Track Activity - Error: {str(e)}")
        results['/api/phase14/engagement/track-activity'] = False
    
    # Test 2: Engagement Metrics
    print_info("Testing Engagement Metrics: /api/phase14/engagement/metrics")
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/phase14/engagement/metrics",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("Engagement Metrics - Status: 200")
            
            if 'daily_active_users' in data:
                print_success(f"  Daily active users: {data.get('daily_active_users')}")
            
            if 'monthly_active_users' in data:
                print_success(f"  Monthly active users: {data.get('monthly_active_users')}")
            
            if 'engagement_rate' in data:
                print_success(f"  Engagement rate: {data.get('engagement_rate')}%")
            
            check_security_headers(response, "Engagement Metrics")
            results['/api/phase14/engagement/metrics'] = True
            
        else:
            print_error(f"Engagement Metrics - Status: {response.status_code}")
            results['/api/phase14/engagement/metrics'] = False
            
    except Exception as e:
        print_error(f"Engagement Metrics - Error: {str(e)}")
        results['/api/phase14/engagement/metrics'] = False
    
    # Test 3: Retention Analysis
    print_info("Testing Retention Analysis: /api/phase14/engagement/retention-analysis")
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/phase14/engagement/retention-analysis",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("Retention Analysis - Status: 200")
            
            if 'total_users' in data:
                print_success(f"  Total users analyzed: {data.get('total_users')}")
            
            if 'overall_retention_rate' in data:
                print_success(f"  Overall retention rate: {data.get('overall_retention_rate')}%")
            
            if 'cohorts' in data:
                print_success(f"  Cohort entries: {len(data['cohorts'])}")
            
            check_security_headers(response, "Retention Analysis")
            results['/api/phase14/engagement/retention-analysis'] = True
            
        else:
            print_error(f"Retention Analysis - Status: {response.status_code}")
            results['/api/phase14/engagement/retention-analysis'] = False
            
    except Exception as e:
        print_error(f"Retention Analysis - Error: {str(e)}")
        results['/api/phase14/engagement/retention-analysis'] = False
    
    # Test 4: Inactive Users
    print_info("Testing Inactive Users: /api/phase14/engagement/inactive-users?days=30")
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/phase14/engagement/inactive-users?days=30",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("Inactive Users - Status: 200")
            
            if 'total_inactive' in data:
                print_success(f"  Total inactive users: {data.get('total_inactive')}")
            
            if 'inactivity_threshold_days' in data:
                print_success(f"  Inactivity threshold: {data.get('inactivity_threshold_days')} days")
            
            check_security_headers(response, "Inactive Users")
            results['/api/phase14/engagement/inactive-users'] = True
            
        else:
            print_error(f"Inactive Users - Status: {response.status_code}")
            results['/api/phase14/engagement/inactive-users'] = False
            
    except Exception as e:
        print_error(f"Inactive Users - Error: {str(e)}")
        results['/api/phase14/engagement/inactive-users'] = False
    
    return results


def test_phase14_power_tools_endpoints():
    """Test Phase 14.6 Admin Power Tools Endpoints"""
    print_header("PHASE 14.6 - ADMIN POWER TOOLS ENDPOINTS")
    
    results = {}
    admin_token = get_admin_token()
    
    if not admin_token:
        print_warning("Skipping power tools tests - no authentication token available")
        return {}
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Test 1: Admin Dashboard
    print_info("Testing Admin Dashboard: /api/phase14/power-tools/dashboard")
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/phase14/power-tools/dashboard",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("Admin Dashboard - Status: 200")
            
            if 'statistics' in data:
                print_success("  Statistics section present")
            
            if 'pending_actions' in data:
                print_success("  Pending actions section present")
            
            check_security_headers(response, "Admin Dashboard")
            results['/api/phase14/power-tools/dashboard'] = True
            
        else:
            print_error(f"Admin Dashboard - Status: {response.status_code}")
            results['/api/phase14/power-tools/dashboard'] = False
            
    except Exception as e:
        print_error(f"Admin Dashboard - Error: {str(e)}")
        results['/api/phase14/power-tools/dashboard'] = False
    
    # Test 2: Advanced Search
    print_info("Testing Advanced Search: /api/phase14/power-tools/advanced-search/blogs")
    try:
        search_data = {
            "search": "mental health",
            "page": 1,
            "limit": 10
        }
        
        response = requests.post(
            f"{BACKEND_URL}/api/phase14/power-tools/advanced-search/blogs",
            json=search_data,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("Advanced Search - Status: 200")
            
            if 'collection' in data:
                print_success(f"  Collection: {data.get('collection')}")
            
            if 'results' in data:
                print_success(f"  Results: {len(data['results'])} items")
            
            if 'pagination' in data:
                pagination = data['pagination']
                print_success(f"  Total: {pagination.get('total')} items")
            
            check_security_headers(response, "Advanced Search")
            results['/api/phase14/power-tools/advanced-search/blogs'] = True
            
        else:
            print_error(f"Advanced Search - Status: {response.status_code}")
            results['/api/phase14/power-tools/advanced-search/blogs'] = False
            
    except Exception as e:
        print_error(f"Advanced Search - Error: {str(e)}")
        results['/api/phase14/power-tools/advanced-search/blogs'] = False
    
    return results


def test_phase14_hardening_endpoints():
    """Test Phase 14.7 Final Go-Live Hardening Endpoints"""
    print_header("PHASE 14.7 - FINAL GO-LIVE HARDENING ENDPOINTS")
    
    results = {}
    admin_token = get_admin_token()
    
    if not admin_token:
        print_warning("Skipping hardening tests - no authentication token available")
        return {}
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Test 1: Security Audit
    print_info("Testing Security Audit: /api/phase14/hardening/security-audit")
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/phase14/hardening/security-audit",
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("Security Audit - Status: 200")
            
            if 'overall_status' in data:
                print_success(f"  Overall status: {data.get('overall_status')}")
            
            if 'checks' in data:
                print_success(f"  Security checks: {len(data['checks'])}")
            
            if 'warnings' in data:
                print_success(f"  Warnings: {len(data['warnings'])}")
            
            if 'recommendations' in data:
                print_success(f"  Recommendations: {len(data['recommendations'])}")
            
            check_security_headers(response, "Security Audit")
            results['/api/phase14/hardening/security-audit'] = True
            
        else:
            print_error(f"Security Audit - Status: {response.status_code}")
            results['/api/phase14/hardening/security-audit'] = False
            
    except Exception as e:
        print_error(f"Security Audit - Error: {str(e)}")
        results['/api/phase14/hardening/security-audit'] = False
    
    # Test 2: Performance Review
    print_info("Testing Performance Review: /api/phase14/hardening/performance-review")
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/phase14/hardening/performance-review",
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("Performance Review - Status: 200")
            
            if 'database_stats' in data:
                db_stats = data['database_stats']
                print_success(f"  Total collections: {db_stats.get('total_collections')}")
                print_success(f"  Total documents: {db_stats.get('total_documents')}")
            
            if 'optimization_opportunities' in data:
                print_success(f"  Optimization opportunities: {len(data['optimization_opportunities'])}")
            
            check_security_headers(response, "Performance Review")
            results['/api/phase14/hardening/performance-review'] = True
            
        else:
            print_error(f"Performance Review - Status: {response.status_code}")
            results['/api/phase14/hardening/performance-review'] = False
            
    except Exception as e:
        print_error(f"Performance Review - Error: {str(e)}")
        results['/api/phase14/hardening/performance-review'] = False
    
    # Test 3: Comprehensive Health Check
    print_info("Testing Comprehensive Health Check: /api/phase14/hardening/health-comprehensive")
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/phase14/hardening/health-comprehensive",
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("Comprehensive Health Check - Status: 200")
            
            if 'overall_status' in data:
                print_success(f"  Overall status: {data.get('overall_status')}")
            
            if 'components' in data:
                components = data['components']
                print_success(f"  Components checked: {len(components)}")
                
                for component in components:
                    comp_name = component.get('component')
                    comp_status = component.get('status')
                    print_info(f"    {comp_name}: {comp_status}")
            
            check_security_headers(response, "Comprehensive Health Check")
            results['/api/phase14/hardening/health-comprehensive'] = True
            
        else:
            print_error(f"Comprehensive Health Check - Status: {response.status_code}")
            results['/api/phase14/hardening/health-comprehensive'] = False
            
    except Exception as e:
        print_error(f"Comprehensive Health Check - Error: {str(e)}")
        results['/api/phase14/hardening/health-comprehensive'] = False
    
    # Test 4: Production Checklist
    print_info("Testing Production Checklist: /api/phase14/hardening/production-checklist")
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/phase14/hardening/production-checklist",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("Production Checklist - Status: 200")
            
            if 'summary' in data:
                summary = data['summary']
                print_success(f"  Total checks: {summary.get('total_checks')}")
                print_success(f"  Completed: {summary.get('completed_checks')}")
                print_success(f"  Overall completion: {summary.get('overall_completion_rate')}%")
                print_success(f"  Ready for production: {summary.get('ready_for_production')}")
            
            if 'categories' in data:
                print_success(f"  Categories: {len(data['categories'])}")
            
            check_security_headers(response, "Production Checklist")
            results['/api/phase14/hardening/production-checklist'] = True
            
        else:
            print_error(f"Production Checklist - Status: {response.status_code}")
            results['/api/phase14/hardening/production-checklist'] = False
            
    except Exception as e:
        print_error(f"Production Checklist - Error: {str(e)}")
        results['/api/phase14/hardening/production-checklist'] = False
    
    # Test 5: Optimization (Dry Run)
    print_info("Testing Optimization: /api/phase14/hardening/optimize")
    try:
        optimization_data = {
            "optimization_type": "all",
            "dry_run": True
        }
        
        response = requests.post(
            f"{BACKEND_URL}/api/phase14/hardening/optimize",
            json=optimization_data,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("Optimization - Status: 200")
            
            if data.get('dry_run') is True:
                print_success("  Dry run mode confirmed")
            
            if 'actions_taken' in data:
                print_success(f"  Actions planned: {len(data['actions_taken'])}")
            
            if 'recommendations' in data:
                print_success(f"  Recommendations: {len(data['recommendations'])}")
            
            check_security_headers(response, "Optimization")
            results['/api/phase14/hardening/optimize'] = True
            
        else:
            print_error(f"Optimization - Status: {response.status_code}")
            results['/api/phase14/hardening/optimize'] = False
            
    except Exception as e:
        print_error(f"Optimization - Error: {str(e)}")
        results['/api/phase14/hardening/optimize'] = False
    
    return results


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
    print_header("PHASE 14.1 SCALABILITY & INFRASTRUCTURE TESTING")
    print_info(f"Testing backend at: {BACKEND_URL}")
    print_info(f"Test started at: {datetime.now().isoformat()}")
    
    all_results = {}
    
    # Run all tests
    try:
        # Test Phase 14.1 Scalability & Infrastructure
        phase14_results = test_phase14_scalability_endpoints()
        all_results.update(phase14_results)
        
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
        print_success("\n🎉 All Phase 14.1 Scalability and backend tests passed!")
        sys.exit(0)
    else:
        print_error(f"\n💥 {total - passed} tests failed. Please check the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main()