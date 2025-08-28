'''
This file contains the hashes / list constants
'''
from typing import Dict, List

CLIENT_SDK_TYPES: Dict[str, Dict[str, str]] = {
    'unity': {
        'type': 'csharp',
        'subtype': 'unity',
        'http-lib': ['httpclient', 'unitywebrequest', 'restsharp'],
    },
    'unreal': {
        'type': 'cpp-ue4',
        'subtype': 'unreal',
        'http-lib': [],
    },
    'roblox': {
        'type': 'lua',
        'subtype': 'roblox',
        'http-lib': [],
    },
    'godot-csharp': {
        'type': 'csharp',
        'subtype': 'godot',
        'http-lib': [],
    },
    'godot-cpp': {
        'type': 'cpp-restsdk',
        'subtype': 'godot',
        'http-lib': [],
    },
    'cocos': {
        'type': 'cpp-restsdk',
        'subtype': 'cocos',
        'http-lib': [],
    },
    'ios-objc': {
        'type': 'objc',
        'subtype': 'ios',
        'http-lib': [],
    },
    'ios-swift': {
        'type': 'swift5',
        'subtype': 'ios',
        'http-lib': [],
    },
    'android-java': {
        'type': 'android',
        'subtype': 'android',
        'http-lib': [],
    },
    'android-kotlin': {
        'type': 'android',
        'subtype': 'android',
        'http-lib': [],
    },
    'web-ts': {
        'type': 'typescript',
        'subtype': 'web',
        'http-lib': ['axios', 'fetch'],
    },
    'web-js': {
        'type': 'javascript',
        'subtype': 'web',
        'http-lib': [],
    },
}

SERVER_SDK_TYPES: Dict[str, Dict[str, str]] = {
    'csharp': {
        'type': 'csharp',
        'subtype': '',
        'http-lib': ['httpclient', 'restsharp'],
    },
    'cpp': {
        'type': 'cpp-restsdk',
        'subtype': '',
        'http-lib': [],
    },
    'lua': {
        'type': 'lua',
        'subtype': '',
        'http-lib': [],
    },
    'ts': {
        'type': 'typescript',
        'subtype': '',
        'http-lib': ['axios', 'fetch'],
    },
    'go': {
        'type': 'go',
        'subtype': '',
        'http-lib': [],
    },
    'python': {
        'type': 'python',
        'subtype': '',
        'http-lib': [],
    },
    'kotlin': {
        'type': 'kotlin',
        'subtype': '',
        'http-lib': [],
    },
    'java': {
        'type': 'java',
        'subtype': '',
        'http-lib': [],
    },
    'c': {
        'type': 'c',
        'subtype': '',
        'http-lib': [],
    },
    'node': {
        'type': 'typescript-node',
        'subtype': '',
        'http-lib': [],
    },
    'js': {
        'type': 'javascript',
        'subtype': '',
        'http-lib': [],
    },
    'perl': {
        'type': 'perl',
        'subtype': '',
        'http-lib': [],
    },
    'php': {
        'type': 'php',
        'subtype': '',
        'http-lib': [],
    },
    'clojure': {
        'type': 'clojure',
        'subtype': '',
        'http-lib': [],
    },
    'ruby': {
        'type': 'ruby',
        'subtype': '',
        'http-lib': [],
    },
    'rust': {
        'type': 'rust',
        'subtype': '',
        'http-lib': [],
    },
}

SDK_TYPES: Dict[str, Dict[str, str]] = {**CLIENT_SDK_TYPES, **SERVER_SDK_TYPES}

PROTOS_TYPES: Dict[str, Dict[str, str]] = {
    'cpp': {
        'type': 'cpp',
        'subtype': '',
    },
    'csharp': {
        'type': 'csharp',
        'subtype': '',
    },
    'go': {
        'type': 'go',
        'subtype': '',
    },
    'raw': {
        'type': 'raw',
        'subtype': '',
    },
}

SNAPEND_MANIFEST_TYPES: Dict[str, Dict[str, str]] = {
    'json': {
        'type': 'json',
        'subtype': '',
    },
    'yaml': {
        'type': 'yaml',
        'subtype': '',
    },
}

SERVICE_IDS: List[str] = [
    'analytics', 'auth', 'client-logs', 'events', 'experiments', 'gdpr', 'guilds', 'hades', 'iap',
    'inventory', 'leaderboards', 'matchmaking', 'notifications', 'parties', 'profiles', 'quests',
    'relay', 'remote-config', 'scheduler', 'sequencer', 'social-graph', 'statistics', 'storage',
    'trackables', 'xp'
]

SDK_ACCESS_AUTH_TYPE_LOOKUP: Dict[str, Dict[str, str]] = {
    # 'omni': {
    #     'access_type': 'external',
    #     'auth_type': 'omni'
    # },
    'user': {
        'access_type': 'external',
        'auth_type': 'user'
    },
    'api-key': {
        'access_type': 'external',
        'auth_type': 'api-key'
    },
    'internal': {
        'access_type': 'internal',
    },
    'app': {
        'access_type': 'external',
        'auth_type': 'app'
    },
}

DEFAULT_BYOSNAP_DEV_TEMPLATE: Dict[str, object] = {
    'cpu': 100,
    'memory': 0.125,
    'min_replicas': 1,
    'cmd': '',
    'args': [],
    'env_params': [{'key': "SNAPSER_ENVIRONMENT", 'value': "DEVELOPMENT"}]
}

DEFAULT_BYOSNAP_STAGE_TEMPLATE: Dict[str, object] = {
    'cpu': 100,
    'memory': 0.125,
    'min_replicas': 1,
    'cmd': '',
    'args': [],
    'env_params': [{'key': "SNAPSER_ENVIRONMENT", 'value': "STAGING"}]
}

DEFAULT_BYOSNAP_PROD_TEMPLATE: Dict[str, object] = {
    'cpu': 100,
    'memory': 0.125,
    'min_replicas': 2,
    'cmd': '',
    'args': [],
    'env_params': [{'key': "SNAPSER_ENVIRONMENT", 'value': "PRODUCTION"}]
}

ARCHITECTURE_MAPPING: Dict[str, str] = {
    'x86_64': 'amd64',
    'arm64': 'arm64',
    'aarch64': 'arm64',
    'amd64': 'amd64'
}
