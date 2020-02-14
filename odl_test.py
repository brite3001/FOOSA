from json2xml import json2xml, readfromurl, readfromstring, readfromjson
import requests
import pprint
import json

uri = "http://127.0.0.1:8181/restconf/config/opendaylight-inventory:nodes/node/openflow:1/table/2"
login_url = "http://localhost:8181/index.html#/login"

data = {"flow": {
    "-xmlns": "urn:opendaylight:flow:inventory",
    "strict": "false",
    "instructions": {
        "instruction": {
            "order": "1",
            "apply-actions": {
                "action": {"order": "1"}
            }
        }
    },
    "table_id": "2",
    "id": "111",
    "cookie_mask": "10",
    "out_port": "10",
    "installHw": "false",
    "out_group": "2",
    "match": {
        "ethernet-match": {
            "ethernet-type": {"type": "2048"}
        },
        "ipv4-destination": "10.0.0.1/24"
    },
    "hard-timeout": "0",
    "cookie": "10",
    "idle-timeout": "0",
    "flow-name": "FooXf22",
    "priority": "2",
    "barrier": "false"
    }
}

xml_upload_flow_rule = \
'<flow \
    xmlns="urn:opendaylight:flow:inventory">\
    <strict>false</strict>\
    <instructions>\
        <instruction>\
          	<order>1</order>\
            <apply-actions>\
                <action>\
                  <order>1</order>\
                    <flood-all-action/>\
                </action>\
            </apply-actions>\
        </instruction>\
    </instructions>\
    <table_id>2</table_id>\
    <id>111</id>\
    <cookie_mask>10</cookie_mask>\
    <out_port>10</out_port>\
    <installHw>false</installHw>\
    <out_group>2</out_group>\
    <match>\
        <ethernet-match>\
            <ethernet-type>\
                <type>2048</type>\
            </ethernet-type>\
        </ethernet-match>\
        <ipv4-destination>10.0.0.1/24</ipv4-destination>\
    </match>\
    <hard-timeout>0</hard-timeout>\
    <cookie>10</cookie>\
    <idle-timeout>0</idle-timeout>\
    <flow-name>FooXf22</flow-name>\
    <priority>2</priority>\
    <barrier>false</barrier>\
</flow>'




payload = {
    'username': 'admin',
    'password': 'admin'
}

uri_get_openflow_switches = 'http://127.0.0.1:8181/config/network-topology:network-topology/'    
uri_test = 'http://localhost:8181/restconf/operational/network-topology:network-topology/'
uri_test2 = 'http://localhost:8181/restconf/config/opendaylight-inventory:nodes'


uri_check_flows_in_table_2 = 'http://127.0.0.1:8181/restconf/config/opendaylight-inventory:nodes/node/openflow:1/table/2/'

# Convert the JSON to XML because ODL expects an XML file
#data = json2xml.Json2xml(data).to_xml()

#Convert it to ascii to be sent to the REST API
#data = data.encode('ascii')

xml_upload_flow_rule = xml_upload_flow_rule.encode("UTF-8")


with requests.Session() as session:
    headers = {'Content-type':'application/xml', 'Accept':'application/json'}
    #post = session.post(login_url, data=payload)
    req = requests.post(uri, data=xml_upload_flow_rule, auth=('admin', 'admin'),headers=headers)
    #req = requests.get(uri, auth=('admin', 'admin'))
    print(req.text)
    print(req.headers)
    
    with open('data.json', 'w') as outfile:
        json.dump(req, outfile)



