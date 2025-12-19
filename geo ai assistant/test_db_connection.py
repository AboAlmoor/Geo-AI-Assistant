"""
Database Connection Diagnostic Script
Run from QGIS Python Console to diagnose database connection issues
"""

import os
from dotenv import load_dotenv

# Get plugin directory
plugin_dir = os.path.dirname(os.path.dirname(__file__))
env_path = os.path.join(plugin_dir, ".env")

print("=" * 60)
print("DATABASE CONNECTION DIAGNOSTIC")
print("=" * 60)

# Load .env file
print(f"\n1. Loading .env file from: {env_path}")
if os.path.exists(env_path):
    print("   ✅ .env file found")
else:
    print(f"   ❌ .env file NOT found at {env_path}")
    
load_dotenv(env_path, override=True)

# Check database credentials
print("\n2. Checking database credentials:")
db_host = os.getenv('DB_HOST', 'localhost')
db_port = os.getenv('DB_PORT', '5432')
db_name = os.getenv('DB_NAME')
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')

print(f"   Host: {db_host}")
print(f"   Port: {db_port}")
print(f"   Database: {db_name if db_name else '❌ NOT SET'}")
print(f"   User: {db_user if db_user else '❌ NOT SET'}")
print(f"   Password: {'✅ SET' if db_password else '❌ NOT SET'}")

# Test connection
print("\n3. Testing PostgreSQL connection:")
try:
    import psycopg2
    conn = psycopg2.connect(
        host=db_host,
        port=int(db_port),
        database=db_name,
        user=db_user,
        password=db_password
    )
    print("   ✅ Connection successful!")
    
    # Test a simple query
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    version = cursor.fetchone()
    print(f"   PostgreSQL version: {version[0][:50]}...")
    
    conn.close()
    
except ImportError:
    print("   ⚠️  psycopg2 not installed. Install with:")
    print("      pip install psycopg2-binary")
except Exception as e:
    print(f"   ❌ Connection failed: {str(e)}")

print("\n" + "=" * 60)
