import os
import json
import requests
from azure.identity import DefaultAzureCredential
from azure.mgmt.apimanagement import ApiManagementClient


def get_routes_path():
    base_dir = os.path.abspath(os.getcwd())
    routes_path = os.path.join(base_dir, 'interceptor', 'routes.json')
    print(f"[DEBUG] Writing routes.json to: {routes_path}")
    return routes_path


def sync_azure_apim_routes(resource_group, service_name, proxy_domain, subscription_id=None, api_version="2022-08-01"):
    print(f"[DEBUG] Starting Azure APIM sync for resource_group={resource_group}, service_name={service_name}, proxy_domain={proxy_domain}, subscription_id={subscription_id}")
    proxy_domain = proxy_domain.replace('https://', '').replace('http://', '').strip('/')
    if not subscription_id:
        subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")
    if not subscription_id:
        raise ValueError("Parameter 'subscription_id' must not be None. Provide it or set AZURE_SUBSCRIPTION_ID env variable.")

    credential = DefaultAzureCredential()
    client = ApiManagementClient(credential, subscription_id)
    routes_backends = {}

    apis = client.api.list_by_service(resource_group, service_name)
    for api in apis:
        api_id = api.name
        print(f"[DEBUG] Processing API: {api_id}")

        # Skip revisions and proxy APIs
        if ";rev=" in api_id or api_id.endswith("-proxy"):
            print(f"[DEBUG] Skipping revision or proxy API: {api_id}")
            continue

        api_details = client.api.get(resource_group, service_name, api_id)
        backend_url = getattr(api_details, "service_url", "")
        if backend_url == f"https://{proxy_domain}":
            print(f"[DEBUG] API {api_id} already has proxy domain as backend, skipping revision creation.")
            continue

        # Collect existing routes for saving
        operations = client.api_operation.list_by_api(resource_group, service_name, api_id)
        for op in operations:
            url_template = getattr(op.request, "url_template", None)
            operation_name = getattr(op, "name", "")
            if url_template:
                route_key = f"/{api_details.path.lstrip('/')}/{url_template.lstrip('/')}" if api_details.path else f"/{url_template.lstrip('/')}"
            else:
                route_key = f"/{api_details.path.lstrip('/')}/{operation_name}" if api_details.path else f"/{operation_name}"
            if backend_url:
                routes_backends[route_key] = backend_url
                print(f"[DEBUG] Added route {route_key} -> {backend_url}")
            else:
                print(f"[WARN] Backend URL is None for {route_key}")

        # Calculate new revision number
        orig_revision = getattr(api_details, "api_revision", "1")
        new_revision_num = int(orig_revision) + 1 if orig_revision.isdigit() else 2
        new_revision = str(new_revision_num)
        new_backend_url = f"https://{proxy_domain}"

        # Full ARM resource ID of source API to clone
        source_api_id_full = f"/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.ApiManagement/service/{service_name}/apis/{api_id}"

        api_params = {
            "path": api_details.path,
            "display_name": api_details.display_name,
            "service_url": new_backend_url,
            "api_revision": new_revision,
            "api_revision_description": f"Revision {new_revision} created via script",
            "protocols": api_details.protocols,
            "subscription_required": api_details.subscription_required,
            "source_api_id": source_api_id_full
        }

        revision_api_id = f"{api_id};rev={new_revision}"

        try:
            print(f"[DEBUG] Creating new revision {revision_api_id} from source API {source_api_id_full}...")
            # Use client.api.begin_create_or_update (not begin_create_or_update_and_wait)
            poller = client.api.begin_create_or_update(
                resource_group_name=resource_group,
                service_name=service_name,
                api_id=revision_api_id,
                parameters=api_params,
            )
            poller.result()  # Wait for completion
            print(f"[INFO] Successfully created new revision {new_revision} for API {api_id}")
        except Exception as e:
            print(f"[ERROR] Failed to create new revision {new_revision} for API {api_id}: {e}")
            continue

    # Save routes.json file
    routes_path = get_routes_path()
    try:
        with open(routes_path, 'w', encoding='utf-8') as f:
            json.dump(routes_backends, f, indent=2)
        print(f"[DEBUG] Wrote routes to {routes_path}: {routes_backends}")
    except Exception as e:
        print(f"[ERROR] Could not write routes file: {e}")

    print("[INFO] Azure APIM sync completed.")
    return routes_backends
    return routes_backends
