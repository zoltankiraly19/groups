from flask import Flask, jsonify, request
from flask_cors import CORS
import ibm_boto3
from ibm_botocore.config import Config
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
priorities_data = load_data_from_cos('servicenow', 'global_priorities')

DROPDOWN_OPTIONS = {
    "assignment_labels": [group["name"] for group in assignment_groups_data],
    "assignment_values": {group["name"]: group["sys_id"] for group in assignment_groups_data},
    "priority_labels": [priority["label"] for priority in priorities_data],
    "priority_values": {priority["label"]: priority["value"] for priority in priorities_data}
}

@app.route('/dropdown', methods=['POST'])
def submit_selected():
    """Felhasználói kiválasztás feldolgozása."""
    selected_assignment = request.json.get('selectedOption')
    selected_priority = request.json.get('selectedPriority')
    short_description = request.json.get('shortDescription', '')

    assignment_id = DROPDOWN_OPTIONS["assignment_values"].get(selected_assignment)
    priority_value = DROPDOWN_OPTIONS["priority_values"].get(selected_priority)

    if assignment_id and priority_value:
        return jsonify({
            "success": True,
            "message": f"Selected option ID: {assignment_id} for {selected_assignment} with priority {priority_value} and description provided.",
            "assignment_group_id": assignment_id,
            "priority_value": priority_value,
            "short_description": short_description
        }), 200
    else:
        return jsonify({
            "success": False,
            "message": "Invalid option selected"
        }), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
