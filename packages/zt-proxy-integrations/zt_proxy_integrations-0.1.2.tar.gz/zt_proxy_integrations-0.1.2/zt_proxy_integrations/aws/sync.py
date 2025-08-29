import boto3
import json
import os

def get_routes_path():
    # Always use the interceptor folder for routes.json
    base_dir = os.path.abspath(os.getcwd())
    routes_path = os.path.join(base_dir, 'interceptor', 'routes.json')
    print(f"[DEBUG] Writing routes.json to: {routes_path}")
    return routes_path

def sync_apigateway_routes(rest_api_id, ngrok_domain, stage_name="prod", s3_bucket=None):
    print(f"[DEBUG] sync_apigateway_routes called with rest_api_id={rest_api_id}, ngrok_domain={ngrok_domain}, stage_name={stage_name}, s3_bucket={s3_bucket}")
    ngrok_domain = ngrok_domain.replace('https://', '').replace('http://', '').strip('/')
    print(f"[DEBUG] Normalized ngrok_domain: {ngrok_domain}")
    client = boto3.client('apigateway')
    resources = client.get_resources(restApiId=rest_api_id)['items']
    print(f"[DEBUG] Fetched {len(resources)} resources from API Gateway")
    routes_backends = {}

    for r in resources:
        print(f"[DEBUG] Resource: {r.get('path')} (ID: {r.get('id')})")
        if 'resourceMethods' in r:
            for method in r['resourceMethods']:
                print(f"[DEBUG] Processing method: {method} for path: {r['path']}")
                try:
                    integration = client.get_integration(
                        restApiId=rest_api_id,
                        resourceId=r['id'],
                        httpMethod=method
                    )
                    uri = integration.get('uri', '')
                    print(f"[DEBUG] Existing integration URI for {r['path']} [{method}]: {uri}")
                    backend = uri.split('/')[2] if uri.startswith('https://') or uri.startswith('http://') else uri
                    routes_backends[r['path']] = f"https://{backend}"
                    print(f"[DEBUG] Will update integration for {r['path']} [{method}] to https://{ngrok_domain}{r['path']}")
                    client.put_integration(
                        restApiId=rest_api_id,
                        resourceId=r['id'],
                        httpMethod=method,
                        type="HTTP_PROXY",
                        integrationHttpMethod=method,
                        uri=f"https://{ngrok_domain}{r['path']}"
                    )
                except Exception as e:
                    print(f"[ERROR] Exception updating integration for {r['path']} [{method}]: {e}")
                    continue

    print(f"[DEBUG] routes_backends to write: {routes_backends}")

    # Deploy changes
    try:
        client.create_deployment(
            restApiId=rest_api_id,
            stageName=stage_name,
            description='Sync routes to ngrok proxy'
        )
        print(f"[DEBUG] Deployment created for stage: {stage_name}")
    except Exception as e:
        print(f"[ERROR] Exception creating deployment: {e}")

    # Save backend info to S3 (for SaaS dashboard)
    if s3_bucket:
        try:
            s3 = boto3.client('s3')
            s3.put_object(
                Bucket=s3_bucket,
                Key=f"{rest_api_id}_routes.json",
                Body=json.dumps(routes_backends, indent=2),
                ContentType="application/json"
            )
            print(f"[DEBUG] routes_backends written to S3 bucket: {s3_bucket}")
        except Exception as e:
            print(f"[ERROR] Exception writing to S3: {e}")

    # Write backend info to local routes.json for proxy/interceptor use
    routes_path = get_routes_path()
    try:
        with open(routes_path, 'w', encoding='utf-8') as f:
            json.dump(routes_backends, f, indent=2)
        print(f"[DEBUG] Wrote routes to {routes_path}: {routes_backends}")
    except Exception as e:
        print(f"[ERROR] Error writing to {routes_path}: {e}")

    return routes_backends
