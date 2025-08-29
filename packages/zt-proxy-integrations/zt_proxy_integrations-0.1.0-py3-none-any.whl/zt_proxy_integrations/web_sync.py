from flask import Flask, request, render_template_string
import json
import os

from aws.sync import sync_apigateway_routes as aws_sync
from aws.revert import revert_apigateway_routes as aws_revert
from azure.sync import sync_azure_apim_routes as azure_sync
from azure.revert import revert_azure_apim_routes as azure_revert
from kong.sync import sync_kong_routes as kong_sync
from kong.revert import revert_kong_routes as kong_revert
from apigee.sync import sync_apigee_routes as apigee_sync
from apigee.revert import revert_apigee_routes as apigee_revert

app = Flask(__name__)

HTML_FORM = """
<h2>API Gateway Route Sync</h2>
<form method="post" action="/sync" id="sync-form">
  Provider:
  <select name="provider" id="provider-sync">
    <option value="aws">AWS</option>
    <option value="azure">Azure</option>
    <option value="kong">Kong</option>
    <option value="apigee">Apigee</option>
  </select><br>
  <div class="provider-fields" id="aws-fields-sync">
    AWS API Gateway ID: <input name="rest_api_id"><br>
    Ngrok Domain: <input name="ngrok_domain"><br>
    S3 Bucket (optional): <input name="s3_bucket"><br>
  </div>
  <div class="provider-fields" id="azure-fields-sync" style="display:none;">
    Resource Group: <input name="resource_group"><br>
    APIM Service Name: <input name="service_name"><br>
    Proxy Domain: <input name="proxy_domain_azure"><br>
    Subscription ID (optional): <input name="subscription_id"><br>
    Revision (optional): <input name="revision"><br>
  </div>
  <div class="provider-fields" id="kong-fields-sync" style="display:none;">
    Kong Admin API URL: <input name="admin_api_url"><br>
    Proxy Domain: <input name="proxy_domain_kong"><br>
    Kong API Key (optional): <input name="kong_api_key"><br>
    Control Plane ID: <input name="control_plane_id"><br>
  </div>
  <div class="provider-fields" id="apigee-fields-sync" style="display:none;">
    Apigee Organization: <input name="org"><br>
    Proxy Domain: <input name="proxy_domain_custom"><br>
    Access Token: <input name="access_token"><br>
  </div>
  <button type="submit">Sync Routes</button>
</form>
{% if sync_message %}
  <div style="color: green;">{{ sync_message }}</div>
{% endif %}
<br>
<h2>Revert API Gateway Routes</h2>
<form method="post" action="/revert" id="revert-form">
  Provider:
  <select name="provider" id="provider-revert">
    <option value="aws">AWS</option>
    <option value="azure">Azure</option>
    <option value="kong">Kong</option>
    <option value="apigee">Apigee</option>
  </select><br>
  <div class="provider-fields" id="aws-fields-revert">
    AWS API Gateway ID: <input name="rest_api_id"><br>
  </div>
  <div class="provider-fields" id="azure-fields-revert" style="display:none;">
    Resource Group: <input name="resource_group"><br>
    APIM Service Name: <input name="service_name"><br>
    Proxy Domain: <input name="proxy_domain_azure"><br>
    Subscription ID (optional): <input name="subscription_id"><br>
    Revision (optional): <input name="revision"><br>
  </div>
  <div class="provider-fields" id="kong-fields-revert" style="display:none;">
    Kong Admin API URL: <input name="admin_api_url"><br>
    Proxy Domain: <input name="proxy_domain_kong"><br>
    Kong API Key (optional): <input name="kong_api_key"><br>
    Control Plane ID: <input name="control_plane_id"><br>
  </div>
  <div class="provider-fields" id="apigee-fields-revert" style="display:none;">
    Apigee Organization: <input name="org"><br>
    Access Token: <input name="access_token"><br>
  </div>
  <button type="submit">Revert Routes</button>
</form>
{% if revert_message %}
  <div style="color: green;">{{ revert_message }}</div>
{% endif %}
<script>
function updateFields(formId, selectId, suffix) {
  var provider = document.getElementById(selectId).value;
  var fields = document.querySelectorAll('#' + formId + ' .provider-fields');
  fields.forEach(function(div) {
    div.style.display = "none";
  });
  var active = document.getElementById(provider + '-fields-' + suffix);
  if (active) active.style.display = "";
}
document.addEventListener("DOMContentLoaded", function() {
  updateFields("sync-form", "provider-sync", "sync");
  updateFields("revert-form", "provider-revert", "revert");
  document.getElementById("provider-sync").addEventListener("change", function() {
    updateFields("sync-form", "provider-sync", "sync");
  });
  document.getElementById("provider-revert").addEventListener("change", function() {
    updateFields("revert-form", "provider-revert", "revert");
  });
});
</script>
"""

@app.route("/", methods=["GET"])
def index():
    return render_template_string(HTML_FORM)

@app.route("/sync", methods=["POST"])
def sync():
    provider = request.form["provider"]
    sync_message = ""
    try:
        if provider == "aws":
            rest_api_id = request.form["rest_api_id"]
            ngrok_domain = request.form["ngrok_domain"]
            s3_bucket = request.form.get("s3_bucket") or None
            if not rest_api_id or not ngrok_domain:
                raise ValueError("AWS API Gateway ID and Ngrok Domain are required.")
            routes = aws_sync(rest_api_id, ngrok_domain, s3_bucket=s3_bucket)
        elif provider == "azure":
            resource_group = request.form["resource_group"]
            service_name = request.form["service_name"]
            proxy_domain = request.form.get("proxy_domain_azure", "").strip()
            subscription_id = request.form.get("subscription_id") or None
            revision = request.form.get("revision") or None
            if not resource_group or not service_name or not proxy_domain:
                raise ValueError("Resource Group, APIM Service Name, and Proxy Domain are required for Azure sync.")
            routes = azure_sync(resource_group, service_name, proxy_domain, subscription_id)
        elif provider == "kong":
            admin_api_url = request.form["admin_api_url"]
            proxy_domain = request.form.get("proxy_domain_kong", "").strip()
            kong_api_key = request.form.get("kong_api_key") or None
            control_plane_id = request.form["control_plane_id"]
            print(f"[DEBUG] Kong sync: admin_api_url={admin_api_url}, control_plane_id={control_plane_id}, proxy_domain={proxy_domain}, kong_api_key={kong_api_key}")
            if not proxy_domain or not control_plane_id or not admin_api_url:
                raise ValueError("Proxy Domain, Control Plane ID, and Admin API URL are required for Kong sync.")
            routes = kong_sync(admin_api_url, control_plane_id, proxy_domain, kong_api_key)
        elif provider == "apigee":
            org = request.form["org"]
            proxy_domain = request.form.get("proxy_domain_custom", "").strip()
            access_token = request.form["access_token"]
            if not org or not proxy_domain or not access_token:
                raise ValueError("Organization, Proxy Domain, and Access Token are required for Apigee sync.")
            routes = apigee_sync(org, proxy_domain, access_token)
        else:
            routes = {}
        sync_message = "Sync successful! Routes updated." if routes else "No routes found or sync failed."
    except Exception as e:
        sync_message = f"Sync error: {e}"
    return render_template_string(HTML_FORM, sync_message=sync_message)

@app.route("/revert", methods=["POST"])
def revert():
    provider = request.form["provider"]
    revert_message = ""
    try:
        if provider == "aws":
            rest_api_id = request.form["rest_api_id"]
            routes_path = os.path.join(os.path.abspath(os.getcwd()), 'interceptor', 'routes.json')
            if os.path.exists(routes_path):
                with open(routes_path, 'r', encoding='utf-8') as f:
                    routes_backends = json.load(f)
            else:
                routes_backends = {}
            result = aws_revert(rest_api_id, routes_backends)
        elif provider == "azure":
            resource_group = request.form["resource_group"]
            service_name = request.form["service_name"]
            proxy_domain = request.form.get("proxy_domain_azure") or None
            subscription_id = request.form.get("subscription_id") or None
            revision = request.form.get("revision") or None
            result = azure_revert(resource_group, service_name, subscription_id)
        elif provider == "kong":
            admin_api_url = request.form["admin_api_url"]
            kong_api_key = request.form.get("kong_api_key") or None
            proxy_domain = request.form.get("proxy_domain_kong") or None
            print(f"[DEBUG] Kong revert: admin_api_url={admin_api_url}, proxy_domain={proxy_domain}, kong_api_key={kong_api_key}")
            result = kong_revert(admin_api_url, kong_api_key, proxy_domain)
        elif provider == "apigee":
            org = request.form["org"]
            access_token = request.form["access_token"]
            result = apigee_revert(org, access_token)
        else:
            result = {"status": "error"}
        if result.get("status") == "done":
            revert_message = "Revert successful! Routes restored."
        else:
            revert_message = "Revert failed."
    except Exception as e:
        revert_message = f"Revert error: {e}"
    return render_template_string(HTML_FORM, revert_message=revert_message)

if __name__ == "__main__":
    app.run(port=5000)
if __name__ == "__main__":
    app.run(port=5000)
