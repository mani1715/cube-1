#!/usr/bin/env python3
"""
Data Persistence Verification Test
"""

import requests
import json

BASE_URL = "https://cube-visualizer-2.preview.emergentagent.com/api"

def verify_data_persistence():
    """Verify that data is properly persisted in MongoDB"""
    session = requests.Session()
    
    print("🔍 Verifying Data Persistence...")
    
    # Check sessions
    response = session.get(f"{BASE_URL}/sessions")
    if response.status_code == 200:
        sessions = response.json()
        print(f"✅ Sessions in database: {len(sessions)}")
        if sessions:
            print(f"   Latest session: {sessions[0]['full_name']} - Status: {sessions[0]['status']}")
    
    # Check volunteers
    response = session.get(f"{BASE_URL}/volunteers")
    if response.status_code == 200:
        volunteers = response.json()
        print(f"✅ Volunteers in database: {len(volunteers)}")
        if volunteers:
            print(f"   Latest volunteer: {volunteers[-1]['full_name']} - Interest: {volunteers[-1]['interest_area']}")
    
    # Check contact forms
    response = session.get(f"{BASE_URL}/contact")
    if response.status_code == 200:
        contacts = response.json()
        print(f"✅ Contact forms in database: {len(contacts)}")
        if contacts:
            print(f"   Latest contact: {contacts[-1]['full_name']} - Subject: {contacts[-1]['subject']}")
    
    # Check seeded data
    response = session.get(f"{BASE_URL}/events")
    if response.status_code == 200:
        events = response.json()
        print(f"✅ Events (seeded): {len(events)}")
    
    response = session.get(f"{BASE_URL}/blogs")
    if response.status_code == 200:
        blogs = response.json()
        print(f"✅ Blogs (seeded): {len(blogs)}")
    
    response = session.get(f"{BASE_URL}/careers")
    if response.status_code == 200:
        careers = response.json()
        print(f"✅ Careers (seeded): {len(careers)}")

if __name__ == "__main__":
    verify_data_persistence()