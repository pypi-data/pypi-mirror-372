import os
import json
import requests

def get_routes_path():
    base_dir = os.path.abspath(os.getcwd())
    routes_path = os.path.join(base_dir, 'interceptor', 'routes.json')
    print(f"[DEBUG] Writing routes.json to: {routes_path}")
    return routes_path

def sync_kong_routes(admin_api_url, control_plane_id, proxy_domain, kong_api_key=None):
    """
    Sync Kong Konnect routes to proxy and save original backend info.
    """
    print(f"[DEBUG] Using Kong Konnect API URL: {admin_api_url}, Control Plane: {control_plane_id}, Proxy Domain: {proxy_domain}, Kong API Key: {kong_api_key}")

    if not control_plane_id:
        print("[ERROR] control_plane_id is required and was not provided.")
        return {}

    print(f"[DEBUG] proxy domain ID: {proxy_domain}")
    proxy_domain = proxy_domain.replace('https://', '').replace('http://', '').strip('/')
    print(f"[DEBUG] proxy domain ID: {proxy_domain}")
    
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    if kong_api_key:
        headers['Authorization'] = f'Bearer {kong_api_key}'

    # Ensure admin_api_url does NOT end with a slash
    admin_api_url = admin_api_url.rstrip('/')

    # Correct API path for listing routes
    routes_url = f"{admin_api_url}/core-entities/routes?size=100"
    routes_resp = requests.get(routes_url, headers=headers)
    print(f"[DEBUG] Fetched routes from {routes_url}: {routes_resp.status_code}")
    print(f"[DEBUG] Fetched routes response: {routes_resp.json()}")
    if routes_resp.status_code == 401:
        print(f"[ERROR] Unauthorized. Check your Kong API key/token.")
        return {}
    if routes_resp.status_code != 200:
        print(f"[ERROR] Failed to fetch routes: {routes_resp.text}")
        return {}
    routes = routes_resp.json().get('data', [])
    routes_backends = {}

    for route in routes:
        route_id = route['id']
        route_paths = route.get('paths', [])
        service_id = route.get('service', {}).get('id')
        original_host = None

        # Fetch service details to get backend info
        if service_id:
            service_url_api = f"{admin_api_url}/core-entities/services/{service_id}"
            service_resp = requests.get(service_url_api, headers=headers)
            if service_resp.status_code == 200:
                service_obj = service_resp.json()
                original_host = service_obj.get('host')
            else:
                print(f"[ERROR] Failed to fetch service {service_id}: {service_resp.text}")

        for path in route_paths:
            # Store the original host for this route
            routes_backends[path] = original_host

            # Update the gateway service backend to proxy domain
            if service_id and service_obj:
                update_service_url = f"{admin_api_url}/core-entities/services/{service_id}"
                # Update only the host field in the full service object
                updated_service = service_obj.copy()
                updated_service['host'] = proxy_domain
                try:
                    resp = requests.put(
                        update_service_url,
                        headers=headers,
                        json=updated_service
                    )
                    print(f"[DEBUG] Updated service {service_id} for path {path} to proxy {proxy_domain}, status: {resp.status_code}, resp: {resp.text}")
                except Exception as e:
                    print(f"[ERROR] Could not update service {service_id} for path {path}: {e}")

    routes_path = get_routes_path()
    try:
        with open(routes_path, 'w', encoding='utf-8') as f:
            json.dump(routes_backends, f, indent=2)
        print(f"[DEBUG] Wrote routes to {routes_path}: {routes_backends}")
    except Exception as e:
        print(f"[ERROR] Error writing to {routes_path}: {e}")

    return routes_backends

def test_kong_api_connection(admin_api_url, kong_api_key=None):
    """
    Test connectivity to Kong Admin API by fetching services.
    """
    headers = {}
    if kong_api_key:
        headers['Kong-Admin-Token'] = kong_api_key
    try:
        resp = requests.get(f"{admin_api_url}/services", headers=headers)
        resp.raise_for_status()
        print(f"[TEST] Kong API reachable. Services: {resp.json().get('data', [])}")
        return True
    except Exception as e:
        print(f"[TEST ERROR] Unable to reach Kong API: {e}")
        return False
    except Exception as e:
        print(f"[TEST ERROR] Unable to reach Kong API: {e}")
        return False
        return False
    except Exception as e:
        print(f"[TEST ERROR] Unable to reach Kong API: {e}")
        return False
        return False
