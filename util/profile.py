# Provide utility functions for interacting with user profiles
from google.cloud import datastore

class Profile():
    def __init__(self, existing_profile_data):
        self.update_profile_attributes(existing_profile_data)

    def update_profile_attributes(self, profile_data):
        self._set_game(profile_data.get('game'))
        self._set_level(profile_data.get('level'))
        self._set_level_match_limit(profile_data.get('level_match_limit'))
        self._set_discord_chat(profile_data.get('discord_chat'))
        self._set_skype_chat(profile_data.get('skype_chat'))
        self._set_ingame_chat(profile_data.get('ingame_chat'))

    def _set_game(self, game):
        # Validate game from config
        self.game = game

    def _set_level(self, level):
        # Validate level according to game config
        self.level = level

    def _set_level_match_limit(self, level_match_limit):
        # Validate level according to game config
        self.level_match_limit = level_match_limit

    def _set_discord_chat(self, discord_chat):
        if discord_chat is not None and not isinstance(discord_chat, bool):
            raise Exception("Invalid discord_chat value. Should be boolean")
        self.discord_chat = discord_chat

    def _set_skype_chat(self, skype_chat):
        if skype_chat is not None and not isinstance(skype_chat, bool):
            raise Exception("Invalid skype_chat value. Should be boolean")
        self.skype_chat = skype_chat

    def _set_ingame_chat(self, ingame_chat):
        if ingame_chat is not None and not isinstance(ingame_chat, bool):
            raise Exception("Invalid ingame_chat value. Should be boolean")
        self.ingame_chat = ingame_chat


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

def create_new_profile(datastore_client, username, profile_data):
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


