#!/usr/bin/env python3
"""
A-Cube Mental Health Platform Backend API Tests - Phase 8.1A & 8.1B
Tests Phase 8.1A (Admin Workflow Automation) and Phase 8.1B (Basic Analytics Dashboard)
"""

import requests
import json
import sys
from datetime import datetime, timedelta
from typing import Dict, Any, List
import bcrypt

# Backend URL from frontend/.env
BASE_URL = "https://cube-solver-25.preview.emergentagent.com/api"

class Phase8Tester:
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.test_results = []
        self.admin_token = None
        self.super_admin_token = None
        self.created_workflow_ids = []
        self.created_execution_ids = []
    
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
    
    # ==========================================
    # PHASE 8.1A - WORKFLOW AUTOMATION TESTS
    # ==========================================
    
    def test_workflow_types_endpoint(self):
        """Test workflow types endpoint"""
        print("\n🧪 Testing Workflow Types Endpoint...")
        
        if not self.admin_token:
            self.log_result("Workflow Types - Setup", False, "No admin token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            response = self.session.get(
                f"{self.base_url}/admin/phase8/workflows/types",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    types_data = data.get('data', {})
                    workflow_types = types_data.get('workflow_types', [])
                    workflow_status = types_data.get('workflow_status', [])
                    step_status = types_data.get('step_status', [])
                    
                    expected_types = ['content_review', 'bulk_approval', 'data_cleanup', 'report_generation', 'scheduled_publish', 'user_onboarding']
                    expected_statuses = ['pending', 'in_progress', 'completed', 'failed', 'cancelled']
                    
                    if all(wtype in workflow_types for wtype in expected_types):
                        self.log_result("Workflow Types - Get Types", True, f"Retrieved {len(workflow_types)} workflow types")
                        
                        if all(status in workflow_status for status in expected_statuses):
                            self.log_result("Workflow Types - Get Status Lists", True, f"Retrieved {len(workflow_status)} workflow statuses")
                            return True
                        else:
                            self.log_result("Workflow Types - Get Status Lists", False, f"Missing expected statuses")
                            return False
                    else:
                        missing_types = [wtype for wtype in expected_types if wtype not in workflow_types]
                        self.log_result("Workflow Types - Get Types", False, f"Missing workflow types: {missing_types}")
                        return False
                else:
                    self.log_result("Workflow Types - Response", False, "API response not successful")
                    return False
            else:
                self.log_result("Workflow Types - HTTP", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Workflow Types", False, f"Error: {str(e)}")
            return False
    
    def test_workflow_template_management(self):
        """Test workflow template CRUD operations"""
        print("\n🧪 Testing Workflow Template Management...")
        
        if not self.admin_token:
            self.log_result("Workflow Templates - Setup", False, "No admin token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            # Test GET workflows (should have 4 default templates)
            response = self.session.get(
                f"{self.base_url}/admin/phase8/workflows",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    workflows = data.get('data', [])
                    if len(workflows) >= 4:
                        self.log_result("Workflow Templates - List Default", True, f"Found {len(workflows)} default workflow templates")
                        
                        # Test CREATE new workflow template
                        new_workflow = {
                            "name": "Test Workflow Template",
                            "description": "A test workflow for automated testing",
                            "workflow_type": "content_review",
                            "steps": [
                                {
                                    "name": "Review Content",
                                    "action": "review_content",
                                    "parameters": {
                                        "entity_type": "blogs",
                                        "status": "pending"
                                    }
                                },
                                {
                                    "name": "Send Notification",
                                    "action": "send_notification",
                                    "parameters": {
                                        "message": "Content review completed"
                                    }
                                }
                            ],
                            "config": {
                                "auto_execute": False,
                                "timeout_minutes": 30
                            }
                        }
                        
                        response = self.session.post(
                            f"{self.base_url}/admin/phase8/workflows",
                            json=new_workflow,
                            headers=headers,
                            timeout=10
                        )
                        
                        if response.status_code == 200:
                            create_data = response.json()
                            if create_data.get('success'):
                                workflow_id = create_data.get('data', {}).get('id')
                                if workflow_id:
                                    self.created_workflow_ids.append(workflow_id)
                                    self.log_result("Workflow Templates - Create", True, f"Created workflow template {workflow_id}")
                                    
                                    # Test UPDATE workflow template
                                    update_data = {
                                        "name": "Updated Test Workflow Template",
                                        "description": "Updated description for testing",
                                        "enabled": True
                                    }
                                    
                                    response = self.session.put(
                                        f"{self.base_url}/admin/phase8/workflows/{workflow_id}",
                                        json=update_data,
                                        headers=headers,
                                        timeout=10
                                    )
                                    
                                    if response.status_code == 200:
                                        update_result = response.json()
                                        if update_result.get('success'):
                                            self.log_result("Workflow Templates - Update", True, f"Updated workflow template {workflow_id}")
                                            return True
                                        else:
                                            self.log_result("Workflow Templates - Update", False, "Update operation failed")
                                            return False
                                    else:
                                        self.log_result("Workflow Templates - Update", False, f"HTTP {response.status_code}: {response.text}")
                                        return False
                                else:
                                    self.log_result("Workflow Templates - Create", False, "No workflow ID returned")
                                    return False
                            else:
                                self.log_result("Workflow Templates - Create", False, "Create operation failed")
                                return False
                        else:
                            self.log_result("Workflow Templates - Create", False, f"HTTP {response.status_code}: {response.text}")
                            return False
                    else:
                        self.log_result("Workflow Templates - List Default", False, f"Expected 4+ templates, found {len(workflows)}")
                        return False
                else:
                    self.log_result("Workflow Templates - List", False, "API response not successful")
                    return False
            else:
                self.log_result("Workflow Templates - List", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Workflow Template Management", False, f"Error: {str(e)}")
            return False
    
    def test_workflow_execution_engine(self):
        """Test workflow execution functionality"""
        print("\n🧪 Testing Workflow Execution Engine...")
        
        if not self.admin_token:
            self.log_result("Workflow Execution - Setup", False, "No admin token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            # First, get available workflows
            response = self.session.get(
                f"{self.base_url}/admin/phase8/workflows",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                workflows = data.get('data', [])
                
                if workflows:
                    # Find a suitable workflow to execute (prefer Content Review Workflow)
                    test_workflow = None
                    for workflow in workflows:
                        if workflow.get('name') == 'Content Review Workflow' or workflow.get('workflow_type') == 'content_review':
                            test_workflow = workflow
                            break
                    
                    if not test_workflow:
                        test_workflow = workflows[0]  # Use first available workflow
                    
                    workflow_id = test_workflow.get('id')
                    
                    if workflow_id:
                        # Test EXECUTE workflow
                        execute_data = {
                            "input_data": {
                                "test_execution": True,
                                "entity_ids": ["test-blog-1", "test-blog-2"]
                            }
                        }
                        
                        response = self.session.post(
                            f"{self.base_url}/admin/phase8/workflows/{workflow_id}/execute",
                            json=execute_data,
                            headers=headers,
                            timeout=15
                        )
                        
                        if response.status_code == 200:
                            exec_data = response.json()
                            if exec_data.get('success'):
                                execution = exec_data.get('data', {})
                                execution_id = execution.get('id')
                                
                                if execution_id:
                                    self.created_execution_ids.append(execution_id)
                                    status = execution.get('status')
                                    steps_completed = execution.get('steps_completed', 0)
                                    
                                    self.log_result("Workflow Execution - Execute", True, f"Executed workflow {workflow_id}, status: {status}, steps completed: {steps_completed}")
                                    
                                    # Test GET execution details
                                    response = self.session.get(
                                        f"{self.base_url}/admin/phase8/workflows/executions/{execution_id}",
                                        headers=headers,
                                        timeout=10
                                    )
                                    
                                    if response.status_code == 200:
                                        details_data = response.json()
                                        if details_data.get('success'):
                                            execution_details = details_data.get('data', {})
                                            step_results = execution_details.get('step_results', [])
                                            
                                            self.log_result("Workflow Execution - Get Details", True, f"Retrieved execution details with {len(step_results)} step results")
                                            
                                            # Test GET workflow executions history
                                            response = self.session.get(
                                                f"{self.base_url}/admin/phase8/workflows/{workflow_id}/executions",
                                                headers=headers,
                                                timeout=10
                                            )
                                            
                                            if response.status_code == 200:
                                                history_data = response.json()
                                                if history_data.get('success'):
                                                    executions = history_data.get('data', [])
                                                    if any(exec.get('id') == execution_id for exec in executions):
                                                        self.log_result("Workflow Execution - Get History", True, f"Found execution in history list")
                                                        
                                                        # Test GET all executions
                                                        response = self.session.get(
                                                            f"{self.base_url}/admin/phase8/workflows/executions/all",
                                                            headers=headers,
                                                            timeout=10
                                                        )
                                                        
                                                        if response.status_code == 200:
                                                            all_exec_data = response.json()
                                                            if all_exec_data.get('success'):
                                                                all_executions = all_exec_data.get('data', [])
                                                                if any(exec.get('id') == execution_id for exec in all_executions):
                                                                    self.log_result("Workflow Execution - Get All Executions", True, f"Found execution in all executions list")
                                                                    return True
                                                                else:
                                                                    self.log_result("Workflow Execution - Get All Executions", False, "Execution not found in all executions list")
                                                                    return False
                                                            else:
                                                                self.log_result("Workflow Execution - Get All Executions", False, "API response not successful")
                                                                return False
                                                        else:
                                                            self.log_result("Workflow Execution - Get All Executions", False, f"HTTP {response.status_code}: {response.text}")
                                                            return False
                                                    else:
                                                        self.log_result("Workflow Execution - Get History", False, "Execution not found in history")
                                                        return False
                                                else:
                                                    self.log_result("Workflow Execution - Get History", False, "API response not successful")
                                                    return False
                                            else:
                                                self.log_result("Workflow Execution - Get History", False, f"HTTP {response.status_code}: {response.text}")
                                                return False
                                        else:
                                            self.log_result("Workflow Execution - Get Details", False, "API response not successful")
                                            return False
                                    else:
                                        self.log_result("Workflow Execution - Get Details", False, f"HTTP {response.status_code}: {response.text}")
                                        return False
                                else:
                                    self.log_result("Workflow Execution - Execute", False, "No execution ID returned")
                                    return False
                            else:
                                self.log_result("Workflow Execution - Execute", False, "Execution failed")
                                return False
                        else:
                            self.log_result("Workflow Execution - Execute", False, f"HTTP {response.status_code}: {response.text}")
                            return False
                    else:
                        self.log_result("Workflow Execution - Find Workflow", False, "No workflow ID available")
                        return False
                else:
                    self.log_result("Workflow Execution - Get Workflows", False, "No workflows available for testing")
                    return False
            else:
                self.log_result("Workflow Execution - Get Workflows", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Workflow Execution Engine", False, f"Error: {str(e)}")
            return False
    
    # ==========================================
    # PHASE 8.1B - ANALYTICS DASHBOARD TESTS
    # ==========================================
    
    def test_analytics_dashboard_overview(self):
        """Test analytics dashboard overview endpoint"""
        print("\n🧪 Testing Analytics Dashboard Overview...")
        
        if not self.admin_token:
            self.log_result("Analytics Dashboard - Setup", False, "No admin token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            # Test dashboard overview (default last 30 days)
            response = self.session.get(
                f"{self.base_url}/admin/phase8/analytics/dashboard",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    dashboard_data = data.get('data', {})
                    overview = dashboard_data.get('overview', {})
                    
                    # Check required overview fields
                    required_fields = ['total_sessions', 'total_events', 'total_blogs', 'total_volunteers', 'total_contacts']
                    if all(field in overview for field in required_fields):
                        self.log_result("Analytics Dashboard - Overview Fields", True, f"All overview fields present")
                        
                        # Check detailed sections
                        required_sections = ['sessions', 'events', 'blogs', 'volunteers', 'contacts']
                        if all(section in dashboard_data for section in required_sections):
                            self.log_result("Analytics Dashboard - Detailed Sections", True, f"All detailed sections present")
                            
                            # Test with custom date range
                            start_date = (datetime.now() - timedelta(days=7)).isoformat()
                            end_date = datetime.now().isoformat()
                            
                            response = self.session.get(
                                f"{self.base_url}/admin/phase8/analytics/dashboard?start_date={start_date}&end_date={end_date}",
                                headers=headers,
                                timeout=10
                            )
                            
                            if response.status_code == 200:
                                custom_data = response.json()
                                if custom_data.get('success'):
                                    self.log_result("Analytics Dashboard - Custom Date Range", True, "Dashboard works with custom date range")
                                    return True
                                else:
                                    self.log_result("Analytics Dashboard - Custom Date Range", False, "Custom date range request failed")
                                    return False
                            else:
                                self.log_result("Analytics Dashboard - Custom Date Range", False, f"HTTP {response.status_code}: {response.text}")
                                return False
                        else:
                            missing_sections = [section for section in required_sections if section not in dashboard_data]
                            self.log_result("Analytics Dashboard - Detailed Sections", False, f"Missing sections: {missing_sections}")
                            return False
                    else:
                        missing_fields = [field for field in required_fields if field not in overview]
                        self.log_result("Analytics Dashboard - Overview Fields", False, f"Missing fields: {missing_fields}")
                        return False
                else:
                    self.log_result("Analytics Dashboard - Response", False, "API response not successful")
                    return False
            else:
                self.log_result("Analytics Dashboard - HTTP", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Analytics Dashboard Overview", False, f"Error: {str(e)}")
            return False
    
    def test_individual_analytics_endpoints(self):
        """Test individual analytics endpoints"""
        print("\n🧪 Testing Individual Analytics Endpoints...")
        
        if not self.admin_token:
            self.log_result("Individual Analytics - Setup", False, "No admin token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        analytics_endpoints = [
            ("sessions", ["total_sessions", "avg_sessions_per_day", "status_breakdown"]),
            ("events", ["total_events", "active_events", "total_registrations", "top_events"]),
            ("blogs", ["total_blogs", "published_blogs", "featured_blogs", "category_breakdown"]),
            ("volunteers", ["total_applications", "status_breakdown", "applications_over_time"]),
            ("contacts", ["total_contacts", "resolved_contacts", "response_rate", "status_breakdown"])
        ]
        
        all_passed = True
        
        try:
            for endpoint, required_fields in analytics_endpoints:
                response = self.session.get(
                    f"{self.base_url}/admin/phase8/analytics/{endpoint}",
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success'):
                        analytics_data = data.get('data', {})
                        
                        if all(field in analytics_data for field in required_fields):
                            self.log_result(f"Analytics - {endpoint.title()}", True, f"All required fields present")
                        else:
                            missing_fields = [field for field in required_fields if field not in analytics_data]
                            self.log_result(f"Analytics - {endpoint.title()}", False, f"Missing fields: {missing_fields}")
                            all_passed = False
                    else:
                        self.log_result(f"Analytics - {endpoint.title()}", False, "API response not successful")
                        all_passed = False
                else:
                    self.log_result(f"Analytics - {endpoint.title()}", False, f"HTTP {response.status_code}: {response.text}")
                    all_passed = False
            
            return all_passed
                
        except Exception as e:
            self.log_result("Individual Analytics Endpoints", False, f"Error: {str(e)}")
            return False
    
    def test_analytics_csv_export(self):
        """Test analytics CSV export functionality"""
        print("\n🧪 Testing Analytics CSV Export...")
        
        if not self.admin_token:
            self.log_result("Analytics CSV Export - Setup", False, "No admin token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        export_types = ["sessions", "events", "blogs", "volunteers", "contacts"]
        
        try:
            # Test CSV export for sessions (most likely to have data)
            response = self.session.get(
                f"{self.base_url}/admin/phase8/analytics/export/sessions",
                headers=headers,
                timeout=15
            )
            
            if response.status_code == 200:
                # Check if response is CSV format
                content_type = response.headers.get('content-type', '')
                if 'text/csv' in content_type:
                    csv_content = response.text
                    if csv_content and len(csv_content) > 0:
                        # Check if it has CSV headers
                        lines = csv_content.split('\n')
                        if len(lines) > 0 and 'id' in lines[0]:
                            self.log_result("Analytics CSV Export - Sessions", True, f"CSV export successful, {len(lines)} lines")
                            
                            # Test export with custom date range
                            start_date = (datetime.now() - timedelta(days=7)).isoformat()
                            end_date = datetime.now().isoformat()
                            
                            response = self.session.get(
                                f"{self.base_url}/admin/phase8/analytics/export/events?start_date={start_date}&end_date={end_date}",
                                headers=headers,
                                timeout=15
                            )
                            
                            if response.status_code == 200:
                                self.log_result("Analytics CSV Export - Custom Date Range", True, "CSV export with custom date range successful")
                                
                                # Test invalid export type
                                response = self.session.get(
                                    f"{self.base_url}/admin/phase8/analytics/export/invalid_type",
                                    headers=headers,
                                    timeout=10
                                )
                                
                                if response.status_code == 400:
                                    self.log_result("Analytics CSV Export - Invalid Type", True, "Properly rejected invalid export type")
                                    return True
                                else:
                                    self.log_result("Analytics CSV Export - Invalid Type", False, f"Expected 400, got {response.status_code}")
                                    return False
                            else:
                                self.log_result("Analytics CSV Export - Custom Date Range", False, f"HTTP {response.status_code}: {response.text}")
                                return False
                        else:
                            self.log_result("Analytics CSV Export - Sessions", False, "CSV content doesn't have expected headers")
                            return False
                    else:
                        self.log_result("Analytics CSV Export - Sessions", True, "CSV export successful (empty data)")
                        return True
                else:
                    self.log_result("Analytics CSV Export - Sessions", False, f"Expected CSV content-type, got {content_type}")
                    return False
            else:
                self.log_result("Analytics CSV Export - Sessions", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Analytics CSV Export", False, f"Error: {str(e)}")
            return False
    
    def cleanup_test_data(self):
        """Clean up created test data"""
        print("\n🧹 Cleaning up test data...")
        
        if not self.admin_token:
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Delete created workflows
        for workflow_id in self.created_workflow_ids:
            try:
                response = self.session.delete(
                    f"{self.base_url}/admin/phase8/workflows/{workflow_id}",
                    headers=headers,
                    timeout=10
                )
                if response.status_code == 200:
                    self.log_result("Cleanup - Delete Workflow", True, f"Deleted workflow {workflow_id}")
                else:
                    self.log_result("Cleanup - Delete Workflow", False, f"Failed to delete workflow {workflow_id}")
            except Exception as e:
                self.log_result("Cleanup - Delete Workflow", False, f"Error deleting workflow {workflow_id}: {str(e)}")
    
    def run_phase8_tests(self):
        """Run all Phase 8.1A and 8.1B tests"""
        print("🚀 Starting Phase 8.1A & 8.1B Tests")
        print("Phase 8.1A: Admin Workflow Automation")
        print("Phase 8.1B: Basic Analytics Dashboard")
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
        
        if not self.admin_token:
            print("\n❌ Failed to login admin accounts.")
            return False
        
        # Run Phase 8.1A tests (Workflow Automation)
        print("\n" + "=" * 50)
        print("🤖 PHASE 8.1A - WORKFLOW AUTOMATION TESTS")
        print("=" * 50)
        
        self.test_workflow_types_endpoint()
        self.test_workflow_template_management()
        self.test_workflow_execution_engine()
        
        # Run Phase 8.1B tests (Analytics Dashboard)
        print("\n" + "=" * 50)
        print("📊 PHASE 8.1B - ANALYTICS DASHBOARD TESTS")
        print("=" * 50)
        
        self.test_analytics_dashboard_overview()
        self.test_individual_analytics_endpoints()
        self.test_analytics_csv_export()
        
        # Cleanup
        self.cleanup_test_data()
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 PHASE 8.1A & 8.1B TEST SUMMARY")
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
    tester = Phase8Tester()
    success = tester.run_phase8_tests()
    sys.exit(0 if success else 1)