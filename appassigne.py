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

# Adatok betöltése a COS-ból
assignment_groups_data = load_data_from_cos('servicenow', 'global_assignment_groups')

@app.route('/dropdown', methods=['POST'])
def handle_dropdown():
    """Dropdown opciók lekérdezése vagy kiválasztás feldolgozása."""
    data = request.json
    action = data.get('action', 'getOptions')

    # Ha az opciók lekérdezése a cél
    if action == 'getOptions':
        return jsonify({
            "success": True,
            "message": "Available options retrieved",
            "labels": [group["name"] for group in assignment_groups_data],
            "values": [group["sys_id"] for group in assignment_groups_data]
        })

    # Ha egy konkrét opció kiválasztása történik
    elif action == 'select':
        selected_name = data.get('selectedOption')
        selected_group = next((group for group in assignment_groups_data if group["name"] == selected_name), None)

        if selected_group:
            return jsonify({
                "success": True,
                "message": f"Selected option ID: {selected_group['sys_id']} for {selected_name}"
            }), 200
        else:
            return jsonify({
                "success": False,
                "message": "Invalid option selected"
            }), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
