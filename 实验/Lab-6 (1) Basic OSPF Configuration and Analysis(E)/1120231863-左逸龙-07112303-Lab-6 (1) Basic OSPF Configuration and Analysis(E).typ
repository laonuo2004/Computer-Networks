#import "../problemst/pset.typ": pset, framed

#show: pset.with(
  class: "07112303",
  student: "左逸龙",
  lab_number: 6,
  title: "Lab-6 (1) Basic OSPF Configuration and Analysis(E)",
  date: datetime.today()
)

= BASIC MULTIPLE AREA OSPF CONFIGURATION

== Paste the screenshot of the created topology.

#framed[
  // 用于填写我的回答
]

== Paste the screenshots of the OSPF routing table, Link-State Database, OSPF neighbor, updates of the LSAs that the LSDB receives and route calculation statistics on the router RTA.

#framed[
  // 用于填写我的回答
]

== Paste the screenshots of the OSPF routing table, Link-State Database, OSPF neighbor, updates of the LSAs that the LSDB receives and route calculation statistics on the router RTB.

#framed[
  // 用于填写我的回答
]

== Paste the screenshots of the OSPF routing table, Link-State Database, OSPF neighbor, updates of the LSAs that the LSDB receives and route calculation statistics on the router RTC.

#framed[
  // 用于填写我的回答
]

== Paste the screenshots of the OSPF routing table, Link-State Database, OSPF neighbor, updates of the LSAs that the LSDB receives and route calculation statistics on the router RTD.

#framed[
  // 用于填写我的回答
]

== Can PC-10-1 and PC-30-1 ping each other? Please paste the screenshot of the ping result.

#framed[
  // 用于填写我的回答
]

== Can PC-10-1 and loopback 0 on RTD ping each other? Please paste the screenshot of the ping result.

#framed[
  // 用于填写我的回答
]

== Please paste the screenshot of the result of command "tracert 192.168.30.11" issued from PC-10-1.

#framed[
  // 用于填写我的回答
]

== Just after configuring OSPF on RTA and RTB, what OSPF packets are exchanged between RTA and RTB? Please explain with the captured OSPF communications.

#framed[
  // 用于填写我的回答
]

== With the completion of the OSPF configurations on each router, how does RTA know that the network topology has changed? Please explain with the captured OSPF communications.

#framed[
  // 用于填写我的回答
]

== What OSPF packets are sent and received from the interface GE 0/0/0 and GE 0/0/1 on RTB? Paste the screenshot of the captured OSPF packets.

#framed[
  // 用于填写我的回答
]

== What OSPF packets are sent and received from the interface GE 0/0/0 and GE 0/0/1 on RTC? Paste the screenshot of the captured OSPF packets.

#framed[
  // 用于填写我的回答
]

== In what type of packet are the OSPF Link State Advertisements sent from the interface GE 0/0/0 on RTB transmitted? What are their LSA types? Paste the screenshot of the expanded information of the captured LSAs.

#framed[
  // 用于填写我的回答
]

== In what type of packet are the OSPF Link State Advertisements sent from the interface GE 0/0/1 on RTB transmitted? What are their LSA types? Paste the screenshot of the expanded information of the captured LSAs.

#framed[
  // 用于填写我的回答
]

== How are the Link State Advertisements in area 1 transmitted to area 2 through area 0? Please explain with the captured OSPF communications.

#framed[
  // 用于填写我的回答
]

== How are the Link State Advertisements in area 2 transmitted to area 1 through area 0? Please explain with the captured OSPF communications.

#framed[
  // 用于填写我的回答
]