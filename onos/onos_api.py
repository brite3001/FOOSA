import requests
import pprint
import json
import random

# Used to import the helper function
import sys
sys.path.append("..")
from status_helper_functions import create_error_status, is_dict_a_success_dict, is_dict_an_error_dict

# Import the flow template
flow_rule_template = {
  "priority": 40000,
  #"timeout": 0,
  "isPermanent": 'true',
  "deviceId": "of:0000000000000001",
  "tableId": 2,
  "treatment": {
    "instructions": [
      {"type": "OUTPUT","port": '9'}
    ]
  },
  "selector": {
    "criteria": [
      {"type": "IN_PORT","port": "10"},
    ]
  }
}

flow_rule_drop_template = {
  "priority": 50000,
  #"timeout": 0,
  "isPermanent": 'true',
  "deviceId": "of:0000000000000001",
  "tableId": 0,
  "treatment": {
    "instructions": [
      {"type": "NOACTION"}
    ]
  },
  "selector": {
    "criteria": [ 
        {
        "type": "ETH_SRC",
        "mac": "00:00:11:00:00:01"
      },
    ]
  }
}

# IP of the controller and login information
controller_ip = 'http://127.0.0.1:8181/onos/v1/'
onos_login_username = 'onos'
onos_login_password = 'rocks'

# Config for pprint
pp = pprint.PrettyPrinter(indent=2)

# Header information used by the html requests
headers = {'Content-type':'application/json', 'Accept':'application/json'}
del_headers = {'Accept': 'application/json'}


# [POST] Used to add a flow rule to a switch
add_flow_rule_endpoint = controller_ip + 'flows/deviceId'

# [GET] Used to get all the flow rules from every switch connected to the ONOS controller
get_all_flows_endpoint = controller_ip + 'flows'

# [DELETE] Removes a single flow rule from a specific controller
delete_flow_endpoint = controller_ip + 'flows/deviceId/flowId/'

# [GET] Provides information about the hosts on the network
get_topology_information_endpoint = controller_ip + 'hosts'

# [GET] Provides information about switch to switch links
get_switch_links_endpoint = controller_ip + 'links'

# [GET] Provides statistics about network devices
get_network_statistics_endpoint = controller_ip + 'statistics/delta/ports'


def add_flow(flow_rule):
    """
    Adds a flow rule to a particular ONOS switch

    Arguments:
        flow_rule {Dictionary} -- A flow rule formatted to be read by an ONOS controller

    Returns:
        [Dictionary] -- Returns a status dict depending on the outcome of the operation
    """
    with requests.Session() as session:
        mac_addr = flow_rule['deviceId']
        uri = add_flow_rule_endpoint
        uri = uri.replace('deviceId', mac_addr)
        req = requests.post(uri, json=flow_rule, headers=headers, auth=(onos_login_username, onos_login_password))
        session.close()
        
    # check return code
    data = {}
    if req.status_code == 201:
        data = {'status_success': 'Flow successfully added', 'flow_url': req.headers['location']}
    else:
        data = create_error_status(req, 'Error adding flow') 
        
    return data
        

def del_flow(device_id, flow_id):
    """
    Deletes a flow rule from a specific switch
    
    Arguments:
        device_id {String} -- The id of the switch to delete the flow from
        flow_id {[type]} -- The id of the flow to delete
    
    Returns:
        [Dictionary] -- Returns a status dict depending on the outcome of the operation
    """
    with requests.Session() as session:
        # add details of flow to delete to endpoint uri
        uri = delete_flow_endpoint
        uri = uri.replace('deviceId', device_id)
        uri = uri.replace('flowId', flow_id)
        #print(uri)
        req = requests.delete(uri, headers=del_headers, auth=(onos_login_username, onos_login_password))
        session.close()
        
    # check status code
    return {'status_success':'Flow rule deleted'} if req.status_code == 204 else create_error_status(req, 'Failed to delete flow rule') 
    

def get_flows():
    """
    Gets all the flows on all the switches connected to the ONOS controller

    Returns:
        [Dictionary] -- Returns a list of flows or a status dictionary depending on the success of the API call
    """
    with requests.Session() as session:
        req = requests.get(get_all_flows_endpoint, auth=(onos_login_username, onos_login_password))
        session.close()
    
    # Check the status code
    return json.loads(req.text)['flows'] if req.status_code == 200 else create_error_status(req, 'Failed to get flows')
  
      
def del_all_flows():
  """
  Deletes all the flows stored on all the controllers
  
  Returns:
      [Dictionary] -- Returns a status dict depending on the outcome of the operation
  """
  flow_list = get_flows()
  data = {'status_success': 'All flows deleted successfully'}
  
  # If an error is returned from get_flows(), change the message in data
  if is_dict_an_error_dict(flow_list):
    data = flow_list
  else:
    # delete all the flows in the flow_list
    for flow in flow_list:
      del_flow(flow['deviceId'], flow['id'])
    
  return data


def search_for_flow_rule(flow_rule_id):
    """
    Searches for a flow rule across all the switches
    
    Arguments:
        flow_rule_id {String} -- The id of the flow to search for
    
    Returns:
        [DIctionary] -- Will return the flow is a matching flow is found or a status dict on failure
    """
    flow_list = get_flows()
    data = {'status_error':'Flow rule not found', 
            'number_of_flows': len(flow_list)}
    
    for flow in flow_list:
        if flow['id'] == flow_rule_id:
            data = flow
            
    return data


def modify_a_flow(old_flow_id, new_flow):
    """
    Take an exisiting flow, delete it and replace it with a flow with the same id with different parameters
    
    Arguments:
        old_flow_id {String} -- The id of the old flow to delete
        new_flow {Dictionary} -- The new flow to add to the switch
    
    Returns:
        [Dict] -- Returns a status dict depending on the outcome of the operation
    """
    old_flow = search_for_flow_rule(old_flow_id)
    data = {}
    
    # check if the search returned an error dict
    if is_dict_an_error_dict(old_flow):
        data = old_flow
    else:
        # If a matching flow was found, grab the info from it
        old_flow_id = old_flow['id']
        old_flow_device_id = old_flow['deviceId']
        status = del_flow(old_flow_device_id, old_flow_id)
        if is_dict_a_success_dict(status):
            # Old flow deleted, add new flow and return status
            data = add_flow(new_flow)
        else:
            # Old flow failed to delete, return status
            data = status
    
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
        - Active and deleted flows
    """
    # Get info about all the hosts on the network
    node_info = get_topology_information()['hosts']
    
    # pp.pprint(node_info)
    # pp.pprint(get_flows())
    # print('------------------')
    # Get a list of the switch names on the network
    switch_list = [x['locations'][0]['elementId'] for x in node_info if 'of' in x['locations'][0]['elementId']]
    
    # Get a list of host mac addresses
    host_list = [x['mac'] for x in node_info]
    
    # Get the links a host has on the network
    host_links = [{'host_mac': x['mac'], 'link': x['locations']} for x in node_info]
    
    # Get all flow rules across all switches
    flows_list = [create_simple_flow_dict(x) for x in get_flows() if x['priority'] != 40000 and x['priority'] != 5]

    return {'switch_list': list(set(switch_list)), 
            'host_list': list(dict.fromkeys(host_list)), 
            'host_links': host_links, 
            'switch_links': get_switch_links()['links'],
            'number_of_hosts': len(host_list),
            'number_of_switches': len(switch_list),
            'flows': flows_list,
            'network_statistics': create_network_statistics_list()
             }


def create_flow_rule(priority, device_id, table_id, in_port, out_port):
  """
  Takes the template ONOS flow rule from onos_flow_template.py and modifies it to create a new flow rule
  
  Arguments:
      priority {String} -- The priority of the flow
      device_id {String} -- The id of the flow
      table_id {String} -- The table the flow will be added to
      in_port {String} -- The in_port of the flow
      out_port {String} -- The out_port of the flow
  
  Returns:
      [Dictionary] -- Returns the requested flow rule
  """
  flow = flow_rule_template
  flow['priority'] = priority
  flow['deviceId'] = device_id
  flow['tableId'] = random.randint(1, 3)
  flow['selector']['criteria'][0]['port'] = in_port
  flow['treatment']['instructions'][0]['port'] = out_port
  
  return flow

def create_flow_drop_rule(device_id, host_to_block):
  """
  Takes the template ONOS flow rule from onos_flow_template.py and modifies it to create a new flow rule
  
  Arguments:
      priority {String} -- The priority of the flow
      device_id {String} -- The id of the flow
      table_id {String} -- The table the flow will be added to
      in_port {String} -- The in_port of the flow
      out_port {String} -- The out_port of the flow
  
  Returns:
      [Dictionary] -- Returns the requested flow rule
  """
  flow = flow_rule_drop_template
  flow['deviceId'] = device_id
  flow['selector']['criteria'][0]['mac'] = host_to_block
  
  return flow


  
  
  


  
  
  
################################
# ONOS SPECIFIC HELPER FUNCTIONS
################################

def get_topology_information():
    """
    Gets network topology information about hosts, switches, links and other info
    
    Returns:
        [Dictionary] -- Returns the topology information or a status dict
    """
    with requests.Session() as session:
        req = requests.get(get_topology_information_endpoint, auth=(onos_login_username, onos_login_password))
        session.close()
    
    # Check the status code
    return json.loads(req.text) if req.status_code == 200 else create_error_status(req, 'Failed to get system information')


def get_switch_links():
    """
    Gets network topology information about hosts, switches, links and other info
    
    Returns:
        [Dictionary] -- Returns the topology information or a status dict
    """
    with requests.Session() as session:
        req = requests.get(get_switch_links_endpoint, auth=(onos_login_username, onos_login_password))
        session.close()
    
    # Check the status code
    return json.loads(req.text) if req.status_code == 200 else create_error_status(req, 'Failed to get system information')


def get_network_statistics():
    """
    Gets network topology information about hosts, switches, links and other info
    
    Returns:
        [Dictionary] -- Returns the topology information or a status dict
    """
    with requests.Session() as session:
        req = requests.get(get_network_statistics_endpoint, auth=(onos_login_username, onos_login_password))
        session.close()
    
    # Check the status code
    return json.loads(req.text) if req.status_code == 200 else create_error_status(req, 'Failed to get network statistics')
  

def create_simple_flow_dict(flow_rule):
    """
    Takes a flow object and extracts relevant information to create a dictionary
    Used to convert a flow from the 'ONOS' format to a general format used by the API
    
    Arguments:
        flow_rule {Dictionary} -- The flow dictionary to pull information from
        switch_name {String} -- The name of the switch the flow came from
    
    Returns:
        [Dictionary] -- A flow rule in a simplified and general format
    """
    return {'switch_name': flow_rule.get('deviceId'),
            'flow_name': flow_rule.get('id'),
            'flow_id': flow_rule.get('id'),
            #'cookie': flow_rule['cookie'],
            'match_condition': flow_rule['selector']['criteria'],
            'out_port': flow_rule['treatment']['instructions'],
            'priority': flow_rule.get('priority'),
            'table_id': flow_rule.get('tableId')
            }

def create_network_statistics_list():
    statistics = get_network_statistics()
    node_info = get_topology_information()['hosts']
    host_links = [{'host_mac': x['mac'], 'link': x['locations']} for x in node_info]
    #pp.pprint(statistics)
    #pp.pprint(switch_links)
    #pp.pprint(host_links)
    
    data = []
    
    if statistics.get('statistics') is not None:
        
        for switch_stats in statistics['statistics']:
            # go through all the switches
            switch = switch_stats['device']
            
            for stat in switch_stats['ports']:
                # go through all the stats for the selected switch
                    
                stat['switch'] = switch
                stat['mac'] = get_host_mac_address_from_port_number(str(stat['port']), str(switch), host_links)
                data.append(stat)
        
        
        for stat in data:
            if len(stat['mac']) == 0:
                stat['mac'] = get_switch_name_from_port_number(str(stat['port']), str(stat['switch']))[0]

            
                    

    else:
        data = []
    
    return data


def get_host_mac_address_from_port_number(port, switch, host_links):
    
    data = ''
    #pp.pprint(host_links)
    for x in host_links:
        if x['link'][0]['elementId'] == switch and x['link'][0]['port'] == port:
            data = x['host_mac']
    
    return data

def get_switch_name_from_port_number(port_src, switch_src):
    switch_links = get_switch_links()['links']
    
    return [x['dst']['device'] for x in switch_links if x['src']['device'] == switch_src and x['src']['port'] == port_src]
    
    



#print(del_flow('of:0000000000000002', '54043195772693806'))

#print((search_for_flow_rule('54043195761223953')))


#print(modify_a_flow('54043195761223953', flow_rule_example))

#pp.pprint(get_flows())
#del_all_flows()

# block_flow = create_flow_drop_rule('of:0000000000000001', '66:26:23:3F:17:93')
# print(block_flow)

# pp.pprint(add_flow(block_flow))
#pp.pprint(create_simple_flow_dict(get_flows()[4]))

#pp.pprint(add_flow(create_flow_rule(random.randint(1,10000), 'of:0000000000000001', random.randint(1, 3), random.randint(1,100), random.randint(1,100))))

#pp.pprint(get_network_information())

#pp.pprint(get_network_statistics())

#pp.pprint(get_switch_name_from_port_number('2', 'of:0000000000000001'))

#pp.pprint(create_network_statistics_list())

# node_info = get_topology_information()['hosts']
# host_links = [{'host_mac': x['mac'], 'link': x['locations']} for x in node_info]

#pp.pprint(get_host_mac_address_from_port_number('1', 'of:0000000000000003', host_links ))