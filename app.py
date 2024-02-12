from flask import Flask, request, jsonify, render_template
from elasticsearch import Elasticsearch, helpers
import json

app = Flask(__name__)

es = Elasticsearch([{'host': 'elasticsearch', 'port': 9200, "scheme": "http"}], verify_certs=False)


@app.route('/create_index', methods=['POST'])
def create_index():
    index_name = request.json.get('index_name')
    if not index_name:
        return jsonify({'error': 'Index name not provided'}), 400

    field_mappings = {}
    if index_name == 'pincode_data':
        field_mappings = {
            "properties": {
                "postal_code": {"type": "integer"},
                "name": {"type": "search_as_you_type"},
                "state": {"type": "search_as_you_type"},
                "latitude": {"type": "float"},
                "longitude": {"type": "float"}
            }
        }
    elif index_name == 'location_data':
        field_mappings = {
            "properties": {
                "geonameid": {"type": "integer"},
                "name": {"type": "search_as_you_type"},
                "state": {"type": "search_as_you_type"},
                "asciiname": {"type": "search_as_you_type"},
                "alternatenames": {"type": "search_as_you_type"},
                "latitude": {"type": "float"},
                "longitude": {"type": "float"},
                "feature_class": {"type": "keyword"},
                "feature_code": {"type": "keyword"}
            }
        }

    # Create index with field mappings
    if es.indices.exists(index=index_name):
        return jsonify({'error': f'Index {index_name} already exists'}), 400
    es.indices.create(index=index_name, body={"mappings": field_mappings})
    return jsonify({'message': f'Index {index_name} created successfully'}), 200


@app.route('/add_data', methods=['POST'])
def add_data():
    index_name = request.json.get('index_name')

    if index_name == 'pincode_data':
        with open('documents/pincode_data.json', 'r') as file:
            data_list = json.load(file)
    elif index_name == 'location_data':
        with open('documents/location_data.json', 'r') as file:
            data_list = json.load(file)

    if not index_name or not data_list:
        return jsonify({'error': 'Index name or data not provided'}), 400
    actions = [
        {
            "_index": index_name,
            "_source": doc
        }
        for doc in data_list
    ]
    try:
        res = helpers.bulk(es, actions)
        return jsonify({'message': f'{res[0]} documents added successfully'}), 200
    except Exception as e:
        return jsonify({'error': f'Error adding documents: {str(e)}'}), 500


@app.route('/search', methods=['GET'])
def search_location():
    search_token = request.args.get('q')

    if not search_token:
        return jsonify({'error': 'No search token provided'}), 400

    field_mappings = {
        "pincode_data": ["name", "state"],
        "location_data": ["name", "state", "asciiname", "alternatenames"]
    }

    should_conditions = []
    for fields in field_mappings.values():
        for field in fields:
            should_conditions.append({
                "bool": {
                    "should": [
                        {"term": {field: search_token}},

                        {"match_phrase": {field: {"query": search_token, "boost": 2}}},

                        {"prefix": {field: {"value": search_token, "boost": 1.5}}},

                        {"match": {"alternatenames": {"query": search_token, "fuzziness": "AUTO"}}}
                    ]
                }
            })

    search_query = {
        "query": {
            "bool": {
                "should": should_conditions
            }
        }
    }

    res = es.search(index=list(field_mappings.keys()), body=search_query)

    formatted_results = []
    for hit in res['hits']['hits']:
        entity_type = hit['_index']
        entity_data = hit['_source']
        latitude = entity_data.get('latitude', 'Unknown')
        longitude = entity_data.get('longitude', 'Unknown')

        formatted_result = {}

        if entity_type == 'pincode_data':
            normalized_data = {
                "latitude": latitude,
                "longitude": longitude,
                "geoId": "XXX",
                "City": entity_data.get('name', 'Unknown'),
                "State": entity_data.get('state', 'Unknown')
            }
            formatted_result = {
                "entity_type": "pincode",
                "entity_name": entity_data.get('postal code'),
                "latitude": latitude,
                "longitude": longitude,
                "normalized": normalized_data
            }
        elif entity_type == 'location_data':
            feature_class = entity_data.get('feature_class', '').lower()
            entity_name = entity_data.get('name') or 'Unknown'
            normalized_data = {
                "latitude": latitude,
                "longitude": longitude,
                "geoId": entity_data.get('geonameid', 'Unknown'),
                "City": entity_data.get('asciiname', 'Unknown'),
                "State": entity_data.get('state', 'Unknown')
            }
            formatted_result = {
                "entity_type": feature_class,
                "entity_name": entity_name,
                "latitude": latitude,
                "longitude": longitude,
                "normalized": normalized_data
            }

        formatted_results.append(formatted_result)

    return jsonify(formatted_results)


@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('index.html')


app.run(host='0.0.0.0', port=5001)
