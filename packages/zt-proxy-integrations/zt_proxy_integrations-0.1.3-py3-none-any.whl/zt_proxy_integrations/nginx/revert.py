import os
import json
import shutil

def get_routes_path():
    base_dir = os.path.abspath(os.getcwd())
    routes_path = os.path.join(base_dir, 'interceptor', 'routes.json')
    print(f"[DEBUG] Reading routes.json from: {routes_path}")
    return routes_path

def revert_nginx_routes(nginx_conf_path, backup_conf_path=None):
    """
    Revert Nginx config to original backend URLs using backup or routes.json.
    nginx_conf_path: Path to nginx.conf or site config file.
    backup_conf_path: Optional path to restore original config.
    """
    routes_path = get_routes_path()
    if backup_conf_path and os.path.exists(backup_conf_path):
        shutil.copyfile(backup_conf_path, nginx_conf_path)
        print(f"[DEBUG] Restored config from backup {backup_conf_path}")
    elif os.path.exists(routes_path):
        # If no backup, try to restore proxy_pass lines from routes.json
        with open(routes_path, 'r', encoding='utf-8') as f:
            routes_backends = json.load(f)
        with open(nginx_conf_path, 'r', encoding='utf-8') as f:
            config_lines = f.readlines()
        new_config_lines = []
        for line in config_lines:
            if 'proxy_pass' in line:
                for original_backend in routes_backends:
                    if f"https://{original_backend}" in line:
                        new_line = line.replace(f"https://{original_backend}", original_backend)
                        new_config_lines.append(new_line)
                        print(f"[DEBUG] Reverted proxy_pass to {original_backend}")
                        break
                else:
                    new_config_lines.append(line)
            else:
                new_config_lines.append(line)
        with open(nginx_conf_path, 'w', encoding='utf-8') as f:
            f.writelines(new_config_lines)
        print(f"[DEBUG] Reverted nginx config at {nginx_conf_path}")
    else:
        print("[ERROR] No backup or routes.json found for revert.")

    # Optionally clear routes.json after revert
    try:
        with open(routes_path, 'w', encoding='utf-8') as f:
            json.dump({}, f, indent=2)
        print(f"[DEBUG] Cleared {routes_path}")
    except Exception as e:
        print(f"[ERROR] Error clearing {routes_path}: {e}")
    return {"status": "done"}
    return {"status": "done"}
