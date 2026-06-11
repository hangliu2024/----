"""Test Docker login with detailed debug"""
import sys
sys.path.insert(0, '/app')

from app import app
from app.models import User, InvestigationSOP
import re

app.config['WTF_CSRF_ENABLED'] = False

with app.test_client() as client:
    # 1. Login (CSRF disabled for testing)
    print("=== 1. Login (CSRF disabled) ===")
    login_data = {
        'email': 'admin@example.com',
        'password': 'Admin123!',
        'remember': 'y',
        'submit': '登录'
    }
    resp = client.post('/login', data=login_data, follow_redirects=True)
    print(f"  Status: {resp.status_code}")
    print(f"  Final path: {resp.request.path}")
    page_text = resp.data.decode('utf-8')
    if 'dashboard' in resp.request.path:
        print("  OK - Login successful, redirected to dashboard")
    elif 'login' in resp.request.path:
        print("  FAIL - Still on login page")
        # Find error message
        if 'alert' in page_text:
            matches = re.findall(r'class="[^"]*alert[^"]*"[^>]*>(.*?)</div>', page_text, re.DOTALL)
            for m in matches:
                print(f"  Error: {m.strip()}")
    else:
        print(f"  Path: {resp.request.path}")

    # 2. Access case management
    print("\n=== 2. Case management ===")
    resp = client.get('/case/', follow_redirects=True)
    print(f"  Status: {resp.status_code}")
    if resp.status_code == 200:
        print("  OK - Case management accessible")
    else:
        print(f"  FAIL - Status: {resp.status_code}")

    # 3. Access SOP list
    print("\n=== 3. SOP list ===")
    resp = client.get('/case/sop', follow_redirects=True)
    print(f"  Status: {resp.status_code}")
    if resp.status_code == 200:
        page_text = resp.data.decode('utf-8')
        print("  OK - SOP list accessible")
        if 'SOP-NJ-001' in page_text:
            print("  OK - SOP-NJ-001 found in page")
        if '匿名举报' in page_text:
            print("  OK - Anonymous report SOP found in page")
        if '暂无数据' in page_text:
            print("  WARN - No data shown")
    else:
        print(f"  FAIL - Status: {resp.status_code}")

    # 4. Logout
    print("\n=== 4. Logout ===")
    resp = client.get('/logout', follow_redirects=True)
    print(f"  Status: {resp.status_code}")
    print("  OK - Logged out")

print("\n=== Test complete ===")