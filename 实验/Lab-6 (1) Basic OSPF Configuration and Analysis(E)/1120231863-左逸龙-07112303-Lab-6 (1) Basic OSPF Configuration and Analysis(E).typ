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
  #align(center)[
    #image("attachments/6-1-1.png", width: 80%)
  ]  
]

== Paste the screenshots of the OSPF routing table, Link-State Database, OSPF neighbor, updates of the LSAs that the LSDB receives and route calculation statistics on the router RTA.

#framed[
  #align(center)[
    #image("attachments/6-1-2-1.png", width: 80%)
    #image("attachments/6-1-2-2.png", width: 80%)
    #image("attachments/6-1-2-3.png", width: 80%)
    #image("attachments/6-1-2-4.png", width: 80%)
    #image("attachments/6-1-2-5.png", width: 80%)
  ]
]

== Paste the screenshots of the OSPF routing table, Link-State Database, OSPF neighbor, updates of the LSAs that the LSDB receives and route calculation statistics on the router RTB.

#framed[
  #align(center)[
    #image("attachments/6-1-3-1.png", width: 80%)
    #image("attachments/6-1-3-2.png", width: 80%)
    #image("attachments/6-1-3-3.png", width: 80%)
    #image("attachments/6-1-3-4.png", width: 80%)
    #image("attachments/6-1-3-5.png", width: 80%)
  ]
]

== Paste the screenshots of the OSPF routing table, Link-State Database, OSPF neighbor, updates of the LSAs that the LSDB receives and route calculation statistics on the router RTC.

#framed[
  #align(center)[
    #image("attachments/6-1-4-1.png", width: 80%)
    #image("attachments/6-1-4-2.png", width: 80%)
    #image("attachments/6-1-4-3.png", width: 80%)
    #image("attachments/6-1-4-4.png", width: 80%)
    #image("attachments/6-1-4-5.png", width: 80%)
  ]
]

== Paste the screenshots of the OSPF routing table, Link-State Database, OSPF neighbor, updates of the LSAs that the LSDB receives and route calculation statistics on the router RTD.

#framed[
  #align(center)[
    #image("attachments/6-1-5-1.png", width: 80%)
    #image("attachments/6-1-5-2.png", width: 80%)
    #image("attachments/6-1-5-3.png", width: 80%)
    #image("attachments/6-1-5-4.png", width: 80%)
    #image("attachments/6-1-5-5.png", width: 80%)
  ]
]

== Can PC-10-1 and PC-30-1 ping each other? Please paste the screenshot of the ping result.

#framed[
  可以互相 ping 通。
  #align(center)[
    #image("attachments/6-1-6.png", width: 80%)
  ]
]

== Can PC-10-1 and loopback 0 on RTD ping each other? Please paste the screenshot of the ping result.

#framed[
  可以互相 ping 通。
  #align(center)[
    #image("attachments/6-1-7.png", width: 80%)
  ]
]

== Please paste the screenshot of the result of command "tracert 192.168.30.11" issued from PC-10-1.

#framed[
  #align(center)[
    #image("attachments/6-1-8.png", width: 80%)
  ]
]

== Just after configuring OSPF on RTA and RTB, what OSPF packets are exchanged between RTA and RTB? Please explain with the captured OSPF communications.

#framed[
  在刚配置 OSPF 时，RTA 与 RTB 之间互相交换了 5 种 OSPF 报文：
  
  - 发送 *Hello* 报文，用于发现和建立邻居关系。
  - 发送 *Database Description (DD)* 报文，用于交换链路状态数据库 (LSDB) 的摘要信息。
  - 发送 *Link State Request (LSR)* 报文，用于向对方请求自身缺失的链路状态通告 (LSA)。
  - 发送 *Link State Update (LSU)* 报文，用于发送完整的 LSA 详细信息给对方。
  - 发送 *Link State Acknowledgment (LSAck)* 报文，用于对收到的 LSU 进行确认。
  
  #align(center)[
    #image("attachments/6-1-9.png", width: 80%)
  ]
]

== With the completion of the OSPF configurations on each router, how does RTA know that the network topology has changed? Please explain with the captured OSPF communications.

#framed[
  OSPF 协议基于触发更新 (Triggered Updates) 机制。当网络拓扑发生改变（例如有新路由器加入或路由宣告完成）时，感知到变化的路由器（如 RTB）会立即向目标组播地址 $224.0.0.5$ 发送装载了最新链路状态通告 (LSA) 的 *LSU* 报文进行泛洪。
  
  RTA 接收到该 LSU 报文后，会更新自身的链路状态数据库 (LSDB)，并重新运行 *SPF (Dijkstra)* 算法，计算出新的最短路径并更新路由表。
]

== What OSPF packets are sent and received from the interface GE 0/0/0 and GE 0/0/1 on RTB? Paste the screenshot of the captured OSPF packets.

#framed[
  RTB 的 GE 0\/0\/0 和 GE 0\/0\/1 接口发送和接收了 Hello, DB Description (DD), LS Request (LSR), LS Update (LSU) 以及 LS Acknowledge (LSAck) 报文，绝大多数报文的目标 IP 地址为 OSPF 组播地址 $224.0.0.5$。
  
  #align(center)[
    #image("attachments/6-1-11-1.png", width: 80%)
    #image("attachments/6-1-11-2.png", width: 80%)
  ]
]

== What OSPF packets are sent and received from the interface GE 0/0/0 and GE 0/0/1 on RTC? Paste the screenshot of the captured OSPF packets.

#framed[
  与 RTB 类似，RTC 的 GE 0\/0\/0 和 GE 0\/0\/1 接口同样发送和接收了全部 5 种 OSPF 报文（Hello, DD, LSR, LSU, LSAck），目标地址主要是组播地址 $224.0.0.5$。
  
  #align(center)[
    #image("attachments/6-1-12-1.png", width: 80%)
    #image("attachments/6-1-12-2.png", width: 80%)
  ]
]

== In what type of packet are the OSPF Link State Advertisements sent from the interface GE 0/0/0 on RTB transmitted? What are their LSA types? Paste the screenshot of the expanded information of the captured LSAs.

#framed[
  OSPF 的链路状态通告 (LSA) 是被封装在 *LS Update (LSU)* 报文中进行传输的。
  
  从截图中可以看出，在 RTB 的 GE 0\/0\/0 接口（连接 Area 1，源地址为 $172.16.101.2$）发送的报文中，包含了 *Type 3 (Summary-LSA)* 类型的 LSA。这是因为 RTB 作为区域边界路由器 (ABR)，将其学习到的其他区域的路由信息（如图中展开的属于 Area 2 的 $192.168.200.100$）转换为 Type 3 LSA，并通过该接口注入到 Area 1 中供 RTA 学习。
  
  #align(center)[
    #image("attachments/6-1-13.png", width: 80%)
  ]
]

== In what type of packet are the OSPF Link State Advertisements sent from the interface GE 0/0/1 on RTB transmitted? What are their LSA types? Paste the screenshot of the expanded information of the captured LSAs.

#framed[
  LSA 同样是被封装在 *LS Update (LSU)* 报文中传输的。
  
  从截图中可以看出，在 RTB 的 GE 0\/0\/1 接口（连接骨干区域 Area 0，源地址为 $172.16.102.1$）发送的报文中，包含了 *Type 1 (Router-LSA)* 类型的 LSA。RTB 作为 Area 0 的一员，需要发送 Type 1 LSA 来描述自身在骨干区域的链路状态（截图中展开的 `Flags: (B) Area border router` 标识清晰地证明了它是 ABR）。
  
  #align(center)[
    #image("attachments/6-1-14.png", width: 80%)
  ]
]

== How are the Link State Advertisements in area 1 transmitted to area 2 through area 0? Please explain with the captured OSPF communications.

#framed[
  - 首先，Area 1 内的 RTA 会生成 *Type 1 Router-LSA*，用于描述其直连网络并在 Area 1 内部进行泛洪。
  - 其次，RTB 作为连接 Area 1 和 Area 0 的区域边界路由器 (ABR)，在收到该 Type 1 LSA 后，会将其转换为 *Type 3 Summary-LSA*，并将该路由汇总信息注入到骨干区域 Area 0 中传输。
  - 最后，RTC 作为另一端的 ABR，在 Area 0 中接收到该 Type 3 LSA 后，会重新生成新的 Type 3 LSA 并将其泛洪到 Area 2 中。最终 RTD 收到该通告，从而学习到了通往 Area 1 的路由。
]

== How are the Link State Advertisements in area 2 transmitted to area 1 through area 0? Please explain with the captured OSPF communications.

#framed[
  传递机制与上一题的逻辑完全相同，方向相反：
  
  - 首先，Area 2 内的 RTD 会生成 *Type 1 Router-LSA* 来描述其网络（包含 $192.168.30.0\/24$ 以及 Loopback 0 接口的网络），并在 Area 2 内泛洪。
  - 其次，RTC 作为 ABR，在收到该通告后将其打包转换为 *Type 3 Summary-LSA*，并将其泛洪至骨干区域 Area 0。
  - 最后，RTB 从 Area 0 中接收到该 Type 3 LSA 后，生成新的 Type 3 LSA 并泛洪进 Area 1 中，从而使得 RTA 最终学习到通往 Area 2 的跨区域路由。
]