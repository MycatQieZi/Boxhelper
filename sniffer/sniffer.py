# -*- coding:utf-8 -*-
from struct import *
import socket
import datetime
import pcapy
import warnings
warnings.filterwarnings("ignore",category=DeprecationWarning)

def eth_addr(a):
    return ":".join("%02x" % i for i in a)

def parserPacket(header, packet):
    package_content = {}
    pcap_header = {}
    time_now = datetime.datetime.now()
    time = datetime.datetime.strftime(time_now, '%Y-%m-%d %H:%M:%S')
    header_len = header.getlen()
    pcap_header["Time"] = time
    pcap_header["Package_len"] = str(header_len)
    package_content.update(pcap_header)

    ethh_context = {"Destination MAC": 0, "Source MAC": 0, "Protocol": 8}
    eth_len = 14
    eth_header = packet[:eth_len]
    eth = eth_headereth = unpack("!6s6sH", eth_header)
    eth_protocol = socket.ntohs(eth[2])
    ethh_context["Destination MAC"] = eth_addr(packet[0:6])
    ethh_context["Source MAC"] = eth_addr(packet[6:12])
    ethh_context["Protocol"] = str(eth_protocol)

    if str(eth_protocol) == '1544':
        ethh_content["protocol"] = "ARP"
    package_content.update(ethh_context)

    if eth_protocol == 8:
        ip_header = packet[eth_len:20 + eth_len]
        iph = unpack('!BBHHHBBH4s4s', ip_header)
        version_ih1 = iph[0]
        version = version_ih1 >> 4
        print("ip version:", version)
        ihl = version_ih1 & 0xF
        iph_length = ihl * 4
        service = iph[1]
        total_ip_length = iph[2]
        identification = iph[3]
        flag0 = iph[4]
        flag = flag0 >> 3
        ttl = iph[5]
        protocol = iph[6]  # 1:ICMP  2:IGMP  6:TCP  17:UDP  50:ESP  47:GRE
        checksum = iph[7]
        s_addr = socket.inet_ntoa(iph[8])
        d_addr = socket.inet_ntoa(iph[9])
        iph_context = {"IP Version": 4, "IP Header Length": 5, "TTL": 0, "Protocol based on IP": 1, "Checksum": 0,
                        "Source": 0, "Destination": 0}
        iph_context["IP Version"] = str(version)
        iph_context["IP Header Length"] = str(ihl)
        iph_context["TTL"] = str(ttl)
        iph_context["Protocol based on IP"] = str(protocol)
        if str(protocol) == "6":
            ethh_context["Protocol"] == "TCP" 
        elif str(protocol) == "1":
            ethh_context["Protocol"] == "ICMP"
        elif str(protocol) == "17":
            ethh_context["Protocol"] == "udp"
        else:
            ethh_context["Protocol"] == "other protocol"
        iph_context["Checksum"] = str(checksum)
        iph_context["Source"] = s_addr
        iph_context["Destination"] = d_addr

        package_content.update(ethh_context)
        package_content.update(iph_context)
        if protocol == 6:
            t = iph_length + eth_len
            tcp_header = packet[t:t + 20]

            tcph = unpack('!HHLLBBHHH', tcp_header)
            # print ("tcph: ",tcph)

            s_port = tcph[0]  # 源端口
            d_port = tcph[1]  # 目的端口
            sequence = tcph[2]  # 序列号
            ack = tcph[3]  # 确认号
            # tcph_length = tcph[4] #TCP头部长度
            # doff_reversed = tcph[5]  # 保留字段
            # tcph_length = doff_reversed >> 4 #TCP 头长度
            doff_reserved = tcph[4]
            tcph_length = doff_reserved >> 4

            window = tcph[6]
            checksum_tcp = tcph[7]
            urgepkt = tcph[8]

            # print ("Source Port: " + str(s_port) + " Destination Port: " + str(d_port) + " Sequence Number: " + str(sequence) +\
            #     " Acknowledge Number: " + str(ack)  + " TCP Header Length: " + str(tcph_length) + " Window length: " + str(window) + " Checksum_tcp: " + str(checksum_tcp) + " Urgepkt: " + str(urgepkt))

            h_size = eth_len + iph_length + tcph_length * 4  # ???
            data_size = len(packet) - h_size

            #data = packet[h_size:]
            data = str(s_port)+ "->" + str(d_port)
            # print("TCP Data: " + str(data))

            tcph_context = {"Source Port": 0, "Destination Port": 0, "Sequence Number": 0, "Acknowledge Number": 0, \
                            "TCP Header Length": 0, "Window length": 0, "Checksum_tcp": 0, "Urgepkt": 0,
                            "Data": 0}
            tcph_context["Source Port"] = str(s_port)
            tcph_context["Destination Port"] = str(d_port)
            tcph_context["Sequence Number"] = str(sequence)
            tcph_context["Acknowledge Number"] = str(ack)
            tcph_context["TCP Header Length"] = str(tcph_length)
            tcph_context["Window length"] = str(window)
            tcph_context["Checksum_tcp"] = str(checksum_tcp)
            tcph_context["Urgepkt"] = str(urgepkt)
            tcph_context["Data"] = str(data)
            # print("tcph_context: ", tcph_context)
            package_content.update(tcph_context)
            return package_content
        # ICMP 包
        elif protocol == 1:
            u = iph_length + eth_len
            icmph_length = 8
            icmp_header = packet[u:u + 8]

            icmph = unpack("!BBHHH", icmp_header)
            # print ("icmph: " ,icmph)

            icmp_type = icmph[0]
            code = icmph[1]
            checksum_icmp = icmph[2]
            identifier = icmph[3]
            sequence_icmp = icmph[4]

            # print ("ICMP Type: " + str(icmp_type) + " ICMP Code: " + str(code) + " ICMP Checksum: " + str(checksum_icmp))

            h_size = iph_length + eth_len + icmph_length
            data_size = len(packet) - h_size
            #data = packet[h_size:]
            data = str(icmp_type) + " id=" + str(identifier) + " seq=" + str(sequence_icmp)
            # print ("ICMP data: " + str(data))

            icmph_context = {"ICMP Type": 0, "ICMP Code": 0, "ICMP Checksum": 0, "Identifier": 0,"Sequence":0}
            icmph_context["ICMP Type"] = str(icmp_type)
            icmph_context["ICMP Code"] = str(code)
            icmph_context["ICMP Checksum"] = str(checksum_icmp)
            icmph_context["Identifier"] = str(identifier)
            icmph_context["Sequence"] = str(sequence_icmp)
            icmph_context["Data"] = str(data)

            # print ("ICMP Header Context: ",icmph_context)

            package_content.update(icmph_context)
            return package_content


        # #UDP包
        elif protocol == 17: # UDP
            u = iph_length + eth_len
            udp_length = 8
            udp_header = packet[u:u + 8]
            # print ("udp_h: "+str(udp_header))

            udph = unpack("!HHHH", udp_header)
            # print ("udph: "+str(udph))

            sourceport = udph[0]
            destinport = udph[1]
            userpacket_length = udph[2]
            checksum_udp = udph[3]

            # print ("Souce port: " + str(sourceport)+" Destination port: " + str(destinport) + " User packet length: " + str(userpacket_length) +\
            #        " Checksum UDP: " + str(checksum_udp))

            h_length = eth_len + iph_length + udp_length
            data_size = len(packet) - h_length
            #data = packet[h_length:]
            data = str(sourceport) + " -> " + str(destinport) + " Len=" + str(userpacket_length)
            # print ("UDP data: " + str(data))

            udph_context = {"Souce port": 0, "Destination port": 0, "User packet length": 0, "Checksum UDP": 0,
                            "Data": 0}
            udph_context["Souce port"] = str(sourceport)
            udph_context["Destination port"] = str(destinport)
            udph_context["User packet length"] = str(userpacket_length)
            udph_context["Checksum UDP"] = str(checksum_udp)
            udph_context["Data"] = str(data)

            # print ("UDP Header Context: ",udph_context)

            package_content.update(udph_context)
            return package_content

        else:
            non = {"Data":0}
            package_content.update(non)
            return package_content
            #return ("Protocol is not TCP,ICMP,UDP")

    elif eth_protocol == 1544 :#0x0608
        #print ("&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
        arp_header = packet[eth_len: 28+ eth_len]
        arph = unpack('!HHBBH6s4s6s4s',arp_header)

        hardware_type = arph[0]
        pro_type = arph[1]
        hardware_size = arph[2]
        pro_size = arph[3]
        op = arph[4]
        sender_MAC = eth_addr(arph[5])
        sender_IP = socket.inet_ntoa(arph[6])
        target_MAC = eth_addr(arph[7])
        target_IP = socket.inet_ntoa(arph[8])

        arph_context = {"Hardware type": 1, "Protocol type": 4, "Hardware size": 6, "Protocol Size": 4, "Opcode": 1, \
                        "Source" : 0, "Source IP Address": 0, "Destination": 0, "Destination IP Address": 0}
        arph_context["Hardware type"] = hardware_type
        arph_context["Protocol type"] = pro_type
        arph_context["Hardware size"] = hardware_size
        arph_context["Protocol Size"] = pro_size
        arph_context["Opcode"] = op
        arph_context["Source"] = sender_MAC
        arph_context["Sender IP Address"] = sender_IP
        arph_context["Destination"] = target_MAC
        arph_context["Target IP Address"] = target_IP
        arph_context["Data"] = "Who has" + target_IP +"? Tell " + sender_IP

        package_content.update(arph_context)
        return package_content

def getDevices():
    devices = pcapy.findalldevs()
    return devices
def run(dev, filter, Status):
     
    pack_list = []
    cap = pcapy.open_live(dev, 65535, 1, 0)
    if filter != 0:
        cap.setfilter(filter)
    while Status:
        (header, packet) = cap.next()
        if len(packet) >= 14:
            parse = parserPacket(header, packet)
            if parse != None:
                parse["Original_hex"] = packet.hex()
                pack_list.append(parse)
                print(parse)
    return pack_list
pack_list = run(getDevices()[0], "udp", True)

