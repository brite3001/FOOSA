import pytest
import pprint
import time
import random

# Import status code helper functions
import sys
sys.path.append("..")
from status_helper_functions import is_dict_a_success_dict, is_dict_an_error_dict

# Config for pprint
pp = pprint.PrettyPrinter(indent=4)

# Import functions from the FL API
from onos_api import add_flow, del_flow, del_all_flows, search_for_flow_rule, modify_a_flow, get_flows, create_flow_rule, get_network_information

# Flows targeting switch 1
flow_rule_one = create_flow_rule('1000', 'of:0000000000000001', '1', '10', '11')
flow_rule_two = create_flow_rule('1000', 'of:0000000000000001', '1', '12', '13')
flow_rule_three = create_flow_rule('1000', 'of:0000000000000001', '1', '14', '15')
flow_rule_four = create_flow_rule('1000', 'of:0000000000000001', '1', '16', '17')
flow_rule_five = create_flow_rule('1000', 'of:0000000000000001', '1', '18', '19')

# Flows targeting switch 2
flow_rule_six = create_flow_rule('2000', 'of:0000000000000002', '2', '20', '21')
flow_rule_seven = create_flow_rule('2000', 'of:0000000000000002', '2', '22', '23')
flow_rule_eight = create_flow_rule('2000', 'of:0000000000000002', '2', '24', '25')
flow_rule_nine = create_flow_rule('2000', 'of:0000000000000002', '2', '26', '27')
flow_rule_ten = create_flow_rule('2000', 'of:0000000000000002', '2', '28', '29')



def add_flow_rules_switch_one():
    assert is_dict_a_success_dict(add_flow(flow_rule_one)),"Failed to add Flow Rule 1 to switch 1!!"
    assert is_dict_a_success_dict(add_flow(flow_rule_two)),"Failed to add Flow Rule 2 to switch 1!!"
    assert is_dict_a_success_dict(add_flow(flow_rule_three)),"Failed to add Flow Rule 3 to switch 1!!"
    assert is_dict_a_success_dict(add_flow(flow_rule_four)),"Failed to add Flow Rule 4 to switch 1!!"
    assert is_dict_a_success_dict(add_flow(flow_rule_five)),"Failed to add Flow Rule 5 to switch 1!!"

def add_flow_rules_switch_two():
    assert is_dict_a_success_dict(add_flow(flow_rule_six)),"Failed to add Flow Rule 6 to switch 2!!"
    assert is_dict_a_success_dict(add_flow(flow_rule_seven)),"Failed to add Flow Rule 7 to switch 2!!"
    assert is_dict_a_success_dict(add_flow(flow_rule_eight)),"Failed to add Flow Rule 8 to switch 2!!"
    assert is_dict_a_success_dict(add_flow(flow_rule_nine)),"Failed to add Flow Rule 9 to switch 2!!"
    assert is_dict_a_success_dict(add_flow(flow_rule_ten)),"Failed to add Flow Rule 10 to switch 2!!"



flow_list = [{'flow_id':flow['id'], 'device_id':flow['deviceId']} for flow in get_flows()]

def check_flow_rules_are_on_switches():
    
    if len(flow_list) == 10:
        assert not(is_dict_an_error_dict(search_for_flow_rule(flow_list[0]['flow_id']))),"A flow rule was not found!!"
        assert not(is_dict_an_error_dict(search_for_flow_rule(flow_list[1]['flow_id']))),"A flow rule was not found!!"
        assert not(is_dict_an_error_dict(search_for_flow_rule(flow_list[2]['flow_id']))),"A flow rule was not found!!"
        assert not(is_dict_an_error_dict(search_for_flow_rule(flow_list[3]['flow_id']))),"A flow rule was not found!!"
        assert not(is_dict_an_error_dict(search_for_flow_rule(flow_list[4]['flow_id']))),"A flow rule was not found!!"
        assert not(is_dict_an_error_dict(search_for_flow_rule(flow_list[5]['flow_id']))),"A flow rule was not found!!"
        assert not(is_dict_an_error_dict(search_for_flow_rule(flow_list[6]['flow_id']))),"A flow rule was not found!!"
        assert not(is_dict_an_error_dict(search_for_flow_rule(flow_list[7]['flow_id']))),"A flow rule was not found!!"
        assert not(is_dict_an_error_dict(search_for_flow_rule(flow_list[8]['flow_id']))),"A flow rule was not found!!"
        assert not(is_dict_an_error_dict(search_for_flow_rule(flow_list[9]['flow_id']))),"A flow rule was not found!!"
    else:
        assert False, "The number of flows returned by get_flows() is not 10!!"
        

def delete_flows():
    assert is_dict_a_success_dict(del_flow(flow_list[0]['device_id'], flow_list[0]['flow_id'])),"Failed to delete flow_list[0]"
    assert is_dict_a_success_dict(del_flow(flow_list[1]['device_id'], flow_list[1]['flow_id'])),"Failed to delete flow_list[1]"
    assert is_dict_a_success_dict(del_flow(flow_list[2]['device_id'], flow_list[2]['flow_id'])),"Failed to delete flow_list[2]"
    assert is_dict_a_success_dict(del_flow(flow_list[3]['device_id'], flow_list[3]['flow_id'])),"Failed to delete flow_list[3]"

def check_flows_where_deleted():
    assert (is_dict_an_error_dict(search_for_flow_rule(flow_list[0]['flow_id']))),"Flow flow_list[0] was not removed!!"
    assert (is_dict_an_error_dict(search_for_flow_rule(flow_list[1]['flow_id']))),"Flow flow_list[1] was not removed!!"
    assert (is_dict_an_error_dict(search_for_flow_rule(flow_list[2]['flow_id']))),"Flow flow_list[2] was not removed!!"
    assert (is_dict_an_error_dict(search_for_flow_rule(flow_list[3]['flow_id']))),"Flow flow_list[3] was not removed!!"
    

if __name__ == '__main__':
    #del_all_flows()
    add_flow_rules_switch_one()
    add_flow_rules_switch_two()
    pp.pprint(get_network_information())
    check_flow_rules_are_on_switches()
    delete_flows()
    check_flows_where_deleted()
    #del_all_flows()
    
    print('All Tests Passed Successfully')
    