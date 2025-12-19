import os
import sys
import django
from django.core.wsgi import get_wsgi_application

print("--- DEBUGGING WSGI LOAD ---")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "news_guardian.settings")

try:
    print("1. Setting up Django...")
    django.setup()
    print("2. Loading WSGI Application...")
    application = get_wsgi_application()
    print("SUCCESS: WSGI application loaded successfully! Code is valid.")
except Exception as e:
    print(f"FAILURE: Could not load WSGI application.\nError: {e}")
    import traceback
    traceback.print_exc()
