#!/usr/bin/python3
# -*- coding: utf-8 -*-
from threading import Thread

from flask import Flask, request, make_response, Response, json, request
# import json
import logging
from DeliveryApi import DeliveryApi
from send_message_to_slack_class import SendMessageToSlack
from dialog_to_slack_class import DialogToSlack
from create_delivery_dialog import CreateDeliveryDialogToSlack

from slack import WebClient
from slackeventsapi import SlackEventAdapter

# Flask webserver for incoming traffic from Slack
app = Flask(__name__)

SLACK_BOT_TOKEN = "xoxb-*********-********-****************"
SLACK_VERIFICATION_TOKEN = '*******************'

# Slack client for Web API requests
slack_client = WebClient(SLACK_BOT_TOKEN)

# Create an events adapter and register it to an endpoint in the slack app for event ingestion.
slack_events_adapter = SlackEventAdapter("***********************", "/slack/events", app)


# Helper for verifying that requests came from Slack
def verify_slack_token(request_token):
    if SLACK_VERIFICATION_TOKEN != request_token:
        print("Error: invalid verification token!")
        print("Received {} but was expecting {}".format(request_token, SLACK_VERIFICATION_TOKEN))
        return make_response("Request contains invalid Slack verification token", 403)


# The endpoint Slack will load your menu options from
@app.route("/slack/message_options", methods=["POST"])
def message_options():
    # Parse the request payload
    form_json = json.loads(request.form["payload"])

    # Verify that the request came from Slack
    verify_slack_token(form_json["token"])
    # print(sending_get_products.available_classes_dict)
    classes = {}
    for element in sending_get_products.available_classes_dict['products']:
        # print(element['display_name'] + ':' + element['id'])
        if element['display_name'] not in classes:
            classes[element['display_name']] = []
        classes[element['display_name']].append(element['id'])

    # find matching options
    # will match if user input string is in name
    options = list()
    for name, value in classes.items():
        if form_json["value"] in name:
            options.append({
                "label": name,
                "value": value
            })

    # build response structure
    response = {
        "options": options
    }

    return json.jsonify(response)


def creating_delivery(form_json, product_id, scheduled_at, pickup_building, pickup_street, pickup_city, pickup_country,
                      pickup_contact_name, pickup_contact_phone, drop_off_address,
                      drop_off_contact_name, drop_off_contact_phone):
    creating_delivery_response = DeliveryApi(client_id=message.client_id,
                                             client_secret=message.client_secret,
                                             scope=message.scope,
                                             business_id=message.business_id).create_delivery(message.token,
                                                                                              message.business_id,
                                                                                              product_id,
                                                                                              scheduled_at,
                                                                                              pickup_building,
                                                                                              pickup_street,
                                                                                              pickup_city,
                                                                                              pickup_country,
                                                                                              pickup_contact_name,
                                                                                              pickup_contact_phone,
                                                                                              drop_off_address,
                                                                                              drop_off_contact_name,
                                                                                              drop_off_contact_phone)
    print(creating_delivery_response)
    print("Delivery token: ", message.token)
    # json.loads(creating_delivery_response)['bundle_id']
    creating_delivery.bundle_id = json.loads(creating_delivery_response)['bundle_id']
    print(type(creating_delivery.bundle_id))
    slack_client.api_call("chat.postMessage", json=SendMessageToSlack(form_json, "*`Bundle created: `* \n{}",
                                                                      "<https://delivery-app.gett.com/" + message.env
                                                                      + "/bundles/" + json.loads(creating_delivery_response)['bundle_id'] + "|" + json.loads(creating_delivery_response)['bundle_id'] + ">\n").post_to_slack())

    file = './Resources/created_bundle_' + form_json["user"]["id"] + '.json'
    with open(file, 'w') as f:
        f.write(creating_delivery_response)
    channel_id = form_json["channel"]["id"]
    with open(file, "rb"):
        response = slack_client.files_upload(
            channels=channel_id,
            file=file,
            title='Create Delivery Response',
            filetype='json'
        )
        print(response)
    return creating_delivery.bundle_id


def sending_get_products(form_json, pickup_city, pickup_street, pickup_building, pickup_country, scope):
    # getting get_products response message from DeliveryAPi Class
    get_products_response_message = DeliveryApi(client_id=message.client_id,
                                                client_secret=message.client_secret,
                                                scope=scope,
                                                business_id=message.business_id).get_products(pickup_city,
                                                                                              pickup_street,
                                                                                              pickup_building,
                                                                                              pickup_country)

    # sending message to Slack with the Get Products request Response
    # slack_client.api_call("chat.postMessage", json=SendMessageToSlack(form_json, "*`Available Products:`* \n{}",
    #                                                                   get_products_response_message).post_to_slack())

    file = './Resources/available_products_' + form_json["user"]["id"] + '.json'
    with open(file, 'w') as f:
        f.write(get_products_response_message)
    channel_id = form_json["channel"]["id"]
    with open(file, "rb"):
        response = slack_client.files_upload(
            channels=channel_id,
            file=file,
            title='Available Products: ',
            filetype='json'
        )
    print(response)

    sending_get_products.available_classes_dict = json.loads(get_products_response_message)
    # print(available_classes_dict)
    for element in sending_get_products.available_classes_dict['products']:
        print(element['display_name'] + ':' + element['id'])

    return sending_get_products.available_classes_dict


# The endpoint Slack will send the user's menu selection to
@app.route("/slack/message_actions", methods=["POST"])
def message_actions(address_details_dict={}, delivery_details_dict={}):
    # Parse the request payload
    form_json = json.loads(request.form["payload"])

    # Verify that the request came from Slack
    verify_slack_token(form_json["token"])

    # Check to see what the user's selection was and update the message accordingly

    if form_json['type'] == "block_actions":
        selection = form_json["actions"][0]["action_id"]

        if selection == "generate_token_clicked":
            # sending message to Slack that we are processing authentication Request
            slack_client.api_call("chat.postMessage", json=SendMessageToSlack(form_json, "*Sending {} "
                                                                                         "request..........!* "
                                                                                         ":passport_control:",
                                                                              "Authentication").post_to_slack())

            # sending message to Slack with the authentication request Response
            slack_client.api_call("chat.postMessage", json=SendMessageToSlack(form_json, "*`Token Response:`* \n{}",
                                                                              message.token_response_message).post_to_slack())

        if selection == "get_products_clicked":
            # todo: geocoding review

            # get user input from dialog for 'city', 'street', 'building', 'country'
            address_details = slack_client.api_call("chat.postMessage", json=DialogToSlack(form_json["channel"]["id"],
                                                                                           form_json["user"][
                                                                                               "id"]).dialog_to_slack())

            address_details_dict[form_json["user"]["id"]] = {
                "address_channel": address_details["channel"],
                "message_ts": "",
                "address": {}
            }

        if selection == "create_delivery_clicked":
            try:
                if sending_get_products.available_classes_dict is not None:

                    # get user input for required fields for creating Delivery
                    create_delivery_dialog = slack_client.api_call("chat.postMessage",
                                                                   json=CreateDeliveryDialogToSlack(
                                                                       form_json["channel"]["id"],
                                                                       form_json["user"][
                                                                           "id"]).create_delivery_dialog_to_slack())
                    delivery_details_dict[form_json["user"]["id"]] = {
                        "address_channel": create_delivery_dialog["channel"],
                        "message_ts": "",
                        "address": {}
                    }
                else:
                    # sending message to Slack warning that Get Products should be clicked first
                    slack_client.api_call("chat.postMessage", json=SendMessageToSlack(form_json,
                                                                                      "*You should check for available products first :arrow_right: {}!!!*",
                                                                                      "click GET PRODUCTS").post_to_slack())
                    #todo Add button that will allow create Delivery providing all details

            except AttributeError:
                # sending message to Slack warning that Get Products should be clicked first
                slack_client.api_call("chat.postMessage", json=SendMessageToSlack(form_json,
                                                                                  "*You should check for available products first :arrow_right: {}!!!*",
                                                                                  "click GET PRODUCTS").post_to_slack())

        if selection == "cancel_delivery_clicked":
            # canceling the bundle
            cancel_bundle_response_message = DeliveryApi(client_id=message.client_id,
                                                         client_secret=message.client_secret,
                                                         scope=message.scope,
                                                         business_id=message.business_id).cancel_bundle(message.token,
                                                                                                        creating_delivery.bundle_id)
            slack_client.api_call("chat.postMessage", json=SendMessageToSlack(form_json, "*`Bundle Cancel Response:`* \n{}",
                                                                              cancel_bundle_response_message).post_to_slack())

    if form_json["type"] == "interactive_message":
        for item in form_json['actions']:
            if item['name'] == 'delivery_details':
                # Add the message_ts to the user's delivery info
                delivery_details_dict[form_json["user"]["id"]]["message_ts"] = form_json["message_ts"]
                # Show the ordering dialog to the user

                if message.env == 'RU':
                    open_dialog = slack_client.api_call(
                        "dialog.open",
                        json={
                            'trigger_id': form_json["trigger_id"],
                            'dialog': {
                                "title": "Enter delivery details",
                                "submit_label": "Submit",
                                "notify_on_cancel": True,
                                "state": "Limo",
                                "callback_id": form_json["user"]["id"] + "delivery_details_form",
                                "elements": [
                                    {
                                        "label": "Available classes for your location",
                                        "name": "classes_list",
                                        "text": "Pick a class...",
                                        "type": "select",
                                        "data_source": "external"
                                    },
                                    {
                                        "type": "text",
                                        "label": "Pick up contact details:",
                                        "value": "Алексей Осипов",
                                        "name": "pickup_contact_name",
                                    },
                                    {
                                        "type": "text",
                                        "label": "Pick up contact phone:",
                                        "subtype": "tel",
                                        "value": "+79263494018",
                                        "name": "pickup_contact_phone",
                                    },
                                    {
                                        "type": "text",
                                        "label": "Drop-off address: City,Street,Building,Country:",
                                        "value": "Красногорск,Лесная,3,Россия",
                                        "name": "drop_off_address",
                                    },
                                    {
                                        "type": "text",
                                        "label": "Drop off contact:",
                                        "value": "Осипова Елена",
                                        "name": "drop_off_contact_name"
                                    },
                                    {
                                        "type": "text",
                                        "label": "Drop off contact phone:",
                                        "subtype": "tel",
                                        "value": "+79260096532",
                                        "name": "drop_off_contact_phone"
                                    },
                                    {
                                        "type": "text",
                                        "label": "Scheduled at:",
                                        "value": "2020-10-20T16:54:29Z",
                                        "name": "scheduled_at",
                                        "optional": True
                                    }
                                ]
                            }
                        }
                    )
                if message.env == 'IL':
                    open_dialog = slack_client.api_call(
                        "dialog.open",
                        json={
                            'trigger_id': form_json["trigger_id"],
                            'dialog': {
                                "title": "Enter delivery details",
                                "submit_label": "Submit",
                                "notify_on_cancel": True,
                                "state": "Limo",
                                "callback_id": form_json["user"]["id"] + "delivery_details_form",
                                "elements": [
                                    {
                                        "label": "Available classes for your location",
                                        "name": "classes_list",
                                        "text": "Pick a class...",
                                        "type": "select",
                                        "data_source": "external"
                                    },
                                    {
                                        "type": "text",
                                        "label": "Pick up contact details:",
                                        "value": "Alexey Osipov",
                                        "name": "pickup_contact_name",
                                    },
                                    {
                                        "type": "text",
                                        "label": "Pick up contact phone:",
                                        "subtype": "tel",
                                        "value": "+79262662626",
                                        "name": "pickup_contact_phone",
                                    },
                                    {
                                        "type": "text",
                                        "label": "Drop-off address: City,Street,Building,Country:",
                                        "value": "תל אביב יפו,הברזל,3,ישראל",
                                        "name": "drop_off_address",
                                    },
                                    {
                                        "type": "text",
                                        "label": "Drop off contact:",
                                        "value": "Elena Osipov",
                                        "name": "drop_off_contact_name"
                                    },
                                    {
                                        "type": "text",
                                        "label": "Drop off contact phone:",
                                        "subtype": "tel",
                                        "value": "+79266666666",
                                        "name": "drop_off_contact_phone"
                                    },
                                    {
                                        "type": "text",
                                        "label": "Scheduled at:",
                                        "value": "2020-10-20T16:54:29Z",
                                        "name": "scheduled_at",
                                        "optional": True
                                    }
                                ]
                            }
                        }
                    )

                # Update the message to show that we're in the process of taking drop off address
                address_updating_message = slack_client.api_call(
                    "chat.update",
                    json={
                        'channel': address_details_dict[form_json["user"]["id"]]["address_channel"],
                        'ts': form_json["message_ts"],
                        'text': ":pencil: Taking delivery details, Boss!",
                        'attachments': []
                    }
                )

    if form_json["type"] == "interactive_message":
        for item in form_json['actions']:
            if item['name'] == 'location_details':
                # Add the message_ts to the user's order info
                address_details_dict[form_json["user"]["id"]]["message_ts"] = form_json["message_ts"]

                if message.env == 'RU':
                    # Show the ordering dialog to the user
                    open_dialog = slack_client.api_call(
                        "dialog.open",
                        json={
                            'trigger_id': form_json["trigger_id"],
                            'dialog': {
                                "title": "Enter location address",
                                "submit_label": "Submit",
                                "notify_on_cancel": True,
                                "state": "Limo",
                                "callback_id": form_json["user"]["id"] + "location_details_form",
                                "elements": [
                                    {
                                        "type": "text",
                                        "label": "Enter pickup city:",
                                        "value": "Красногорск",
                                        "name": "pickup_city"
                                    },
                                    {
                                        "type": "text",
                                        "label": "Enter pickup street:",
                                        "value": "Лесная",
                                        "name": "pickup_street"
                                    },
                                    {
                                        "type": "text",
                                        "label": "Enter pickup building number:",
                                        "value": "9",
                                        "name": "pickup_building"
                                    },
                                    {
                                        "type": "text",
                                        "label": "Enter pickup country:",
                                        "value": "Россия",
                                        "name": "pickup_country"
                                    }
                                ]
                            }
                        }
                    )
                if message.env == 'IL':
                    # Show the ordering dialog to the user
                    open_dialog = slack_client.api_call(
                        "dialog.open",
                        json={
                            'trigger_id': form_json["trigger_id"],
                            'dialog': {
                                "title": "Enter location address",
                                "submit_label": "Submit",
                                "notify_on_cancel": True,
                                "state": "Limo",
                                "callback_id": form_json["user"]["id"] + "location_details_form",
                                "elements": [
                                    {
                                        "type": "text",
                                        "label": "Enter pickup city:",
                                        "value": "תל אביב יפו",
                                        "name": "pickup_city"
                                    },
                                    {
                                        "type": "text",
                                        "label": "Enter pickup street:",
                                        "value": "הברזל",
                                        "name": "pickup_street"
                                    },
                                    {
                                        "type": "text",
                                        "label": "Enter pickup building number:",
                                        "value": "19",
                                        "name": "pickup_building"
                                    },
                                    {
                                        "type": "text",
                                        "label": "Enter pickup country:",
                                        "value": "ישראל",
                                        "name": "pickup_country"
                                    }
                                ]
                            }
                        }
                    )

                # Update the message to show that we're in the process of taking their address
                address_updating_message = slack_client.api_call(
                    "chat.update",
                    json={
                        'channel': address_details_dict[form_json["user"]["id"]]["address_channel"],
                        'ts': form_json["message_ts"],
                        'text': ":pencil: Taking your address details...",
                        'attachments': []
                    }
                )

    # handling all dialogs submissions events
    elif form_json["type"] == "dialog_submission":
        # if location details form was submitted do the following:
        if form_json['callback_id'] == form_json['user']['id'] + "location_details_form":
            location_details = address_details_dict[form_json["user"]["id"]]
            message_actions.pickup_city = form_json["submission"]['pickup_city']
            message_actions.pickup_street = form_json["submission"]['pickup_street']
            message_actions.pickup_building = form_json["submission"]['pickup_building']
            message_actions.pickup_country = form_json["submission"]['pickup_country']
            # Update the message to show that we've received the address
            response = slack_client.api_call(
                "chat.update",
                json={
                    'channel': address_details_dict[form_json["user"]["id"]]["address_channel"],
                    'ts': location_details["message_ts"],
                    'text': ":white_check_mark: Address received!",
                    'attachments': []
                    # 'user': form_json["user"]["id"]
                }
            )

            scope = "business"
            Thread(target=sending_get_products, args=(
                form_json, message_actions.pickup_city, message_actions.pickup_street, message_actions.pickup_building,
                message_actions.pickup_country, scope,)).start()

        # if delivery_details_form was submitted do the following:
        elif form_json['callback_id'] == form_json['user']['id'] + "delivery_details_form":
            print(message_actions.pickup_city)
            print(message_actions.pickup_street)
            print(message_actions.pickup_country)
            print(message_actions.pickup_building)
            print(form_json["submission"]['classes_list'])
            print(form_json["submission"]['pickup_contact_name'])
            print(form_json["submission"]['pickup_contact_phone'])
            print(form_json["submission"]['drop_off_address'].split(',')[0])
            print(form_json["submission"]['drop_off_address'].split(',')[1])
            print(form_json["submission"]['drop_off_address'].split(',')[2])
            print(form_json["submission"]['drop_off_address'].split(',')[3])
            print(form_json["submission"]['drop_off_contact_name'])
            print(form_json["submission"]['drop_off_contact_phone'])
            print(form_json["submission"]['scheduled_at'])
            delivery_details = delivery_details_dict[form_json["user"]["id"]]
            slack_client.api_call(
                "chat.update",
                json={
                    'channel': delivery_details_dict[form_json["user"]["id"]]["address_channel"],
                    'ts': delivery_details["message_ts"],
                    'text': ":nerd_face: *Creating delivery, wait!:awaiter:*",
                    'attachments': []
                    # 'user': form_json["user"]["id"]
                }
            )

            Thread(target=creating_delivery, args=(
                form_json, form_json["submission"]['classes_list'], form_json["submission"]['scheduled_at'],
                message_actions.pickup_building, message_actions.pickup_street, message_actions.pickup_city,
                message_actions.pickup_country, form_json["submission"]['pickup_contact_name'],
                form_json["submission"]['pickup_contact_phone'], form_json["submission"]['drop_off_address'],
                form_json["submission"]['drop_off_contact_name'],
                form_json["submission"]['drop_off_contact_phone'],)).start()

    # Send an HTTP 200 response with empty body to close the Dialog window
    return make_response("", 200)


# A Dictionary of message attachment options
attachments_json = [
    {
        "color": "#3AA3E3",
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*What do you want me to do lazy bastard?* :male-technologist: \n\n Please select an action:"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "divider"
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Generate Token",
                        },
                        "action_id": "generate_token_clicked"
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Get Products",
                        },
                        "action_id": "get_products_clicked"
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Create Delivery",
                        },
                        "action_id": "create_delivery_clicked"
                    },
{
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Cancel Delivery",
                        },
                        "action_id": "cancel_delivery_clicked"
                    }
                ]
            }
        ]
    }
]


# Send a message with the above attachment, asking the user what do they want
def actions_offer(channel):
    slack_client.api_call(
        "chat.postMessage",
        json={
            'channel': channel,
            'text': "",
            'attachments': attachments_json
        }
    )


# When a 'message' event is detected by the events adapter, forward that payload
# to this function.
@slack_events_adapter.on("app_mention")
def message(payload):
    """Parse the message on mention event, and if the activation string is in the text,
    return the menu
    """

    sending_get_products.available_classes_dict = None

    # Get the event data from the payload
    event = payload.get("event", {})

    # Get the text from the event that came through
    text = event.get("text")
    message.business_id = text.split()[1]
    message.client_id = text.split()[2]
    message.client_secret = text.split()[3]
    message.scope = text.split()[4]
    if message.business_id[0:2] == 'RU':
        message.env = 'RU'
    elif message.business_id[0:2] == 'IL':
        message.env = 'IL'
    else:
        raise Exception("Unknown env bitch!")
    # getting response message to auth API from DeliveryAPI Class
    message.token_response_message = DeliveryApi(client_id=message.client_id, client_secret=message.client_secret,
                                                 scope=message.scope, business_id=message.business_id).authentication()
    message.token = json.loads(message.token_response_message)['access_token']
    # Check and see if the activation phrase was in the text of the message.
    # If so, execute the code to flip a coin.
    channel_id = event.get("channel")
    return actions_offer(channel_id)


# Start the Flask server
if __name__ == "__main__":
    # Create the logging object
    logger = logging.getLogger()

    # Set the log level to DEBUG. This will increase verbosity of logging messages
    logger.setLevel(logging.DEBUG)

    # Add the StreamHandler as a logging handler
    logger.addHandler(logging.StreamHandler())

    # Run your app on your externally facing IP address on port 3000 instead of
    # running it on localhost, which is traditional for development.
    app.run(host='0.0.0.0', port=3000)
