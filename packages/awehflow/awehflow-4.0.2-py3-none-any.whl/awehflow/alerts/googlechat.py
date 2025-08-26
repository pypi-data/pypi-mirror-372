from json import dumps
from httplib2 import Http
from airflow.hooks.base import BaseHook

from awehflow.alerts.base import Alerter


class GoogleChatAlerter(Alerter):
    def __init__(self, gchat_conn_id='gchat_default'):
        self.gchat_conn_id = gchat_conn_id

    def alert(self, context):
        client = Http()
        message_header = {'Content-Type': 'application/json; charset=UTF-8'}
        uri = BaseHook.get_connection(self.gchat_conn_id).password

        client.request(
            uri=uri,
            method='POST',
            headers=message_header,
            body=dumps(self.__generate_blocks(context)),
        )

    def __message_title(self, context):
        return context.get('name', 'alert').upper()

    def __message_header(self, context):
        if context.get('name', '') == 'success':
            return "*{}*".format(self.__message_title(context))
        else:
            return "*{} <users/all>*".format(self.__message_title(context))

    def __generate_message_body(self, items_dict):
        return {
            "widgets": [
                {
                    "keyValue": {
                        "topLabel": "{}".format(key),
                        "content": "{}".format(value),
                    },
                } for key, value in items_dict.items()]
        }

    def __message_body(self, context):
        if context['name'] == 'failure':
            items = {
                'DAG': context['body']['name'],
                'Task': context['body']['error']['task_id'],
                'Exception': context['body']['error']['message'],
            }
            if 'engineers' in context['body']:
                engineer_name = []
                for engineer in context['body']['engineers']:
                    if 'name' in engineer:
                        engineer_name.append(engineer['name'])
                if engineer_name:
                    items['Engineers'] = ', '.join(['{}'.format(engineer) for engineer in engineer_name])
        else:
            items = {key: context['body'][key] for key in context['body'].keys() if
                     key not in ['project', 'engineers', 'status']}

        return self.__generate_message_body(items)

    def __message_footer(self, context):
        return {
            "keyValue": {
                "topLabel": "Project",
                "content": "{}".format(context['body']['project'])
            }
        }

    def __message_url(self, context):
        if context['name'] == 'failure':
            return {
               "buttons": [
                   {
                       "textButton": {
                           "text": "VIEW LOGS",
                           "onClick": {
                               "openLink": {
                                   "url": "{}".format(context['body']['error']['log_url'])
                               }
                           }
                       }
                   }
               ]
            }
        else:
            return {}

    def __generate_blocks(self, context):
        blocks = {
            "cards": [
                {
                    "sections": [
                        self.__message_body(context),
                        {
                            "widgets": [
                                self.__message_footer(context)
                            ]
                        },
                        {
                            "widgets": [
                                self.__message_url(context),
                            ]
                        },
                    ]
                }
            ],
            "text": self.__message_header(context)
        }

        return blocks
