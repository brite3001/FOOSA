import pytest
import pprint
import time

# Import status code helper functions
import sys
sys.path.append("..")
from status_helper_functions import is_dict_a_success_dict, is_dict_an_error_dict

# Import functions from the FL API
from odl_api import add_flow, del_flow, del_all_flows, search_for_flow_rule, modify_a_flow, get_flows, get_network_information, create_flow_rule

# Config for pprint
pp = pprint.PrettyPrinter(indent=4)

# Flow rules for testing
flow_rule_one = create_flow_rule('2', '11', 'flow-11', '10', '11', '999')
flow_rule_two = create_flow_rule('2', '12', 'flow-12', '12', '13', '999')
flow_rule_three = create_flow_rule('2', '13', 'flow-13', '14', '15', '999')
flow_rule_four = create_flow_rule('2', '14', 'flow-14', '16', '17', '999')
flow_rule_five = create_flow_rule('2', '15', 'flow-15', '18', '19', '999')
flow_rule_six = create_flow_rule('2', '21', 'flow-21', '20', '21', '999')
flow_rule_seven = create_flow_rule('2', '22', 'flow-22', '22', '23', '999')
flow_rule_eight = create_flow_rule('2', '23', 'flow-23', '24', '25', '999')
flow_rule_nine = create_flow_rule('2', '24', 'flow-24', '26', '27', '999')
flow_rule_ten = create_flow_rule('2', '25', 'flow-25', '28', '29', '999')

flow_modify_one = create_flow_rule('2', '14', 'flow-14', '34', '35', '1234')
flow_modify_two = create_flow_rule('2', '24', 'flow-24', '46', '47', '1235')


def add_flow_rules_switch_one():
    assert is_dict_a_success_dict(add_flow(flow_rule_one, 'openflow:1')),"Failed to add Flow Rule 1 to switch 1!!"
    assert is_dict_a_success_dict(add_flow(flow_rule_two, 'openflow:1')),"Failed to add Flow Rule 2 to switch 1!!"
    assert is_dict_a_success_dict(add_flow(flow_rule_three, 'openflow:1')),"Failed to add Flow Rule 3 to switch 1!!"
    assert is_dict_a_success_dict(add_flow(flow_rule_four, 'openflow:1')),"Failed to add Flow Rule 4 to switch 1!!"
    assert is_dict_a_success_dict(add_flow(flow_rule_five, 'openflow:1')),"Failed to add Flow Rule 5 to switch 1!!"

def add_flow_rules_switch_two():
    assert is_dict_a_success_dict(add_flow(flow_rule_six, 'openflow:2')),"Failed to add Flow Rule 6 to switch 2!!"
    assert is_dict_a_success_dict(add_flow(flow_rule_seven, 'openflow:2')),"Failed to add Flow Rule 7 to switch 2!!"
    assert is_dict_a_success_dict(add_flow(flow_rule_eight, 'openflow:2')),"Failed to add Flow Rule 8 to switch 2!!"
    assert is_dict_a_success_dict(add_flow(flow_rule_nine, 'openflow:2')),"Failed to add Flow Rule 9 to switch 2!!"
    assert is_dict_a_success_dict(add_flow(flow_rule_ten, 'openflow:2')),"Failed to add Flow Rule 10 to switch 2!!"


def check_flow_rules_are_on_switches():    
    assert not(is_dict_an_error_dict(search_for_flow_rule('11', 'openflow:1'))),"flow 1 was not found!!"
    assert not(is_dict_an_error_dict(search_for_flow_rule('12', 'openflow:1'))),"flow 2 was not found!!"
    assert not(is_dict_an_error_dict(search_for_flow_rule('13', 'openflow:1'))),"flow 3 was not found!!"
    assert not(is_dict_an_error_dict(search_for_flow_rule('14', 'openflow:1'))),"flow 4 was not found!!"
    assert not(is_dict_an_error_dict(search_for_flow_rule('15', 'openflow:1'))),"flow 5 was not found!!"
    assert not(is_dict_an_error_dict(search_for_flow_rule('21', 'openflow:2'))),"flow 6 was not found!!"
    assert not(is_dict_an_error_dict(search_for_flow_rule('22', 'openflow:2'))),"flow 7 was not found!!"
    assert not(is_dict_an_error_dict(search_for_flow_rule('23', 'openflow:2'))),"flow 8 was not found!!"
    assert not(is_dict_an_error_dict(search_for_flow_rule('24', 'openflow:2'))),"flow 9 was not found!!"
    assert not(is_dict_an_error_dict(search_for_flow_rule('25', 'openflow:2'))),"flow 10 was not found!!"
        

def delete_flows():
    assert is_dict_a_success_dict(del_flow('openflow:1', '12')),"Failed to delete flow 2"
    assert is_dict_a_success_dict(del_flow('openflow:1', '13')),"Failed to delete flow 3"
    assert is_dict_a_success_dict(del_flow('openflow:2', '22')),"Failed to delete flow 7"
    assert is_dict_a_success_dict(del_flow('openflow:2', '23')),"Failed to delete flow 8"

def check_flows_where_deleted():
    assert (is_dict_an_error_dict(search_for_flow_rule('12', 'openflow:1'))),"Flow flow 2 was not removed!!"
    assert (is_dict_an_error_dict(search_for_flow_rule('13', 'openflow:1'))),"Flow flow 3 was not removed!!"
    assert (is_dict_an_error_dict(search_for_flow_rule('22', 'openflow:2'))),"Flow flow 7 was not removed!!"
    assert (is_dict_an_error_dict(search_for_flow_rule('23', 'openflow:2'))),"Flow flow 8 was not removed!!"


def modify_flows():
    assert (is_dict_a_success_dict(modify_a_flow('openflow:1', '14', flow_modify_one)))
    assert (is_dict_a_success_dict(modify_a_flow('openflow:2', '24', flow_modify_two)))


def check_flows_where_modified():
    assert (search_for_flow_rule('14', 'openflow:1')['out_port'] == 34), 'Flow 4''s out_port is not correct!'
    assert (search_for_flow_rule('24', 'openflow:2')['out_port'] == 46), 'Flow 9''s out_port is not correct!'
    assert (search_for_flow_rule('14', 'openflow:1')['match_condition']['in-port'] == '35'), 'Flow 4''s in_port is not correct!'
    assert (search_for_flow_rule('24', 'openflow:2')['match_condition']['in-port'] == '47'), 'Flow 9''s in_port is not correct!'
    
def check_network_topology():
    topology = get_network_information()
    assert len(topology['flows']) == 6, 'Topology not listing the right amount of flows'
    assert len(topology['host_list']) == 2, 'Topology not listing the right amount of hosts'
    assert len(topology['switch_list']) == 2, 'Topology not listing the right amount of switches'
    

if __name__ == '__main__':
    del_all_flows()
    add_flow_rules_switch_one()
    add_flow_rules_switch_two()
    check_flow_rules_are_on_switches()
    delete_flows()
    check_flows_where_deleted()
    modify_flows()
    check_flows_where_modified()
    check_network_topology()
    del_all_flows()
    
    print('All Tests Passed Successfully')
    