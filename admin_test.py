#!/usr/bin/env python3
"""
A-Cube Mental Health Platform Admin Panel API Tests
Tests all Phase 4 CRUD endpoints for the admin panel
"""

import requests
import json
import sys
import io
from datetime import datetime
from typing import Dict, Any, List

# Backend URL from frontend/.env
BASE_URL = "https://rubiks-hub-2.preview.emergentagent.com/api"

class AdminTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.test_results = []
        self.admin_token = None
        self.created_ids = {
            'sessions': [],
            'events': [],
            'blogs': [],
            'psychologists': [],
            'jobs': [],
            'volunteers': [],
            'contacts': []
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
    
    def admin_login(self):
        """Login as admin and get JWT token"""
        print("\n🔐 Testing Admin Authentication...")
        
        login_data = {
            "email": "admin@acube.com",
            "password": "Admin@2025!"
        }
        
        try:
            response = self.session.post(f"{self.base_url}/admin/auth/login", json=login_data, timeout=10)
            if response.status_code == 200:
                token_data = response.json()
                self.admin_token = token_data.get('access_token')
                if self.admin_token:
                    # Set authorization header for all future requests
                    self.session.headers.update({'Authorization': f'Bearer {self.admin_token}'})
                    self.log_result("Admin Login", True, "Successfully logged in as admin")
                    return True
                else:
                    self.log_result("Admin Login", False, "No access token in response")
                    return False
            else:
                self.log_result("Admin Login", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_result("Admin Login", False, f"Error: {str(e)}")
            return False
    
    def test_sessions_crud(self):
        """Test Sessions CRUD endpoints"""
        print("\n🧪 Testing Sessions CRUD...")
        
        # Test GET /api/admin/sessions with pagination
        try:
            response = self.session.get(f"{self.base_url}/admin/sessions", 
                                      params={"page": 1, "limit": 10}, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and 'pagination' in data:
                    self.log_result("Sessions - GET with pagination", True, 
                                  f"Retrieved {len(data['data'])} sessions, total: {data['pagination']['total']}")
                else:
                    self.log_result("Sessions - GET with pagination", False, "Invalid response format")
            else:
                self.log_result("Sessions - GET with pagination", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_result("Sessions - GET with pagination", False, f"Error: {str(e)}")
        
        # Test GET /api/admin/sessions with status filter
        try:
            response = self.session.get(f"{self.base_url}/admin/sessions", 
                                      params={"status_filter": "pending"}, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if 'data' in data:
                    self.log_result("Sessions - GET with status filter", True, 
                                  f"Retrieved {len(data['data'])} pending sessions")
                else:
                    self.log_result("Sessions - GET with status filter", False, "Invalid response format")
            else:
                self.log_result("Sessions - GET with status filter", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_result("Sessions - GET with status filter", False, f"Error: {str(e)}")
        
        # Test POST /api/admin/sessions (create new session)
        session_data = {
            "full_name": "Admin Test User",
            "email": "admintest@example.com",
            "phone": "555-012-3456",
            "age": "30",
            "gender": "non-binary",
            "therapy_type": "group",
            "concerns": ["depression", "anxiety"],
            "current_feelings": "Testing admin session creation functionality through the admin panel interface",
            "previous_therapy": "no",
            "preferred_time": "mornings",
            "additional_info": "Created via admin panel test",
            "consent": True
        }
        
        try:
            response = self.session.post(f"{self.base_url}/admin/sessions", json=session_data, timeout=10)
            if response.status_code == 200:
                result = response.json()
                if 'session' in result and 'id' in result['session']:
                    session_id = result['session']['id']
                    self.created_ids['sessions'].append(session_id)
                    self.log_result("Sessions - POST (create)", True, f"Created session with ID: {session_id}")
                else:
                    self.log_result("Sessions - POST (create)", False, "No session ID in response")
            else:
                self.log_result("Sessions - POST (create)", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_result("Sessions - POST (create)", False, f"Error: {str(e)}")
        
        # Test PUT /api/admin/sessions/{id} (update session)
        if self.created_ids['sessions']:
            session_id = self.created_ids['sessions'][0]
            update_data = {
                "status": "confirmed",
                "additional_info": "Updated via admin panel test"
            }
            
            try:
                response = self.session.put(f"{self.base_url}/admin/sessions/{session_id}", 
                                          json=update_data, timeout=10)
                if response.status_code == 200:
                    result = response.json()
                    if 'message' in result:
                        self.log_result("Sessions - PUT (update)", True, f"Updated session {session_id}")
                    else:
                        self.log_result("Sessions - PUT (update)", False, "No message in response")
                else:
                    self.log_result("Sessions - PUT (update)", False, f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_result("Sessions - PUT (update)", False, f"Error: {str(e)}")
            
            # Test DELETE /api/admin/sessions/{id} (delete session)
            try:
                response = self.session.delete(f"{self.base_url}/admin/sessions/{session_id}", timeout=10)
                if response.status_code == 200:
                    result = response.json()
                    if 'message' in result:
                        self.log_result("Sessions - DELETE", True, f"Deleted session {session_id}")
                    else:
                        self.log_result("Sessions - DELETE", False, "No message in response")
                else:
                    self.log_result("Sessions - DELETE", False, f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_result("Sessions - DELETE", False, f"Error: {str(e)}")
    
    def test_events_crud(self):
        """Test Events CRUD endpoints"""
        print("\n🧪 Testing Events CRUD...")
        
        # Test GET /api/admin/events with pagination
        try:
            response = self.session.get(f"{self.base_url}/admin/events", 
                                      params={"page": 1, "limit": 10}, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and 'pagination' in data:
                    self.log_result("Events - GET with pagination", True, 
                                  f"Retrieved {len(data['data'])} events, total: {data['pagination']['total']}")
                else:
                    self.log_result("Events - GET with pagination", False, "Invalid response format")
            else:
                self.log_result("Events - GET with pagination", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_result("Events - GET with pagination", False, f"Error: {str(e)}")
        
        # Test POST /api/admin/events (create event)
        event_data = {
            "title": "Admin Test Workshop",
            "description": "A comprehensive test workshop created via admin panel to verify event creation functionality",
            "event_type": "workshop",
            "date": "2025-02-15",
            "time": "14:00",
            "price": "Free",
            "is_paid": False,
            "schedule": "One-time",
            "features": ["Interactive sessions", "Q&A", "Networking"]
        }
        
        try:
            response = self.session.post(f"{self.base_url}/admin/events", json=event_data, timeout=10)
            if response.status_code == 200:
                result = response.json()
                if 'event' in result and 'id' in result['event']:
                    event_id = result['event']['id']
                    self.created_ids['events'].append(event_id)
                    self.log_result("Events - POST (create)", True, f"Created event with ID: {event_id}")
                else:
                    self.log_result("Events - POST (create)", False, "No event ID in response")
            else:
                self.log_result("Events - POST (create)", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_result("Events - POST (create)", False, f"Error: {str(e)}")
        
        # Test PUT /api/admin/events/{id} (update event)
        if self.created_ids['events']:
            event_id = self.created_ids['events'][0]
            update_data = {
                "title": "Updated Admin Test Workshop",
                "max_participants": 30,
                "is_active": False
            }
            
            try:
                response = self.session.put(f"{self.base_url}/admin/events/{event_id}", 
                                          json=update_data, timeout=10)
                if response.status_code == 200:
                    result = response.json()
                    if 'message' in result:
                        self.log_result("Events - PUT (update)", True, f"Updated event {event_id}")
                    else:
                        self.log_result("Events - PUT (update)", False, "No message in response")
                else:
                    self.log_result("Events - PUT (update)", False, f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_result("Events - PUT (update)", False, f"Error: {str(e)}")
            
            # Test DELETE /api/admin/events/{id} (delete event)
            try:
                response = self.session.delete(f"{self.base_url}/admin/events/{event_id}", timeout=10)
                if response.status_code == 200:
                    result = response.json()
                    if 'message' in result:
                        self.log_result("Events - DELETE", True, f"Deleted event {event_id}")
                    else:
                        self.log_result("Events - DELETE", False, "No message in response")
                else:
                    self.log_result("Events - DELETE", False, f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_result("Events - DELETE", False, f"Error: {str(e)}")
    
    def test_blogs_crud(self):
        """Test Blogs CRUD endpoints"""
        print("\n🧪 Testing Blogs CRUD...")
        
        # Test GET /api/admin/blogs with pagination and category filter
        try:
            response = self.session.get(f"{self.base_url}/admin/blogs", 
                                      params={"page": 1, "limit": 10, "category": "Wellness"}, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and 'pagination' in data:
                    self.log_result("Blogs - GET with pagination and filter", True, 
                                  f"Retrieved {len(data['data'])} wellness blogs, total: {data['pagination']['total']}")
                else:
                    self.log_result("Blogs - GET with pagination and filter", False, "Invalid response format")
            else:
                self.log_result("Blogs - GET with pagination and filter", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_result("Blogs - GET with pagination and filter", False, f"Error: {str(e)}")
        
        # Test POST /api/admin/blogs (create blog)
        blog_data = {
            "title": "Admin Test Blog Post",
            "excerpt": "This is a test blog post excerpt created via the admin panel for comprehensive testing purposes.",
            "content": "This is a comprehensive test blog post created via the admin panel for testing purposes. It contains detailed information about the testing process and validates that the blog creation functionality works correctly through the administrative interface. The content is sufficiently long to meet the minimum character requirements.",
            "author": "Admin Tester",
            "category": "Testing",
            "read_time": "5 min",
            "featured": False
        }
        
        try:
            response = self.session.post(f"{self.base_url}/admin/blogs", json=blog_data, timeout=10)
            if response.status_code == 200:
                result = response.json()
                if 'blog' in result and 'id' in result['blog']:
                    blog_id = result['blog']['id']
                    self.created_ids['blogs'].append(blog_id)
                    self.log_result("Blogs - POST (create)", True, f"Created blog with ID: {blog_id}")
                else:
                    self.log_result("Blogs - POST (create)", False, "No blog ID in response")
            else:
                self.log_result("Blogs - POST (create)", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_result("Blogs - POST (create)", False, f"Error: {str(e)}")
        
        # Test PUT /api/admin/blogs/{id} (update blog)
        if self.created_ids['blogs']:
            blog_id = self.created_ids['blogs'][0]
            update_data = {
                "title": "Updated Admin Test Blog Post",
                "featured": True,
                "is_published": False
            }
            
            try:
                response = self.session.put(f"{self.base_url}/admin/blogs/{blog_id}", 
                                          json=update_data, timeout=10)
                if response.status_code == 200:
                    result = response.json()
                    if 'message' in result:
                        self.log_result("Blogs - PUT (update)", True, f"Updated blog {blog_id}")
                    else:
                        self.log_result("Blogs - PUT (update)", False, "No message in response")
                else:
                    self.log_result("Blogs - PUT (update)", False, f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_result("Blogs - PUT (update)", False, f"Error: {str(e)}")
            
            # Test DELETE /api/admin/blogs/{id} (delete blog)
            try:
                response = self.session.delete(f"{self.base_url}/admin/blogs/{blog_id}", timeout=10)
                if response.status_code == 200:
                    result = response.json()
                    if 'message' in result:
                        self.log_result("Blogs - DELETE", True, f"Deleted blog {blog_id}")
                    else:
                        self.log_result("Blogs - DELETE", False, "No message in response")
                else:
                    self.log_result("Blogs - DELETE", False, f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_result("Blogs - DELETE", False, f"Error: {str(e)}")
    
    def test_psychologists_crud(self):
        """Test Psychologists CRUD endpoints"""
        print("\n🧪 Testing Psychologists CRUD...")
        
        # Test GET /api/admin/psychologists with pagination
        try:
            response = self.session.get(f"{self.base_url}/admin/psychologists", 
                                      params={"page": 1, "limit": 10}, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and 'pagination' in data:
                    self.log_result("Psychologists - GET with pagination", True, 
                                  f"Retrieved {len(data['data'])} psychologists, total: {data['pagination']['total']}")
                else:
                    self.log_result("Psychologists - GET with pagination", False, "Invalid response format")
            else:
                self.log_result("Psychologists - GET with pagination", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_result("Psychologists - GET with pagination", False, f"Error: {str(e)}")
        
        # Test POST /api/admin/psychologists (create psychologist)
        psychologist_data = {
            "full_name": "Dr. Admin Test",
            "email": "dr.admintest@acube.com",
            "phone": "555-098-7654",
            "license_number": "PSY123456",
            "specializations": ["Cognitive Behavioral Therapy", "Anxiety Disorders"],
            "years_of_experience": 5,
            "education": ["PhD in Clinical Psychology", "Masters in Counseling"],
            "bio": "Test psychologist profile created via admin panel for comprehensive testing of the psychologist management system",
            "session_rate": 150.0
        }
        
        try:
            response = self.session.post(f"{self.base_url}/admin/psychologists", json=psychologist_data, timeout=10)
            if response.status_code == 200:
                result = response.json()
                if 'psychologist' in result and 'id' in result['psychologist']:
                    psychologist_id = result['psychologist']['id']
                    self.created_ids['psychologists'].append(psychologist_id)
                    self.log_result("Psychologists - POST (create)", True, f"Created psychologist with ID: {psychologist_id}")
                else:
                    self.log_result("Psychologists - POST (create)", False, "No psychologist ID in response")
            else:
                self.log_result("Psychologists - POST (create)", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_result("Psychologists - POST (create)", False, f"Error: {str(e)}")
        
        # Test PUT /api/admin/psychologists/{id} (update psychologist)
        if self.created_ids['psychologists']:
            psychologist_id = self.created_ids['psychologists'][0]
            update_data = {
                "years_of_experience": 7,
                "bio": "Updated test psychologist profile with more experience"
            }
            
            try:
                response = self.session.put(f"{self.base_url}/admin/psychologists/{psychologist_id}", 
                                          json=update_data, timeout=10)
                if response.status_code == 200:
                    result = response.json()
                    if 'message' in result:
                        self.log_result("Psychologists - PUT (update)", True, f"Updated psychologist {psychologist_id}")
                    else:
                        self.log_result("Psychologists - PUT (update)", False, "No message in response")
                else:
                    self.log_result("Psychologists - PUT (update)", False, f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_result("Psychologists - PUT (update)", False, f"Error: {str(e)}")
            
            # Test DELETE /api/admin/psychologists/{id} (delete psychologist)
            try:
                response = self.session.delete(f"{self.base_url}/admin/psychologists/{psychologist_id}", timeout=10)
                if response.status_code == 200:
                    result = response.json()
                    if 'message' in result:
                        self.log_result("Psychologists - DELETE", True, f"Deleted psychologist {psychologist_id}")
                    else:
                        self.log_result("Psychologists - DELETE", False, "No message in response")
                else:
                    self.log_result("Psychologists - DELETE", False, f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_result("Psychologists - DELETE", False, f"Error: {str(e)}")
    
    def test_jobs_crud(self):
        """Test Jobs CRUD endpoints"""
        print("\n🧪 Testing Jobs CRUD...")
        
        # Test GET /api/admin/jobs with pagination
        try:
            response = self.session.get(f"{self.base_url}/admin/jobs", 
                                      params={"page": 1, "limit": 10}, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and 'pagination' in data:
                    self.log_result("Jobs - GET with pagination", True, 
                                  f"Retrieved {len(data['data'])} jobs, total: {data['pagination']['total']}")
                else:
                    self.log_result("Jobs - GET with pagination", False, "Invalid response format")
            else:
                self.log_result("Jobs - GET with pagination", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_result("Jobs - GET with pagination", False, f"Error: {str(e)}")
        
        # Test POST /api/admin/jobs (create job)
        job_data = {
            "title": "Admin Test Position",
            "department": "Mental Health Services",
            "location": "Remote",
            "employment_type": "full-time",
            "description": "Test job posting created via admin panel for comprehensive testing purposes",
            "responsibilities": ["Test responsibility 1", "Test responsibility 2"],
            "qualifications": ["Test qualification 1", "Test qualification 2"],
            "benefits": ["Health insurance", "Remote work"]
        }
        
        try:
            response = self.session.post(f"{self.base_url}/admin/jobs", json=job_data, timeout=10)
            if response.status_code == 200:
                result = response.json()
                if 'job' in result and 'id' in result['job']:
                    job_id = result['job']['id']
                    self.created_ids['jobs'].append(job_id)
                    self.log_result("Jobs - POST (create)", True, f"Created job with ID: {job_id}")
                else:
                    self.log_result("Jobs - POST (create)", False, "No job ID in response")
            else:
                self.log_result("Jobs - POST (create)", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_result("Jobs - POST (create)", False, f"Error: {str(e)}")
        
        # Test PUT /api/admin/jobs/{id} (update job)
        if self.created_ids['jobs']:
            job_id = self.created_ids['jobs'][0]
            update_data = {
                "title": "Updated Admin Test Position",
                "location": "Hybrid"
            }
            
            try:
                response = self.session.put(f"{self.base_url}/admin/jobs/{job_id}", 
                                          json=update_data, timeout=10)
                if response.status_code == 200:
                    result = response.json()
                    if 'message' in result:
                        self.log_result("Jobs - PUT (update)", True, f"Updated job {job_id}")
                    else:
                        self.log_result("Jobs - PUT (update)", False, "No message in response")
                else:
                    self.log_result("Jobs - PUT (update)", False, f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_result("Jobs - PUT (update)", False, f"Error: {str(e)}")
            
            # Test DELETE /api/admin/jobs/{id} (delete job)
            try:
                response = self.session.delete(f"{self.base_url}/admin/jobs/{job_id}", timeout=10)
                if response.status_code == 200:
                    result = response.json()
                    if 'message' in result:
                        self.log_result("Jobs - DELETE", True, f"Deleted job {job_id}")
                    else:
                        self.log_result("Jobs - DELETE", False, "No message in response")
                else:
                    self.log_result("Jobs - DELETE", False, f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_result("Jobs - DELETE", False, f"Error: {str(e)}")
    
    def test_volunteers_crud(self):
        """Test Volunteers CRUD endpoints"""
        print("\n🧪 Testing Volunteers CRUD...")
        
        # Test GET /api/admin/volunteers with pagination
        try:
            response = self.session.get(f"{self.base_url}/admin/volunteers", 
                                      params={"page": 1, "limit": 10}, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and 'pagination' in data:
                    self.log_result("Volunteers - GET with pagination", True, 
                                  f"Retrieved {len(data['data'])} volunteers, total: {data['pagination']['total']}")
                    
                    # If we have volunteers, test update on the first one
                    if data['data']:
                        volunteer_id = data['data'][0].get('id')
                        if volunteer_id:
                            # Test PUT /api/admin/volunteers/{id} (update volunteer)
                            update_data = {
                                "status": "approved"
                            }
                            
                            try:
                                response = self.session.put(f"{self.base_url}/admin/volunteers/{volunteer_id}", 
                                                          json=update_data, timeout=10)
                                if response.status_code == 200:
                                    result = response.json()
                                    if 'message' in result:
                                        self.log_result("Volunteers - PUT (update)", True, f"Updated volunteer {volunteer_id}")
                                    else:
                                        self.log_result("Volunteers - PUT (update)", False, "No message in response")
                                else:
                                    self.log_result("Volunteers - PUT (update)", False, f"HTTP {response.status_code}: {response.text}")
                            except Exception as e:
                                self.log_result("Volunteers - PUT (update)", False, f"Error: {str(e)}")
                            
                            # Test DELETE /api/admin/volunteers/{id} (delete volunteer)
                            try:
                                response = self.session.delete(f"{self.base_url}/admin/volunteers/{volunteer_id}", timeout=10)
                                if response.status_code == 200:
                                    result = response.json()
                                    if 'message' in result:
                                        self.log_result("Volunteers - DELETE", True, f"Deleted volunteer {volunteer_id}")
                                    else:
                                        self.log_result("Volunteers - DELETE", False, "No message in response")
                                else:
                                    self.log_result("Volunteers - DELETE", False, f"HTTP {response.status_code}: {response.text}")
                            except Exception as e:
                                self.log_result("Volunteers - DELETE", False, f"Error: {str(e)}")
                else:
                    self.log_result("Volunteers - GET with pagination", False, "Invalid response format")
            else:
                self.log_result("Volunteers - GET with pagination", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_result("Volunteers - GET with pagination", False, f"Error: {str(e)}")
    
    def test_contacts_crud(self):
        """Test Contacts CRUD endpoints"""
        print("\n🧪 Testing Contacts CRUD...")
        
        # Test GET /api/admin/contacts with pagination
        try:
            response = self.session.get(f"{self.base_url}/admin/contacts", 
                                      params={"page": 1, "limit": 10}, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and 'pagination' in data:
                    self.log_result("Contacts - GET with pagination", True, 
                                  f"Retrieved {len(data['data'])} contacts, total: {data['pagination']['total']}")
                    
                    # If we have contacts, test update on the first one
                    if data['data']:
                        contact_id = data['data'][0].get('id')
                        if contact_id:
                            # Test PUT /api/admin/contacts/{id} (update contact)
                            update_data = {
                                "status": "read"
                            }
                            
                            try:
                                response = self.session.put(f"{self.base_url}/admin/contacts/{contact_id}", 
                                                          json=update_data, timeout=10)
                                if response.status_code == 200:
                                    result = response.json()
                                    if 'message' in result:
                                        self.log_result("Contacts - PUT (update)", True, f"Updated contact {contact_id}")
                                    else:
                                        self.log_result("Contacts - PUT (update)", False, "No message in response")
                                else:
                                    self.log_result("Contacts - PUT (update)", False, f"HTTP {response.status_code}: {response.text}")
                            except Exception as e:
                                self.log_result("Contacts - PUT (update)", False, f"Error: {str(e)}")
                            
                            # Test DELETE /api/admin/contacts/{id} (delete contact)
                            try:
                                response = self.session.delete(f"{self.base_url}/admin/contacts/{contact_id}", timeout=10)
                                if response.status_code == 200:
                                    result = response.json()
                                    if 'message' in result:
                                        self.log_result("Contacts - DELETE", True, f"Deleted contact {contact_id}")
                                    else:
                                        self.log_result("Contacts - DELETE", False, "No message in response")
                                else:
                                    self.log_result("Contacts - DELETE", False, f"HTTP {response.status_code}: {response.text}")
                            except Exception as e:
                                self.log_result("Contacts - DELETE", False, f"Error: {str(e)}")
                else:
                    self.log_result("Contacts - GET with pagination", False, "Invalid response format")
            else:
                self.log_result("Contacts - GET with pagination", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_result("Contacts - GET with pagination", False, f"Error: {str(e)}")
    
    def test_settings(self):
        """Test Settings endpoints"""
        print("\n🧪 Testing Settings...")
        
        # Test GET /api/admin/settings
        try:
            response = self.session.get(f"{self.base_url}/admin/settings", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if 'message' in data:
                    self.log_result("Settings - GET", True, "Retrieved settings successfully")
                else:
                    self.log_result("Settings - GET", False, "Invalid response format")
            else:
                self.log_result("Settings - GET", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_result("Settings - GET", False, f"Error: {str(e)}")
        
        # Test PUT /api/admin/settings (update settings)
        settings_data = {
            "site_name": "A-Cube Mental Health Platform",
            "maintenance_mode": False,
            "max_sessions_per_day": 50
        }
        
        try:
            response = self.session.put(f"{self.base_url}/admin/settings", json=settings_data, timeout=10)
            if response.status_code == 200:
                result = response.json()
                if 'message' in result:
                    self.log_result("Settings - PUT (update)", True, "Updated settings successfully")
                else:
                    self.log_result("Settings - PUT (update)", False, "No message in response")
            else:
                self.log_result("Settings - PUT (update)", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_result("Settings - PUT (update)", False, f"Error: {str(e)}")
    
    def test_file_upload(self):
        """Test File Upload endpoint"""
        print("\n🧪 Testing File Upload...")
        
        # Create a simple test image file in memory
        test_image_content = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\nIDATx\x9cc\xf8\x00\x00\x00\x01\x00\x01\x00\x00\x00\x00IEND\xaeB`\x82'
        
        try:
            files = {'file': ('test_image.png', io.BytesIO(test_image_content), 'image/png')}
            response = self.session.post(f"{self.base_url}/admin/upload", files=files, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if 'url' in result and 'filename' in result:
                    self.log_result("File Upload - POST", True, f"Uploaded file: {result['filename']}")
                else:
                    self.log_result("File Upload - POST", False, "No URL or filename in response")
            else:
                self.log_result("File Upload - POST", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_result("File Upload - POST", False, f"Error: {str(e)}")
    
    def run_all_tests(self):
        """Run all admin panel CRUD tests"""
        print("🚀 Starting A-Cube Admin Panel CRUD Tests")
        print(f"🔗 Testing against: {self.base_url}")
        print("=" * 80)
        
        # Login first
        if not self.admin_login():
            print("\n❌ Admin login failed. Cannot proceed with tests.")
            return False
        
        # Run all CRUD tests
        self.test_sessions_crud()
        self.test_events_crud()
        self.test_blogs_crud()
        self.test_psychologists_crud()
        self.test_jobs_crud()
        self.test_volunteers_crud()
        self.test_contacts_crud()
        self.test_settings()
        self.test_file_upload()
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 ADMIN PANEL TEST SUMMARY")
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
    tester = AdminTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)