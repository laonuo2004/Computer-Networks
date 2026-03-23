#import "../problemst/pset.typ": pset, framed

#show: pset.with(
  class: "07112303",
  student: "左逸龙",
  title: "计算机网络 第1章作业",
  date: datetime.today()
)

= Calculate the total time required to transfer a 1000-kB file in the following cases, assuming an RTT of 100 ms, a packet size of 1 kB data, and an initial $2 times "RTT"$ of "handshaking" before data are sent.

== The bandwidth is 1.5 Mbps, and data packets can be sent continuously.

#framed[
  按 $1 "KB" = 8192 "bits"$ 算，单个包传输时间 $t_p = 8192 / (1.5 times 10^6) approx 5.46 "ms"$。

  由于包连续发送，整个文件共有 1000 个包，总传输时间为 $1000 times t_p = 5.46 "s"$。

  最后一个 bit 发出后，还需经过单向传播延迟 $"RTT" / 2 = 50 "ms"$ 才能到达接收方。

  总耗时 = 初始握手时间 + 传输时间 + 传播延迟：

  $T = 2 "RTT" + 5.46 "s" + "RTT" / 2 = 0.2 "s" + 5.46 "s" + 0.05 "s" = 5.71 "s"$
]

== The bandwidth is 1.5 Mbps, but after we finish sending each data packet, we must wait one RTT before sending the next.

#framed[
  发送完每个包都要等 $1 "RTT"$，1000 个包需要等 999 次。

  最后一个包发送完成后，还需经过单向传播延迟 $"RTT" / 2 = 50 "ms"$ 才能到达接收方。

  总耗时 = 握手时间 + 所有包的传输时间 + 999 次等待时间 + 传播延迟：

  $T = 0.2 "s" + (1000 times 5.46 "ms") + (999 times 100 "ms") + 0.05 "s" = 105.61 "s"$
]

== The bandwidth is "infinite," meaning that we take transmit time to be zero, and up to 20 packets can be sent per RTT.

#framed[
  带宽无限大说明传输时间忽略不计（$t_p = 0$）。

  每 RTT 发送 20 个包，1000 个包需要 $1000 / 20 = 50$ 批，即 $50 "RTT"$ 发完。

  总耗时 = 握手时间 + 发送时间：

  $T = 2 "RTT" + 50 "RTT" = 52 "RTT" = 5.2 "s"$
]

== The bandwidth is infinite, and during the first RTT, we can send one packet ($2^1 - 1$), during the second RTT we can send two packets ($2^2 - 1$), during the third we can send four ($2^3 - 1$), and so on.

#framed[
  第 $n$ 个 RTT 发送 $2^(n-1)$ 个包，前 $n$ 个 RTT 累计发送了 $2^n - 1$ 个。

  令 $2^n - 1 >= 1000$，解得最小的 $n = 10$，说明需要 $10 "RTT"$ 才能发完 1000 个包。

  总耗时 = 握手时间 + 发送时间：
  
  $T = 2 "RTT" + 10 "RTT" = 12 "RTT" = 1.2 "s"$
]

= This elementary problem begins to explore propagation delay and transmission delay, two central concepts in data networking. Consider two hosts, A and B, connected by a single link of rate $R$ bps. Suppose that the two hosts are separated by $m$ meters, and suppose the propagation speed along the link is $s$ meters/sec. Host A is to send a packet of size $L$ bits to Host B.

== Express the propagation delay, $d_"prop"$, in terms of $m$ and $s$.

#framed[
  $d_"prop" = m / s$
]

== Determine the transmission time of the packet, $d_"trans"$, in terms of $L$ and $R$.

#framed[
  $d_"trans" = L / R$
]

== Ignoring processing and queuing delays, obtain an expression for the end-to-end delay.

#framed[
  $d_"end-to-end" = d_"trans" + d_"prop" = L / R + m / s$
]

== Suppose Host A begins to transmit the packet at time $t=0$. At time $t=d_"trans"$, where is the last bit of the packet?

#framed[
  刚好离开主机 A（刚刚被推上链路）。
]

== Suppose $d_"prop"$ is greater than $d_"trans"$. At time $t=d_"trans"$, where is the first bit of the packet?

#framed[
  还在链路上，尚未到达主机 B。
  
  它距离主机 A 的位置是 $s times d_"trans"$ 米。
]

== Suppose $d_"prop"$ is less than $d_"trans"$. At time $t=d_"trans"$, where is the first bit of the packet?

#framed[
  第一个 bit 已经到达主机 B 了。
]

== Suppose $s=2.5 times 10^8$, $L=120$ bits, and $R=56$ kbps. Find the distance $m$ so that $d_"prop"$ equals $d_"trans"$.

#framed[
  令 $d_"prop" = d_"trans"$，即 $m / s = L / R$。
  
  代入数据得 $m = s times (L / R) = (2.5 times 10^8) times (120 / 56000)$。
  
  算得 $m approx 535714 "m"$（约 $535.7 "km"$）。
]

#pagebreak()

= Compare the delay in sending an $x$-bit message over a $k$-hop path in a circuit-switched network and in a (lightly loaded) packet-switched network. The circuit setup time is $s$ sec, the propagation delay is $d$ sec per hop, the packet size is $p$ bits, and the data rate is $b$ bps. Under what conditions does the packet network have a lower delay?

#framed[
  电路交换总延迟：$t_"cs" = s + x/b + k d$
  
  分组交换总延迟：源端发完所有包需 $x/b$，最后一个包经 $k-1$ 跳到达目的端，共需 $(k-1) p/b$，加总传播延迟 $k d$。
  
  即分组交换延迟为 $t_"ps" = x/b + (k-1) p/b + k d$
  
  要使分组交换更低，令 $t_"ps" < t_"cs"$：
  
  $x/b + (k-1) p/b + k d < s + x/b + k d$
  
  化简得条件为：$s > (k-1) p / b$
]

= A system has an $n$-layer protocol hierarchy. Applications generate messages of length $M$ bytes. At each of the layers, an $h$-byte header is added. What fraction of the network bandwidth is filled with headers?

#framed[
  报文初始长度为 $M$ 字节，共 $n$ 层协议，每层加 $h$ 字节头部。
  
  总头部长度为 $n h$ 字节，最终发送的总长度为 $M + n h$ 字节。
  
  头部占据的带宽比例为：$(n h) / (M + n h)$
]

= What are two reasons for using layered protocols? What is one possible disadvantage of using layered protocols?

#framed[
  原因：
  1. 结构清晰，便于模块化设计与维护（每层独立完成相应功能，降低整体复杂性）。
  2. 灵活性好，某一层协议或技术发生改变时，只要接口不变，就不会影响其他层。
  
  缺点：
  会带来额外的数据开销（每层都要加头部，浪费部分网络带宽）和处理延迟，且层与层间信息隔离有时会导致通信效率下降。
]
