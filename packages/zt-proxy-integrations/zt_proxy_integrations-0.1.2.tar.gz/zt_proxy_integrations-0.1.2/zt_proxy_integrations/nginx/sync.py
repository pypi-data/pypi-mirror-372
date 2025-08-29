import os
import json
import shutil

def get_routes_path():
    base_dir = os.path.abspath(os.getcwd())
    routes_path = os.path.join(base_dir, 'interceptor', 'routes.json')
    print(f"[DEBUG] Writing routes.json to: {routes_path}")
    return routes_path

def sync_nginx_routes(nginx_conf_path, proxy_domain, backup_conf_path=None):
    """
    Sync Nginx routes to proxy and save original backend info.
    nginx_conf_path: Path to nginx.conf or site config file.
    proxy_domain: Domain to route traffic to.
    backup_conf_path: Optional path to backup original config.
    """
    proxy_domain = proxy_domain.replace('https://', '').replace('http://', '').strip('/')
    routes_backends = {}

    # Backup original config
    if backup_conf_path:
        shutil.copyfile(nginx_conf_path, backup_conf_path)
        print(f"[DEBUG] Backed up original config to {backup_conf_path}")

    # Read nginx config
    with open(nginx_conf_path, 'r', encoding='utf-8') as f:
        config_lines = f.readlines()

    # Find and replace upstream/server blocks (simple demo: replace all proxy_pass lines)
    new_config_lines = []
    for line in config_lines:
        if 'proxy_pass' in line:
            # Save original backend
            original_backend = line.split('proxy_pass')[1].split(';')[0].strip()
            routes_backends[original_backend] = original_backend
            # Replace with proxy domain
            new_line = line.replace(original_backend, f"https://{proxy_domain}")
            new_config_lines.append(new_line)
            print(f"[DEBUG] Updated proxy_pass from {original_backend} to https://{proxy_domain}")
        else:
            new_config_lines.append(line)

    # Write updated config
    with open(nginx_conf_path, 'w', encoding='utf-8') as f:
        f.writelines(new_config_lines)
    print(f"[DEBUG] Updated nginx config at {nginx_conf_path}")

    # Save original backends to routes.json
    routes_path = get_routes_path()
    with open(routes_path, 'w', encoding='utf-8') as f:
        json.dump(routes_backends, f, indent=2)
    print(f"[DEBUG] Wrote routes to {routes_path}: {routes_backends}")

    # Note: You may need to reload nginx after updating config
    return routes_backends
