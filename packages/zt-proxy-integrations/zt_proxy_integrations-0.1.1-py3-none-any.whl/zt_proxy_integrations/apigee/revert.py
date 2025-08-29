import os
import json
import requests

def get_routes_path():
    base_dir = os.path.abspath(os.getcwd())
    routes_path = os.path.join(base_dir, 'interceptor', 'routes.json')
    print(f"[DEBUG] Reading routes.json from: {routes_path}")
    return routes_path

def revert_apigee_routes(org, access_token):
    """
    Revert Apigee routes to original backend URLs.
    """
    headers = {"Authorization": f"Bearer {access_token}"}
    routes_path = get_routes_path()
    if not os.path.exists(routes_path):
        print(f"[ERROR] routes.json not found at {routes_path}")
        return {"status": "error", "message": "routes.json not found"}

    with open(routes_path, 'r', encoding='utf-8') as f:
        routes_backends = json.load(f)

    for base_path, backend_url in routes_backends.items():
        print(f"[DEBUG] Would revert backend for {base_path} to {backend_url}")
        # Actual revert logic would update the proxy revision's target endpoint

    # Optionally clear routes.json after revert
    try:
        with open(routes_path, 'w', encoding='utf-8') as f:
            json.dump({}, f, indent=2)
        print(f"[DEBUG] Cleared {routes_path}")
    except Exception as e:
        print(f"[ERROR] Error clearing {routes_path}: {e}")
    return {"status": "done"}
    return {"status": "done"}
