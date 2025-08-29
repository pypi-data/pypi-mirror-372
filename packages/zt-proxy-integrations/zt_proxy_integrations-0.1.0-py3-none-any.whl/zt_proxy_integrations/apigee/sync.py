import os
import json
import requests

def get_routes_path():
    # Refactored to use the correct folder structure
    base_dir = os.path.abspath(os.getcwd())
    routes_path = os.path.join(base_dir, 'interceptor', 'routes.json')
    print(f"[DEBUG] Writing routes.json to: {routes_path}")
    return routes_path

def sync_apigee_routes(org, proxy_domain, access_token):
    """
    Sync Apigee routes to proxy and save original backend info.
    """
    proxy_domain = proxy_domain.replace('https://', '').replace('http://', '').strip('/')
    headers = {"Authorization": f"Bearer {access_token}"}
    # Fetch all API proxies
    proxies_resp = requests.get(f"https://apigee.googleapis.com/v1/organizations/{org}/apis", headers=headers)
    proxies = proxies_resp.json().get('proxies', [])
    routes_backends = {}

    for proxy in proxies:
        # Fetch proxy details
        proxy_details_resp = requests.get(f"https://apigee.googleapis.com/v1/organizations/{org}/apis/{proxy}/revisions/1", headers=headers)
        proxy_details = proxy_details_resp.json()
        base_path = proxy_details.get('basePath', f"/{proxy}")
        target_endpoint = proxy_details.get('targetEndpoint', '')
        routes_backends[base_path] = target_endpoint
        # Update target endpoint to proxy
        # Actual update would require modifying the proxy revision
        print(f"[DEBUG] Would update backend for {base_path} to {proxy_domain}")

    routes_path = get_routes_path()
    try:
        with open(routes_path, 'w', encoding='utf-8') as f:
            json.dump(routes_backends, f, indent=2)
        print(f"[DEBUG] Wrote routes to {routes_path}: {routes_backends}")
    except Exception as e:
        print(f"[ERROR] Error writing to {routes_path}: {e}")

    return routes_backends
