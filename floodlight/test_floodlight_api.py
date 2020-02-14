import pytest

# Import functions from the FL API
from floodlight_api import add_flow, del_flow, get_switch_flow_rules, remove_all_flows_and_groups, search_for_flow_rule

# Import status code helper functions
import sys
sys.path.append("..")
from status_helper_functions import is_dict_a_success_dict, is_dict_an_error_dict

# These are flow rules that target the switch 00:00:00:00:00:00:00:01
from floodlight_example_flows import flow_rule_one, flow_rule_two, flow_rule_three, flow_rule_four, flow_rule_five

# These flow rules target switch 00:00:00:00:00:00:00:02
from floodlight_example_flows import flow_rule_six, flow_rule_seven, flow_rule_eight, flow_rule_nine, flow_rule_ten

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


def check_flow_rules_switch_one():
    assert list(search_for_flow_rule('flow-rule-1', '00:00:00:00:00:00:00:01'))[0] == 'flow-rule-1',"Failed to find flow-rule-1 in switch 1"
    assert list(search_for_flow_rule('flow-rule-2', '00:00:00:00:00:00:00:01'))[0] == 'flow-rule-2',"Failed to find flow-rule-2 in switch 1"
    assert list(search_for_flow_rule('flow-rule-3', '00:00:00:00:00:00:00:01'))[0] == 'flow-rule-3',"Failed to find flow-rule-3 in switch 1"
    assert list(search_for_flow_rule('flow-rule-4', '00:00:00:00:00:00:00:01'))[0] == 'flow-rule-4',"Failed to find flow-rule-4 in switch 1"
    assert list(search_for_flow_rule('flow-rule-5', '00:00:00:00:00:00:00:01'))[0] == 'flow-rule-5',"Failed to find flow-rule-5 in switch 1"
    


def check_flow_rules_switch_two():
    assert list(search_for_flow_rule('flow-rule-6', '00:00:00:00:00:00:00:02'))[0] == 'flow-rule-6',"Failed to find flow-rule-6 in switch 2"
    assert list(search_for_flow_rule('flow-rule-7', '00:00:00:00:00:00:00:02'))[0] == 'flow-rule-7',"Failed to find flow-rule-7 in switch 2"
    assert list(search_for_flow_rule('flow-rule-8', '00:00:00:00:00:00:00:02'))[0] == 'flow-rule-8',"Failed to find flow-rule-8 in switch 2"
    assert list(search_for_flow_rule('flow-rule-9', '00:00:00:00:00:00:00:02'))[0] == 'flow-rule-9',"Failed to find flow-rule-9 in switch 2"
    assert list(search_for_flow_rule('flow-rule-10', '00:00:00:00:00:00:00:02'))[0] == 'flow-rule-10',"Failed to find flow-rule-10 in switch 2"

def delete_flows():
    assert is_dict_a_success_dict(del_flow({"name":"flow-rule-2"}, '00:00:00:00:00:00:00:01')),"Failed to delete flow-rule-2 in switch 1"
    assert is_dict_a_success_dict(del_flow({"name":"flow-rule-3"}, '00:00:00:00:00:00:00:01')),"Failed to delete flow-rule-3 in switch 1"
    assert is_dict_a_success_dict(del_flow({"name":"flow-rule-8"}, '00:00:00:00:00:00:00:02')),"Failed to delete flow-rule-8 in switch 2"
    assert is_dict_a_success_dict(del_flow({"name":"flow-rule-9"}, '00:00:00:00:00:00:00:02')),"Failed to delete flow-rule-9 in switch 2"

def check_flows_where_deleted():
    assert is_dict_an_error_dict(search_for_flow_rule('flow-rule-2', '00:00:00:00:00:00:00:01')),"flow-rule-2 was not deleted"
    assert is_dict_an_error_dict(search_for_flow_rule('flow-rule-3', '00:00:00:00:00:00:00:01')),"flow-rule-3 was not deleted"
    assert is_dict_an_error_dict(search_for_flow_rule('flow-rule-8', '00:00:00:00:00:00:00:02')),"flow-rule-8 was not deleted"
    assert is_dict_an_error_dict(search_for_flow_rule('flow-rule-9', '00:00:00:00:00:00:00:02')),"flow-rule-9 was not deleted"
    

if __name__ == '__main__':
    remove_all_flows_and_groups()
    add_flow_rules_switch_one()
    add_flow_rules_switch_two()
    check_flow_rules_switch_one()
    check_flow_rules_switch_two
    delete_flows()
    check_flows_where_deleted
    
    print('All Tests Passed Successfully')
    