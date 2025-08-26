import datetime
from unittest import TestCase

import pendulum

from awehflow.config import Config


class TestConfig(TestCase):

    def setUp(self):
        self.dummy_config_dict = {
            'name': 'some_name',
            'version': 2,
            'start_date': '2020-03-29',
            'schedule': '30 23 * * *',
            'catchup': True,
            'timezone': 'Africa/Johannesburg',
            'engineers': [
                {
                    'name': 'John Doe',
                    'slack': 'johndoe'
                }
            ],
            'params': {
                'default': {
                    'var1': 'var1 value',
                    'var2': 'var2 value'
                },
                'prod': {
                    'var2': 'var2 prod value'
                }
            },
            'tasks': [
                {
                    'id': 'stage_1',
                    'operator': 'airflow.operators.bash_operator.BashOperator',
                    'params': {
                        'bash_command': 'echo "hello world"'
                    }
                }
            ]
        }

    def test_config_init(self):
        config = Config(self.dummy_config_dict)

        self.assertEqual(config.get('name'), 'some_name')
        self.assertEqual(config.get('dag_id'), 'some_name_v2')
        self.assertEqual(config.get('start_date'),
                         datetime.datetime(2020, 3, 29, tzinfo=pendulum.timezone('Africa/Johannesburg')))
        self.assertEqual(config.get('schedule'), '30 23 * * *')
        self.assertEqual(config.get('engineers.0.name'), 'John Doe')
        self.assertEqual(config.get('engineers.0.slack'), 'johndoe')
        self.assertEqual(config.get('params.var1'), 'var1 value')
        self.assertEqual(config.get('params.var2'), 'var2 value')
        self.assertEqual(config.get('catchup'), True)
        self.assertEqual(config.get('default_dag_args'), {})

    def test_variables_prod(self):
        config = Config(self.dummy_config_dict, environment='prod')

        self.assertEqual(config.get('params.var1'), 'var1 value')
        self.assertEqual(config.get('params.var2'), 'var2 prod value')

