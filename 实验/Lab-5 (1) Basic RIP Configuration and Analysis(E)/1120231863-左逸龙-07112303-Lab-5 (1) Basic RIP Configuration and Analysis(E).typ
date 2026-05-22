#import "../problemst/pset.typ": pset, framed

#show: pset.with(
  class: "07112303",
  student: "左逸龙",
  lab_number: 5,
  title: "Lab-5 (1) Basic RIP Configuration and Analysis(E)",
  date: datetime.today()
)

= BASIC RIPV1 CONFIGURATION

== Paste the screenshot of the created topology.

#framed[
  #align(center)[
    #image("attachments/5-1-1.png", width: 80%)
  ]  
]

== Paste the screenshot of the IP routing table on the router RTA. Highlight the RIPv1 routes in the screenshot. Which routes are learned from the RIP neighbors?

#framed[
  #align(center)[
    #image("attachments/5-1-2.png", width: 80%)
  ]
  
  RTA并没有从RIP邻居学习到任何路由。由于RTA仅配置了去往 $0.0.0.0\/0$ 的静态默认路由（Static），且没有运行RIP协议，因此其路由表中不存在通过RIP动态学习到的路由。
]

== Paste the screenshot of the IP routing table on the router RTB. Highlight the RIPv1 routes in the screenshot. Which routes are learned from the RIP neighbors?

#framed[
  #align(center)[
    #image("attachments/5-1-3.png", width: 80%)
  ]
  
  从截图中可以看出，协议类型（Proto）为RIP的路由是通过RIP邻居学习到的。RTB学习到的RIP路由包括：
  - 目的网段 $172.16.103.0\/24$
  - 目的网段 $192.168.30.0\/24$
  - 目的网段 $192.168.200.0\/24$
]

== Paste the screenshot of the IP routing table on the router RTC. Highlight the RIPv1 routes in the screenshot. Which routes are learned from the RIP neighbors?

#framed[
  #align(center)[
    #image("attachments/5-1-4.png", width: 80%)
  ]
  
  从截图中可以看出，RTC通过RIP邻居学习到了以下目的网段的路由：
  - 目的网段 $172.16.101.0\/24$
  - 目的网段 $192.168.30.0\/24$
  - 目的网段 $192.168.200.0\/24$
]

== Paste the screenshot of the IP routing table on the router RTD. Highlight the RIPv1 routes in the screenshot. Which routes are learned from the RIP neighbors?

#framed[
  #align(center)[
    #image("attachments/5-1-5.png", width: 80%)
  ]
  
  从截图中可以看出，RTD通过RIP邻居学习到了以下目的网段的路由：
  - 目的网段 $172.16.101.0\/24$
  - 目的网段 $172.16.102.0\/24$
]

== Can PC-10-1 and PC-30-1 ping each other? Please paste the screenshot of the ping result.

#framed[
  可以互相ping通。
  
  #align(center)[
    #image("attachments/5-1-6.png", width: 80%)
  ]
]

== Can PC-10-1 and loopback 0 on RTD ping each other? Please paste the screenshot of the ping result.

#framed[
  可以互相ping通。
  
  #align(center)[
    #image("attachments/5-1-7.png", width: 80%)
  ]
]

== Please paste the screenshot of the result of command "tracert 192.168.30.11" issued from PC-10-1.

#framed[
  #align(center)[
    #image("attachments/5-1-8.png", width: 80%)
  ]
]

== How many types of RIPv1 packets are there? What are they?

#framed[
  RIPv1共有两种类型的报文，分别是：
  - *Request*（请求报文）：路由器刚启动时或需要更新时主动向邻居发送，用于请求完整的或部分的路由表信息。
  - *Response*（响应报文）：路由器周期性广播或在收到Request报文后触发发送，包含具体的路由条目信息。
]

== What is the interval between RIPv1 routing updates?

#framed[
  RIPv1默认的路由更新时间间隔是 *30秒*。
]

== Which protocol does RIPv1 use to transmit RIP packets? What are the source port number and destination port number?

#framed[
  RIPv1使用 *UDP* 协议传输报文。其源端口号和目的端口号均为 *520*。
]

== When RIPv1 sends a routing update message, what is the destination IP address of the message? What type of IP address is it?

#framed[
  RIPv1发送路由更新报文时，目的IP地址为 $255.255.255.255$。这是一个受限的*广播地址*。
]

== How many routes are there in each RIPv1 route update message? What information does each route contain in the route update message? Please paste the screenshot of the route information contained in the captured update routing message.

#framed[
  每个RIPv1路由更新报文最多可以包含 *25* 条路由记录。
  
  每条路由记录中包含的主要信息有：
  - *AFI*（Address Family Identifier，地址族标识符，IPv4通常对应的值为2）
  - *IP Address*（目的网络的IP地址）
  - *Metric*（到达目的网络的跳数开销）

  #align(center)[
    #image("attachments/5-1-13.png", width: 80%)
  ]
]

== Please give the format of RIPv1 routing update message.

#framed[
  RIPv1更新报文的基本格式如下：

  - *Command*（1字节）：标识报文类型，1表示Request，2表示Response。
  - *Version*（1字节）：RIP协议的版本号，对于RIPv1此处必须为1。
  - *Must be zero*（2字节）：保留填充字段，必须全为0。

  随后是最多包含25条路由记录（Route Entries）的更新列表，每条路由记录长度为20字节，具体包含：
  - *Address Family Identifier (AFI)*（2字节）：地址族标识符，IPv4对应的值为2。
  - *Route Tag / Must be zero*（2字节）：在RIPv1中不使用该标签，必须全为0。
  - *IP Address*（4字节）：目的网络的IP地址。
  - *Subnet Mask / Must be zero*（4字节）：RIPv1属于有类路由协议，不支持可变长子网掩码（VLSM），此字段必须全为0。
  - *Next Hop / Must be zero*（4字节）：RIPv1中不携带下一跳地址，此字段必须全为0。
  - *Metric*（4字节）：到达目的网络的跳数（Hop Count），有效取值范围为1到15，16表示目标网络不可达。
]