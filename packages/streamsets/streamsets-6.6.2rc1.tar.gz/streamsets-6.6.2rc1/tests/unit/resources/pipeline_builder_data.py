# List of tuples (<config_definition>, <expected default value>)
CONFIG_TYPE_TEST_CASES_JSON = [
    (
        {
            "fieldName": "Dummy",
            "name": "config.dummy",
            "type": "MODEL",
            "defaultValue": None,
            "model": {
                "labels": ["None"],
                "values": ["MANUAL"],
                "modelType": "FIELD_SELECTOR_MULTI_VALUE",
            },
        },
        [],
    ),
    (
        {
            "fieldName": "Dummy",
            "name": "config.dummy",
            "type": "MODEL",
            "defaultValue": None,
            "model": {
                "configDefinitions": [
                    {'name': 'config1', 'type': 'STRING', 'defaultValue': "default1"},
                    # Since there is no default value for config2, we don't expect this key to appear in the default.
                    {'name': 'config2', 'type': 'STRING', 'defaultValue': None},
                ],
                "modelType": "LIST_BEAN",
            },
        },
        [{'config1': 'default1'}],
    ),
    (
        {
            "fieldName": "Dummy",
            "name": "config.dummy",
            "type": "BOOLEAN",
            "defaultValue": None,
        },
        False,
    ),
    (
        {
            "fieldName": "Dummy",
            "name": "config.dummy",
            "type": "LIST",
            "defaultValue": None,
        },
        [],
    ),
    (
        {
            "fieldName": "Dummy",
            "name": "config.dummy",
            "type": "MAP",
            "defaultValue": None,
        },
        [],
    ),
]

PIPELINE_BUILDER_DEFINITIONS = {
    'services': [
        {
            'provides': 'com.streamsets.pipeline.api.service.dataformats.DataFormatParserService',
            'configDefinitions': [
                {
                    'label': 'JSON Content',
                    'name': 'dataFormatConfig.jsonContent',
                    'fieldName': 'jsonContent',
                    'type': 'MODEL',
                    'model': {
                        'labels': ['JSON array of objects', 'Multiple JSON objects'],
                        'values': [
                            'ARRAY_OBJECTS',
                            'MULTIPLE_OBJECTS',
                        ],
                        'modelType': 'VALUE_CHOOSER',
                    },
                },
                {
                    'label': 'Max Object Length (chars)',
                    'name': 'dataFormatConfig.jsonMaxObjectLen',
                    'fieldName': 'jsonMaxObjectLen',
                    'type': 'NUMBER',
                },
            ],
        },
    ]
}


PIPELINE_BUILDER_STAGE_DATA_DEFINITION = {
    'configDefinitions': [
        {
            'label': 'On Record Error',
            'fieldName': 'stageOnRecordError',
            'name': 'stageOnRecordError',
            'type': 'MODEL',
            'model': {
                'modelType': 'VALUE_CHOOSER',
                'labels': ['Discard', 'Send to Error', 'Stop Pipeline'],
                'values': ['DISCARD', 'TO_ERROR', 'STOP_PIPELINE'],
            },
        },
        {
            'label': 'Number of Threads',
            'fieldName': 'numberOfThreads',
            'name': 'numberOfThreads',
            'type': 'NUMBER',
        },
    ],
    'services': [
        {'service': 'com.streamsets.pipeline.api.service.dataformats.DataFormatParserService'},
    ],
}
