import requests
import json

# -----------------------------
# CONFIGURATION
# -----------------------------
superset_url = ""
dashboard_id = 47
new_datasource_id = 118
new_datasource_type = "table"
username = "username"
password = "pasword"

# -----------------------------
# SESSION WITH COOKIES
# -----------------------------
session = requests.Session()

# STEP 1: LOGIN
login_url = f"{superset_url}/api/v1/security/login"
credentials = {
    "username": username,
    "password": password,
    "provider": "db",
    "refresh": True
}

login_response = session.post(login_url, json=credentials)
if login_response.status_code != 200:
    print("❌ Login failed")
    print(login_response.text)
    exit()

access_token = login_response.json()["access_token"]
print("✅ Logged in. Token acquired.")

# STEP 2: GET CSRF TOKEN
csrf_response = session.get(
    f"{superset_url}/api/v1/security/csrf_token/",
    headers={"Authorization": f"Bearer {access_token}"}
)

if csrf_response.status_code != 200:
    print("❌ Failed to fetch CSRF token")
    print(csrf_response.text)
    exit()

csrf_token = csrf_response.json()["result"]
print("✅ CSRF token acquired.")

# Common headers for all requests
headers = {
    "Authorization": f"Bearer {access_token}",
    "X-CSRFToken": csrf_token,
    "Content-Type": "application/json"
}

# STEP 3: GET CHART IDs FROM DASHBOARD
dashboard_url = f"{superset_url}/api/v1/dashboard/{dashboard_id}"
response = session.get(dashboard_url, headers=headers)

if response.status_code != 200:
    print("❌ Failed to fetch dashboard.")
    exit()

dashboard_data = response.json()
position_json = dashboard_data["result"].get("position_json", "{}")
position_data = json.loads(position_json) if isinstance(position_json, str) else position_json

chart_ids = []
for key, value in position_data.items():
    if isinstance(value, dict) and value.get("type") == "CHART" and "meta" in value:
        chart_id = value["meta"].get("chartId")
        if chart_id:
            chart_ids.append(chart_id)

print(f"✅ Found {len(chart_ids)} charts: {chart_ids}")

# STEP 4: FETCH AND UPDATE CHARTS
for chart_id in chart_ids:
    chart_url = f"{superset_url}/api/v1/chart/{chart_id}"
    get_response = session.get(chart_url, headers=headers)

    if get_response.status_code != 200:
        print(f"❌ Failed to fetch chart {chart_id}")
        continue

    chart_data = get_response.json()["result"]

    # Extract current datasource info
    datasource_id = None
    datasource_type = None
    ds_string = chart_data.get("datasource")
    if ds_string and "__" in ds_string:
        datasource_id, datasource_type = ds_string.split("__")

    print(f"\n🔍 Chart ID: {chart_id}")
    print(f" - Name: {chart_data.get('slice_name', 'N/A')}")
    print(f" - Viz Type: {chart_data.get('viz_type', 'N/A')}")
    print(f" - Old Datasource: {datasource_id or 'N/A'}__{datasource_type or 'N/A'}")

    # Update chart config
    chart_data["datasource_id"] = new_datasource_id
    chart_data["datasource_type"] = new_datasource_type

    # Update 'params'
    if "params" in chart_data:
        try:
            params_data = json.loads(chart_data["params"])
            params_data["datasource"] = f"{new_datasource_id}__{new_datasource_type}"
            chart_data["params"] = json.dumps(params_data)
        except Exception as e:
            print(f"⚠️ Error parsing params for chart {chart_id}: {e}")

    # Update 'query_context'
    if "query_context" in chart_data:
        try:
            qc_data = json.loads(chart_data["query_context"])
            if "datasource" in qc_data:
                qc_data["datasource"]["id"] = new_datasource_id
                qc_data["datasource"]["type"] = new_datasource_type
            if "form_data" in qc_data:
                qc_data["form_data"]["datasource"] = f"{new_datasource_id}__{new_datasource_type}"
            chart_data["query_context"] = json.dumps(qc_data)
        except Exception as e:
            print(f"⚠️ Error parsing query_context for chart {chart_id}: {e}")

    # Remove non-editable fields
    for field in [
        "id", "url", "thumbnail_url", "changed_on_delta_humanized",
        "dashboards", "owners"
    ]:
        chart_data.pop(field, None)

    # PUT update
    update_response = session.put(chart_url, headers=headers, json=chart_data)

    if update_response.status_code == 200:
        print(f"✅ Updated chart {chart_id} to {new_datasource_id}__{new_datasource_type}")
    else:
        print(f"❌ Failed to update chart {chart_id}")
        print(update_response.text)
