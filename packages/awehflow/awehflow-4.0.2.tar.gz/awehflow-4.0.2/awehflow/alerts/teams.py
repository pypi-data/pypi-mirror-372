import requests

from awehflow.alerts.base import Alerter
from airflow.hooks.base import BaseHook

class MSTeamsAlerter(Alerter):
    """Sends an adaptive card message to microsoft teams"""
    def __init__(self, ms_teams_conn_id: str):
        self.ms_teams_conn_id=ms_teams_conn_id
   
    def alert(self, context):
        
        headers = {"content-type": "application/json"}
        requests.post(
            url=BaseHook.get_connection(self.ms_teams_conn_id).password,
            json=self.__build_message(context), 
            headers=headers
        )

    def __build_message(self, context) -> dict:

        alert_level = context['name'].upper()
        entities = []

        if alert_level == 'FAILURE':
            dag_id = context['body']['name']
            task_id = context['body']['error']['task_id']
            log_url = context['body']['error']['log_url']
            message_body=context['body']['error']['message']
            heading_color="attention"
            if 'engineers' in context['body']:
                engineers=[
                    {
                        'name': engineer['name'],
                        'email': engineer['email'],
                    } for engineer in context['body']['engineers']
                ]
                engineers_fact = ", ".join([
                    f"<at>{ engineer['name'] }</at> ({ engineer['email'] })" 
                    for engineer in engineers
                ])
                entities = [
                    {
                        "type": "mention",
                        "text": f"<at>{ engineer['name'] }</at>",
                        "mentioned": {
                            "id": f"{engineer['email']}",
                            "name": f"{engineer['name']}"
                        }
                    } for engineer in engineers
                ]
            else:
                engineers_fact = "UNKNOWN"

            facts = [
                {
                "title": "Engineers",
                "value": engineers_fact
                },
                {
                "title": "DAG",
                "value": dag_id
                },
                {
                "title": "Task",
                "value": task_id
                },
            ]
            error_message_formatted = {
                                "type": "TextBlock",
                                "style": "default",
                                "size": "default",
                                "weight": "default",
                                "color": "default",
                                "wrap": True,
                                "max_lines": 10,
                                "text": f"{message_body}"
                            }
            
            log_viewer = [
                            {
                                "type": "Action.OpenUrl",
                                "title": "View",
                                "url": f"{log_url}",
                                "role": "button"
                            }
                        ]

        elif alert_level == 'SUCCESS':
            heading_color="good"
            facts = [{'title': key, 'value': context['body'][key]} for key, value in context['body'].items() if
                        key not in ['project', 'engineers', 'status', 'end_time']]
        else:
            heading_color="default"
            facts = [{'title': key, 'value': context['body'][key]} for key, value in context['body'].items() if
                        key not in ['project', 'engineers', 'status', 'end_time']]
    
        message = {
            "type":"message",
            "attachments":[
                {
                    "contentType":"application/vnd.microsoft.card.adaptive",
                    "content":{
                        "$schema":"http://adaptivecards.io/schemas/adaptive-card.json",
                        "type":"AdaptiveCard",
                        "version":"1.2",
                        "body":[
                            {
                                "type": "TextBlock",
                                "style": "heading",
                                "size": "medium",
                                "weight": "bolder",
                                "color": heading_color,
                                "text": alert_level
                            },
                            {
                                "type": "FactSet",
                                "spacing": "large",
                                "facts": facts
                            }
                        ]
                    }
                }
            ]
        }
             
        if len(entities) > 0:
            message["attachments"][0]["content"]["msteams"]={"entities": entities}
        if alert_level == 'FAILURE':
            message["attachments"][0]["content"]["body"].append(error_message_formatted)
            message["attachments"][0]["content"]["actions"] = log_viewer

        return message