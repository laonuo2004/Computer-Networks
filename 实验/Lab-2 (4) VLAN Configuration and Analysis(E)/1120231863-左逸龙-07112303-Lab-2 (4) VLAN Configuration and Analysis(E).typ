#import "../problemst/pset.typ": pset, framed

#show: pset.with(
  class: "07112303",
  student: "左逸龙",
  lab_number: 2,
  title: "Lab-2 (4) VLAN Configuration and Analysis(E)",
  date: datetime.today()
)



= PORT-BASED VLAN CONFIGURATION

== Paste the screenshot of the created topology.

#framed[
  #align(center)[
    #image("attachments/2-1-1.png", width: 80%)
  ]
]

== Draw IEEE 802.1D tagged frame format.

#framed[
  普通的以太网帧在源 MAC 地址和类型字段之间插入了 4 字节的 802.1Q 标签（VLAN Tag）。帧格式如下：

  #align(center)[
    #table(
      columns: (auto, auto, auto, auto, auto, auto),
      align: center + horizon,[*目的 MAC 地址*\ 6 字节],
      [*源 MAC 地址*\ 6 字节],
      fill: (_, c) => if c == 2 { rgb("e6f7ff") } else { none },[*802.1Q VLAN 标签*\ 4 字节],[*类型 / 长度*\ 2 字节],
      [*数据载荷*\ 46 - 1500 字节],[*FCS 校验*\ 4 字节]
    )
  ]

  其中，4 字节的 802.1Q VLAN 标签内部结构详细拆分为：

  #align(center)[
    #table(
      columns: (auto, auto, auto, auto),
      align: center + horizon,
      fill: rgb("e6f7ff"),[*TPID (标签协议标识符)*\ 2 字节 (固定值 0x8100)],
      [*PRI (优先级)*\ 3 bits],
      [*CFI/DEI (规范格式指示符)*\ 1 bit],[*VID (VLAN ID)*\ 12 bits]
    )
  ]
]

== Paste the screenshot of VLAN 10 information.

#framed[
  #align(center)[
    #image("attachments/2-1-3.png", width: 80%)
  ]
]

== Paste the screenshot of VLAN 30 information.

#framed[
  #align(center)[
    #image("attachments/2-1-4.png", width: 80%)
  ]
]

== Suppose you are going to create a new VLAN 40, and add ports 17-20 to this VLAN in batches. Please list the configuration command.

#framed[
  在华为交换机中，可以通过建立端口组（port-group）的方式批量将端口加入到新建的 VLAN 中。配置命令如下：

  ```text
  [LSW1] vlan 40
  [LSW1-vlan40] quit
  [LSW1] port-group pgvlan40
  [LSW1-port-group-pgvlan40] group-member GigabitEthernet 0/0/17 to GigabitEthernet 0/0/20
  [LSW1-port-group-pgvlan40] port link-type access
  [LSW1-port-group-pgvlan40] port default vlan 40
  [LSW1-port-group-pgvlan40] quit
  ```
]

== Can PCs in the same VLAN ping each other? Please paste the screenshot of the ping result.

#framed[
  可以相互 Ping 通，因为在同一个 VLAN（例如同在 VLAN 10）内的 PC 处于同一个二层广播域，ARP 广播能够正常送达并解析到 MAC 地址，因此可以直接完成二层通信。

  #align(center)[
    #image("attachments/2-1-6.png", width: 70%)
  ]
]

== Can PCs in different VLANs ping each other? Please paste the screenshot of the ping result. If the ping fails, please explain the reasons.

#framed[
  不能互相 Ping 通，因为不同的 VLAN 在逻辑上属于独立的二层广播域。二层交换机会隔离不同 VLAN 之间的广播流量，这意味着终端跨 VLAN 发送的 ARP 请求无法被对方收到，因而无法获取目标设备的 MAC 地址。
  
  #align(center)[
    #image("attachments/2-1-7.png", width: 70%)
  ]
]

= MAC ADDRESS-BASED VLAN CONFIGURATION

== Paste the screenshot of the created topology.

#framed[
  #align(center)[
    #image("attachments/2-2-1.png", width: 80%) // 请替换为第一张拓扑图的文件名
  ]
]

== Paste the table of MAC addresses of the two laptops you recorded.

#framed[
  #align(center)[
    #image("attachments/2-2-2-1.png", width: 80%),
    #image("attachments/2-2-2-2.png", width: 80%)
  ]
]

== Paste the screenshot of the configuration information of all MAC address-based VLANs.

#framed[
  #align(center)[
    #image("attachments/2-2-3.png", width: 80%) // 请替换为 display mac-vlan mac-address all 的截图
  ]
]

== When adding members to VLAN 10 and VLAN 30 based on the MAC address, what is the difference between VLAN 10 and VLAN 30 information before and after adding members? Please paste the screenshot of VLAN 10 information before and after adding members.

#framed[
  在基于 MAC 地址添加成员之前，VLAN 10 中只包含最初基于端口划分的 Access 接口（GE 0/0/9 到 GE 0/0/12）。
  在配置了 MAC 地址划分，并将连接 Laptop 的 GE 0/0/5 和 GE 0/0/6 设置为 Hybrid 端口（且允许 VLAN 10 报文以 Untagged 形式通过）之后，VLAN 10 的端口列表中新增了 GE 0/0/5 和 GE 0/0/6，且状态标记为 `UT` (Untagged)。这说明这两个端口现在已经能够合法收发属于 VLAN 10 的无标签数据帧。

  *配置前 VLAN 10 信息：*
  #align(center)[
    #image("attachments/2-2-4-1.png", width: 80%) // 请替换为配置前的 display vlan 10 截图
  ]

  *配置后 VLAN 10 信息：*
  #align(center)[
    #image("attachments/2-2-4-2.png", width: 80%) // 请替换为配置后的 display vlan 10 截图
  ]
]

== Can PC-10-1 ping PC-BOOK10-1 each other? Please paste the screenshot of the ping result.

#framed[
  可以相互 Ping 通。

  #align(center)[
    #image("attachments/2-2-5.png", width: 70%) // 请替换为 PC-10-1 ping PC-BOOK-10-1 的截图
  ]
]

== Can PC-30-1 ping PC-BOOK30-1 each other? Please paste the screenshot of the ping result.

#framed[
  可以相互 Ping 通。

  #align(center)[
    #image("attachments/2-2-6.png", width: 70%) // 请替换为 PC-30-1 ping PC-BOOK-30-1 的截图
  ]
]

== Paste the screenshot of the new topology.

#framed[
  #align(center)[
    #image("attachments/2-2-7.png", width: 80%) // 请替换为交叉连线后的新拓扑截图
  ]
]

== Can PC-10-1 ping PC-BOOK10-1 each other? Please paste the screenshot of the ping result.

#framed[
  换线后，依然可以相互 Ping 通。
  因为开启了 MAC-VLAN，交换机不再依赖物理端口划分 VLAN，而是读取数据帧的源 MAC 地址，动态识别出这是属于部门 A 的设备，并将其自动划入 VLAN 10。

  #align(center)[
    #image("attachments/2-2-8.png", width: 70%) // 请替换为换线后 PC-10-1 ping PC-BOOK-10-1 的截图
  ]
]

== Can PC-30-1 ping PC-BOOK30-1 each other? Please paste the screenshot of the ping result.

#framed[
  换线后，依然可以相互 Ping 通。原因同上。

  #align(center)[
    #image("attachments/2-2-9.png", width: 70%) // 请替换为换线后 PC-30-1 ping PC-BOOK-30-1 的截图
  ]
]

= IP SUBNET-BASED VLAN CONFIGURATION

== Paste the screenshot of the created topology.

#framed[
  #align(center)[
    #image("attachments/2-3-1.png", width: 80%) // 请替换为第一张拓扑图的文件名
  ]
]

== Paste the screenshot of the configuration information of all IP subnet-based VLANs.

#framed[
  #align(center)[
    #image("attachments/2-3-2.png", width: 80%) // 请替换为 display ip-subnet-vlan vlan all 的截图
  ]
]

== Can PC-10-1, PC-BOOK10-1 and PC-10-A ping each other? Please paste the screenshot of the ping result.

#framed[
  可以相互 Ping 通。
  此时 PC-10-A 的 IP 为 192.168.10.20，属于 10 网段。当数据帧进入交换机的 Hybrid 接口时，交换机会根据源 IP 地址匹配到 VLAN 10 的子网规则，将其动态划入 VLAN 10，因此可以与同在 VLAN 10 的另外两台电脑互通。

  #align(center)[
    #image("attachments/2-3-3.png", width: 70%) // 请替换为 PC-10-A ping 10.11 和 10.18 的截图
  ]
]

== Can PC-30-1, PC-BOOK30-1 and PC-30-A ping each other? Please paste the screenshot of the ping result.

#framed[
  可以相互 Ping 通。
  此时 PC-30-A 的 IP 为 192.168.30.20，匹配到 30 网段的规则，被交换机自动划入 VLAN 30。

  #align(center)[
    #image("attachments/2-3-4.png", width: 70%) // 请替换为 PC-30-A ping 30.11 和 30.18 的截图
  ]
]

== Can PC-10-1, PC-BOOK10-1 and PC-30-A ping each other? Please paste the screenshot of the ping result.

#framed[
  更改 IP 后，可以互相 Ping 通。
  在未更改物理连线的情况下，仅仅将 PC-30-A 的 IP 地址修改为 `192.168.10.20`。此时交换机收到其发出的 Untagged 数据帧，解析三层源 IP 头发现属于 10 网段，便动态将其所属 VLAN 更改为 VLAN 10，从而实现了与部门 A 的通信。

  #align(center)[
    #image("attachments/2-3-5.png", width: 70%) // 请替换为 PC-30-A(IP变更为10.20后) 成功 ping 10.11/10.18 的截图
  ]
]

== Can PC-30-1, PC-BOOK30-1 and PC-10-A ping each other? Please paste the screenshot of the ping result.

#framed[
  更改 IP 后，可以互相 Ping 通。
  同理，将 PC-10-A 的 IP 地址修改为 `192.168.30.20` 后，基于 IP 子网的 VLAN 划分策略生效，设备被动态划入 VLAN 30，因此能够与部门 B 的设备正常通信。

  #align(center)[
    #image("attachments/2-3-6.png", width: 70%) // 请替换为 PC-10-A(IP变更为30.20后) 成功 ping 30.11/30.18 的截图
  ]
]

== Paste information about ports or interfaces that belong to each VLAN.

#framed[
  根据接口信息输出可以看到，GE 0/0/9 ~ 0/0/12 为 Access 接口并默认划入 VLAN 10；GE 0/0/13 ~ 0/0/16 为 Access 接口并默认划入 VLAN 30。而我们配置的基于 MAC 和 IP 子网划分的接口（包括 0/0/5 ~ 0/0/8）则均为 Hybrid 接口，其 PVID 为 1，依靠动态识别规则分配 VLAN 标签。

  #align(center)[
    #image("attachments/2-3-7.png", width: 80%) // 请替换为 display port vlan 的截图
  ]
]

= 802.1Q TRUNK CONFIGURATION

== Paste the screenshot of the created topology.

#framed[
  #align(center)[
    #image("attachments/2-4-1.png", width: 80%) // 请将拓扑图截图重命名为 2-4-1.png
  ]
]

== Can PC-10-1 and PC-10-3 ping each other? Please paste the screenshot of the ping result.

#framed[
  可以相互 Ping 通。
  虽然两台 PC 连接在不同的交换机上，但它们同属于 VLAN 10，并且两台交换机之间配置了 Trunk 链路且允许 VLAN 10 的数据帧通过，因此实现了跨交换机的同 VLAN 通信。

  #align(center)[
    #image("attachments/2-4-2.png", width: 70%) // 请替换为 PC-10-1 ping 10.13 成功的截图
  ]
]

== Can PC-30-1 and PC-30-3 ping each other? Please paste the screenshot of the ping result.

#framed[
  可以相互 Ping 通。
  同理，PC-30-1 和 PC-30-3 同属于 VLAN 30，Trunk 链路允许 VLAN 30 的数据帧跨交换机传输。

  #align(center)[
    #image("attachments/2-4-3.png", width: 70%) // 请替换为 PC-30-1 ping 30.13 成功的截图
  ]
]

== Can PC-10-1 and PC-30-3 ping each other? Please paste the screenshot of the ping result.

#framed[
  不能互相 Ping 通。
  即使跨越了交换机，不同 VLAN 之间依然属于不同的二层广播域。由于没有路由设备的介入，二层网络默认相互隔离，因此 Ping 失败（Destination host unreachable）。

  #align(center)[
    #image("attachments/2-4-4.png", width: 70%) // 请替换为 PC-10-1 ping 30.13 失败的截图
  ]
]

== Are the Ethernet frames captured on interface GE 0/0/24 on switch LSW1 tagged or untagged frames? If they are tagged frames, what are the VLAN IDs? Please paste the screenshot of all field information of two captured Ethernet frames with different VLAN IDs.

#framed[
  在 LSW1 的 GE 0/0/24 接口（Trunk 链路）上捕获的以太网帧是 *带有标签的（Tagged frames）*。
  
  捕获到的以太网帧中包含 802.1Q Virtual LAN 字段，其 VLAN IDs 分别为 *10* 和 *30*。这是因为 Trunk 端口在转发非 PVID（默认 VLAN 1）的数据帧时，必须保留其 VLAN 标签，以便对端交换机能够正确区分数据流所属的 VLAN。

  *VLAN ID 为 10 的数据帧抓包详情：*
  #align(center)[
    #image("attachments/2-4-5-1.png", width: 80%) // 请替换为显示 ID: 10 的 Wireshark 截图
  ]

  *VLAN ID 为 30 的数据帧抓包详情：*
  #align(center)[
    #image("attachments/2-4-5-2.png", width: 80%) // 请替换为显示 ID: 30 的 Wireshark 截图
  ]
]

== Are the Ethernet frames captured on interface GE 0/0/9 on switch LSW1 tagged or untagged frames? If they are tagged frames, what are the VLAN IDs? Please paste the screenshot of all field information of a captured Ethernet frame.

#framed[
  在 LSW1 的 GE 0/0/9 接口（Access 链路）上捕获的以太网帧是 *无标签的（Untagged frames）*。

  从抓包信息中可以看出，在 `Ethernet II` 头部之后直接是 `Internet Protocol Version 4`（IPv4）头部，*并没有 802.1Q 标签字段*。这是因为 Access 端口连接的是普通终端（PC），PC 无法识别带有 VLAN 标签的数据帧。因此，交换机在将数据帧从 Access 端口发送给 PC 前，会自动剥离（Untag）其 VLAN 标签。

  #align(center)[
    #image("attachments/2-4-6.png", width: 80%) // 请替换为 GE 0/0/9 接口剥离标签后的 Wireshark 截图
  ]
]