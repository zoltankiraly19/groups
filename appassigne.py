import json
import ibm_boto3
from botocore.config import Config
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# IBM COS konfiguráció és adatok betöltése
cos = ibm_boto3.client(
    's3',
    ibm_api_key_id='a2g6_5isBRzu-zm2vGL4ITcXhyL__rUe_RNWjGYVrkWr',
    ibm_service_instance_id='e669d0c8-4f96-478e-86bf-fd49039ff1f8',
    config=Config(signature_version='oauth'),
    endpoint_url='https://s3.us-south.cloud-object-storage.appdomain.cloud'
)

def load_data_from_cos(bucket_name, key):
    """Adatok betöltése IBM COS-ból."""
    try:
        response = cos.get_object(Bucket=bucket_name, Key=key)
        content = response['Body'].read().decode('utf-8')
        return json.loads(content)
    except Exception as e:
        print(f"Error loading {key} data: {e}")
        return []

# Adatok betöltése globális változókba
assignment_groups_data = load_data_from_cos('servicenow', 'global_assignment_groups')
priorities_data = load_data_from_cos('servicenow', 'global_priorities')

@app.route('/selections', methods=['GET'])
def get_selection_options():
    """Visszaadja az összes választható opciót."""
    return jsonify({
        "groups": assignment_groups_data,
        "priorities": priorities_data
    }), 200

@app.route('/selections', methods=['POST'])
def submit_selection():
    """Kiválasztott értékek feldolgozása és válasz küldése."""
    data = request.json
    selected_group_id = data.get('selectedGroupId')
    selected_priority = data.get('selectedPriority')

    # Kiválasztott csoport megkeresése
    selected_group = next(
        (group for group in assignment_groups_data if group['sys_id'] == selected_group_id),
        None
    )

    # Kiválasztott prioritás megkeresése
    selected_priority_obj = next(
        (priority for priority in priorities_data if priority['value'] == selected_priority),
        None
    )

    if selected_group and selected_priority_obj:
        return jsonify({
            "success": True,
            "selectedGroup": selected_group,
            "selectedPriority": selected_priority_obj
        }), 200
    else:
        return jsonify({
            "success": False,
            "message": "Invalid selection"
        }), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)