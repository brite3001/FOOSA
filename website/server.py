from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap
import pprint
import json


# Config for pprint
pp = pprint.PrettyPrinter(indent=2)

# Used to import the helper function
import sys
sys.path.append("..")

# Import the APIs
from onos import onos_api
from opendaylight import odl_api
from floodlight import floodlight_api

controller_types = ['OpenDayLight', 'ONOS', 'FloodLight']

controller_list = [ ]
# ['ONOS', 'localhost:2222']
# ['OpenDayLight', 'localhost:1111'] 
# ['FloodLight', 'localhost:1234']


restricted_hosts = []


app = Flask(__name__)
Bootstrap(app)


@app.route('/index.html')
def index():
  return render_template('index.html', controller_types=controller_types, controller_list=controller_list,restricted_hosts=restricted_hosts)

@app.route('/add_flow.html')
def add_flow():
  return render_template('add_flow.html', controller_list=controller_list)

@app.route('/delete_flow.html')
def delete_flow():
  return render_template('delete_flow.html', controller_list=controller_list)

@app.route('/controller_management.html')
def controller_management():
  return render_template('controller_management.html', controller_types=controller_types, controller_list=controller_list)

@app.route('/network_topology.html')
def network_topology():
  return render_template('network_topology.html', controller_list=controller_list)


@app.route('/get_network_info', methods=['POST'])
def get_network_information():
  data = request.get_json()
  print('[/get_network_info]: ' + str(data))
  if data['type'] == 'FloodLight':
    info = floodlight_api.get_network_information()
    info['restricted_hosts'] = restricted_hosts
    return info
  elif data['type'] == 'ONOS':
    data = onos_api.get_network_information()
    data['restricted_hosts'] = restricted_hosts
    return data
  elif data['type'] == 'OpenDayLight':
    data = odl_api.get_network_information()
    data['restricted_hosts'] = restricted_hosts
    return data
  else:
    return {'status_error': 'Unknown controller'}

  
@app.route('/add_controller', methods=['POST'])
def add_controller():
  data = request.get_json()
  print('[/add_controller]: ' + str(data))
  controller_list.append([data['type'], data['ip']])
  print(controller_list)
  return('none')

@app.route('/add_to_restricted_list', methods=['POST'])
def add_to_restricted_list():
  data = request.get_json()
  print('[/add_to_restricted_list]: ' + str(data))
  restricted_hosts.append(data['host'])
  status = {}
  if data['controller'] == 'FloodLight':
    flow = floodlight_api.create_block_rule(data['switch'], data['host'])
    status = floodlight_api.add_flow(flow)
  if data['controller'] == 'ONOS':
    flow = onos_api.create_flow_drop_rule(data['switch'], data['host'])
    status = onos_api.add_flow(flow)
    
  
  return(status)

@app.route('/add_flow_rule', methods=['POST'])
def add_flow_rule():
  data = request.get_json()
  status = {}
  print('[/add_flow_list]: ' + str(data))
  if data['controller'] == 'FloodLight':
    flow = floodlight_api.create_flow_rule(data['name'], 
                                           data['priority'], 
                                           data['switch'], 
                                           data['cookie'], 
                                           data['in_port'], 
                                           data['out_port']
    )
    status = floodlight_api.add_flow(flow)
  elif data['controller'] == 'ONOS':
    flow = onos_api.create_flow_rule(data['priority'], 
                                     data['switch'], 
                                     '0',
                                     data['in_port'],
                                     data['out_port']
                                     )
    status = onos_api.add_flow(flow)
  elif data['controller'] == 'OpenDayLight':
    flow = odl_api.create_flow_rule(data['cookie'], 
                                    data['name'],
                                    data['name'],
                                    data['out_port'],
                                    data['in_port'],
                                    data['priority'])
    status = odl_api.add_flow(flow, data['switch'])
    
  return(status)


@app.route('/delete_controller', methods=['POST'])
def delete_controller():
  data = request.get_data().decode("utf-8") 
  data = data.split(':')
  print('[/delete_controller]: ' + str(data))
  controller_name = data[0].rstrip()
  controller_ip = data[1] + data[2]
  for controller in controller_list:
    if controller[0] == controller_name and controller[1].replace(':', '') == controller_ip.strip():
      print('Controller ' + str(controller) + ' deleted successfully')
      controller_list.remove(controller)
  print(controller_list)
  return('success')

@app.route('/delete_flow', methods=['POST'])
def delete_flow_api():
  data = request.get_json()
  print('[/delete_flow]: ' + str(data))
  status = {}
  if data['controller_name'] == 'FloodLight':  
    status = floodlight_api.del_flow(data['flow_name'], data['switch_name'])
  elif data['controller_name'] == 'ONOS':
    status = onos_api.del_flow(data['switch_name'], data['flow_name'])
  elif data['controller_name'] == 'OpenDayLight':
    status = odl_api.del_flow(data['switch_name'], data['flow_name'])
    
  return(status)



if __name__ == '__main__':
  app.run(debug=True)
