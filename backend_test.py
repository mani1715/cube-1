#!/usr/bin/env python3
"""
A-Cube Mental Health Platform Backend API Tests
Tests all backend endpoints for functionality and data persistence
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, Any, List

# Backend URL from frontend/.env
BASE_URL = "https://data-viz-hub-19.preview.emergentagent.com/api"

class BackendTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.test_results = []
        self.created_ids = {
            'sessions': [],
            'events': [],
            'blogs': [],
            'careers': [],
            'volunteers': [],
            'psychologists': [],
            'contacts': [],
            'payments': []
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
    
    def test_session_booking_api(self):
        """Test Session Booking API endpoints"""
        print("\n🧪 Testing Session Booking API...")
        
        # Test data for session booking
        session_data = {
            "full_name": "Sarah Johnson",
            "email": "sarah.johnson@email.com",
            "phone": "555-012-3456",
            "age": "28",
            "gender": "female",
            "therapy_type": "individual",
            "concerns": ["anxiety", "work stress", "relationships"],
            "current_feelings": "I've been feeling overwhelmed with work and personal relationships. I often feel anxious and have trouble sleeping.",
            "previous_therapy": "yes",
            "preferred_time": "evenings",
            "additional_info": "I prefer video sessions and have experience with CBT therapy.",
            "consent": True
        }
        
        # Test POST /api/sessions/book
        try:
            response = self.session.post(f"{self.base_url}/sessions/book", json=session_data, timeout=10)
            if response.status_code == 201:
                booking = response.json()
                session_id = booking.get('id')
                if session_id:
                    self.created_ids['sessions'].append(session_id)
                    self.log_result("Session Booking - Create", True, f"Session booked successfully with ID: {session_id}")
                else:
                    self.log_result("Session Booking - Create", False, "No ID returned in response")
                    return False
            else:
                self.log_result("Session Booking - Create", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_result("Session Booking - Create", False, f"Error: {str(e)}")
            return False
        
        # Test GET /api/sessions
        try:
            response = self.session.get(f"{self.base_url}/sessions", timeout=10)
            if response.status_code == 200:
                sessions = response.json()
                if isinstance(sessions, list) and len(sessions) > 0:
                    self.log_result("Session Booking - List All", True, f"Retrieved {len(sessions)} sessions")
                else:
                    self.log_result("Session Booking - List All", False, "No sessions found or invalid response format")
            else:
                self.log_result("Session Booking - List All", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_result("Session Booking - List All", False, f"Error: {str(e)}")
        
        # Test GET /api/sessions/{id}
        if self.created_ids['sessions']:
            session_id = self.created_ids['sessions'][0]
            try:
                response = self.session.get(f"{self.base_url}/sessions/{session_id}", timeout=10)
                if response.status_code == 200:
                    session = response.json()
                    if session.get('id') == session_id:
                        self.log_result("Session Booking - Get by ID", True, f"Retrieved session {session_id}")
                    else:
                        self.log_result("Session Booking - Get by ID", False, "Session ID mismatch")
                else:
                    self.log_result("Session Booking - Get by ID", False, f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_result("Session Booking - Get by ID", False, f"Error: {str(e)}")
            
            # Test PATCH /api/sessions/{id}/status
            try:
                response = self.session.patch(f"{self.base_url}/sessions/{session_id}/status", 
                                            params={"new_status": "confirmed"}, timeout=10)
                if response.status_code == 200:
                    result = response.json()
                    if "message" in result:
                        self.log_result("Session Booking - Update Status", True, "Status updated successfully")
                    else:
                        self.log_result("Session Booking - Update Status", False, "Unexpected response format")
                else:
                    self.log_result("Session Booking - Update Status", False, f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_result("Session Booking - Update Status", False, f"Error: {str(e)}")
        
        return True
    
    def test_event_api(self):
        """Test Event API endpoints"""
        print("\n🧪 Testing Event API...")
        
        # Test GET /api/events (should return seeded events)
        try:
            response = self.session.get(f"{self.base_url}/events", timeout=10)
            if response.status_code == 200:
                events = response.json()
                if isinstance(events, list):
                    if len(events) >= 4:  # Should have 4 seeded events
                        self.log_result("Event API - List Events", True, f"Retrieved {len(events)} events (expected 4+)")
                        
                        # Test event registration with first event
                        if events:
                            event_id = events[0].get('id')
                            if event_id:
                                registration_data = {
                                    "full_name": "Michael Chen",
                                    "email": "michael.chen@email.com",
                                    "phone": "555-0456"
                                }
                                
                                try:
                                    response = self.session.post(f"{self.base_url}/events/{event_id}/register", 
                                                               params=registration_data, timeout=10)
                                    if response.status_code == 201:
                                        registration = response.json()
                                        if registration.get('event_id') == event_id:
                                            self.log_result("Event API - Register", True, f"Registered for event {event_id}")
                                        else:
                                            self.log_result("Event API - Register", False, "Event ID mismatch in registration")
                                    else:
                                        self.log_result("Event API - Register", False, f"HTTP {response.status_code}: {response.text}")
                                except Exception as e:
                                    self.log_result("Event API - Register", False, f"Error: {str(e)}")
                    else:
                        self.log_result("Event API - List Events", False, f"Expected 4+ events, got {len(events)}")
                else:
                    self.log_result("Event API - List Events", False, "Invalid response format")
            else:
                self.log_result("Event API - List Events", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_result("Event API - List Events", False, f"Error: {str(e)}")
        
        return True
    
    def test_blog_api(self):
        """Test Blog API endpoints"""
        print("\n🧪 Testing Blog API...")
        
        # Test GET /api/blogs (should return seeded blogs)
        try:
            response = self.session.get(f"{self.base_url}/blogs", timeout=10)
            if response.status_code == 200:
                blogs = response.json()
                if isinstance(blogs, list):
                    if len(blogs) >= 6:  # Should have 6 seeded blogs
                        self.log_result("Blog API - List All", True, f"Retrieved {len(blogs)} blogs (expected 6+)")
                        
                        # Test category filtering
                        response = self.session.get(f"{self.base_url}/blogs", params={"category": "Wellness"}, timeout=10)
                        if response.status_code == 200:
                            wellness_blogs = response.json()
                            if isinstance(wellness_blogs, list):
                                self.log_result("Blog API - Category Filter", True, f"Retrieved {len(wellness_blogs)} wellness blogs")
                            else:
                                self.log_result("Blog API - Category Filter", False, "Invalid response format")
                        else:
                            self.log_result("Blog API - Category Filter", False, f"HTTP {response.status_code}: {response.text}")
                        
                        # Test featured filtering
                        response = self.session.get(f"{self.base_url}/blogs", params={"featured": True}, timeout=10)
                        if response.status_code == 200:
                            featured_blogs = response.json()
                            if isinstance(featured_blogs, list):
                                self.log_result("Blog API - Featured Filter", True, f"Retrieved {len(featured_blogs)} featured blogs")
                            else:
                                self.log_result("Blog API - Featured Filter", False, "Invalid response format")
                        else:
                            self.log_result("Blog API - Featured Filter", False, f"HTTP {response.status_code}: {response.text}")
                    else:
                        self.log_result("Blog API - List All", False, f"Expected 6+ blogs, got {len(blogs)}")
                else:
                    self.log_result("Blog API - List All", False, "Invalid response format")
            else:
                self.log_result("Blog API - List All", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_result("Blog API - List All", False, f"Error: {str(e)}")
        
        return True
    
    def test_career_api(self):
        """Test Career API endpoints"""
        print("\n🧪 Testing Career API...")
        
        # Test GET /api/careers (should return seeded careers)
        try:
            response = self.session.get(f"{self.base_url}/careers", timeout=10)
            if response.status_code == 200:
                careers = response.json()
                if isinstance(careers, list):
                    if len(careers) >= 3:  # Should have 3 seeded careers
                        self.log_result("Career API - List All", True, f"Retrieved {len(careers)} job postings (expected 3+)")
                        
                        # Test GET /api/careers/{id} with first career
                        if careers:
                            career_id = careers[0].get('id')
                            if career_id:
                                try:
                                    response = self.session.get(f"{self.base_url}/careers/{career_id}", timeout=10)
                                    if response.status_code == 200:
                                        career = response.json()
                                        if career.get('id') == career_id:
                                            self.log_result("Career API - Get by ID", True, f"Retrieved career {career_id}")
                                        else:
                                            self.log_result("Career API - Get by ID", False, "Career ID mismatch")
                                    else:
                                        self.log_result("Career API - Get by ID", False, f"HTTP {response.status_code}: {response.text}")
                                except Exception as e:
                                    self.log_result("Career API - Get by ID", False, f"Error: {str(e)}")
                    else:
                        self.log_result("Career API - List All", False, f"Expected 3+ careers, got {len(careers)}")
                else:
                    self.log_result("Career API - List All", False, "Invalid response format")
            else:
                self.log_result("Career API - List All", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_result("Career API - List All", False, f"Error: {str(e)}")
        
        return True
    
    def test_volunteer_api(self):
        """Test Volunteer API endpoints"""
        print("\n🧪 Testing Volunteer API...")
        
        # Test POST /api/volunteers
        volunteer_data = {
            "full_name": "Emma Rodriguez",
            "email": "emma.rodriguez@email.com",
            "phone": "555-0789",
            "interest_area": "peer support",
            "availability": "weekends",
            "experience": "I have been volunteering with local mental health organizations for 2 years. I have experience in peer support and crisis intervention.",
            "motivation": "I want to help others who are struggling with mental health challenges because I understand how important it is to have support during difficult times."
        }
        
        try:
            response = self.session.post(f"{self.base_url}/volunteers", json=volunteer_data, timeout=10)
            if response.status_code == 201:
                volunteer = response.json()
                volunteer_id = volunteer.get('id')
                if volunteer_id:
                    self.created_ids['volunteers'].append(volunteer_id)
                    self.log_result("Volunteer API - Submit Application", True, f"Volunteer application submitted with ID: {volunteer_id}")
                else:
                    self.log_result("Volunteer API - Submit Application", False, "No ID returned in response")
            else:
                self.log_result("Volunteer API - Submit Application", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_result("Volunteer API - Submit Application", False, f"Error: {str(e)}")
        
        return True
    
    def test_contact_api(self):
        """Test Contact Form API endpoints"""
        print("\n🧪 Testing Contact Form API...")
        
        # Test POST /api/contact
        contact_data = {
            "full_name": "David Wilson",
            "email": "david.wilson@email.com",
            "subject": "Question about therapy services",
            "message": "Hi, I'm interested in learning more about your individual therapy services. Could you please provide information about availability and pricing?"
        }
        
        try:
            response = self.session.post(f"{self.base_url}/contact", json=contact_data, timeout=10)
            if response.status_code == 201:
                contact = response.json()
                contact_id = contact.get('id')
                if contact_id:
                    self.created_ids['contacts'].append(contact_id)
                    self.log_result("Contact API - Submit Form", True, f"Contact form submitted with ID: {contact_id}")
                else:
                    self.log_result("Contact API - Submit Form", False, "No ID returned in response")
            else:
                self.log_result("Contact API - Submit Form", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_result("Contact API - Submit Form", False, f"Error: {str(e)}")
        
        return True
    
    def test_psychologist_api(self):
        """Test Psychologist API endpoints"""
        print("\n🧪 Testing Psychologist API...")
        
        # Test GET /api/psychologists
        try:
            response = self.session.get(f"{self.base_url}/psychologists", timeout=10)
            if response.status_code == 200:
                psychologists = response.json()
                if isinstance(psychologists, list):
                    self.log_result("Psychologist API - List All", True, f"Retrieved {len(psychologists)} psychologists")
                else:
                    self.log_result("Psychologist API - List All", False, "Invalid response format")
            else:
                self.log_result("Psychologist API - List All", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_result("Psychologist API - List All", False, f"Error: {str(e)}")
        
        return True
    
    def run_all_tests(self):
        """Run all backend API tests"""
        print("🚀 Starting A-Cube Mental Health Platform Backend API Tests")
        print(f"🔗 Testing against: {self.base_url}")
        print("=" * 80)
        
        # Test health check first
        if not self.test_health_check():
            print("\n❌ Health check failed. Backend may not be running.")
            return False
        
        # Run all API tests
        self.test_session_booking_api()
        self.test_event_api()
        self.test_blog_api()
        self.test_career_api()
        self.test_volunteer_api()
        self.test_contact_api()
        self.test_psychologist_api()
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 TEST SUMMARY")
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
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)