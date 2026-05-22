#import "../problemst/pset.typ": pset, framed

#show: pset.with(
  class: "07112303",
  student: "左逸龙",
  lab_number: 3,
  title: "Lab-3 (2) InterVLAN Routing(E)",
  date: datetime.today()
)

= VLANIF CONFIGURATION

== Paste the screenshot of the created topology.

#framed[
  #align(center)[
    #image("attachments/3-1-1.png", width: 80%)
  ]
]

== Paste the screenshot of the IP routing table on the switch LSW1.

#framed[
  #align(center)[
    #image("attachments/3-1-2.png", width: 80%)
  ]
]

== Can PC-10-1 and PC-10-3 ping each other? Please paste the screenshot of the ping result.

#framed[
  可以互相 ping 通。
  
  #align(center)[
    #image("attachments/3-1-3.png", width: 80%)
  ]
]

== Can PC-30-1 and PC-30-3 ping each other? Please paste the screenshot of the ping result.

#framed[
  可以互相 ping 通。
  
  #align(center)[
    #image("attachments/3-1-4.png", width: 80%)
  ]
]

== Can PC-10-1 and PC-30-3 ping each other? Please paste the screenshot of the ping result.

#framed[
  可以互相 ping 通。
  
  #align(center)[
    #image("attachments/3-1-5.png", width: 80%)
  ]
  
  （注：由于跨网段通信时需要先通过 ARP 协议获取网关的 MAC 地址，因此第一个 ICMP 请求出现超时属于正常现象。）
]

== Please paste the screenshot of the result of command "tracert 192.168.30.13" issued from PC-10-1.

#framed[
  #align(center)[
    #image("attachments/3-1-6.png", width: 80%)
  ]
]

== Analyze the captured ping traffics between the PC-10-1 and PC-10-2. What are the tagged VLAN IDs of the Ethernet frames leaving and entering the port? Please paste the screenshot of the all field information of the captured Ethernet frame.

#framed[
  （注：按照实验实际保留的设备，此处使用 PC-10-1 与 PC-10-3 进行抓包分析。）

  #align(center)[
    #image("attachments/3-1-7-1.png", width: 80%)
  ]
  
  #align(center)[
    #image("attachments/3-1-7-2.png", width: 80%)
  ]

  捕获到的 Ethernet 帧进入和离开端口的 VLAN ID 均为 $10$。
  因为 PC-10-1 和 PC-10-3 同属于 VLAN $10$，它们之间的通信属于二层交换转发，不经过三层路由。因此，在两台交换机之间的 Trunk 链路上，数据帧仅携带源 VLAN（即 VLAN $10$）的标签。
]

== Analyze the captured ping traffics between the PC-10-1 and PC-30-2. What are the tagged VLAN IDs of the Ethernet frames leaving and entering the port? Please paste the screenshot of the all field information of the captured Ethernet frames.

#framed[
  #align(center)[
    #image("attachments/3-1-8-1.png", width: 80%)
  ]
  
  #align(center)[
    #image("attachments/3-1-8-2.png", width: 80%)
  ]

  捕获到的 Ethernet 帧进入和离开 LSW1 的 Trunk 端口时的 VLAN ID 均为 $30$。原因如下：
  - 数据报文从 PC-10-1 发出到达 LSW1 时，属于 VLAN $10$。
  - 因为目的 IP 属于另一个网段，LSW1 查找内部路由表进行三层转发，将报文从 VLAN $10$ 解封装，并重新打上 VLAN $30$ 的标签。
  - 随后，这个已经被打上 VLAN $30$ 标签的报文才从 LSW1 的 GE 0/0/24 接口离开并发送给 LSW2。因此我们在该接口抓到的跨 VLAN 数据包，其 802.1Q 标签已经被修改为了目的网络的 VLAN ID。
]

= ONE-ARMED ROUTER CONFIGURATION

== Paste the screenshot of the created topology.

#framed[
  #align(center)[
    #image("attachments/3-2-1.png", width: 80%)
  ]
]

== Paste the screenshot of the IP routing table on the router RTA.

#framed[
  #align(center)[
    #image("attachments/3-2-2.png", width: 80%)
  ]
]

== Can PC-10-1 and PC-10-3 ping each other? Please paste the screenshot of the ping result.

#framed[
  可以互相 ping 通。
  
  #align(center)[
    #image("attachments/3-2-3.png", width: 80%)
  ]
]

== Paste the screenshot of the result of command "tracert 192.168.30.13" issued from PC-10-1.

#framed[
  #align(center)[
    #image("attachments/3-2-4.png", width: 80%)
  ]
]

== Analyze the captured ping traffics between the PC-10-1 and PC-10-3. What are the tagged VLAN IDs of the Ethernet frames leaving and entering the interface GE 0/0/2 on switch LSW3 ? Please paste the screenshot of the all field information of the captured Ethernet frame.

#framed[
  #align(center)[
    #image("attachments/3-2-5.png", width: 80%)
  ]

  抓取到的 ARP 广播报文携带的 VLAN ID 为 $10$。
  由于 PC-10-1 和 PC-10-3 同属于 VLAN $10$，它们之间的 Ping 通信在二层交换机（LSW1、LSW3、LSW2）内部根据 MAC 地址表就可以直接完成转发，根本不需要经过路由器。因此，属于单播的 ICMP 数据流不会被上送到连接路由器的 GE 0/0/2 接口。只有像 ARP 这样的广播报文才会被交换机泛洪到该接口。
]

== Analyze the captured ping traffics between the PC-10-1 and PC-10-3. What are the tagged VLAN IDs of the Ethernet frames leaving and entering the interface GE 0/0/24 on switch LSW3 ? Please paste the screenshot of the all field information of the captured Ethernet frame.

#framed[
  下面分别是进入 LSW3 端口和离开 LSW3 端口的数据帧抓包信息：

  #align(center)[
    #image("attachments/3-2-6-1.png", width: 80%)
    #image("attachments/3-2-6-2.png", width: 80%)
  ]

  捕获到的 Ethernet 帧进入和离开接口 GE 0/0/24 的 VLAN ID 均为 $10$。
  由于通信双方处于同一 VLAN 内，数据在跨越交换机的 Trunk 链路上传输时，仅携带其原始的 VLAN $10$ 标签，不涉及三层路由的解封装和重封装。
]

== Analyze the captured ping traffics between the PC-10-1 and PC-30-3. What are the tagged VLAN IDs of the Ethernet frames leaving and entering the interface GE 0/0/2 on router RTA? Please paste the screenshot of the all field information of the captured Ethernet frame.

#framed[
  下面分别是跨 VLAN 通信时，进入路由器 RTA 端口和离开路由器 RTA 端口的同一个 ICMP 请求报文的抓包信息：

  #align(center)[
    #image("attachments/3-2-7-1.png", width: 80%)
    #image("attachments/3-2-7-2.png", width: 80%)
  ]
  
  - *进入接口：* 源自 PC-10-1 的报文通过 LSW3 透传到达 RTA 的子接口 0/0/2.10，此时捕获到的 Ethernet 帧带有源网络的标签，VLAN ID 为 $10$。
  - *离开接口：* RTA 接收该报文后，剥离 VLAN $10$ 的标签，查询路由表发现目的地属于 $192.168.30.0\/24$ 网段。于是该报文被转交由子接口 0/0/2.30 发出，并重新打上 VLAN $30$ 的标签。因此在报文离开该接口时，捕获到的 Ethernet 帧 VLAN ID 变成了 $30$。
]