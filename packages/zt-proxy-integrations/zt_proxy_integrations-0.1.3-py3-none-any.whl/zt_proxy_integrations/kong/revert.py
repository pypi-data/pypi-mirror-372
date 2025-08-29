import os
import json
import requests

def get_routes_path():
    base_dir = os.path.abspath(os.getcwd())
    routes_path = os.path.join(base_dir, 'interceptor', 'routes.json')
    print(f"[DEBUG] Reading routes.json from: {routes_path}")
    return routes_path

def revert_kong_routes(admin_api_url, kong_api_key=None, proxy_domain=None):
    """
    Revert Kong Konnect services to their original backend host from routes.json.
    """
    routes_path = get_routes_path()
    if not os.path.exists(routes_path):
        print(f"[ERROR] routes.json not found at {routes_path}")
        return {"status": "error"}

    with open(routes_path, 'r', encoding='utf-8') as f:
        routes_backends = json.load(f)

    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    if kong_api_key:
        headers['Authorization'] = f'Bearer {kong_api_key}'

    admin_api_url = admin_api_url.rstrip('/')

    # List all routes to get their service IDs
    routes_url = f"{admin_api_url}/core-entities/routes?size=100"
    routes_resp = requests.get(routes_url, headers=headers)
    if routes_resp.status_code != 200:
        print(f"[ERROR] Failed to fetch routes: {routes_resp.text}")
        return {"status": "error"}
    routes = routes_resp.json().get('data', [])

    # Map paths to route objects
    path_to_route = {}
    for route in routes:
        for path in route.get('paths', []):
            path_to_route[path] = route

    # Revert each service's backend host
    reverted_paths = []
    for path, original_host in routes_backends.items():
        route = path_to_route.get(path)
        if not route:
            print(f"[WARN] Route for path {path} not found in Kong.")
            continue
        service_id = route.get('service', {}).get('id')
        if not service_id:
            print(f"[WARN] Service ID not found for route {path}")
            continue

        # Fetch the full service object
        service_url_api = f"{admin_api_url}/core-entities/services/{service_id}"
        service_resp = requests.get(service_url_api, headers=headers)
        if service_resp.status_code != 200:
            print(f"[ERROR] Failed to fetch service {service_id}: {service_resp.text}")
            continue
        service_obj = service_resp.json()

        # Restore the backend domain for the service
        updated_service = service_obj.copy()
        updated_service['host'] = original_host
        try:
            resp = requests.put(
                service_url_api,
                headers=headers,
                json=updated_service
            )
            if resp.status_code in [200, 201, 204]:
                print(f"[DEBUG] Reverted service {service_id} for path {path} to backend {original_host}")
                reverted_paths.append(path)
            else:
                print(f"[ERROR] Failed to revert service {service_id} for path {path}: {resp.status_code} {resp.text}")
        except Exception as e:
            print(f"[ERROR] Exception reverting service {service_id} for path {path}: {e}")

    # Remove reverted paths from routes.json
    for path in reverted_paths:
        routes_backends.pop(path, None)
    try:
        with open(routes_path, 'w', encoding='utf-8') as f:
            json.dump(routes_backends, f, indent=2)
        print(f"[DEBUG] Updated routes.json after revert: {routes_backends}")
    except Exception as e:
        print(f"[ERROR] Error updating routes.json after revert: {e}")

    print("[INFO] Revert complete.")
    return {"status": "done"}

# Example usage:
# revert_kong_routes(admin_api_url="https://in.api.konghq.com/v2/control-planes/<control_plane_id>", kong_api_key="your_token")
# Example usage:
# revert_kong_routes(admin_api_url="https://in.api.konghq.com/v2/control-planes/<control_plane_id>", kong_api_key="your_token")
