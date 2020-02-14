import requests
import json
import pprint
import random

# Config for pprint
pp = pprint.PrettyPrinter(indent=2)

import sys
sys.path.append("..")
from status_helper_functions import create_error_status, is_dict_a_success_dict, is_dict_an_error_dict

flow_template = {
    "switch":"00:00:00:00:00:00:00:01", 
    "name":"flow-rule-155", 
    "cookie":"0", 
    "priority":"32768", 
    "in_port":"2",
    "active":"true", 
    "actions":"output=35",
    }

# IP address of the Floodlight Controller
controller_ip = 'http://127.0.0.1:8080/wm/'

# Header information for the FL API
headers = {'Content-type':'application/json', 'Accept':'application/json'}

flow_rule_name = {"name":"flow-rule-5"}
role = {"role":"MASTER"}

# [POST/DELETE] {flow_rule_name} 
# This URI lets you add or delete flow rules, depending on if the endpoint gets a 'post' request or 'delete' request
pusher = controller_ip + 'staticentrypusher/json'

# [GET] This URI takes a controller mac address and returns all the flow rules and groups associated with it
get_switch_info = controller_ip + 'staticentrypusher/list/'

# [GET] This will return info about the the switches connected to the controller. Returns the switch ip, OF version and DPIP
get_info_about_all_switches = controller_ip + 'core/controller/switches/json'

# [POST] {role} 
# This endpoint can be used to change the role of all the switches
change_role = controller_ip + 'core/switch/all/role/json'

# [GET] 
# Returns information about switch-to-switch links
get_switch_links_endpoint = controller_ip + 'topology/links/json'


get_host_information_endpoint = controller_ip + 'device/'

# [GET] Clears all groups and flows from switches
clear_switches = controller_ip + 'staticentrypusher/clear/all/json'

# [GET] Grabs network statistics from the switches on the network
get_network_statistics_endpoint = controller_ip + 'statistics/bandwidth/<switch>/<port>/json'



def add_flow(flow_rule):
    """
    Add a flow to a particular switch
    
    Arguments:
        flow_rule {Dictionary} -- A dictionary that represents a flow rule
    
    Returns:
        [Dictionary] -- Returns a status message depending on the outcome of the operation
    """
    with requests.Session() as session:
        req = requests.post(pusher, json=flow_rule, headers=headers)
        session.close()
        
    # check to see if the request was successful
    return {'status_success':'Flow successfully added'} if req.status_code == 200 else create_error_status(req, 'Failed to add flow')


def del_flow(flow_name, switch_mac_addr):
    """
    Delete an existing flow rule from a switch
    
    Arguments:
        flow_name {String} -- The name of the flow to delete
        switch_mac_addr {String} -- The name of the switch to delete the flow from
    
    Returns:
        [Dictionary] -- Returns a status message depending on the outcome of the operation
    """
    
    flow_name = {"name": flow_name}
    
    with requests.Session() as session:
        req = requests.delete(pusher, json=flow_name, headers=headers)
        session.close()
        
    # Need to check status code + the status return message as a successful delete and a failed delete
    # Returns the same html status code....
    data = {}
    
    #print('-------------------')
    
    #print(req.json())
    
    #print('-------------------')
    
    if req.status_code == 200 and req.json()['status'] == 'Entry ' + flow_name['name'] + ' deleted':
        data = {'status_success':'Flow successfully deleted'}
    else:
        data = create_error_status(req, 'Failed to delete flow')

    return data


def get_switch_flow_rules(switch_mac_addr):
    """
    Gets the flows for a particular switch, or for all switches
    
    Arguments:
        switch_mac_addr {String} -- Give the switch name to get flows for a particular switch, or give 'all' and get the flows across all switches
    
    Returns:
        [Dictionary] -- Returns a dictionary with the list of flows, or a status message depending on the outcome
    """
    endpoint = controller_ip + 'staticentrypusher/list/' + switch_mac_addr + '/json'
    with requests.Session() as session:
        req = requests.get(endpoint, headers=headers)
        session.close()
        
    return req.json() if req.status_code == 200 else create_error_status(req, 'Failed to get flow rule from switch') 


def remove_all_flows_and_groups():
    """
    Deletes all flows and groups from the Floodlight network
    
    Returns:
        [Dictionary] -- Returns a status dictionary depending on the outcome
    """
    with requests.Session() as session:
        req = requests.get(clear_switches, headers=headers)
        session.close()
    
    return {'status_success':'Deleted All flows/groups'} if req.status_code == 200 else create_error_status(req, 'Failed to get flow rule from switch') 


# Will grab all the flows from get_switch_flow_rules and search through them
def search_for_flow_rule(flow_name):
    """
    Search for a flow across any switch
    
    Arguments:
        flow_name {String} -- Name of the flow to search for
    
    Returns:
        [Dictionary] -- A flow rule or a status dictionary, depending on if a flow is found
    """
    flow_list = get_switch_flow_rules('all')
    switch_list = [x['switchDPID'] for x in get_switch_information()]
    
    data = {'status_error': 'Flow rule not found'}
    if not is_dict_an_error_dict(flow_list) and len(flow_list) != 0:
    # check get_switch_rules has not returned an error
    
        for switch in switch_list:
            # Iterate through all the switches
            
            for flow in flow_list[switch]:
                # Iterate through all the flows for a particular switch
                if flow_name in list(flow)[0]:
                    data = flow[flow_name]
                    data['switch'] = switch
                    break
    return data



def get_network_information():
    """
    Creates a dictionary with information about the entire network
    
    Returns:
        [Dictionary] -- A dictionary with network information including:
        - Switch list
        - Host List
        - Host Links
        - Number of switches
        - Number of hosts
        - Active flows
    """
    # Get info about all the hosts on the network
    switch_info = get_switch_information()
    host_info = get_host_information()
    
    # Get the list of switches
    switch_list = [x['switchDPID'] for x in switch_info]
    
    # Get a list of host mac addresses
    host_list = [x['mac'][0] for x in host_info['devices']]
    
    # Get the links a host has on the network
    host_links = [[x['mac'], x['attachmentPoint']] for x in host_info['devices']]
    
    
    #return switch_info
    return {'switch_list': switch_list, 
            'host_list': host_list, 
            'host_links': host_links, 
            'switch_links': get_switch_links(),
            'number_of_hosts': len(host_list),
            'number_of_switches': len(switch_list),
            'flows': create_simple_flow_list(switch_list),
            'network_statistics': create_network_statistics_list()
             }


def create_flow_rule(flow_name, priority, switch_mac_addr, cookie, in_port, out_port):
    """
    Creates a flow rule using the Floodlight flow template
    
    Arguments:
        priority {String} -- The priority of the flow
        switch_mac_addr {String} -- The mac address of the switch
        cookie {String} -- The cookie value
        in_port {String} -- The in_port or 'matching statement' for the flow
        out_port {String} -- The 'action' or the out port for the flow
    
    Returns:
        [type] -- [description]
    """
    
        
    flow = flow_template
    flow['switch'] = switch_mac_addr
    flow['priority'] = priority
    flow['name'] = flow_name
    #flow['tableId'] = table_id
    flow['in_port'] = in_port
    flow['actions'] = 'output=' + out_port
    flow['cookie'] = cookie

    return flow

def create_block_rule(switch_mac_addr, host_to_block):
    flow = {}
    flow['switch'] = switch_mac_addr
    flow['priority'] = '1000'
    flow['name'] = 'block ' + host_to_block[:8]
    flow['cookie'] = random.randint(1, 100)
    flow['actions'] = 'output=' + ''
    flow['eth_src'] = host_to_block
    
    return flow


def create_network_statistics_list():
    host_info = get_host_information()
    host_links = [[x['mac'], x['attachmentPoint']] for x in host_info['devices']]
    #switch_links = get_switch_links()
    
    #pp.pprint(switch_links) 
    
    statistics = []
    
    for host in host_links:
        #print(host[1][0]['switch'],host[1][0]['port'])
        host_statistics = get_network_statistics(host[1][0]['switch'],host[1][0]['port'])[0]
        #print(host_statistics)
        if host_statistics is not None:
            host_statistics['host'] = host[0][0]

        statistics.append(host_statistics)  
    
    #pp.pprint(statistics)
    return statistics
    


######################################
# FLOODLIGHT SPECIFIC HELPER FUNCTIONS
######################################

def create_simple_flow_dict(flow_rule, switch_mac_addr):
    """
    Takes a flow object and extracts relevant information to create a dictionary
    Used to convert a flow from the 'ONOS' format to a general format used by the API
    
    Arguments:
        flow_rule {Dictionary} -- The flow dictionary to pull information from
        switch_name {String} -- The name of the switch the flow came from
    
    Returns:
        [Dictionary] -- A flow rule in a simplified and general format
    """
    flow_name = list(flow_rule)[0]
    return {'switch_name': switch_mac_addr,
            'flow_name': flow_name,
            'flow_id': flow_name,
            'cookie': flow_rule[flow_name]['cookie'],
            'match_condition': flow_rule[flow_name]['match'],
            'out_port': flow_rule[flow_name]['instructions'],
            'priority': flow_rule[flow_name]['priority'],
            #'table_id': flow_rule['tableId']
            }


def create_simple_flow_list(switch_list):
    """
    Iterate through all the switches on the network and create simplifed flow rule descriptions
    
    Arguments:
        switch_list {List} -- A list of all the switches connected to the Floodlight controller
    
    Returns:
        [List] -- Returns a list of simplifed flow rules
    """
    flow_list = get_switch_flow_rules('all')
    simple_flow_list = []
    
    
    if not is_dict_an_error_dict(flow_list) and len(flow_list) != 0:
        # check get_switch_rules has not returned an error
        # check flow_list actually has a flow in it
        
        for switch in switch_list:
            # Iterate through all the switches
            
            if switch in list(flow_list):
                # check that the switch actually has flow rules in it
                for flow in flow_list[switch]:
                    # Iterate through all the flows for a particular switch
                    simple_flow_list.append(create_simple_flow_dict(flow, switch))
    else:
        # Return the error from get_switch_flow_rules()
        return flow_list
    
    return simple_flow_list


def get_switch_information():
    """
    Queries the Floodlight controller for information about all the switches connected to the controller
    
    Returns:
        [Dictionary] -- A dictionary with switch information
    """
    with requests.Session() as session:
        req = requests.get(get_info_about_all_switches, headers=headers)
        session.close()
    
    return req.json() if req.status_code == 200 else create_error_status(req, 'Failed to get switch information')


def get_switch_links():
    """
    Queries the Floodlight controller for information about switch to switch links on the network
    
    Returns:
        [Dictionary] -- A dictionary with switch link information
    """
    with requests.Session() as session:
        req = requests.get(get_switch_links_endpoint, headers=headers)
        session.close()
    
    return req.json() if req.status_code == 200 else create_error_status(req, 'Failed to get switch information')


def get_host_information():
    """
    Queries the Floodlight controller for information about hosts on the network
    
    Returns:
        [Dictionary] -- Returns host information
    """
    with requests.Session() as session:
        req = requests.get(get_host_information_endpoint, headers=headers)
        session.close()
    
    return req.json() if req.status_code == 200 else create_error_status(req, 'Failed to get switch link information')


def get_network_statistics(switch, port):
    """
    Queries the Floodlight controller for information about hosts on the network
    
    Returns:
        [Dictionary] -- Returns host information
    """
    endpoint = get_network_statistics_endpoint
    endpoint = endpoint.replace('<switch>', switch).replace('<port>', port)
    #print(endpoint)
    
    with requests.Session() as session:
        req = requests.get(endpoint, headers=headers)
        session.close()
    
    return req.json() if req.status_code == 200 else create_error_status(req, 'Failed to get switch link information')
        
    
    

#pp.pprint(add_flow(flow_rule))
# remove_all_rules_and_groups()
#pp.pprint((get_switch_flow_rules('00:00:00:00:00:00:00:01')))
#pp.pprint(type(get_switch_flow_rules('all')))

#print(remove_all_flows_and_groups())

#pp.pprint((del_flow({"name":"flow-rule-111"}, '00:00:00:00:00:00:00:01')))

#flow_example = search_for_flow_rule('flow-rule-979')
#pp.pprint(flow_example)
#pp.pprint(create_simple_flow_dict(flow_example['flow-rule-122'], 'switch', 'name'))
#print(get_host_information_endpoint)


# pp.pprint(add_flow(create_flow_rule('999', '00:00:00:00:00:00:00:01', '999', '12', '17')))
# pp.pprint(add_flow(create_flow_rule('998', '00:00:00:00:00:00:00:02', '999', '12', '16')))
# pp.pprint(add_flow(create_flow_rule('199', '00:00:00:00:00:00:00:02', '999', '12', '15')))
#pp.pprint(get_network_information())

#pp.pprint(get_switch_links())

#pp.pprint(get_network_statistics('00:00:00:00:00:00:00:01', ''))

#pp.pprint(create_network_statistics_list())


