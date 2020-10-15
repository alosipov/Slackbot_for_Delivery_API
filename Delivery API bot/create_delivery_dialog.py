class CreateDeliveryDialogToSlack:
    def __init__(self, channel_id, user_id):
        self.channel_id = channel_id
        self.user_id = user_id

    def create_delivery_dialog_to_slack(self):
        return {
            'as_user': True,
            'channel': self.channel_id,
            'text': "*Create Delivery* :package: The delivery endpoint allows creation of a new delivery given the "
                    "delivery information and a bundle id. "
                    " \nPlease provide required details for delivery creation :shopping_bags::",
            'attachments': [{
                "text": "",
                "callback_id": self.channel_id + "delivery_details_form",
                "color": "#ECB22E",
                "attachment_type": "default",
                "actions": [{
                    "name": "delivery_details",
                    "text": ":shopping_trolley: Enter delivery details",
                    "type": "button",
                    "value": "delivery_details"
                }]
            }]
        }
