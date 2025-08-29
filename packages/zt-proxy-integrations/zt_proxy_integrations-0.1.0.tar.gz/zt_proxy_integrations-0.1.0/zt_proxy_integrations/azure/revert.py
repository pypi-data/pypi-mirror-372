import os
import json
import requests
from azure.identity import DefaultAzureCredential
from azure.mgmt.apimanagement import ApiManagementClient

def get_routes_path():
    base_dir = os.path.abspath(os.getcwd())
    routes_path = os.path.join(base_dir, 'interceptor', 'routes.json')
    print(f"[DEBUG] Reading routes.json from: {routes_path}")
    return routes_path

def revert_azure_apim_routes(resource_group, service_name, subscription_id=None, api_version="2022-08-01"):
    """
    Revert Azure APIM routes to their original backend info from routes.json.
    """
    routes_path = get_routes_path()
    if not subscription_id:
        subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")
    if not subscription_id:
        raise ValueError("Parameter 'subscription_id' must not be None. Please provide it in the form or set AZURE_SUBSCRIPTION_ID environment variable.")

    if not os.path.exists(routes_path):
        print(f"[ERROR] routes.json not found at {routes_path}")
        return {"status": "error"}

    with open(routes_path, 'r', encoding='utf-8') as f:
        routes_backends = json.load(f)

    credential = DefaultAzureCredential()
    token = credential.get_token("https://management.azure.com/.default").token
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    client = ApiManagementClient(credential, subscription_id)
    reverted_paths = []

    for path, original_backend_url in routes_backends.items():
        # Find the API for this path
        apis = client.api.list_by_service(resource_group, service_name)
        found_api = None
        for api in apis:
            api_details = client.api.get(resource_group, service_name, api.name)
            api_path_clean = api_details.path.lstrip('/') if getattr(api_details, "path", None) else ""
            if path.startswith(f"/{api_path_clean}/") or path.startswith(f"/{api_path_clean}") or path.startswith("/" + api_path_clean):
                found_api = api_details
                break
        if not found_api:
            print(f"[WARN] API for path {path} not found in APIM.")
            continue

        orig_revision = getattr(found_api, "api_revision", "1")
        new_revision_num = int(orig_revision) + 1 if str(orig_revision).isdigit() else 2
        new_revision = str(new_revision_num)

        # Prepare full API definition for PUT
        api_def = found_api.as_dict()
        if 'properties' not in api_def:
            api_def['properties'] = {}
        api_def['properties']['serviceUrl'] = original_backend_url

        # Ensure required fields are present for revision creation
        required_fields = {
            "displayName": getattr(found_api, "display_name", found_api.name),
            "path": getattr(found_api, "path", found_api.name),
            "protocols": getattr(found_api, "protocols", ["https"])
        }
        for k, v in required_fields.items():
            if not api_def['properties'].get(k):
                api_def['properties'][k] = v

        # Copy operations from the previous revision to the new revision
        operations_list = client.api_operation.list_by_api(resource_group, service_name, found_api.name)
        operations_defs = []
        for op in operations_list:
            op_details = client.api_operation.get(resource_group, service_name, found_api.name, op.name)
            operations_defs.append(op_details.as_dict())

        create_api_revision_url = (
            f"https://management.azure.com/subscriptions/{subscription_id}/resourceGroups/{resource_group}"
            f"/providers/Microsoft.ApiManagement/service/{service_name}/apis/{found_api.name};rev={new_revision}?api-version={api_version}"
        )
        try:
            resp = requests.put(create_api_revision_url, headers=headers, json=api_def)
            if resp.status_code in [200, 201, 204]:
                print(f"[DEBUG] Created new revision {new_revision} for API {found_api.name} with backend {original_backend_url}")
                # Re-create all operations in the new revision
                for op_def in operations_defs:
                    op_name = op_def.get('name')
                    op_url = (
                        f"https://management.azure.com/subscriptions/{subscription_id}/resourceGroups/{resource_group}"
                        f"/providers/Microsoft.ApiManagement/service/{service_name}/apis/{found_api.name};rev={new_revision}/operations/{op_name}?api-version={api_version}"
                    )
                    try:
                        op_resp = requests.put(op_url, headers=headers, json=op_def)
                        if op_resp.status_code in [200, 201, 204]:
                            print(f"  ✅ Cloned operation {op_name} to revision {new_revision}")
                        else:
                            print(f"  ❌ Failed to clone operation {op_name} to revision {new_revision}: {op_resp.status_code} {op_resp.text}")
                    except Exception as e:
                        print(f"  [ERROR] Exception cloning operation {op_name} to revision {new_revision}: {e}")
                reverted_paths.append(path)
            else:
                print(f"[ERROR] Failed to create new revision for API {found_api.name}: {resp.status_code} {resp.text}")
        except Exception as e:
            print(f"[ERROR] Exception creating revision for API {found_api.name}: {e}")

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
