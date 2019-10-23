# Provide utility functions for interacting with user profiles
from google.cloud import datastore

class Profile():
    game_config_mapping = {
        'borderlands_3': {
            'max_level': 50,
        },
        'cyberpunk2077': {
            'max_level': 110
        },
        'modern_warfare': {
            'max_level': 60
        }
    }

    def __init__(self, existing_profile_data, is_new_profile=False):
        self.update_profile_attributes(existing_profile_data, is_new_profile)

    def update_profile_attributes(self, profile_data, is_new_profile=False):
        self._set_game_mapping(profile_data.get('game_level_mapping'), is_new_profile)
        self.discord_username = profile_data.get('discord_username')
        self.skype_username = profile_data.get('skype_username')
        self.steam_username = profile_data.get('steam_username')

    def _set_game_mapping(self, games_data, is_new_profile):
        if games_data is None and is_new_profile:
            raise Exception("Games level data required to create a profile")

        for game, level in games_data.items():
            if game not in self.game_config_mapping or level > self.game_config_mapping[game]['max_level']:
                raise Exception('Invalid user submitted games data')
        self.game_level_mapping = games_data


def construct_key(datastore_client, username):
    # Construct key
    kind = 'Profile'
    return datastore_client.key(kind, username)

def upload_profile(datastore_client, key, profile):
    # Create entity for write
    profile_entity = datastore.Entity(key=key)
    profile_entity['profile_data'] = vars(profile)

    # Write to datastore
    datastore_client.put(profile_entity)

def create_new_profile(datastore_client, username, profile_data, is_new_profile):
    key = construct_key(datastore_client, username)
    if datastore_client.get(key):
        raise Exception("Duplicate username for new profile")
    upload_profile(datastore_client, key, Profile(profile_data))

def retrieve_profile(datastore_client, username):
    key = construct_key(datastore_client, username)
    profile_entity = datastore_client.get(key)
    if not profile_entity:
        raise Exception("User not found")
    return Profile(profile_entity['profile_data'])

def update_profile(datastore_client, username, profile_data):
    existing_profile = retrieve_profile(datastore_client, username)
    existing_profile.update_profile_attributes(profile_data)
    upload_profile(datastore_client, construct_key(datastore_client, username), existing_profile)

def delete_profile(datastore_client, username):
    key = construct_key(datastore_client, username)
    datastore_client.delete(key)


