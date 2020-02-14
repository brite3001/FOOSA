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