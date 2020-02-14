# What is FOOSA?
FOOSA (FloodLight, OpenDayLight, Open Network Operating System, Software
Defined Networking, Application Programming Interface) is an API that allows developers and administrators to interact with an SDN network via a REST API. FOOSA supports ONOS, FloodLight, OpenDayLight and allows developers and administrators to change the flow of traffic on a network and request network information such as host and switch links. Rather than using each controller’s specific NBI, FOOSA allows a developer to use one standard API to communicate with all three controllers. 

# Features
- A Northbound Interface API that is compatible with ONOS[1, 2], OpenDayLight[1, 3] and
FloodLight[1, 4],
- Standardised REST API endpoints to add, modify, query and delete flow entries.
- Standardised REST API endpoints to request network information including host and
switch lists, host and switch links, flow rules and network statistics.
- An application that visualises the network.
- An application that allows hosts on the network to be blocked (all traffic from the blocked
host is dropped).

# Installastion
During development heavy use of Docker was used to run the three SDN controllers (ONOS, ODL and FL) and Mininet (used to emulate the network topology). The following installation guide was tested on Ubuntu 19.10 (Specifically PopOS!)

## Installing Docker (Ubuntu 19.10)
NOTE: At the time of writing Docker does not support Ubuntu 19.10 officially.
```sh
$ sudo apt update
$ sudo apt install apt-transport-https ca-certificates curl gnupg-agent software-properties-common
$ curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
$ sudo apt-key fingerprint 0EBFCD88
$ sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu disco stable"
$ sudo apt update
$ sudo apt install docker-ce
```

## Starting the ONOS controller in Docker
```sh
$ sudo docker run -t -d -p 8181:8181 -p 8101:8101 -p 6653:6653 --rm --name onos onosproject/onos
```
The web UI can be accessed via: http://localhost:8181/onos/ui/login.html
Username: onos
Password: rocks
The ONOS auto generated documentation can be accessed here: http://127.0.0.1:8181/onos/v1/docs/#!/flows/delete_flows_deviceId_flowId

### Configuring ONOS
By default, ONOS does not start the 'openflow provider suite' and the 'reactive forwarding' modules. This means that once a network topology is connected to an ONOS controller, ONOS will be unable to recognise the network as it's not automatically creating flow rules.

Follow these steps to enable reactive forwarding and Openflow:
1) Login and go to the onos UI
2) Go to the applications menu
3) Search for 'openflow'
4) Click the 'openflow provider suite' app
5) Hit the play button in the top right
6) Search for 'fwd'
7) Click on 'reactive forwarding'
8) Hit the play button
9) Also hit 'h' to toggle the hosts in the topology view

## Setting up ContainerNet for ONOS (Mininet in a docker container)
Install openvswitch:
```sh
$ sudo apt update && sudo apt install openvswitch-switch
```

Start ContainerNet:
```sh
$ sudo docker run --name containernet -it --rm --privileged --pid='host' -v /var/run/docker.sock:/var/run/docker.sock containernet/containernet /bin/bash
```
Now we've started our network topology, lets add ONOS as a remote controller. From inside the terminal running your Mininet container:
```sh
$ cd examples/
$ apt update && apt install vim
$ vim containernet_example.py
```
ContainerNet Uses Python files to create and configure the network topology. We're going to be editing this example configuration file to use our ONOS controller as a remote controller.
- Change the line "from mininet.node import Controller" to:
"from mininet.node import Controller, RemoteController"
- Below the "*** Adding controller" line add. 
c1 = RemoteController('c1', ip='172.17.0.3', port=6653)
(If you're not sure what ONOS's IP is, check the ONOS WebUI)
- Change "net.addController('c0')" to "net.addController(c1)"
- Now hit escape and type ":!wq" to close and save the file

Now to start the network topology type:
```sh
$ python3 containernet_example.py
```
Once the topology has loaded, type the command
```sh
$ pingall
```
This will drum up some traffic between the hosts, as Mininet networks usually don't send traffic unless instructed. So doing a ping between all the hosts generates traffic between them, which causes ONOS to create flow rules so the switches know were to send their traffic. Now if you go back to ONOS's WebUI and hit the 'Topology' tab you should be able to see a network with 2 switches and 2 hosts!

## Install venv
The website which acts as the UI for FOOSA requires some Python dependancies. Before we continue lets setup our virtual environment before we continue
```sh
$ sudo apt-get install python3-venv
```

## Cloning and FOOSA WebUI
Lets clone the FOOSA repo into our home folder and navigate to the website folder
```sh
$ cd ~
$ git pull https://github.com/brite3001/FOOSA
$ cd FOOSA
$ cd website
```

## Starting the FOOSA WebUI
```sh
$ source env/bin/activate
$ python3 server.py
```

Now FOOSA is up and running, we need to give FOOSA a controller to manage!
Boot up the web browser of your choice and head to: http://127.0.0.1:5000/index.html
You'll be greeted with a bit of a sad looking screen with no data, as we haven't told FOOSA were out controller is

## Adding a controller to FOOSA
- Navigate to the "Controller Management" tab in the FOOSA WebUI
- In controller type select 'ONOS'
- In IP type the IP of the ONOS controller (check the ONOS WebUI for the controllers IP: http://localhost:8181/onos/ui/#/topo2 the IP will be displayed up the top left)

Now a controllers been added you can now:
- Add flows
- Delete flows
- Check the network topology
- Check statistics on a device by device basis (scroll down a bit on the network topology page)
- Manage multiple controllers from the same interface
- Specific hosts can also be blocked on the home page by selecting a host in the "Restrict a Host" box and clicking the red "Add flow" button. This will stop a particular host from communicating with any other host on the network
