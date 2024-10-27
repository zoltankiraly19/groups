import json
import ibm_boto3
from botocore.config import Config
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


def load_data_from_cos(bucket_name, key):
    """Segédfüggvény adatok betöltéséhez az IBM COS-ból."""
    try:
        cos = ibm_boto3.client(
            's3',
            ibm_api_key_id='a2g6_5isBRzu-zm2vGL4ITcXhyL__rUe_RNWjGYVrkWr',
            ibm_service_instance_id='e669d0c8-4f96-478e-86bf-fd49039ff1f8',
            config=Config(signature_version='oauth'),
            endpoint_url='https://s3.us-south.cloud-object-storage.appdomain.cloud'
        )

        response = cos.get_object(
            Bucket=bucket_name,
            Key=key
        )

        content = response['Body'].read().decode('utf-8')
        return json.loads(content)  # JSON adat betöltése
    except Exception as e:
        print(f"Error loading {key} data: {e}")
        return []


# Dropdown adatok betöltése a felhőből
assignment_groups_data = load_data_from_cos('servicenow', 'global_assignment_groups')
priorities_data = load_data_from_cos('servicenow', 'global_priorities')

# Adatok előkészítése a frontend dropdown listákhoz
DROPDOWN_OPTIONS = {
    "assignment_groups": {
        "values": [group['sys_id'] for group in assignment_groups_data],
        "labels": [group['name'] for group in assignment_groups_data]
    },
    "priorities": {
        "values": [priority['value'] for priority in priorities_data],
        "labels": [priority['label'] for priority in priorities_data]
    }
}


@app.route('/dropdown', methods=['POST'])
def submit_selected():
    selected_group = request.json.get('selectedGroup')
    selected_priority = request.json.get('selectedPriority')

    group_valid = selected_group in DROPDOWN_OPTIONS["assignment_groups"]["values"]
    priority_valid = selected_priority in DROPDOWN_OPTIONS["priorities"]["values"]

    if group_valid and priority_valid:
        return jsonify({
            "success": True,
            "message": f"Selected group: {selected_group}, Selected priority: {selected_priority}"
        }), 200
    return jsonify({
        "success": False,
        "message": "Invalid option(s)"
    }), 400


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
