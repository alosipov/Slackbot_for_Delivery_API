class SendMessageToSlack:
    def __init__(self, form_json, text, response, ):
        self.form_json = form_json
        self.text = text
        self.response = response

    def post_to_slack(self):
        return {
                'channel': self.form_json["channel"]["id"],
                'text': "",
                'attachments': [
                    {
                        "color": "#E01E5A",
                        "blocks": [
                            {
                                "type": "section",
                                "text": {
                                    "type": "mrkdwn",
                                    "text": self.text.format(self.response)
                                }
                            },
                            {
                                "type": "divider"
                            }
                        ]
                    }
                ]
            }
