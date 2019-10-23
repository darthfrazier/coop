import os
import pylibmc as memcache

MEMCACHE_SERVER = os.environ.get('MEMCACHE_SERVER', 'localhost:11211')
MEMCACHE_USERNAME = os.environ.get('MEMCACHE_USERNAME')
MEMCACHE_PASSWORD = os.environ.get('MEMCACHE_PASSWORD')

class Match():
    default_level_match_buffers = {
        'borderlands_3': 10,
        'cyberpunk2077': 2,
        'modern_warfare': 5,
    }

    def __init__(self, session):
        self._session = session if session is not None else {}

    def add_user_to_session(self, username, user_profile):
        self._session[username] = user_profile

    def find_match(self, user_profile, game, level_match_buffer, use_voice_chat):
        if not self._session:
            return None, None

        matched_profile = None
        matched_username = None
        for username, profile in self._session.items():
            if self._is_match(user_profile, profile, game, level_match_buffer, use_voice_chat):
                matched_profile = profile
                matched_username = username
                self._session.pop(matched_username)
                break

        return matched_username, matched_profile

    def _is_match(self, user_profile, potential_match, game, level_match_buffer, use_voice_chat):
        level_match_buffer = level_match_buffer if level_match_buffer is not None else self.default_level_match_buffers[game]
        user_level = user_profile.get('game_level_mapping').get(game)
        potential_match_level = potential_match.get('game_level_mapping').get(game)
        if user_level is None or potential_match_level is None:
            return False
        level_upper_bound = user_level + level_match_buffer
        level_lower_bound = user_level - level_match_buffer
        if potential_match_level < level_lower_bound or potential_match_level > level_upper_bound:
            return False

        if use_voice_chat != potential_match.get('use_voice_chat'):
            return False

        return True

    def get_session(self):
        return self._session

def start_matchmaking(username, user_profile, game, level_match_buffer, use_voice_chat):
    memcache_client = memcache.Client([MEMCACHE_SERVER], binary=True,
                                      username=MEMCACHE_USERNAME, password=MEMCACHE_PASSWORD)

    match_session = Match(memcache_client.get(game))
    matched_username, matched_profile = match_session.find_match(user_profile, game, level_match_buffer, use_voice_chat)

    game_session = None
    if not matched_profile:
        user_profile['use_voice_chat'] = use_voice_chat
        match_session.add_user_to_session(username, user_profile)
    else:
        game_session = {username: user_profile, matched_username: matched_profile}
    if not memcache_client.set(game, match_session.get_session()):
        raise Exception("Failed to update matchmaking session")

    return game_session


