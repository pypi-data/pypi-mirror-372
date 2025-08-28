'''
Configuration by environment
'''
from typing import Dict

APP_CONFIG: Dict[str, Dict[str, str]] = {
    'DEV': {
        'AMPLITUDE_REGION': 'US',
        'AMPLITUDE_API_KEY': 'ca863e91bfb3ce084e022920083f2898',
        'TELEMETRY_ACTIVE': 'false',
        'TELEMETRY_DRY_RUN': 'true',
    },
    'DEV_TWO': {
        'AMPLITUDE_REGION': 'US',
        'AMPLITUDE_API_KEY': 'ca863e91bfb3ce084e022920083f2898',
        'TELEMETRY_ACTIVE': 'false',
        'TELEMETRY_DRY_RUN': 'true',
    },
    'PLAYTEST': {
        'AMPLITUDE_REGION': 'US',
        'AMPLITUDE_API_KEY': 'ca863e91bfb3ce084e022920083f2898',
        'TELEMETRY_ACTIVE': 'false',
        'TELEMETRY_DRY_RUN': 'false',
    },
    'PROD': {
        'AMPLITUDE_REGION': 'US',
        'AMPLITUDE_API_KEY': '31fe2221f24fc30694cda777e98bd7a1',
        'TELEMETRY_ACTIVE': 'false',
        'TELEMETRY_DRY_RUN': 'false',
    }
}
