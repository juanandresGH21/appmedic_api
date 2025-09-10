#!/usr/bin/env python3
"""
Script de testing para Auth0 Integration
Permite probar todos los endpoints de Auth0 con tokens reales o de prueba

Uso:
python test_auth0_integration.py [--token YOUR_TOKEN] [--base-url http://localhost:8000]
"""

import requests
import json
import argparse
import sys
from datetime import datetime


class Auth0Tester:
    def __init__(self, base_url='http://localhost:8000', token=None):
        self.base_url = base_url.rstrip('/')
        self.token = token
        self.headers = {
            'Content-Type': 'application/json'
        }
        
        if self.token:
            self.headers['Authorization'] = f'Bearer {self.token}'
    
    def print_response(self, response, test_name):
        """Imprimir respuesta de manera formateada"""
        print(f"\n{'='*60}")
        print(f"🧪 TEST: {test_name}")
        print(f"{'='*60}")
        print(f"📍 URL: {response.request.method} {response.url}")
        print(f"📊 Status: {response.status_code}")
        
        try:
            data = response.json()
            print(f"📋 Response:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
        except:
            print(f"📋 Raw Response: {response.text}")
        
        print(f"{'='*60}")
    
    def test_public_endpoint(self):
        """Test del endpoint público"""
        try:
            response = requests.get(f'{self.base_url}/auth/public/')
            self.print_response(response, "Public Endpoint")
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Error en public endpoint: {e}")
            return False
    
    def test_auth0_login(self):
        """Test del login con Auth0"""
        if not self.token:
            print("⚠️  Saltando test de login - no hay token")
            return None
            
        try:
            response = requests.post(f'{self.base_url}/auth/login/', headers=self.headers)
            self.print_response(response, "Auth0 Login")
            
            if response.status_code == 200:
                data = response.json()
                return data.get('success', False)
            return False
        except Exception as e:
            print(f"❌ Error en auth0 login: {e}")
            return False
    
    def test_auth0_profile(self):
        """Test de obtener perfil"""
        if not self.token:
            print("⚠️  Saltando test de profile - no hay token")
            return None
            
        try:
            response = requests.get(f'{self.base_url}/auth/profile/', headers=self.headers)
            self.print_response(response, "Auth0 Profile")
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Error en auth0 profile: {e}")
            return False
    
    def test_auth0_update_profile(self):
        """Test de actualizar perfil"""
        if not self.token:
            print("⚠️  Saltando test de update profile - no hay token")
            return None
            
        try:
            update_data = {
                'name': f'Usuario Test - {datetime.now().strftime("%H:%M:%S")}',
                'tz': 'America/Mexico_City'
            }
            
            response = requests.put(
                f'{self.base_url}/auth/profile/update/', 
                headers=self.headers,
                json=update_data
            )
            self.print_response(response, "Auth0 Update Profile")
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Error en auth0 update profile: {e}")
            return False
    
    def test_private_endpoint(self):
        """Test del endpoint privado"""
        if not self.token:
            print("⚠️  Saltando test de private - no hay token")
            return None
            
        try:
            response = requests.get(f'{self.base_url}/auth/private/', headers=self.headers)
            self.print_response(response, "Private Endpoint")
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Error en private endpoint: {e}")
            return False
    
    def test_auth0_logout(self):
        """Test de logout"""
        if not self.token:
            print("⚠️  Saltando test de logout - no hay token")
            return None
            
        try:
            response = requests.post(f'{self.base_url}/auth/logout/', headers=self.headers)
            self.print_response(response, "Auth0 Logout")
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Error en auth0 logout: {e}")
            return False
    
    def run_all_tests(self):
        """Ejecutar todos los tests"""
        print("🚀 Iniciando tests de Auth0 Integration")
        print(f"🔗 Base URL: {self.base_url}")
        print(f"🎫 Token: {'✅ Configurado' if self.token else '❌ No configurado'}")
        
        results = {}
        
        # Test 1: Public Endpoint (no requiere token)
        results['public'] = self.test_public_endpoint()
        
        # Tests que requieren token
        if self.token:
            results['login'] = self.test_auth0_login()
            results['profile'] = self.test_auth0_profile()
            results['update_profile'] = self.test_auth0_update_profile()
            results['private'] = self.test_private_endpoint()
            results['logout'] = self.test_auth0_logout()
        else:
            print("\n⚠️  Los siguientes tests requieren un token de Auth0:")
            print("   - Login")
            print("   - Profile")
            print("   - Update Profile") 
            print("   - Private Endpoint")
            print("   - Logout")
            print("\n💡 Usa: python test_auth0_integration.py --token YOUR_TOKEN")
        
        # Resumen final
        self.print_summary(results)
        
        return results
    
    def print_summary(self, results):
        """Imprimir resumen de resultados"""
        print(f"\n{'='*60}")
        print("📊 RESUMEN DE TESTS")
        print(f"{'='*60}")
        
        total_tests = len([r for r in results.values() if r is not None])
        passed_tests = len([r for r in results.values() if r is True])
        failed_tests = len([r for r in results.values() if r is False])
        skipped_tests = len([r for r in results.values() if r is None])
        
        for test_name, result in results.items():
            if result is True:
                print(f"✅ {test_name.replace('_', ' ').title()}")
            elif result is False:
                print(f"❌ {test_name.replace('_', ' ').title()}")
            else:
                print(f"⚠️  {test_name.replace('_', ' ').title()} (Saltado)")
        
        print(f"\n📈 Estadísticas:")
        print(f"   Total ejecutados: {total_tests}")
        print(f"   Exitosos: {passed_tests}")
        print(f"   Fallidos: {failed_tests}")
        print(f"   Saltados: {skipped_tests}")
        
        if total_tests > 0:
            success_rate = (passed_tests / total_tests) * 100
            print(f"   Tasa de éxito: {success_rate:.1f}%")
        
        print(f"{'='*60}")


def create_test_token():
    """Crear un token de prueba para testing básico"""
    import jwt
    import time
    
    # Payload de prueba (NO usar en producción)
    payload = {
        'sub': 'auth0|test123456789',
        'email': 'test@auth0integration.com',
        'name': 'Usuario Test Auth0',
        'iss': 'https://test-auth0-domain.auth0.com/',
        'aud': 'test-api-identifier',
        'iat': int(time.time()),
        'exp': int(time.time()) + 3600,  # Expira en 1 hora
        'scope': 'read:messages'
    }
    
    # Crear token sin firma (solo para testing)
    token = jwt.encode(payload, 'secret', algorithm='HS256')
    return token


def main():
    parser = argparse.ArgumentParser(description='Test Auth0 Integration')
    parser.add_argument('--token', help='Auth0 JWT token para testing')
    parser.add_argument('--base-url', default='http://localhost:8000', 
                       help='Base URL del servidor (default: http://localhost:8000)')
    parser.add_argument('--create-test-token', action='store_true',
                       help='Crear un token de prueba para testing básico')
    
    args = parser.parse_args()
    
    if args.create_test_token:
        test_token = create_test_token()
        print("🎫 Token de prueba generado:")
        print(f"   {test_token}")
        print("\n💡 Uso:")
        print(f"   python {sys.argv[0]} --token {test_token}")
        return
    
    # Crear instancia del tester
    tester = Auth0Tester(
        base_url=args.base_url,
        token=args.token
    )
    
    # Ejecutar tests
    results = tester.run_all_tests()
    
    # Exit code basado en resultados
    failed_count = len([r for r in results.values() if r is False])
    sys.exit(failed_count)


if __name__ == '__main__':
    main()
