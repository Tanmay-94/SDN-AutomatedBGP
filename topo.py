from mininet.net import Containernet
from mininet.node import RemoteController
from mininet.node import Docker
from mininet.node import OVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink, Link
import os


def topology():
	"Adding network details for a containerized topology"

	net = Containernet(controller=RemoteController)
	net.addController('c0', controller=RemoteController, ip='127.0.0.1', port=8080)

	info('***** Adding BIRD Routers *****\n')
	r1 = net.addDocker('r1', ip='10.10.1.1/24', dimage='bird:tanmay')
	r2 = net.addDocker('r2', ip='10.11.1.1/24', dimage='bird:tanmay')
	r3 = net.addDocker('r3', ip='10.20.1.1/24', dimage='bird:tanmay')
	r4 = net.addDocker('r4', ip='10.21.1.1/24', dimage='bird:tanmay')
	r5 = net.addDocker('r5', ip='192.168.99.2/24', dimage='bird:tanmay')

	info('***** Adding Hosts *****\n')
	h1 = net.addDocker('h1', ip='10.10.1.2/24', defaultRoute='via 10.10.1.1', dimage='ubuntu:focal')
	h2 = net.addDocker('h2', ip='10.11.1.2/24', defaultRoute='via 10.11.1.1', dimage='ubuntu:focal')
	h3 = net.addDocker('h3', ip='10.20.1.2/24', defaultRoute='via 10.20.1.1', dimage='ubuntu:focal')
	h4 = net.addDocker('h4', ip='10.21.1.2/24', defaultRoute='via 10.21.1.1', dimage='ubuntu:focal')

	info('***** Adding Switches *****\n')
	sdn_r1 = net.addSwitch('sdn_r1')
	sdn_r2 = net.addSwitch('sdn_r2')

	info('***** Creating Links *****\n')
	net.addLink(h1, r1)
	net.addLink(h2, r2)
	net.addLink(h3, r3)
	net.addLink(h4, r4)

	net.addLink(r1, sdn_r1, params1={'ip': '192.168.101.2/24'})
	net.addLink(r2, sdn_r1, params1={'ip': '192.168.102.2/24'})

	net.addLink(r3, sdn_r2, params1={'ip': '192.168.201.2/24'})
	net.addLink(r4, sdn_r2, params1={'ip': '192.168.202.2/24'})
	net.addLink(sdn_r1, r5)
	net.addLink(r5, sdn_r2, params1={'ip': '192.168.98.2/24'})
	net.addLink(sdn_r1, sdn_r2)

	info('***** Starting network *****\n')
	net.start()

	#Adding management interface on router sdn 1
	cmd1 = 'sudo ip addr add 192.168.101.1/24 dev sdn_r1'
	cmd2 = 'sudo ip addr add 192.168.102.1/24 dev sdn_r1'
	cmd3 = 'sudo ip addr add 192.168.99.1/24 dev sdn_r1'
	cmd4 = 'sudo ip link set sdn_r1 up'
	os.system(cmd1)
	os.system(cmd2)
	os.system(cmd3)
	os.system(cmd4)
	cmd5 = 'sudo ovs-vsctl set bridge sdn_r1 other-config:disable-in-band=true'
	os.system(cmd5)

	#Adding management interface on router sdn 2
	cmd1 = 'sudo ip addr add 192.168.201.1/24 dev sdn_r2'
	cmd2 = 'sudo ip addr add 192.168.202.1/24 dev sdn_r2'
	cmd3 = 'sudo ip addr add 192.168.98.1/24 dev sdn_r2'
	cmd4 = 'sudo ip link set sdn_r2 up'
	os.system(cmd1)
	os.system(cmd2)
	os.system(cmd3)
	os.system(cmd4)
	cmd5 = 'sudo ovs-vsctl set bridge sdn_r2 other-config:disable-in-band=true'
	os.system(cmd5)


	#copying BIRD configs in respective dockers
	os.system('sudo docker cp r1.conf mn.r1:/etc/bird.conf')
	os.system('sudo docker cp r2.conf mn.r2:/etc/bird.conf')
	os.system('sudo docker cp r3.conf mn.r3:/etc/bird.conf')
	os.system('sudo docker cp r4.conf mn.r4:/etc/bird.conf')
	os.system('sudo docker cp r5.conf mn.r5:/etc/bird.conf')
	r1.cmd('bird -c /etc/bird.conf')
	r2.cmd('bird -c /etc/bird.conf')
	r3.cmd('bird -c /etc/bird.conf')
	r4.cmd('bird -c /etc/bird.conf')
	r5.cmd('bird -c /etc/bird.conf')

	info('***** Running CLI *****\n')
	CLI(net)
	info('***** Stopping network *****\n')
	net.stop()

if __name__ == '__main__':
	setLogLevel('info')
	topology()



