from collections import namedtuple
import configparser
from importlib.metadata import metadata
import json
import csv
from pickle import FALSE, TRUE
from wsgiref.util import request_uri
import requests



def process_response_json(response_json, parsing_container):
    '''Process the decoded JSON blob from /v1/computers API Endpoint
    '''

    def process_guid_json(guid_json, parsing_container=parsing_container):
        '''Process the individual GUID entry
        '''
        connector_guid = guid_json.get('connector_guid')
        hostname = guid_json.get('hostname')
        last_seen = guid_json.get('last_seen')

        network_addresses = guid_json.get('network_addresses')

        parsing_container.setdefault(hostname, {'macs':[], 'mac_guids':{}, 'guid_last_seen':{}})
        parsing_container[hostname]['guid_last_seen'][connector_guid] = last_seen

        for network_interface in network_addresses:
            mac = network_interface.get('mac')
            # ip = network_interface.get('ip')
            # ipv6 = network_interface.get('ipv6')

            parsing_container[hostname]['macs'].append(mac)
            parsing_container[hostname]['mac_guids'].setdefault(mac, set())
            parsing_container[hostname]['mac_guids'][mac].add(connector_guid)

    for guid_entry in response_json['data']:
        if 'network_addresses' in guid_entry:
            process_guid_json(guid_entry)

def init_amp_session():
    
    config_file = 'api.cfg'

    config = configparser.RawConfigParser()
    config.read(config_file)
    client_id = config.get('AUTH', 'client_id')
    api_key = config.get('AUTH', 'api_key')

    amp_session = requests.session()
    amp_session.auth = (client_id, api_key)

    return amp_session 

def get(session, url):
    '''HTTP GET the URL and return the decoded JSON
    '''
    response = session.get(url)
    response_json = response.json()   
    
    return response_json

def get_total_number_devices(response_json):
    device_total = response_json['metadata']['results']['total']
    return device_total

def display_total_number_devices(response_json):
    print("\nThere are {} computer's that match your query. \n".format(response_json['metadata']['results']['total']))

def main():
    '''The main logic of the script
    '''
    parsed_computers = {}

    # set url params
    request_url = 'https://api.amp.cisco.com/v1/computers/'
    # start amp session
    amp_session = init_amp_session()

    # Query the API
    response_json = get(amp_session, request_url)

    display_total_number_devices(response_json)

    #process_response_json(response_json, parsed_computers)

    # Check if there are more pages and repeat
    #while 'next' in response_json['metadata']['links']:
    #    next_url = response_json['metadata']['links']['next']
    #    response_json = get(amp_session, next_url)
    #    index = response_json['metadata']['results']['index']
    #    print('Processing index: {}'.format(index))
        #process_response_json(response_json, parsed_computers)

    #print(response_json)

if __name__ == "__main__":
    main()