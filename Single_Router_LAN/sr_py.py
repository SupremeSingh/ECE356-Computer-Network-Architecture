from scapy.all import *

# Constants
MINIMUM_ETHERNET_LENGTH = 14
MINIMUM_IP_LENGTH = 20
MINIMUM_ARP_LENGTH = 28


def cksum(pkt):
    del (pkt.chksum)
    return pkt.__class__(bytes(pkt))


def findInterfaceAddr(interface):
    addr = None
    for iface in if_list:
        if iface.name == interface:
            addr = (iface.addr, iface.ip)
            break
    return addr


def sr_longest_match(ip_dst):
    res = None
    for r in rtable:
        if r.dest == ip_dst:
            res = r
            break
    if res == None:
        return None

    interface = res.iface
    addr = findInterfaceAddr(interface)
    assert (addr != None)
    mac, ip = addr[0], addr[1]
    return (mac, ip, interface)


def sr_interface(ip):
    for iface in if_list:
        if iface.ip == ip.dst:
            return True
    return False


class rtableNode:
    def __init__(self, dest, gw, mask, iface):
        self.dest = dest
        self.gw = gw
        self.mask = mask
        self.iface = iface

    def __repr__(self):
        return "%s %s %s %s" % (self.dest, self.gw, self.mask, self.iface)


rtable = []


def load_rt(path):
    f = open(path)
    lines = f.readlines()
    f.close()
    for l in lines:
        dest, gw, mask, iface = l.split()
        rtable.append(rtableNode(dest, gw, mask, iface))


class iflistNode():
    def __init__(self, name, addr, ip):
        self.name = name
        self.addr = addr
        self.ip = ip

    def __repr__(self):
        return "%s %s %s" % (self.name, self.addr, self.ip)


if_list = []


def load_iflist(path):
    f = open(path)
    lines = f.readlines()
    f.close()
    for l in lines:
        name, addr, ip = l.split()
        if_list.append(iflistNode(name, addr, ip))


def init():
    load_rt('/home/ubuntu/projects/cs144_lab3/lab2/rtable')

    load_iflist('/home/ubuntu/projects/cs144_lab3/lab2/if_list')


""" Don't touch the code above """


def handle_arp(ether, interface):
    arp = ether.payload

    if arp.op == 1:
        return handle_arp_request(arp, interface)
    elif arp.op == 2:
        return ("", 0, "")  # None
    else:
        raise NotImplementedError


def handle_arp_request(arp, interface):
    addr = findInterfaceAddr(interface)
    assert (addr != None)
    mac_interface, ip_interface = addr

    """
    Add your code here

    reply = ARP(...)

    """

    reply = ARP(op=2, hwsrc=mac_interface, psrc=ip_interface, hwdst=arp.hwsrc, pdst=arp.psrc)  # Craft an ARP response
    reply_buffer = str(reply)

    return (reply_buffer, len(reply_buffer), interface)


def handle_ip(ether, interface):
    ip = ether.payload
    addr = findInterfaceAddr(interface)
    mac_interface, ip_interface = addr  # Obtain the MAC and ip address of the receiving interface

    """ Add your code here

    if sr_interface(ip): # destination on the router

	Hint: reply the ICMP request or send ICMP error message back

    else:  # destination somewhere else

	Hint: handle ICMP error message, TLE or host unreachable
	To find the next hop, you can call `sr_longest_match`


    """

    ICMP_reply = ip.copy()  # Generic ICMP response for various situations

    ICMP_reply.proto = 1
    ICMP_reply.src = ip.dst
    ICMP_reply.dst = ip.src

    Error_extension = ip.copy()  # Generic payload for ICMP error messages
    Error_payload = str(Error_extension)[:28]

    if sr_interface(ip):  # If the packet was destined for the router

        if ip.proto == 1:  # If it is ICMP
            if ip[ICMP].type == 8:  # If it is a request
                ICMP_reply[ICMP].type = 0  # Send an ICMP Echo response

        else:  # If it is TCP or UDP

            ICMP_reply.remove_payload()
            ICMP_reply.src = ip_interface
            ICMP_reply.len = 56
            ICMP_reply = ICMP_reply / ICMP(type=3, code=3)
            ICMP_reply = IP(str(reply) + Error_payload)

        ICMP_reply[ICMP] = cksum(ICMP_reply[ICMP])  # Re-compute checksums layer-by-layer
        ICMP_reply = cksum(ICMP_reply)

        ICMP_reply_buffer = str(ICMP_reply)  # Convert to raw buffer and send
        return (ICMP_reply_buffer, len(ICMP_reply_buffer), interface)

    else:  # If next-hop

        if ip.ttl <= 1:  # If ttl <= 1

            ICMP_reply.remove_payload()
            ICMP_reply.src = ip_interface
            ICMP_reply.len = 56
            ICMP_reply = ICMP_reply / ICMP(type=11, code=0)
            ICMP_reply = IP(str(reply) + Error_payload)

            ICMP_reply[ICMP] = cksum(ICMP_reply[ICMP])  # Re-compute checksums layer-by-layer
            ICMP_reply = cksum(ICMP_reply)

            ICMP_reply_buffer = str(ICMP_reply)
            return (ICMP_reply_buffer, len(ICMP_reply_buffer), interface)

        else:  # If packet has sufficient ttl

            destination = sr_longest_match(ip.dst)  # Find the destination in the routing table

            if destination is None:  # If destination is not in routing table

                ICMP_reply.remove_payload()
                ICMP_reply.src = ip_interface
                ICMP_reply.len = 56
                ICMP_reply = reply / ICMP(type=3, code=0)
                ICMP_reply = IP(str(reply) + Error_payload)

                ICMP_reply[ICMP] = cksum(ICMP_reply[ICMP])  # Re-compute checksums layer-by-layer
                ICMP_reply = cksum(ICMP_reply)

                ICMP_reply_buffer = str(ICMP_reply)
                return (ICMP_reply_buffer, len(ICMP_reply_buffer), interface)

            else:  # If the destination was found - now send packet to final destination

                ip.ttl -= 1  # Reduce packet ttl
                ip = cksum(ip)
                interface_name = destination[2]

    ip_buffer = str(ip)

    return (ip_buffer, len(ip_buffer), interface_name)


def receive(raw, interface):
    init()

    print("*** -> Receiving packet of length %d through %s\n" % (len(raw), interface));
    """
    Create an Ethernet packet with raw buffer 
    Parameters: 
	raw: the raw buffer
	interface: the name of incoming interface
    Return:
	A tuple: (raw_packet_buffer, len(raw_packet_buffer), outgoing_interface_name)
	if no output packets, return ("", 0, "") 
	raw_packet_buffer: the raw buffer of the output packet, i.e. str(pkt)
	len(raw_packet_buffer): length of the raw buffer
	outgoing_interface_name: the name of outgoing interface
    """

    ether = Ether(raw)
    ether.show()

    """
	Add your code here
	Hint: create different output packets according to different type of input packet (`ether`)
	      if arp, call `handle_arp`
	      if ip, call `handle_ip'
    """

    if len(ether) < MINIMUM_ETHERNET_LENGTH:  # Validate packt length - atleast 14 Bytes
        print("Packet Length Insufficient")
        return ("", 0, "")

    if ether.type == 2048:
        return handle_ip(ether, interface)
    elif ether.type == 2054:
        return handle_arp(ether, interface)
    else:
        print("Packet type not supported")
        raise NotImplementedError







