import requests

from framework.utils.common import get_current_datetime


class TeamsUtil(object):

    def __init__(self, webhook_url):
        self.webhook_url = webhook_url

    def send_teams_card(self, title, content_list):
        headers = {
            "Content-Type": "application/json"
        }

        payload = {
            "type": "message",
            "attachments": [
                {
                    "contentType": "application/vnd.microsoft.card.adaptive",
                    "content": {
                        "type": "AdaptiveCard",
                        "body": [
                            {
                                "type": "TextBlock",
                                "size": "Large",
                                "weight": "Bolder",
                                "text": title
                            },
                        ],
                        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                        "version": "1.0"
                    }
                }
            ]
        }
        content_list.append(f"发送时间: {get_current_datetime()}")
        for item in content_list:
            payload["attachments"][0]["content"]["body"].append({
                "type": "TextBlock",
                "text": item,
                "wrap": True
            })

        response = requests.post(self.webhook_url, headers=headers, json=payload)

        if not response.status_code == 200:
            raise Exception(f"Failed to send card. Status code: {response.status_code}, Response: {response.text}")
