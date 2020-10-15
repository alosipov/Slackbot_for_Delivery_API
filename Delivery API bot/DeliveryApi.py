#!/usr/bin/python3
# -*- coding: utf-8 -*-

import requests
import json
from geopy.geocoders import Nominatim


class DeliveryApi:
    def __init__(self, client_id, client_secret, scope, business_id):
        self.client_id = client_id
        self.client_secret = client_secret
        self.scope = scope
        self.business_id = business_id

    # OAuth 2.0 bearer token
    def authentication(self):
        files = {
            'client_id': (None, self.client_id),
            'client_secret': (None, self.client_secret),
            'grant_type': (None, 'client_credentials'),
            'scope': (None, self.scope),
        }

        authentication_response = requests.post('https://api.gett.com/v1/oauth/token', files=files)
        # print(json.dumps(authentication_response.json(), indent=4, sort_keys=True, ensure_ascii=False))
        return json.dumps(authentication_response.json(), indent=4, sort_keys=True, ensure_ascii=False)

    def get_products(self, pickup_city, pickup_street, pickup_building, pickup_country):
        token = json.loads(self.authentication())['access_token']

        headers = {
            'Authorization': 'Bearer ' + token,
            'Content-Type': 'application/json',
        }

        pickup = {
            'city': pickup_city,
            'street': pickup_street,
            'building': pickup_building,
            'country': pickup_country
        }

        params = (
            ('latitude',
             self.get_coordinates(pickup['building'], pickup['street'], pickup['city'], pickup['country'])[0]),
            ('longitude',
             self.get_coordinates(pickup['building'], pickup['street'], pickup['city'], pickup['country'])[1]),
            ('business_id', self.business_id),
        )

        print("Getting Products for you Boss...")
        get_products_response = requests.get('https://api.gett.com/v1/business/products', headers=headers,
                                             params=params)
        print(json.dumps(get_products_response.json(), indent=4, sort_keys=True, ensure_ascii=False))
        return json.dumps(get_products_response.json(), indent=4, sort_keys=True, ensure_ascii=False)

    def create_delivery(self, token, business_id, product_id, scheduled_at, pickup_building, pickup_street,
                        pickup_city, pickup_country, pickup_contact_name, pickup_contact_phone,
                        drop_off_address, drop_off_contact_name, drop_off_contact_phone):
        headers = {
            'Authorization': 'Bearer ' + token,
            'Content-Type': 'application/json',
        }

        params = (
            ('business_id', business_id),
        )

        if scheduled_at is None:
            data = "{\"product_id\": \"" + product_id + "\", \"display_identifier\":\"DeliveryAPISlackBot\"," \
                                                        "\"avoid_aggregation\":true," \
                   "\"pickup\":{\"lat\": " + \
                   str(self.get_coordinates(pickup_building, pickup_street, pickup_city, pickup_country)[0])\
                   + ",\"lng\": " + \
                   str(self.get_coordinates(pickup_building, pickup_street, pickup_city, pickup_country)[1]) +\
                   ",\"address\":\"" +\
                   self.get_coordinates(pickup_building, pickup_street, pickup_city, pickup_country)[2] + "\"," \
                   "\"note\":\"Apt: 3, floor: 4\"},\"pickup_contact\":{\"name\":\"" + pickup_contact_name + "\"," \
                   "\"phone_number\":\"" + pickup_contact_phone + "\"},\"deliveries\":[{\"drop_off\":{\"lat\": " + \
                   str(self.get_coordinates(drop_off_address.split(',')[2], drop_off_address.split(',')[1],
                                            drop_off_address.split(',')[0], drop_off_address.split(',')[3])[0]) + \
                   ",\"lng\": " + str(self.get_coordinates(drop_off_address.split(',')[2], drop_off_address.split(',')[1],
                                                           drop_off_address.split(',')[0],
                                                           drop_off_address.split(',')[3])[1]) + \
                   ",\"address\":\"" + self.get_coordinates(drop_off_address.split(',')[2], drop_off_address.split(',')[1],
                                                            drop_off_address.split(',')[0],
                                                            drop_off_address.split(',')[3])[2] +\
                   "\",\"note\":\"Floor 5, Door 7\"}," \
                   "\"drop_off_contact\":{\"name\":\"" + drop_off_contact_name + "\",\"phone_number\":\"" +\
                   drop_off_contact_phone + "\"}," \
                   "\"external_identifier\":\"DeliveryAPISlackBot\",\"display_identifier\":\"DeliveryAPISlackBot\"," \
                   "\"vendor\":{\"name\":\"Mother Russia\"},\"parcels\":[{\"display_identifier\":\"666\"," \
                   "\"size_alias\":\"B\",\"length\":125,\"width\":23,\"height\":10,\"weight\":3.15," \
                   "\"barcodes\":[\"0123452\",\"hgcgf5656\"],\"items\":[{\"external_id\":\"6041404739000\"," \
                   "\"name\":\"Vodka, bear, berezka\",\"quantity\":2,\"price\":293.15,\"vat_rate\":10," \
                   "\"exemplars\":[{\"external_id\":\"6390000414047\",\"barcode\":\"01ygitftyf23452\"},{" \
                   "\"external_id\":\"4140463900007\",\"barcode\":\"6527394735\"}]}]}]}]}"
        else:
            data = "{\"product_id\": \"" + product_id + "\", \"scheduled_at\": \"" + scheduled_at + "\"," \
                   "\"display_identifier\":\"DeliveryAPISlackBot\",\"avoid_aggregation\":true," \
                   "\"pickup\":{\"lat\": " + \
                   str(self.get_coordinates(pickup_building, pickup_street, pickup_city, pickup_country)[0])\
                   + ",\"lng\": " + \
                   str(self.get_coordinates(pickup_building, pickup_street, pickup_city, pickup_country)[1]) +\
                   ",\"address\":\"" +\
                   self.get_coordinates(pickup_building, pickup_street, pickup_city, pickup_country)[2] + "\"," \
                   "\"note\":\"Apt: 3, floor: 4\"},\"pickup_contact\":{\"name\":\"" + pickup_contact_name + "\"," \
                   "\"phone_number\":\"" + pickup_contact_phone + "\"},\"deliveries\":[{\"drop_off\":{\"lat\": " + \
                   str(self.get_coordinates(drop_off_address.split(',')[2], drop_off_address.split(',')[1],
                                            drop_off_address.split(',')[0], drop_off_address.split(',')[3])[0]) + \
                   ",\"lng\": " + str(self.get_coordinates(drop_off_address.split(',')[2], drop_off_address.split(',')[1],
                                                           drop_off_address.split(',')[0],
                                                           drop_off_address.split(',')[3])[1]) + \
                   ",\"address\":\"" + self.get_coordinates(drop_off_address.split(',')[2], drop_off_address.split(',')[1],
                                                            drop_off_address.split(',')[0],
                                                            drop_off_address.split(',')[3])[2] +\
                   "\",\"note\":\"Floor 5, Door 7\"}," \
                   "\"drop_off_contact\":{\"name\":\"" + drop_off_contact_name + "\",\"phone_number\":\"" +\
                   drop_off_contact_phone + "\"}," \
                   "\"external_identifier\":\"DeliveryAPISlackBot\",\"display_identifier\":\"DeliveryAPISlackBot\"," \
                   "\"vendor\":{\"name\":\"Mother Russia\"},\"parcels\":[{\"display_identifier\":\"666\"," \
                   "\"size_alias\":\"B\",\"length\":125,\"width\":23,\"height\":10,\"weight\":3.15," \
                   "\"barcodes\":[\"0123452\",\"hgcgf5656\"],\"items\":[{\"external_id\":\"6041404739000\"," \
                   "\"name\":\"Vodka, bear, berezka\",\"quantity\":2,\"price\":293.15,\"vat_rate\":10," \
                   "\"exemplars\":[{\"external_id\":\"6390000414047\",\"barcode\":\"01ygitftyf23452\"},{" \
                   "\"external_id\":\"4140463900007\",\"barcode\":\"6527394735\"}]}]}]}]}"

        print(data)

        create_delivery_response = requests.post('https://api.gett.com/v1/delivery/deliveries', headers=headers,
                                                 params=params, data=data.encode('utf-8'))
        # print(json.dumps(create_delivery_response.json(), indent=4, sort_keys=True, ensure_ascii=False))
        return json.dumps(create_delivery_response.json(), indent=4, sort_keys=True, ensure_ascii=False)

    def cancel_bundle(self, token, bundle_id):

        headers = {
            'Authorization': 'Bearer ' + token,
            'Content-Type': 'application/json',
        }

        params = (
            ('business_id', self.business_id),
        )

        url = "https://api.gett.com/v1/delivery/bundles/" + bundle_id + "/cancel"

        cancel_ride_response = requests.post(url, headers=headers, params=params)
        print(cancel_ride_response.status_code)
        # print(json.dumps(cancel_ride_response.json(), indent=4, sort_keys=True, ensure_ascii=False))
        return cancel_ride_response.status_code

    @staticmethod
    def get_coordinates(building, street, city, country):
        geolocator = Nominatim(user_agent="AlexeyOsipov-DeliveryAPI")
        location = geolocator.geocode(building + ',' + street + ',' + city + ',' + country, language="en-US,en,ru,he")
        # print("latitude is :-", loc.latitude, "\nlongitude is:-", loc.longitude)
        latitude = location.latitude
        longitude = location.longitude
        print(location.address)
        print(str(location.latitude) + "," + str(location.longitude))
        return latitude, longitude, location.address.replace("\"", '')
