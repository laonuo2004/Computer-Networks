#import "../problemst/pset.typ": pset, framed

#show: pset.with(
  class: "07112303",
  student: "左逸龙",
  lab_number: 4,
  title: "Lab-4 (1) Static and Default Routes(E)",
  date: datetime.today()
)

= STATIC AND DEFAULT ROUTE CONFIGURATION

== Paste the screenshot of the created topology.

#framed[
  #align(center)[
    #image("attachments/4-1-1.png", width: 80%)
  ]
]

== Paste the screenshot of the IP routing table on the router RTA.

#framed[
  #align(center)[
    #image("attachments/4-1-2.png", width: 80%)
  ]
]

== Paste the screenshot of the IP routing table on the router RTB.

#framed[
  #align(center)[
    #image("attachments/4-1-3.png", width: 80%)
  ]
]

== Paste the screenshot of the IP routing table on the router RTC.

#framed[
  #align(center)[
    #image("attachments/4-1-4.png", width: 80%)
  ]
]

== Paste the screenshot of the IP routing table on the router RTD.

#framed[
  #align(center)[
    #image("attachments/4-1-5.png", width: 80%)
  ]
]

== Can PC-10-1 and PC-30-1 ping each other? Please paste the screenshot of the ping result.

#framed[
  不能。

  #align(center)[
    #image("attachments/4-1-6.png", width: 80%)
  ]
]

== Can PC-30-1 and loopback 0 on RTD ping each other? Please paste the screenshot of the ping result.

#framed[
  可以。

  #align(center)[
    #image("attachments/4-1-7.png", width: 80%)
  ]
]

== Can PC-10-1 and loopback 0 on RTD ping each other? Please paste the screenshot of the ping result.

#framed[
  不能。

  #align(center)[
    #image("attachments/4-1-8.png", width: 80%)
  ]
]

== Paste the screenshot of the IP routing table on the router RTA.

#framed[
  #align(center)[
    #image("attachments/4-1-9.png", width: 80%)
  ]
]

== Paste the screenshot of the IP routing table on the router RTB.

#framed[
  #align(center)[
    #image("attachments/4-1-10.png", width: 80%)
  ]
]

== Paste the screenshot of the IP routing table on the router RTC.

#framed[
  #align(center)[
    #image("attachments/4-1-11.png", width: 80%)
  ]
]

== Paste the screenshot of the IP routing table on the router RTD.

#framed[
  #align(center)[
    #image("attachments/4-1-12.png", width: 80%)
  ]
]

== Can PC-10-1 and PC-30-1 ping each other? Please paste the screenshot of the ping result.

#framed[
  可以。

  #align(center)[
    #image("attachments/4-1-13.png", width: 80%)
  ]
]

== Can PC-10-1 and loopback 0 on RTD ping each other? Please paste the screenshot of the ping result. If they cannot ping each other, please explain why.

#framed[
  不能。因为各路由器（RTA、RTB、RTC）的路由表中均未配置到达 RTD 的 Loopback 0（$192.168.200.0\/24$）网段的明细路由，导致数据包无法找到下一跳转发路径，在传输中途被丢弃。

  #align(center)[
    #image("attachments/4-1-14.png", width: 80%)
  ]
]

== Please paste the screenshot of the result of command "tracert 192.168.30.11" issued from PC-10-1.

#framed[
  #align(center)[
    #image("attachments/4-1-15.png", width: 80%)
  ]
]

== Paste the screenshot of the IP routing table on the router RTA.

#framed[
  #align(center)[
    #image("attachments/4-1-16.png", width: 80%)
  ]
]

== Paste the screenshot of the IP routing table on the router RTB.

#framed[
  #align(center)[
    #image("attachments/4-1-17.png", width: 80%)
  ]
]

== Paste the screenshot of the IP routing table on the router RTC.

#framed[
  #align(center)[
    #image("attachments/4-1-18.png", width: 80%)
  ]
]

== Paste the screenshot of the IP routing table on the router RTD.

#framed[
  #align(center)[
    #image("attachments/4-1-19.png", width: 80%)
  ]
]

== Can PC-10-1 and Loopback 0 on RTD ping each other? Please paste the screenshot of the ping result. If they can ping each other, please explain why.

#framed[
  可以。因为现在双向路由均完整，发送与接收线路上默认路由与静态路由协同工作，可以确保数据包正确转发。具体而言：

  - *去程*：虽然没有配置到达 $192.168.200.0\/24$ 的明细路由，但由于配置了 $0.0.0.0\/0$ 的默认路由，路由器匹配不到具体网段时会将其作为“兜底”规则，将数据包一路向右转发，最终到达 RTD 并被接收。
  - *回程*：RTD 删除了之前的明细路由，因此回复给 PC-10-1 的数据包同样会命中 RTD 上的默认路由 $0.0.0.0\/0$，被一路向左转发回 PC-10-1。

  #align(center)[
    #image("attachments/4-1-20.png", width: 80%)
  ]
]