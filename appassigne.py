import json
import ibm_boto3
from botocore.config import Config
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def load_group_data():
    try:
        cos = ibm_boto3.client(
            's3',
            ibm_api_key_id='a2g6_5isBRzu-zm2vGL4ITcXhyL__rUe_RNWjGYVrkWr',
            ibm_service_instance_id='e669d0c8-4f96-478e-86bf-fd49039ff1f8',
            config=Config(signature_version='oauth'),
            endpoint_url='https://s3.us-south.cloud-object-storage.appdomain.cloud'
        )
        
        response = cos.get_object(
            Bucket='servicenow',
            Key='admin_assignment_groups.txt'
        )
        
        data = json.loads(response['Body'].read().decode('utf-8'))
        return {
            "values": [group['sys_id'] for group in data],
            "labels": [group['name'] for group in data]
        }
    except Exception as e:
        print(f"Error loading data: {e}")
        return {"values": [], "labels": []}

DROPDOWN_OPTIONS = load_group_data()

@app.route('/dropdown', methods=['POST'])
def submit_selected():
    selected = request.json.get('selectedOption')
    if selected in DROPDOWN_OPTIONS["values"]:
        return jsonify({
            "success": True,
            "message": f"Selected option: {selected}"
        }), 200
    return jsonify({
        "success": False,
        "message": "Invalid option"
    }), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)