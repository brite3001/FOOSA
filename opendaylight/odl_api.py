import requests
import pprint
import json
import re
import xml.etree.ElementTree as ET

# Used to parse the flow rules for ODL, as they're formatted in XML
from bs4 import BeautifulSoup

# Used to import the helper function
import sys
sys.path.append("..")
from status_helper_functions import create_error_status, is_dict_a_success_dict, is_dict_an_error_dict

# IP of the controller and login information
controller_ip = 'http://127.0.0.1:8181/restconf/'
odl_login_username = 'admin'
odl_login_password = 'admin'

# Config for pprint
pp = pprint.PrettyPrinter(indent=2)


######################
# ENDPOINT STRINGS
######################

# [POST] endpoint used to add a flow
add_flow_rule_endpoint = controller_ip + 'config/opendaylight-inventory:nodes/node/switch_name/table/table_id'
# 'config/opendaylight-inventory:nodes/node/openflow:1/table/2'

# [POST] endpoint used to get all the flows in a particular switch
get_flows_endpoint = controller_ip + 'config/opendaylight-inventory:nodes/node/switch_name'

# [DEL] endpoint used to delete a flow rule
del_flow_endpoint = controller_ip + 'config/opendaylight-inventory:nodes/node/switch_name/table/table_number/flow/flow_id'
#'config/opendaylight-inventory:nodes/opendaylight-inventory:node/switch_name/flow-node-inventory:table/flow_id/flow-node-inventory:flow/flow_id'

# [GET] endpoint used to query the controller for network information
get_network_topology_endpoint = controller_ip + 'operational/network-topology:network-topology/topology/flow:1'

# [GET] get links between switches
get_switch_links_endpoint = controller_ip + 'config/network-topology:network-topolog/link/openflow:1'

# [GET] grabs statistics about the network
get_network_statistics_endpoint = controller_ip + 'operations/opendaylight-port-statistics:get-all-node-connectors-statistics'

# Header information used by the html requests/v1/model/controller-node
headers = {'Content-type':'application/xml', 'Accept':'application/json'}
del_headers = {'Accept': 'application/xml'}

####################
# FLOW RULE TEMPLATE
####################

flow_rule_template = \
"""<flow xmlns="urn:opendaylight:flow:inventory">
    <strict>false</strict>
    <instructions>
        <instruction>
          	<order>1</order>
            <apply-actions>
                <action>
                  <order>1</order>
                    <output-action>
                        <output-node-connector>NORMAL</output-node-connector>
                    </output-action>
                </action>
            </apply-actions>
        </instruction>
    </instructions>
    <table_id>1</table_id>
    <id>flow_id_to_replace</id>
    <cookie_mask>10</cookie_mask>
    <out_port>out_port_to_replace</out_port>
    <installHw>false</installHw>
    <out_group>2</out_group>
    <match>
        <in-port>in_port_to_replace</in-port>
    </match>
    <hard-timeout>0</hard-timeout>
    <cookie>cookie_to_replace</cookie>
    <idle-timeout>0</idle-timeout>
    <flow-name>flow_name_to_replace</flow-name>
    <priority>priority_to_replace</priority>
    <barrier>false</barrier>
</flow>"""

flow_rule_template_drop = \
"""<flow xmlns="urn:opendaylight:flow:inventory">
    <strict>false</strict>
    <instructions>
        <instruction>
          	<order>1</order>
            <apply-actions>
                <action>
                  <order>0</order>
                  <drop-action/>
                </action>
            </apply-actions>
        </instruction>
    </instructions>
    <table_id>0</table_id>
    <id>id_to_replace</id>
    <cookie_mask>10</cookie_mask>
    <installHw>false</installHw>
    <out_group>2</out_group>
    <match>
        <ethernet-match>
            <ethernet-type>
                <type>2048</type>
            </ethernet-type>
            <ethernet-destination>
                <address>mac_to_replace</address>
            </ethernet-destination>
        </ethernet-match>
    </match>
    <hard-timeout>0</hard-timeout>
    <cookie>cookie_to_replace</cookie>
    <idle-timeout>0</idle-timeout>
    <flow-name>flow_name_to_replace</flow-name>
    <priority>priority_to_replace</priority>
    <barrier>false</barrier>
</flow>"""

test_drop = \
"""<flow xmlns="urn:opendaylight:flow:inventory">
    <strict>false</strict>
    <instructions>
        <instruction>
            <order>0</order>
            <apply-actions>
                <action>
                    <order>0</order>
                    <drop-action/>
                </action>
            </apply-actions>
        </instruction>
    </instructions>
    <table_id>0</table_id>
    <id>31</id>
    <cookie_mask>255</cookie_mask>
    <installHw>false</installHw>
    <match>
        <ethernet-match>
            <ethernet-source>
                <address>1a:9a:ad:2e:09:f8</address>
            </ethernet-source>
        </ethernet-match>
    </match>
    <cookie>3</cookie>
    <flow-name>FooXf3</flow-name>
    <priority>65000</priority>
    <barrier>false</barrier>
</flow> """






########################
# GENERIC API FUNCTIONS
########################

def add_flow(flow_rule, switch_name):
    """Add a flow rule to a particular switch
    
    Arguments:
        flow_rule {String} -- An XML file formatted as a string, can be generated from the function create_flow_rule()
        switch_name {String} -- Name of the switch, for ODL switch names are formatted as 'openflow:x'
    
    Returns:
        [Dictionary] -- Returns a status_success or status_error dictionary depending on the outcome of the operation
    """
    with requests.Session() as session:
        #bs = BeautifulSoup(flow_rule, features='html.parser')
        #flow_table_id = str(bs.findAll('id')[0]).replace('<id>', '').replace('</id>', '')
        uri = add_flow_rule_endpoint
        uri = uri.replace('switch_name', switch_name)
        uri = uri.replace('table_id', '1')
        #print(uri)

        #pp.pprint(flow_rule[0])
        req = requests.post(uri, data=flow_rule, headers=headers, auth=(odl_login_username, odl_login_password))
        session.close()
        
    # check return code
    return {'status_success': 'Flow successfully added', 'flow_url': req.headers['location']} if req.status_code == 204 else create_error_status(req, 'Error adding flow') 
    
    
def get_flows(switch_name):
    """
    Returns all the flows on a particular switch
    
    Arguments:
        switch_name {String} -- Name of the switch, for ODL switch names are formatted as 'openflow:x'
    
    Returns:
        [Dictionary] -- Returns a dictionary of flow rules if successful, else returns a satus_error dictionary
    """
    with requests.Session() as session:
        uri = get_flows_endpoint
        uri = uri.replace('switch_name', switch_name)

        #pp.pprint(flow_rule[0])
        req = requests.get(uri, headers=headers, auth=(odl_login_username, odl_login_password))
        session.close()
        
        
    # check return code
    return json.loads(req.text)['node'][0]['flow-node-inventory:table'] if req.status_code == 200 else create_error_status(req, 'Failed to get flow') 


def del_flow(switch_name, flow_id):
    """
    Deletes a single flow rule
    
    Arguments:
        switch_name {String} -- The name of the switch, for ODL formatted as 'openflow:x'
        flow_id {String} -- The id of the flow rule to delete
    
    Returns:
        [Dictionary] -- Returns a status_success or status_error dictionary
    """
    with requests.Session() as session:
        # add details of flow to delete to endpoint uri
        uri = del_flow_endpoint
        uri = uri.replace('flow_id', flow_id, 2).replace('switch_name', switch_name).replace('table_number', '1')
        #print(uri)
        req = requests.delete(uri, headers=del_headers, auth=(odl_login_username, odl_login_password))
        session.close()
        
    # check status code
    return {'status_success':'Flow rule deleted'} if req.status_code == 200 else create_error_status(req, 'Failed to delete flow rule')


def modify_a_flow(switch_name, flow_id, flow):
    """
    Change an already existing flow
    
    Arguments:
        switch_name {String} -- The name of the switch to edit the flow on
        flow_id {String} -- The id of the flow to edit
        flow {Dictionary} -- The flow with the modified parameters
    
    Returns:
        [Dictionary] -- Returns a status_success or status_error depending on the outcome
    """
    status_del = del_flow(switch_name, flow_id)
    status_add = add_flow(flow, switch_name)
    
    if is_dict_a_success_dict(status_add) and is_dict_a_success_dict(status_del):
        data = {'status_success': 'Flow updated successfully'}
    elif is_dict_an_error_dict(status_del) and is_dict_a_success_dict(status_add):
        data = {'status_success':'No matching flow to delete, flow added successfully'}
    else:
        data = {'status_error':'Failed to replace flow'}
    
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
    # Get info about all the nodes on the network
    
    node_info = get_topology_information().get('topology')
    if node_info is not None:
        node_info = get_topology_information().get('topology')[0]['node'] 
    else:
        node_info = []
    
    
    # Get a list of the switch names on the network
    switch_list = [x['node-id'] for x in node_info if 'openflow' in x['node-id']]
    
    # Get a list of host mac addresses
    host_list = [x['host-tracker-service:id'] for x in node_info if 'host-tracker-service:id' in list(x)]
    
    # Get the links a host has on the network
    host_links = [x['host-tracker-service:attachment-points'] for x in node_info if 'host-tracker-service:attachment-points' in list(x)]
    
    # Get all flow rules across all switches
    all_flows_list = [get_flows(switch) for switch in switch_list]
    
    # get all the switch to switch links
    switch_links = get_topology_information().get('topology')
    if switch_links is not None:
        switch_links = [[x['source'], x['destination']] for x in get_topology_information()['topology'][0]['link'] if len(x['link-id']) == 12]
    else:
        switch_links = []
    
    return {'switch_list': switch_list, 
            'host_list': host_list, 
            'host_links': host_links, 
            'switch_links': switch_links,
            'number_of_hosts': len(host_list),
            'number_of_switches': len(switch_list),
            'flows': create_simplfied_flows_list(switch_list, all_flows_list)
            }
    

def del_all_flows():
    """
    Iterates through all switches on the network and deletes all their flows
    
    Returns:
        [type] -- [description]
    """
    flows = get_network_information()['flows']
    successfully_flow_deletions = 0
    failed_flow_deletions = 0
    
    for flow in flows:
        status = del_flow(flow['switch_name'], flow['flow_id'])
        if is_dict_a_success_dict(status):
            successfully_flow_deletions += 1
        else:
            failed_flow_deletions += 1

    if failed_flow_deletions > 0:
        data = {'status_error':'Failed to delete ' + str(failed_flow_deletions) + 'flows'}
    else:
        data = {'status_success': 'Deleted: ' + str(len(flows)) + ' flow rules'}
    
    return data


def create_flow_rule(cookie, flow_id, flow_name, out_port, in_port, priority):
    """
    Creates a simple flow rule which uses matches via in-port packets
    
    Arguments:
        cookie {String} -- The cookie value in the flow rule
        flow_id {String} -- The id of the flow rule
        flow_name {String} -- The name of the flow rule
        out_port {String} -- The port which the packets are output
        in_port {String} -- The 'matching part' of the flow rule
        priority {String} -- The priority of the flow rule
    
    Returns:
        [String] -- The modifed flow rule with the requested parameters as an XML file formatted as a String
    """
    flow = flow_rule_template
    text_to_change_list = ['cookie_to_replace', 'flow_id_to_replace', 'flow_name_to_replace', 'out_port_to_replace', 'in_port_to_replace', 'priority_to_replace']
    attributes_list = [cookie, flow_id, flow_name, out_port, in_port, priority]

    tree = ET.ElementTree(ET.fromstring(flow))
    root = tree.getroot()

    for elem in root.getiterator():
        try:
            for text_to_change, attribute in zip(text_to_change_list, attributes_list):
                elem.text = elem.text.replace(text_to_change, attribute)
        except AttributeError:
            pass
        
    return ET.tostring(root, encoding='unicode')


def create_flow_rule_drop(flow_id, flow_name, mac_to_block, cookie, priority):
    
    flow = flow_rule_template_drop
    text_to_change_list = ['cookie_to_replace', 'id_to_replace', 'flow_name_to_replace', 'priority_to_replace', 'mac_to_replace']
    attributes_list = [cookie, flow_id, flow_name, priority, mac_to_block]

    tree = ET.ElementTree(ET.fromstring(flow))
    root = tree.getroot()

    for elem in root.getiterator():
        try:
            for text_to_change, attribute in zip(text_to_change_list, attributes_list):
                elem.text = elem.text.replace(text_to_change, attribute)
        except AttributeError:
            pass
        
    return ET.tostring(root, encoding='unicode')
    

    


def search_for_flow_rule(flow_id, switch_name):
    """
    Checks the flow list for a particular flow
    
    Arguments:
        flow_id {String} -- The id of the flow rule to search for
        switch_name {String} -- The switch to search for the particular flow
    
    Returns:
        [Dictionary] -- Returns the flow rule if found, or a status_error if not found
    """
    flows_list = get_network_information()['flows']
    
    data = {'status_error': 'flow not found'}
    for flow in flows_list:
        if flow['switch_name'] == switch_name and flow['flow_id'] == flow_id:
            data = flow
    
    return data
    
    
    


    
###############################
# ODL SPECIFIC HELPER FUNCTIONS
###############################

def create_simple_flow_dict(flow_rule, switch_name):
    """
    Takes a flow object and extracts relevant information to create a dictionary
    
    Arguments:
        flow_rule {Dictionary} -- The flow dictionary to pull information from
        switch_name {String} -- The name of the switch the flow came from
    
    Returns:
        [type] -- [description]
    """
    return {'switch_name': switch_name,
            'flow_name': flow_rule.get('flow-name'),
            'flow_id': flow_rule.get('id'),
            'cookie': flow_rule.get('cookie'),
            'match_condition': flow_rule.get('match'),
            'out_port': flow_rule.get('out_port'),
            'priority': flow_rule.get('priority'),
            }

def create_simplfied_flows_list(switch_list, flow_list):
    """
    Takes a list of switches and flows, and creates a list of flow rules with simplified descriptions using create_simple_flow_dict() on each flow object
    
    Arguments:
        switch_list {List} -- A list of switch names
        flow_list {List} -- A list which contains dictionaries of flow rules
    
    Returns:
        [Dictionary] -- A dictionary with a list of active flows and a list of deleted flows
    """

    #deleted_flows_list = []
    live_flows_list = []
    
    # pp.pprint((flow_list))
    # print('------------------')
    
    for flows_in_a_single_switch, switch_name in zip(flow_list, switch_list):
        #pp.pprint(type(flows_in_a_single_switch))
        
        # check if there are flows in the list and check to see if it is a list,
        # if its a dict, that means its an error message and not a list of flows
        if isinstance(flows_in_a_single_switch, list) and 'flow' in list(flows_in_a_single_switch[0]):
            
            # go through each individual flow for each switch
            for flow in flows_in_a_single_switch[0]['flow']:
                
                # create a standard flow info dict for a single flow and add it to the live_flows list
                live_flows_list.append(create_simple_flow_dict(flow, switch_name))
            
    
    
    
    return live_flows_list


def get_topology_information():
    """
    Queries the ODL controller for topology information which is the main dict used in get_network_information()
    
    Returns:
        [Dictionary] -- Information about switches, hosts and links on the network
    """
    with requests.Session() as session:
        req = requests.get(get_network_topology_endpoint, headers=headers, auth=(odl_login_username, odl_login_password))
        session.close()
        
    # check return code
    return json.loads(req.text) if req.status_code == 200 else create_error_status(req, 'Failed to get topology information')

def get_network_statistics():
    """
    Queries the ODL controller for topology information which is the main dict used in get_network_information()
    
    Returns:
        [Dictionary] -- Information about switches, hosts and links on the network
    """
    with requests.Session() as session:
        req = requests.get(get_network_statistics_endpoint, headers=headers, auth=(odl_login_username, odl_login_password))
        session.close()
        
    # check return code
    return json.loads(req.text) if req.status_code == 200 else create_error_status(req, 'Failed to get topology information')

    
     

#pp.pprint(create_simple_flow_dict(get_flows('openflow:2')[1]['flow'][0], 'openflow:2'))

#pp.pprint(get_topology_information())

#pp.pprint(get_flows('openflow:1'))

#pp.pprint(del_all_flows())


flow_rule_one = create_flow_rule(cookie = '2',
                                 flow_id = '1',
                                 flow_name = 'flow-1',
                                 out_port = '1',
                                 in_port = '1',
                                 priority = '200')

#pp.pprint(flow_rule_one)

#pp.pprint(add_flow(flow_rule_template_drop, 'openflow:1'))

#pp.pprint(modify_a_flow('openflow:1', '69', flow_rule_one))

#pp.pprint(add_flow(flow_rule_template, 'openflow:1')


#get_flows('openflow:1')
 
#pp.pprint(del_flow('openflow:1', '11'))


#pp.pprint(get_network_information())

#pp.pprint(search_for_flow_rule('12', 'openflow:2'))

#pp.pprint(get_topology_information())

#flow_rule_drop = create_flow_rule_drop('777', 'flow-drop-ce07', 'ce:07:ca:c0:9c:d0', '12', '999')

#pp.pprint(add_flow(test_drop, 'openflow:2'))

#pp.pprint(flow_rule_drop)

#pp.pprint(get_network_statistics())
    


