#!/usr/bin/env python3
"""
A-Cube Mental Health Platform Backend API Tests
Tests all backend endpoints including Phase 7.1 Advanced Security & Compliance
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, Any, List
import bcrypt

# Backend URL from frontend/.env
BASE_URL = "https://code-viewer-47.preview.emergentagent.com/api"

class BackendTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.test_results = []
        self.admin_token = None
        self.super_admin_token = None
        self.created_ids = {
            'sessions': [],
            'events': [],
            'blogs': [],
            'careers': [],
            'volunteers': [],
            'psychologists': [],
            'contacts': [],
            'payments': [],
            'approval_requests': [],
            'admin_notes': []
        }
    
    def log_result(self, test_name: str, success: bool, message: str, details: Dict = None):
        """Log test result"""
        result = {
            'test': test_name,
            'success': success,
            'message': message,
            'details': details or {},
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name} - {message}")
        if details and not success:
            print(f"   Details: {details}")
    
    def test_health_check(self):
        """Test health check endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'healthy':
                    self.log_result("Health Check", True, "API is healthy")
                    return True
                else:
                    self.log_result("Health Check", False, f"Unexpected response: {data}")
                    return False
            else:
                self.log_result("Health Check", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_result("Health Check", False, f"Connection error: {str(e)}")
            return False
    
    def create_admin_accounts(self):
        """Create admin accounts for testing"""
        print("\n🔐 Creating Admin Accounts for Testing...")
        
        # Create admin accounts directly in database
        try:
            import asyncio
            from motor.motor_asyncio import AsyncIOMotorClient
            import os
            from dotenv import load_dotenv
            from pathlib import Path
            
            ROOT_DIR = Path('.')
            load_dotenv(ROOT_DIR / 'backend/.env')
            
            async def create_admins():
                mongo_url = os.environ['MONGO_URL']
                db_name = os.environ['DB_NAME']
                client = AsyncIOMotorClient(mongo_url)
                db = client[db_name]
                
                # Hash passwords
                def get_password_hash(password: str) -> str:
                    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                
                # Create super admin
                super_admin = {
                    "id": "super-admin-test-001",
                    "email": "superadmin@acube.test",
                    "hashed_password": get_password_hash("SuperAdmin123!"),
                    "role": "super_admin",
                    "created_at": datetime.utcnow(),
                    "is_active": True,
                    "last_login": datetime.utcnow(),
                    "password_changed_at": datetime.utcnow(),
                    "two_factor_enabled": False,
                    "two_factor_secret": "",
                    "is_deleted": False,
                    "deleted_at": None,
                    "deleted_by": None
                }
                
                # Create regular admin
                admin = {
                    "id": "admin-test-001",
                    "email": "admin@acube.test",
                    "hashed_password": get_password_hash("Admin123!"),
                    "role": "admin",
                    "created_at": datetime.utcnow(),
                    "is_active": True,
                    "last_login": datetime.utcnow(),
                    "password_changed_at": datetime.utcnow(),
                    "two_factor_enabled": False,
                    "two_factor_secret": "",
                    "is_deleted": False,
                    "deleted_at": None,
                    "deleted_by": None
                }
                
                # Insert or update admins
                await db.admins.update_one(
                    {"email": "superadmin@acube.test"},
                    {"$set": super_admin},
                    upsert=True
                )
                
                await db.admins.update_one(
                    {"email": "admin@acube.test"},
                    {"$set": admin},
                    upsert=True
                )
                
                client.close()
                return True
            
            result = asyncio.run(create_admins())
            if result:
                self.log_result("Admin Account Creation", True, "Created super_admin and admin test accounts")
                return True
            else:
                self.log_result("Admin Account Creation", False, "Failed to create admin accounts")
                return False
                
        except Exception as e:
            self.log_result("Admin Account Creation", False, f"Error: {str(e)}")
            return False
    
    def login_admin(self, email: str, password: str, role: str):
        """Login admin and get token"""
        try:
            login_data = {
                "email": email,
                "password": password
            }
            
            response = self.session.post(f"{self.base_url}/admin/auth/login", json=login_data, timeout=10)
            if response.status_code == 200:
                token_data = response.json()
                access_token = token_data.get('access_token')
                if access_token:
                    if role == "super_admin":
                        self.super_admin_token = access_token
                    else:
                        self.admin_token = access_token
                    self.log_result(f"Admin Login ({role})", True, f"Successfully logged in as {email}")
                    return access_token
                else:
                    self.log_result(f"Admin Login ({role})", False, "No access token in response")
                    return None
            else:
                self.log_result(f"Admin Login ({role})", False, f"HTTP {response.status_code}: {response.text}")
                return None
        except Exception as e:
            self.log_result(f"Admin Login ({role})", False, f"Error: {str(e)}")
            return None
    
    def test_soft_delete_system(self):
        """Test Phase 7.1 - Soft Delete System"""
        print("\n🧪 Testing Phase 7.1 - Soft Delete System...")
        
        if not self.admin_token:
            self.log_result("Soft Delete - Setup", False, "No admin token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # First, create a session booking to soft delete
        session_data = {
            "full_name": "Test User for Soft Delete",
            "email": "softdelete@test.com",
            "phone": "555-0123",
            "age": "30",
            "gender": "other",
            "therapy_type": "individual",
            "concerns": ["testing"],
            "current_feelings": "Testing soft delete functionality",
            "previous_therapy": "no",
            "preferred_time": "morning",
            "additional_info": "Test session for soft delete",
            "consent": True
        }
        
        try:
            # Create session
            response = self.session.post(f"{self.base_url}/sessions/book", json=session_data, timeout=10)
            if response.status_code == 201:
                session = response.json()
                session_id = session.get('id')
                if not session_id:
                    self.log_result("Soft Delete - Create Test Session", False, "No session ID returned")
                    return False
                
                self.log_result("Soft Delete - Create Test Session", True, f"Created session {session_id}")
                
                # Test soft delete
                response = self.session.delete(
                    f"{self.base_url}/admin/security/session_bookings/{session_id}/soft-delete",
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('success'):
                        self.log_result("Soft Delete - Delete Entity", True, f"Successfully soft deleted session {session_id}")
                        
                        # Test that it's hidden from normal queries
                        response = self.session.get(f"{self.base_url}/sessions/{session_id}", timeout=10)
                        if response.status_code == 404:
                            self.log_result("Soft Delete - Hidden from Normal Query", True, "Soft deleted session is hidden from normal queries")
                        else:
                            self.log_result("Soft Delete - Hidden from Normal Query", False, "Soft deleted session still visible in normal queries")
                        
                        # Test list deleted entities
                        response = self.session.get(
                            f"{self.base_url}/admin/security/session_bookings/deleted",
                            headers=headers,
                            timeout=10
                        )
                        
                        if response.status_code == 200:
                            deleted_data = response.json()
                            deleted_entities = deleted_data.get('data', [])
                            if any(entity.get('id') == session_id for entity in deleted_entities):
                                self.log_result("Soft Delete - List Deleted Entities", True, f"Found soft deleted session in deleted list")
                                
                                # Test restore entity
                                response = self.session.post(
                                    f"{self.base_url}/admin/security/session_bookings/{session_id}/restore",
                                    headers=headers,
                                    timeout=10
                                )
                                
                                if response.status_code == 200:
                                    restore_result = response.json()
                                    if restore_result.get('success'):
                                        self.log_result("Soft Delete - Restore Entity", True, f"Successfully restored session {session_id}")
                                        
                                        # Verify it's back in normal queries
                                        response = self.session.get(f"{self.base_url}/sessions/{session_id}", timeout=10)
                                        if response.status_code == 200:
                                            self.log_result("Soft Delete - Restored Entity Visible", True, "Restored session is visible in normal queries")
                                        else:
                                            self.log_result("Soft Delete - Restored Entity Visible", False, "Restored session not visible in normal queries")
                                    else:
                                        self.log_result("Soft Delete - Restore Entity", False, "Restore operation failed")
                                else:
                                    self.log_result("Soft Delete - Restore Entity", False, f"HTTP {response.status_code}: {response.text}")
                            else:
                                self.log_result("Soft Delete - List Deleted Entities", False, "Soft deleted session not found in deleted list")
                        else:
                            self.log_result("Soft Delete - List Deleted Entities", False, f"HTTP {response.status_code}: {response.text}")
                    else:
                        self.log_result("Soft Delete - Delete Entity", False, "Soft delete operation failed")
                else:
                    self.log_result("Soft Delete - Delete Entity", False, f"HTTP {response.status_code}: {response.text}")
            else:
                self.log_result("Soft Delete - Create Test Session", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Soft Delete System", False, f"Error: {str(e)}")
            return False
        
        return True
    
    def test_password_rotation_system(self):
        """Test Phase 7.1 - Password Rotation System"""
        print("\n🧪 Testing Phase 7.1 - Password Rotation System...")
        
        if not self.admin_token:
            self.log_result("Password Rotation - Setup", False, "No admin token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            # Test get password status
            response = self.session.get(
                f"{self.base_url}/admin/security/password/status",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                status_data = response.json()
                required_fields = ['admin_email', 'is_expired', 'days_until_expiry', 'needs_warning', 'password_age_days']
                
                if all(field in status_data for field in required_fields):
                    self.log_result("Password Rotation - Get Status", True, f"Password status retrieved: {status_data['days_until_expiry']} days until expiry")
                    
                    # Test password change
                    change_data = {
                        "current_password": "Admin123!",
                        "new_password": "NewAdmin123!"
                    }
                    
                    response = self.session.post(
                        f"{self.base_url}/admin/security/password/change",
                        json=change_data,
                        headers=headers,
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        change_result = response.json()
                        if change_result.get('success'):
                            self.log_result("Password Rotation - Change Password", True, "Password changed successfully")
                            
                            # Change it back for other tests
                            change_back_data = {
                                "current_password": "NewAdmin123!",
                                "new_password": "Admin123!"
                            }
                            
                            response = self.session.post(
                                f"{self.base_url}/admin/security/password/change",
                                json=change_back_data,
                                headers=headers,
                                timeout=10
                            )
                            
                            if response.status_code == 200:
                                self.log_result("Password Rotation - Restore Password", True, "Password restored for other tests")
                            else:
                                self.log_result("Password Rotation - Restore Password", False, "Failed to restore password")
                        else:
                            self.log_result("Password Rotation - Change Password", False, "Password change failed")
                    else:
                        self.log_result("Password Rotation - Change Password", False, f"HTTP {response.status_code}: {response.text}")
                else:
                    missing_fields = [field for field in required_fields if field not in status_data]
                    self.log_result("Password Rotation - Get Status", False, f"Missing fields: {missing_fields}")
            else:
                self.log_result("Password Rotation - Get Status", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Password Rotation System", False, f"Error: {str(e)}")
            return False
        
        return True
    
    def test_feature_toggle_system(self):
        """Test Phase 7.1 - Feature Toggle System"""
        print("\n🧪 Testing Phase 7.1 - Feature Toggle System...")
        
        if not self.super_admin_token:
            self.log_result("Feature Toggle - Setup", False, "No super admin token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.super_admin_token}"}
        
        try:
            # Test get all feature toggles
            response = self.session.get(
                f"{self.base_url}/admin/security/features",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                features_data = response.json()
                features = features_data.get('features', [])
                
                if len(features) >= 8:  # Should have 8 default features
                    self.log_result("Feature Toggle - Get All Features", True, f"Retrieved {len(features)} feature toggles")
                    
                    # Test update a feature toggle
                    test_feature = None
                    for feature in features:
                        if feature.get('feature_name') == 'blog_comments':
                            test_feature = feature
                            break
                    
                    if test_feature:
                        current_status = test_feature.get('is_enabled', False)
                        new_status = not current_status
                        
                        update_data = {
                            "is_enabled": new_status,
                            "reason": "Testing feature toggle functionality"
                        }
                        
                        response = self.session.put(
                            f"{self.base_url}/admin/security/features/blog_comments",
                            json=update_data,
                            headers=headers,
                            timeout=10
                        )
                        
                        if response.status_code == 200:
                            update_result = response.json()
                            if update_result.get('success'):
                                self.log_result("Feature Toggle - Update Feature", True, f"Successfully toggled blog_comments to {new_status}")
                                
                                # Toggle it back
                                restore_data = {
                                    "is_enabled": current_status,
                                    "reason": "Restoring original state after test"
                                }
                                
                                response = self.session.put(
                                    f"{self.base_url}/admin/security/features/blog_comments",
                                    json=restore_data,
                                    headers=headers,
                                    timeout=10
                                )
                                
                                if response.status_code == 200:
                                    self.log_result("Feature Toggle - Restore Feature", True, "Restored original feature state")
                                else:
                                    self.log_result("Feature Toggle - Restore Feature", False, "Failed to restore feature state")
                            else:
                                self.log_result("Feature Toggle - Update Feature", False, "Feature toggle update failed")
                        else:
                            self.log_result("Feature Toggle - Update Feature", False, f"HTTP {response.status_code}: {response.text}")
                    else:
                        self.log_result("Feature Toggle - Find Test Feature", False, "blog_comments feature not found")
                else:
                    self.log_result("Feature Toggle - Get All Features", False, f"Expected 8+ features, got {len(features)}")
            else:
                self.log_result("Feature Toggle - Get All Features", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Feature Toggle System", False, f"Error: {str(e)}")
            return False
        
        return True
    
    def test_approval_workflow_system(self):
        """Test Phase 7.1 - Approval Workflow System"""
        print("\n🧪 Testing Phase 7.1 - Approval Workflow System...")
        
        if not self.admin_token or not self.super_admin_token:
            self.log_result("Approval Workflow - Setup", False, "Missing admin tokens")
            return False
        
        admin_headers = {"Authorization": f"Bearer {self.admin_token}"}
        super_admin_headers = {"Authorization": f"Bearer {self.super_admin_token}"}
        
        try:
            # Test create approval request (as admin)
            request_data = {
                "action_type": "bulk_delete",
                "entity": "session_bookings",
                "entity_ids": ["test-session-1", "test-session-2"],
                "reason": "Testing approval workflow - bulk delete old test sessions"
            }
            
            response = self.session.post(
                f"{self.base_url}/admin/security/approval/request",
                json=request_data,
                headers=admin_headers,
                timeout=10
            )
            
            if response.status_code == 200:
                request_result = response.json()
                request_id = request_result.get('request_id')
                
                if request_id:
                    self.created_ids['approval_requests'].append(request_id)
                    self.log_result("Approval Workflow - Create Request", True, f"Created approval request {request_id}")
                    
                    # Test list approval requests
                    response = self.session.get(
                        f"{self.base_url}/admin/security/approval/requests",
                        headers=super_admin_headers,
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        requests_data = response.json()
                        requests_list = requests_data.get('data', [])
                        
                        if any(req.get('id') == request_id for req in requests_list):
                            self.log_result("Approval Workflow - List Requests", True, f"Found approval request in list")
                            
                            # Test review approval request (as super_admin)
                            review_data = {
                                "status": "approved",
                                "comment": "Approved for testing purposes"
                            }
                            
                            response = self.session.post(
                                f"{self.base_url}/admin/security/approval/requests/{request_id}/review",
                                json=review_data,
                                headers=super_admin_headers,
                                timeout=10
                            )
                            
                            if response.status_code == 200:
                                review_result = response.json()
                                if review_result.get('success'):
                                    self.log_result("Approval Workflow - Review Request", True, f"Successfully approved request {request_id}")
                                else:
                                    self.log_result("Approval Workflow - Review Request", False, "Review operation failed")
                            else:
                                self.log_result("Approval Workflow - Review Request", False, f"HTTP {response.status_code}: {response.text}")
                        else:
                            self.log_result("Approval Workflow - List Requests", False, "Approval request not found in list")
                    else:
                        self.log_result("Approval Workflow - List Requests", False, f"HTTP {response.status_code}: {response.text}")
                else:
                    self.log_result("Approval Workflow - Create Request", False, "No request ID returned")
            else:
                self.log_result("Approval Workflow - Create Request", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Approval Workflow System", False, f"Error: {str(e)}")
            return False
        
        return True
    
    def test_admin_notes_system(self):
        """Test Phase 7.1 - Admin Notes System"""
        print("\n🧪 Testing Phase 7.1 - Admin Notes System...")
        
        if not self.admin_token:
            self.log_result("Admin Notes - Setup", False, "No admin token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            # Create a test session to add notes to
            session_data = {
                "full_name": "Test User for Notes",
                "email": "notes@test.com",
                "phone": "555-0456",
                "age": "25",
                "gender": "female",
                "therapy_type": "group",
                "concerns": ["testing"],
                "current_feelings": "Testing admin notes functionality",
                "previous_therapy": "yes",
                "preferred_time": "afternoon",
                "additional_info": "Test session for admin notes",
                "consent": True
            }
            
            response = self.session.post(f"{self.base_url}/sessions/book", json=session_data, timeout=10)
            if response.status_code == 201:
                session = response.json()
                session_id = session.get('id')
                
                if session_id:
                    # Test add admin note
                    note_data = {
                        "entity": "session_bookings",
                        "entity_id": session_id,
                        "note": "This is a test admin note for session booking. Client seems motivated for therapy.",
                        "is_internal": True
                    }
                    
                    response = self.session.post(
                        f"{self.base_url}/admin/security/notes",
                        json=note_data,
                        headers=headers,
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        note_result = response.json()
                        note_id = note_result.get('note_id')
                        
                        if note_id:
                            self.created_ids['admin_notes'].append(note_id)
                            self.log_result("Admin Notes - Create Note", True, f"Created admin note {note_id}")
                            
                            # Test retrieve notes for session
                            response = self.session.get(
                                f"{self.base_url}/admin/security/notes/session_bookings/{session_id}",
                                headers=headers,
                                timeout=10
                            )
                            
                            if response.status_code == 200:
                                notes_data = response.json()
                                notes_list = notes_data.get('notes', [])
                                
                                if any(note.get('id') == note_id for note in notes_list):
                                    self.log_result("Admin Notes - Retrieve Notes", True, f"Retrieved notes for session {session_id}")
                                else:
                                    self.log_result("Admin Notes - Retrieve Notes", False, "Created note not found in retrieved notes")
                            else:
                                self.log_result("Admin Notes - Retrieve Notes", False, f"HTTP {response.status_code}: {response.text}")
                        else:
                            self.log_result("Admin Notes - Create Note", False, "No note ID returned")
                    else:
                        self.log_result("Admin Notes - Create Note", False, f"HTTP {response.status_code}: {response.text}")
                else:
                    self.log_result("Admin Notes - Create Test Session", False, "No session ID returned")
            else:
                self.log_result("Admin Notes - Create Test Session", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Admin Notes System", False, f"Error: {str(e)}")
            return False
        
        return True
    
    def test_gdpr_compliance_tools(self):
        """Test Phase 7.1 - GDPR Compliance Tools"""
        print("\n🧪 Testing Phase 7.1 - GDPR Compliance Tools...")
        
        if not self.admin_token:
            self.log_result("GDPR Compliance - Setup", False, "No admin token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            # Test get retention policies
            response = self.session.get(
                f"{self.base_url}/admin/security/gdpr/retention-policy",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                policies_data = response.json()
                policies = policies_data.get('retention_policies', [])
                
                expected_entities = [
                    "session_bookings", "events", "event_registrations", "blogs",
                    "careers", "career_applications", "volunteers", "psychologists",
                    "contact_forms", "admin_logs", "admins"
                ]
                
                if len(policies) >= len(expected_entities):
                    # Check if all expected entities have policies
                    policy_entities = [policy.get('entity') for policy in policies]
                    missing_entities = [entity for entity in expected_entities if entity not in policy_entities]
                    
                    if not missing_entities:
                        self.log_result("GDPR Compliance - Get Retention Policies", True, f"Retrieved retention policies for {len(policies)} entities")
                        
                        # Verify retention periods are correct
                        session_policy = next((p for p in policies if p.get('entity') == 'session_bookings'), None)
                        if session_policy and session_policy.get('retention_days') == 730:  # 2 years
                            self.log_result("GDPR Compliance - Verify Retention Periods", True, "Session bookings retention period is correct (730 days)")
                        else:
                            self.log_result("GDPR Compliance - Verify Retention Periods", False, "Session bookings retention period is incorrect")
                    else:
                        self.log_result("GDPR Compliance - Get Retention Policies", False, f"Missing policies for: {missing_entities}")
                else:
                    self.log_result("GDPR Compliance - Get Retention Policies", False, f"Expected {len(expected_entities)}+ policies, got {len(policies)}")
            else:
                self.log_result("GDPR Compliance - Get Retention Policies", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("GDPR Compliance Tools", False, f"Error: {str(e)}")
            return False
        
        return True
    
    def test_mock_2fa_system(self):
        """Test Phase 7.1 - Mock 2FA System"""
        print("\n🧪 Testing Phase 7.1 - Mock 2FA System...")
        
        if not self.admin_token:
            self.log_result("Mock 2FA - Setup", False, "No admin token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            # Test 2FA setup
            setup_data = {
                "email": "admin@acube.test"
            }
            
            response = self.session.post(
                f"{self.base_url}/admin/security/2fa/setup",
                json=setup_data,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                setup_result = response.json()
                mock_otp = setup_result.get('mock_otp')
                
                if mock_otp and setup_result.get('success'):
                    self.log_result("Mock 2FA - Setup", True, f"2FA setup initiated with mock OTP: {mock_otp}")
                    
                    # Test 2FA verification
                    verify_data = {
                        "email": "admin@acube.test",
                        "otp": mock_otp
                    }
                    
                    response = self.session.post(
                        f"{self.base_url}/admin/security/2fa/verify",
                        json=verify_data,
                        headers=headers,
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        verify_result = response.json()
                        if verify_result.get('success'):
                            self.log_result("Mock 2FA - Verify", True, "2FA verification successful")
                            
                            # Test 2FA disable
                            response = self.session.delete(
                                f"{self.base_url}/admin/security/2fa/disable",
                                headers=headers,
                                timeout=10
                            )
                            
                            if response.status_code == 200:
                                disable_result = response.json()
                                if disable_result.get('success'):
                                    self.log_result("Mock 2FA - Disable", True, "2FA disabled successfully")
                                else:
                                    self.log_result("Mock 2FA - Disable", False, "2FA disable failed")
                            else:
                                self.log_result("Mock 2FA - Disable", False, f"HTTP {response.status_code}: {response.text}")
                        else:
                            self.log_result("Mock 2FA - Verify", False, "2FA verification failed")
                    else:
                        self.log_result("Mock 2FA - Verify", False, f"HTTP {response.status_code}: {response.text}")
                else:
                    self.log_result("Mock 2FA - Setup", False, "2FA setup failed or no mock OTP returned")
            else:
                self.log_result("Mock 2FA - Setup", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Mock 2FA System", False, f"Error: {str(e)}")
            return False
        
        return True
    
    def run_phase7_tests(self):
        """Run all Phase 7.1 Advanced Security & Compliance tests"""
        print("🚀 Starting Phase 7.1 Advanced Security & Compliance Tests")
        print(f"🔗 Testing against: {self.base_url}")
        print("=" * 80)
        
        # Test health check first
        if not self.test_health_check():
            print("\n❌ Health check failed. Backend may not be running.")
            return False
        
        # Create admin accounts
        if not self.create_admin_accounts():
            print("\n❌ Failed to create admin accounts.")
            return False
        
        # Login as admin and super admin
        self.login_admin("admin@acube.test", "Admin123!", "admin")
        self.login_admin("superadmin@acube.test", "SuperAdmin123!", "super_admin")
        
        if not self.admin_token or not self.super_admin_token:
            print("\n❌ Failed to login admin accounts.")
            return False
        
        # Run Phase 7.1 tests
        self.test_soft_delete_system()
        self.test_password_rotation_system()
        self.test_feature_toggle_system()
        self.test_approval_workflow_system()
        self.test_admin_notes_system()
        self.test_gdpr_compliance_tools()
        self.test_mock_2fa_system()
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 PHASE 7.1 TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['message']}")
        
        return failed_tests == 0

if __name__ == "__main__":
    tester = BackendTester()
    success = tester.run_phase7_tests()
    sys.exit(0 if success else 1)