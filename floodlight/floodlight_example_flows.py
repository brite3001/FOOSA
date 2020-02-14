# SWITCH 01 #
#############
flow_rule_one = {
    "switch":"00:00:00:00:00:00:00:01", 
    "name":"flow-rule-1", 
    "cookie":"0", 
    "priority":"32768", 
    "in_port":"1",
    "active":"true", 
    "actions":"output=1",
    }

flow_rule_two = {
    "switch":"00:00:00:00:00:00:00:01", 
    "name":"flow-rule-2", 
    "cookie":"1", 
    "priority":"32768", 
    "in_port":"1",
    "active":"true", 
    "actions":"output=2",
    }

flow_rule_three = {
    "switch":"00:00:00:00:00:00:00:01", 
    "name":"flow-rule-3", 
    "cookie":"2", 
    "priority":"32768", 
    "in_port":"1",
    "active":"false", 
    "actions":"output=3",
    }

flow_rule_four = {
    "switch":"00:00:00:00:00:00:00:01", 
    "name":"flow-rule-4", 
    "cookie":"3", 
    "priority":"32768", 
    "in_port":"1",
    "active":"true", 
    "actions":"output=4",
    }

flow_rule_five = {
    "switch":"00:00:00:00:00:00:00:01", 
    "name":"flow-rule-5", 
    "cookie":"4", 
    "priority":"32768", 
    "in_port":"1",
    "active":"true", 
    "actions":"output=5",
    }

# SWITCH 02 #
#############

flow_rule_six = {
    "switch":"00:00:00:00:00:00:00:02", 
    "name":"flow-rule-6", 
    "cookie":"5", 
    "priority":"32768", 
    "in_port":"1",
    "active":"true", 
    "actions":"output=6",
    }

flow_rule_seven = {
    "switch":"00:00:00:00:00:00:00:02", 
    "name":"flow-rule-7", 
    "cookie":"6", 
    "priority":"32768", 
    "in_port":"1",
    "active":"true", 
    "actions":"output=7",
    }

flow_rule_eight = {
    "switch":"00:00:00:00:00:00:00:02", 
    "name":"flow-rule-8", 
    "cookie":"7", 
    "priority":"32768", 
    "in_port":"1",
    "active":"false", 
    "actions":"output=8",
    }

flow_rule_nine = {
    "switch":"00:00:00:00:00:00:00:02", 
    "name":"flow-rule-9", 
    "cookie":"8", 
    "priority":"32768", 
    "in_port":"1",
    "active":"true", 
    "actions":"output=9",
    }

flow_rule_ten = {
    "switch":"00:00:00:00:00:00:00:02", 
    "name":"flow-rule-10", 
    "cookie":"9", 
    "priority":"32768", 
    "in_port":"1",
    "active":"true", 
    "actions":"output=10",
    }