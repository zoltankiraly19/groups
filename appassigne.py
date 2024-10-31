from flask import Flask, jsonify, request
from flask_cors import CORS
import ibm_boto3
from ibm_botocore.config import Config
import requests
import json

app = Flask(__name__)
CORS(app)

# IBM COS konfiguráció
cos = ibm_boto3.client(
    's3',
    ibm_api_key_id='a2g6_5isBRzu-zm2vGL4ITcXhyL__rUe_RNWjGYVrkWr',
    ibm_service_instance_id='e669d0c8-4f96-478e-86bf-fd49039ff1f8',
    config=Config(signature_version='oauth'),
    endpoint_url='https://s3.us-south.cloud-object-storage.appdomain.cloud'
)

def load_data_from_cos(bucket_name, file_key):
    """Adatok betöltése IBM COS-ból."""
    try:
        response = cos.get_object(Bucket=bucket_name, Key=file_key)
        content = response['Body'].read().decode('utf-8')
        return json.loads(content)
    except Exception as e:
        print(f"Error loading {file_key} data: {e}")
        return []

# Adatok betöltése a COS-ból és különválasztása
assignment_groups_data = load_data_from_cos('servicenow', 'global_assignment_groups')
DROPDOWN_OPTIONS = {
    "labels": [group["name"] for group in assignment_groups_data],
    "values": {group["name"]: group["sys_id"] for group in assignment_groups_data}
}

@app.route('/dropdown', methods=['POST'])
def submit_selected():
    """Felhasználói kiválasztás és jegy létrehozása egyetlen hívással."""
    data = request.json
    selected_label = data.get('selectedOption')
    selected_value = DROPDOWN_OPTIONS["values"].get(selected_label)
    priority = data.get('priority')
    short_description = data.get('short_description')
    user_token = data.get('user_token')  # A felhasználói token

    if not selected_value:
        return jsonify({
            "success": False,
            "message": "Invalid assignment group selection"
        }), 400

    # Jegy adatok ServiceNow-ba történő küldéshez
    ticket_data = {
        "short_description": short_description,
        "assignment_group": selected_value,
        "priority": priority
    }

    # ServiceNow API hívás a jegy létrehozásához
    headers = {
        'Authorization': f'Bearer {user_token}',
        'Content-Type': 'application/json'
    }
    response = requests.post(
        'https://dev227667.service-now.com/api/now/table/incident',
        headers=headers,
        json=ticket_data
    )

    if response.status_code == 201:
        return jsonify({
            "success": True,
            "message": f"Ticket created successfully with ID: {response.json().get('result', {}).get('number')}",
            "selected_option": selected_label,
            "assignment_group_id": selected_value
        }), 201
    else:
        return jsonify({
            "success": False,
            "message": "Failed to create ticket",
            "details": response.text
        }), response.status_code

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
