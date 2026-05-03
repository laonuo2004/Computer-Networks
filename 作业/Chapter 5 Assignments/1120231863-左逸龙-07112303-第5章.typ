#import "../problemst/pset.typ": pset, framed

#show: pset.with(
  class: "07112303",
  student: "左逸龙",
  title: "计算机网络第5章作业",
  date: datetime.today()
)

= Explain the difference between routing, forwarding, and switching.

#framed[
  - routing 指根据网络拓扑和路由算法，计算到目的网络的路径，并生成路由表，偏向于路径计算。

  - forwarding 指路由器收到一个分组后，根据转发表查找下一跳或输出端口，并把分组转发出去，偏向于单个分组的实际转发。

  - switching 一般指网络设备内部将分组/帧从输入端口转移到输出端口的过程；在链路层交换机中，通常表现为根据 MAC 地址表选择合适端口转发帧。
]

= For the network given in @fig:network, give global distance-vector tables like @tab:dv-table (where D is the distance, N is neighbor) when

#figure(image("attachments/fig5-1.png", width: 40%), caption: [A graph of a network]) <fig:network>

#figure(image("attachments/tab5-1.png", width: 80%), caption: [Global Distance-Vector table]) <tab:dv-table>

== Each node knows only the distances to its immediate neighbors.

#framed[
  #align(center)[
    #pad(x: 10%, [
      #table(
        columns: 13 * (1fr,),
        align: center,
        table.header(
          table.cell(rowspan: 3)[Node],
          table.cell(colspan: 12)[Distances and neighbors to reach node],
          table.cell(colspan: 2)[A],
          table.cell(colspan: 2)[B],
          table.cell(colspan: 2)[C],
          table.cell(colspan: 2)[D],
          table.cell(colspan: 2)[E],
          table.cell(colspan: 2)[F],
          [D], [N], [D], [N], [D], [N], [D], [N], [D], [N], [D], [N],
        ),
        [A], [0], [-], [2], [B], [$infinity$], [-], [5], [D], [$infinity$], [-], [$infinity$], [-],
        [B], [2], [A], [0], [-], [2], [C], [$infinity$], [-], [1], [E], [$infinity$], [-],
        [C], [$infinity$], [-], [2], [B], [0], [-], [2], [D], [$infinity$], [-], [3], [F],
        [D], [5], [A], [$infinity$], [-], [2], [C], [0], [-], [$infinity$], [-], [$infinity$], [-],
        [E], [$infinity$], [-], [1], [B], [$infinity$], [-], [$infinity$], [-], [0], [-], [3], [F],
        [F], [$infinity$], [-], [$infinity$], [-], [3], [C], [$infinity$], [-], [3], [E], [0], [-],
      )
    ])
  ]
]

== Each node has reported the information it had in the preceding step to its immediate neighbors.

#framed[
  #align(center)[
    #pad(x: 10%, [
      #table(
        columns: 13 * (1fr,),
        align: center,
        table.header(
          table.cell(rowspan: 3)[Node],
          table.cell(colspan: 12)[Distances and neighbors to reach node],
          table.cell(colspan: 2)[A],
          table.cell(colspan: 2)[B],
          table.cell(colspan: 2)[C],
          table.cell(colspan: 2)[D],
          table.cell(colspan: 2)[E],
          table.cell(colspan: 2)[F],
          [D], [N], [D], [N], [D], [N], [D], [N], [D], [N], [D], [N],
        ),
        [A], [0], [-], [2], [B], [4], [B], [5], [D], [3], [B], [$infinity$], [-],
        [B], [2], [A], [0], [-], [2], [C], [4], [C], [1], [E], [4], [E],
        [C], [4], [B], [2], [B], [0], [-], [2], [D], [3], [B], [3], [F],
        [D], [5], [A], [4], [C], [2], [C], [0], [-], [$infinity$], [-], [5], [C],
        [E], [3], [B], [1], [B], [3], [B], [$infinity$], [-], [0], [-], [3], [F],
        [F], [$infinity$], [-], [4], [E], [3], [C], [5], [C], [3], [E], [0], [-],
      )    
    ])
  ]
]

== Step (b) happens a second time.

#framed[
  #align(center)[
    #pad(x: 10%, [
      #table(
        columns: 13 * (1fr,),
        align: center,
        table.header(
          table.cell(rowspan: 3)[Node],
          table.cell(colspan: 12)[Distances and neighbors to reach node],
          table.cell(colspan: 2)[A],
          table.cell(colspan: 2)[B],
          table.cell(colspan: 2)[C],
          table.cell(colspan: 2)[D],
          table.cell(colspan: 2)[E],
          table.cell(colspan: 2)[F],
          [D], [N], [D], [N], [D], [N], [D], [N], [D], [N], [D], [N],
        ),
        [A], [0], [-], [2], [B], [4], [B], [5], [D], [3], [B], [6], [B],
        [B], [2], [A], [0], [-], [2], [C], [4], [C], [1], [E], [4], [E],
        [C], [4], [B], [2], [B], [0], [-], [2], [D], [3], [B], [3], [F],
        [D], [5], [A], [4], [C], [2], [C], [0], [-], [5], [C], [5], [C],
        [E], [3], [B], [1], [B], [3], [B], [5], [B], [0], [-], [3], [F],
        [F], [6], [E], [4], [E], [3], [C], [5], [C], [3], [E], [0], [-],
      )
    ])
  ]
]

= Suppose we have the forwarding tables shown in @tab:forwarding for nodes A and F in a network where all links have cost 1. Give a diagram of the smallest network consistent with these tables.

#figure(image("attachments/tab5-2.png", width: 70%), caption: [Forwarding table]) <tab:forwarding>

#framed[
  #align(center)[
    #image("attachments/problem3-network.svg", width: 80%)
  ]
]

= An unfragmented IP packet, shown in @fig:fragmentation(a), has 1400 bytes of data and a 20-byte IP header. When the packet arrives at router RA, which has an MTU of 532 bytes, it has to be fragmented. The 3 fragmented packets are shown in @fig:fragmentation(b). Suppose these fragments all pass through another router RB with an MTU of 380 bytes, not counting the link header.

#figure(image("attachments/fig5-2.png", width: 90%), caption: [(a) One unfragmented packet, (b) Three fragmented packets]) <fig:fragmentation>

== Show the fragments the router RB produced.

#framed[
  RB 的 MTU 为 $380$ 字节，去掉 $20$ 字节 IP 首部后，每个分片最多有 $360$ 字节数据。

  由于 $360$ 是 $8$ 的整数倍，所以可以作为非最后分片的数据长度。

  #align(center)[
    #table(
      columns: 4,
      align: center,
      table.header([原分片], [数据长度], [MF], [Offset]),
      [1], [$360$], [$1$], [$0$],
      [1], [$152$], [$1$], [$45$],
      [2], [$360$], [$1$], [$64$],
      [2], [$152$], [$1$], [$109$],
      [3], [$360$], [$1$], [$128$],
      [3], [$16$], [$0$], [$173$],
    )
  ]

  因此 RB 共生成 $6$ 个分片。
]

== If the packet were originally fragmented for this MTU, how many fragments would be produced?

#framed[
  若一开始就按 $380$ 字节 MTU 分片，则每片最多仍是 $360$ 字节数据。

  原数据长度为 $1400$ 字节：
  $1400 = 360 times 3 + 320$

  所以会产生 $4$ 个分片，数据长度分别为 $360,360,360,320$ 字节。

  对应 offset 为 $0,45,90,135$。
]

= What is the maximum bandwidth at which an IP host can send 576-byte packets without having the Ident field wrap around within 60 seconds? Suppose that IP’s maximum segment lifetime (MSL) is 60 seconds; that is, delayed packets can arrive up to 60 seconds late but no later. What might happen if this bandwidth were exceeded?

#framed[
  IP 的 Ident 字段为 $16$ bit，因此共有 $2^16 = 65536$ 个取值。

  为了不在 $60$ 秒内回绕，最多只能发送 $65536$ 个分组。

  每个分组大小为 $576$ 字节，即 $576 times 8 = 4608$ bit。

  所以最大带宽为
  $R = (65536 times 4608) / 60 approx 5.03 times 10^6 "bps"$

  即约为 $5.03 "Mbps"$。

  如果超过这个带宽，Ident 字段可能在旧分组仍可能到达时重复使用，接收方可能把不同 IP 分组的分片错误地重组在一起。
]

= An organization has been assigned the prefix 200.1.1.0/24 and wants to form subnets for four departments, with hosts as follows:

Department A 72 hosts,

Department B 35 hosts,

Department C 20 hosts,

Department D 18 hosts.

*There are 145 hosts in all.*

== Give a possible arrangement of subnet masks to make this possible.

#framed[
  按主机数从大到小分配。

  A 需要 $72$ 个主机地址，所以至少要 $7$ 位主机号，即 /25。

  B 需要 $35$ 个主机地址，所以至少要 $6$ 位主机号，即 /26。

  C、D 分别需要 $20$ 和 $18$ 个主机地址，所以都至少要 $5$ 位主机号，即 /27。

  #align(center)[
    #table(
      columns: 5,
      align: center,
      table.header([部门], [主机数], [子网], [子网掩码], [可用主机范围]),
      [A], [$72$], [200.1.1.0/25], [255.255.255.128], [200.1.1.1 - 200.1.1.126],
      [B], [$35$], [200.1.1.128/26], [255.255.255.192], [200.1.1.129 - 200.1.1.190],
      [C], [$20$], [200.1.1.192/27], [255.255.255.224], [200.1.1.193 - 200.1.1.222],
      [D], [$18$], [200.1.1.224/27], [255.255.255.224], [200.1.1.225 - 200.1.1.254],
    )
  ]

  这样可以刚好用完整个 200.1.1.0/24 地址块。
]

== Suggest what the organization might do if department D grows to 34 hosts.

#framed[
  若 D 增长到 $34$ 台主机，则 /27 不够，因为 /27 只有 $2^5 - 2 = 30$ 个可用主机地址。

  此时 D 至少需要 /26，即 $62$ 个可用主机地址。

  但原来的 /24 已经被 A、B、C、D 四个子网刚好用完，无法直接扩大 D。

  因此组织可以申请更大的地址块，例如 /23，或者再申请一个额外的地址块给 D 使用。
]

= A router has just received the following new IP addresses: 57.6.96.0/21, 57.6.104.0/21, 57.6.112.0/21, and 57.6.120.0/21. If all of them use the same outgoing line, can they be aggregated? If so, to what? If not, why not?

#framed[
  可以聚合。

  这四个地址块分别覆盖：

  - 57.6.96.0/21：57.6.96.0 到 57.6.103.255

  - 57.6.104.0/21：57.6.104.0 到 57.6.111.255

  - 57.6.112.0/21：57.6.112.0 到 57.6.119.255

  - 57.6.120.0/21：57.6.120.0 到 57.6.127.255

  合起来正好是 57.6.96.0 到 57.6.127.255。

  第三个字节从 $96$ 到 $127$，二进制公共前缀为 $011$，所以前缀长度为 $16 + 3 = 19$。

  因此可聚合为 57.6.96.0/19。
]

= Given the network in @fig:aggregation, determine the routing table of R2 by aggregating the routes. The main entries of the routing table are shown in @tab:routing-table.

#figure(image("attachments/fig5-3.png", width: 50%), caption: [A network]) <fig:aggregation>
#figure(image("attachments/tab5-3.png", width: 90%), caption: [Routing Table]) <tab:routing-table>

#framed[
  R1 后面的两个网段 211.14.5.0/25 和 211.14.5.128/25 可以聚合为 211.14.5.0/24。

  R3 方向的 196.17.20.0/25 和 196.17.21.0/24 可以和 196.17.20.128/25 所在范围一起概括为 196.17.20.0/23。

  #align(center)[
    #pad(x: 10%, [
      #table(
        columns: 5 * (1fr,),
        align: center,
        table.header([Destination], [Mask], [Next-hop], [Interface], [Metric]),
        [211.14.5.0], [255.255.255.0], [211.14.3.2], [S0], [1],
        [196.17.20.0], [255.255.254.0], [196.17.24.2], [S1], [1],
      )
    ])
  ]

  其中 R2 的直连网络仍按直连路由匹配，实际转发时采用最长前缀匹配。
]
