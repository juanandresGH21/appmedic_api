import requests
import json

# Test simple de la integración Auth0
print("🧪 Testing Auth0 Integration")
print("=" * 50)

base_url = "http://localhost:8000"

# Test 1: Public endpoint
try:
    response = requests.get(f"{base_url}/auth/public/")
    print(f"✅ Public endpoint: {response.status_code}")
    print(f"   Response: {response.json()}")
except Exception as e:
    print(f"❌ Public endpoint error: {e}")

# Test 2: Login con token de prueba
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhdXRoMHx0ZXN0MTIzNDU2Nzg5IiwiZW1haWwiOiJ0ZXN0QGF1dGgwaW50ZWdyYXRpb24uY29tIiwibmFtZSI6IlVzdWFyaW8gVGVzdCBBdXRoMCIsImlzcyI6Imh0dHBzOi8vdGVzdC1hdXRoMC1kb21haW4uYXV0aDAuY29tLyIsImF1ZCI6InRlc3QtYXBpLWlkZW50aWZpZXIiLCJpYXQiOjE3NTc0Njc4MjQsImV4cCI6MTc1NzQ3MTQyNCwic2NvcGUiOiJyZWFkOm1lc3NhZ2VzIn0.4hRLOKyshmbD6UAho6noWYsDDySOmbnBbiHo2TzvdlI"

headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}

try:
    response = requests.post(f"{base_url}/auth/login/", headers=headers)
    print(f"\n✅ Login endpoint: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Success: {data.get('success')}")
        print(f"   User ID: {data.get('user', {}).get('id')}")
        print(f"   User Email: {data.get('user', {}).get('email')}")
        print(f"   User Type: {data.get('user', {}).get('user_type')}")
    else:
        print(f"   Error: {response.text}")
except Exception as e:
    print(f"❌ Login endpoint error: {e}")

print("\n🎉 Test completed!")
