
import re
from twisted.trial import unittest
from allmydata.util import iputil
import allmydata.test.common_util as testutil

try:
    set()
except:
    from sets import Set as set

DOTTED_QUAD_RE=re.compile("^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$")

# TODO: do throw in some things that look like IP address that aren't.
tool_output_map = {'linux': ("""
lo        Link encap:Local Loopback  
          inet addr:127.0.0.1  Mask:255.0.0.0
          inet6 addr: ::1/128 Scope:Host
          UP LOOPBACK RUNNING  MTU:16436  Metric:1
          RX packets:2279 errors:0 dropped:0 overruns:0 frame:0
          TX packets:2279 errors:0 dropped:0 overruns:0 carrier:0
          collisions:0 txqueuelen:0 
          RX bytes:3147030 (3.1 MB)  TX bytes:3147030 (3.1 MB)
ppp0      Link encap:Point-to-Point Protocol  
          inet addr:192.168.222.222  P-t-P:192.168.222.1  Mask:255.255.255.255
          UP POINTOPOINT RUNNING NOARP MULTICAST  MTU:1400  Metric:1
          RX packets:93620 errors:0 dropped:0 overruns:0 frame:0
          TX packets:74807 errors:0 dropped:0 overruns:0 carrier:0
          collisions:0 txqueuelen:3 
          RX bytes:86216111 (86.2 MB)  TX bytes:6195896 (6.1 MB)
wlan0     Link encap:Ethernet  HWaddr 00:11:22:33:44:55  
          inet addr:192.168.128.143  Bcast:192.168.128.255  Mask:255.255.255.0
          inet6 addr: 2001:888:1234:111:f0cf:9396:cf9a:dd42/64 Scope:Global
          inet6 addr: 2001:888:1235:111:211:22ff:fe33:4455/64 Scope:Global
          inet6 addr: fe80::211:22ff:fe33:4455/64 Scope:Link
          UP BROADCAST RUNNING MULTICAST  MTU:1500  Metric:1
          RX packets:290228 errors:0 dropped:0 overruns:0 frame:0
          TX packets:212885 errors:0 dropped:0 overruns:0 carrier:0
          collisions:0 txqueuelen:1000 
          RX bytes:261990974 (261.9 MB)  TX bytes:34436273 (34.4 MB)
6in4      Link encap:IPv6-in-IPv4  
          inet6 addr: fe80::c0a8:808a/64 Scope:Link
          inet6 addr: 2001:999:1235:999::1/128 Scope:Global
          inet6 addr: 2001:999:1234:999::2/64 Scope:Global
          UP POINTOPOINT RUNNING NOARP  MTU:1480  Metric:1
          RX packets:538443 errors:0 dropped:0 overruns:0 frame:0
          TX packets:350834 errors:7 dropped:0 overruns:0 carrier:7
          collisions:0 txqueuelen:0 
          RX bytes:489416286 (466.7 MiB)  TX bytes:87717718 (83.6 MiB)
eth1      Link encap:Ethernet  HWaddr 00:22:33:44:55:66  
          inet addr:192.168.128.138  Bcast:192.168.128.255  Mask:255.255.255.0
          inet6 addr: fe80::222:33ff:fe44:5566/64 Scope:Link
          inet6 addr: 2001:999:1235:999::1/64 Scope:Global
          UP BROADCAST RUNNING MULTICAST  MTU:1500  Metric:1
          RX packets:61616438 errors:0 dropped:0 overruns:0 frame:0
          TX packets:35975963 errors:0 dropped:0 overruns:0 carrier:0
          collisions:0 txqueuelen:1000 
          RX bytes:2161662543 (2.0 GiB)  TX bytes:3453404653 (3.2 GiB)
          Interrupt:15 
""",set(['127.0.0.1',
     '::1',
     '192.168.222.222',
     '192.168.128.143',
     '192.168.128.138',
     'fe80::c0a8:808a',
     '2001:999:1235:999::1',
     '2001:999:1234:999::2',
     'fe80::222:33ff:fe44:5566',
     '00:22:33:44:55:66',
     '00:11:22:33:44:55',
     #TODO: we want to be able to force use of this address if it exists.  Privacy and all...
     '2001:888:1234:111:f0cf:9396:cf9a:dd42',     # IPv6 Privacy Address, random except for network 
     '2001:888:1235:111:211:22ff:fe33:4455',      # Autoconfigured Address, based on network + HWaddr
     'fe80::211:22ff:fe33:4455'])),               # Link-local Address, based on 'fe80::' + HWaddr

            'bsd': ("""
lo0: flags=8049<UP,LOOPBACK,RUNNING,MULTICAST> mtu 16384
        inet6 fe80::1%lo0 prefixlen 64 scopeid 0x1 
        inet 127.0.0.1 netmask 0xff000000 
        inet6 ::1 prefixlen 128 
gif0: flags=8051<UP,POINTOPOINT,RUNNING,MULTICAST> mtu 1280
        tunnel inet 192.168.1.2 --> 123.45.678.90
        inet6 fe80::211:22ff:fe33:4455%gif0 prefixlen 64 scopeid 0x2 
        inet6 2001:888:1234:222::2 --> 2001:888:1234:222::1 prefixlen 128 
stf0: flags=0<> mtu 1280
en0: flags=8863<UP,BROADCAST,SMART,RUNNING,SIMPLEX,MULTICAST> mtu 1500
        inet6 fe80::211:22ff:fe33:4455%en0 prefixlen 64 scopeid 0x4 
        inet 192.168.1.2 netmask 0xffffff00 broadcast 192.168.1.255
        inet6 2001:888:1235:222::1 prefixlen 64 
        ether 00:11:22:33:44:55 
        media: autoselect (100baseTX <full-duplex>) status: active
        supported media: none autoselect 10baseT/UTP <half-duplex> 10baseT/UTP <full-duplex> 10baseT/UTP <full-duplex,flow-control> 10baseT/UTP <full-duplex,hw-loopback> 100baseTX <half-duplex> 100baseTX <full-duplex> 100baseTX <full-duplex,flow-control> 100baseTX <full-duplex,hw-loopback> 1000baseT <full-duplex> 1000baseT <full-duplex,flow-control> 1000baseT <full-duplex,hw-loopback>
fw0: flags=8863<UP,BROADCAST,SMART,RUNNING,SIMPLEX,MULTICAST> mtu 4078
        lladdr 00:11:22:ff:fe:33:44:55 
        media: autoselect <full-duplex> status: inactive
        supported media: autoselect <full-duplex>
gif1: flags=8010<POINTOPOINT,MULTICAST> mtu 1280
tun0: flags=8851<UP,POINTOPOINT,RUNNING,SIMPLEX,MULTICAST> mtu 1500
        inet 192.168.10.1 --> 192.168.10.2 netmask 0xffffffff 
        open (pid 282)
""",
    set(['fe80::1',
     '127.0.0.1',
     '::1',
     'fe80::211:22ff:fe33:4455',    # Link-local Address, based on 'fe80::' + HWaddr
     '192.168.1.2',
     '2001:888:1235:222::1',        # This is my private /64
     '00:11:22:33:44:55',
     '2001:888:1234:222::2',        # This is my tunnel's address on the local side
     '192.168.10.1']),),
        'win32': ("""
===========================================================================
Interface List
 10...00 11 22 33 44 55 ......NVIDIA nForce 10/100 Mbps Ethernet 
  1...........................Software Loopback Interface 1
 15...00 00 00 00 00 00 00 e0 Microsoft ISATAP Adapter
 12...00 00 00 00 00 00 00 e0 Teredo Tunneling Pseudo-Interface
===========================================================================

IPv4 Route Table
===========================================================================
Active Routes:
Network Destination        Netmask          Gateway       Interface  Metric
          0.0.0.0          0.0.0.0    192.168.222.1  192.168.222.110     20
        127.0.0.0        255.0.0.0         On-link         127.0.0.1    306
        127.0.0.1  255.255.255.255         On-link         127.0.0.1    306
  127.255.255.255  255.255.255.255         On-link         127.0.0.1    306
    192.168.222.0    255.255.255.0         On-link   192.168.222.110    276
  192.168.222.110  255.255.255.255         On-link   192.168.222.110    276
  192.168.222.255  255.255.255.255         On-link   192.168.222.110    276
        224.0.0.0        240.0.0.0         On-link         127.0.0.1    306
        224.0.0.0        240.0.0.0         On-link   192.168.222.110    276
  255.255.255.255  255.255.255.255         On-link         127.0.0.1    306
  255.255.255.255  255.255.255.255         On-link   192.168.222.110    276
===========================================================================
Persistent Routes:
  None

IPv6 Route Table
===========================================================================
Active Routes:
 If Metric Network Destination      Gateway
 12     58 ::/0                     On-link
  1    306 ::1/128                  On-link
 12     58 2001::/32                On-link
 12    306 2001:0:5ef5:79fd:14d7:3137:1234:5678/128
                                    On-link
 10    276 fe80::/64                On-link
 12    306 fe80::/64                On-link
 12    306 fe80::14d7:3137:a803:5c0e/128
                                    On-link
 10    276 fe80::406d:150d:6f2c:8f8b/128
                                    On-link
  1    306 ff00::/8                 On-link
 12    306 ff00::/8                 On-link
 10    276 ff00::/8                 On-link
===========================================================================
Persistent Routes:
  None
""",
    set(['127.0.0.1',
        '192.168.222.110'] ),),
}

class ListAddresses(testutil.SignalMixin, unittest.TestCase):
    def test_get_local_ip_for(self):
        addr = iputil.get_local_ip_for('127.0.0.1')
        self.failUnless(DOTTED_QUAD_RE.match(addr[0]))

    def test_list_async(self):
        d = iputil.get_local_addresses_async()
        def _check(addresses):
            self.failUnless(len(addresses) >= 1) # always have localhost
            self.failUnless("127.0.0.1" in addresses, addresses)
            self.failIf("0.0.0.0" in addresses, addresses)
        d.addCallbacks(_check)
        return d
    def test_platform_regex(self):
        for platform in tool_output_map.keys():
            matchSet = set([iputil._tool_map[platform][2].match(outline).groupdict()['address']
                for outline in tool_output_map[platform][0].split('\n')
                if iputil._tool_map[platform][2].match(outline)] + 
            [iputil._tool_map[platform][3].match(outline).groupdict()['macAddress']
                for outline in tool_output_map[platform][0].split('\n')
                if iputil._tool_map[platform][3].match(outline)])
            trueSet = tool_output_map[platform][1]
            symSet = matchSet.symmetric_difference(trueSet)
            self.assertTrue(len(symSet) == 0, "Your test for " + platform + " failed, this set should be empty: " + str(symSet))
            self.assertTrue(len(trueSet) > 0, "Your test for " + platform + " doesn't have a set of IP addresses that should be found in the test.")
            self.assertTrue(len(matchSet) > 0, "Your test for " + platform + " doesn't result in any IP address, check the test cases and the regex.")

    # David A.'s OpenSolaris box timed out on this test one time when it was at 2s.
    test_list_async.timeout=4
