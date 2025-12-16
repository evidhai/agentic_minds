import sys
import os

# Ensure we can import migration_agent
sys.path.append(os.getcwd())

from migration_agent import app

print("Inspecting Routes...")
if hasattr(app, 'routes'):
    for route in app.routes:
        print(f"Route: {route.path} [{route.methods}]")
elif hasattr(app, 'router') and hasattr(app.router, 'routes'):
    for route in app.router.routes:
         print(f"Route: {route.path} [{route.methods}]")
else:
    print("Could not find routes attribute on app object:", type(app))
    print(dir(app))
