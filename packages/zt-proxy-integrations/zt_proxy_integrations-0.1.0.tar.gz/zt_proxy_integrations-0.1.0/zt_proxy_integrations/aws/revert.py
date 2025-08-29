import boto3
import json
import os

def get_routes_path():
    base_dir = os.path.abspath(os.getcwd())
    routes_path = os.path.join(base_dir, 'interceptor', 'routes.json')
    print(f"[DEBUG] Reading routes.json from: {routes_path}")
    return routes_path

def revert_apigateway_routes(rest_api_id, routes_backends, stage_name="prod"):
    print(f"[DEBUG] revert_apigateway_routes called with rest_api_id={rest_api_id}, stage_name={stage_name}")
    client = boto3.client('apigateway')
    resources = client.get_resources(restApiId=rest_api_id)['items']
    print(f"[DEBUG] Fetched {len(resources)} resources from API Gateway")
    path_to_id = {r['path']: r['id'] for r in resources}

    for path, backend_url in routes_backends.items():
        resource_id = path_to_id.get(path)
        if not resource_id:
            print(f"[ERROR] Resource not found for path: {path}")
            continue
        # Find available methods for this resource
        methods = []
        for r in resources:
            if r['path'] == path and 'resourceMethods' in r:
                methods = list(r['resourceMethods'].keys())
                break
        for method in methods:
            try:
                # Compose the full backend URI for AWS HTTP_PROXY
                if backend_url.endswith('/') and path.startswith('/'):
                    original_uri = backend_url.rstrip('/') + path
                elif not backend_url.endswith('/') and not path.startswith('/'):
                    original_uri = backend_url + '/' + path
                else:
                    original_uri = backend_url + path
                print(f"[DEBUG] Reverting integration for {path} [{method}] to {original_uri}")
                client.put_integration(
                    restApiId=rest_api_id,
                    resourceId=resource_id,
                    httpMethod=method,
                    type="HTTP_PROXY",
                    integrationHttpMethod=method,
                    uri=original_uri
                )
                print(f"[DEBUG] Reverted integration for {path} [{method}] -> {original_uri}")
            except Exception as e:
                print(f"[ERROR] Error reverting integration for {path} [{method}]: {e}")

    # Deploy changes
    try:
        client.create_deployment(
            restApiId=rest_api_id,
            stageName=stage_name,
            description='Revert routes to backend APIs'
        )
        print(f"[DEBUG] Deployment created for stage: {stage_name}")
    except Exception as e:
        print(f"[ERROR] Error creating deployment: {e}")

    # Clear routes.json after revert
    routes_path = get_routes_path()
    try:
        with open(routes_path, 'w', encoding='utf-8') as f:
            json.dump({}, f, indent=2)
        print(f"[DEBUG] Cleared {routes_path}")
    except Exception as e:
        print(f"[ERROR] Error clearing {routes_path}: {e}")

    return {"status": "done"}