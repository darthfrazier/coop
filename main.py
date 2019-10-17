from flask import Flask, jsonify, request
from google.cloud import datastore

from util import match, profile

app = Flask(__name__)

# CRUD interface
@app.route('/CreateNewProfile', methods=['POST'])
def create_new_profile():
    datastore_client = datastore.Client()
    profile.create_new_profile(datastore_client, request.args['username'], request.get_json())
    return jsonify(success=True)

@app.route('/RetrieveProfile', methods=['GET'])
def retrieve_profile():
    datastore_client = datastore.Client()
    return jsonify(vars(profile.retrieve_profile(datastore_client, request.args['username'])))

@app.route('/UpdateProfile', methods=['PUT'])
def update_profile():
    datastore_client = datastore.Client()
    profile.update_profile(datastore_client, request.args['username'], request.get_json())
    return jsonify(success=True)

@app.route('/DeleteProfile', methods=['DELETE'])
def delete_profile():
    datastore_client = datastore.Client()
    profile.delete_profile(datastore_client, request.args['username'])
    return jsonify(success=True)

# Matchmaking
@app.route('/StartMatchmaking', methods=['POST'])
def start_matchmaking():
    datastore_client = datastore.Client()
    user_profile = profile.retrieve_profile(datastore_client, request.args['username'])
    return jsonify(match.start_matchmaking(request.args['username'], vars(user_profile), request.args['game'], request.args['use_voice_chat']))


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
