class DialogToSlack:
    def __init__(self, channel_id, user_id):
        self.channel_id = channel_id
        self.user_id = user_id

    def dialog_to_slack(self):
        return {
            'as_user': True,
            'channel': self.channel_id,
            'text': "*Get Products* :package: API returns the supported Gett products offered at the specified location."
                    " \nPlease provide location address :city_sunset::",
            'attachments': [{
                "text": "",
                "callback_id": self.channel_id + "location_details_form",
                "color": "#ECB22E",
                "attachment_type": "default",
                "actions": [{
                    "name": "location_details",
                    "text": ":postbox: Enter location address",
                    "type": "button",
                    "value": "location_details"
                }]
            }]
        }
