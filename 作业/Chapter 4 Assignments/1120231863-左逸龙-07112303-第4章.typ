#import "../problemst/pset.typ": pset, framed

#show: pset.with(
  class: "07112303",
  student: "左逸龙",
  title: "计算机网络第4章作业",
  date: datetime.today()
)

= Consider building a CSMA/CD network running at $1 "Gbps"$ over a $1 "km"$ cable with no repeaters. The signal speed in the cable is $200000 "km/sec"$. What is the minimum frame size?

#framed[
  单程传播时延为
  $T_p = (1 "km") / (200000 "km/sec") = 5 times 10^(-6) "s" = 5 "μs"$。

  对于 CSMA/CD，为了能检测到最远端的碰撞，帧发送时间至少应为 $2 T_p$。

  因此最小帧长为
  $L = 1 times 10^9 times 2 times 5 times 10^(-6) = 10000 "bit" = 1250 "B"$。
]

= Let A and B be two stations attempting to transmit on an Ethernet. Each has a steady queue of frames ready to send; A's frames will be numbered A1, A2, and so on, and B's similarly. Let $T = 51.2 "μs"$ be the exponential backoff base unit. Suppose A and B simultaneously attempt to send frame 1, collide, and happen to choose backoff times of $0 times T$ and $1 times T$, respectively, meaning A wins the race and transmits A1 while B waits. At the end of this transmission, B will attempt to retransmit B1 while A will attempt to transmit A2. These first attempts will collide, but now A backs off for either $0 times T$ or $1 times T$, while B backs off for time equal to one of $0 times T, ..., 3 times T$.

(a) Give the probability that A wins this second backoff race immediately after this first collision; that is, A's first choice of backoff time $k times 51.2$ is less than B's.

#framed[
  此时 A 是第 $1$ 次碰撞后退避，所以 A 可取 $0,1$。

  B 的 B1 已经第 $2$ 次碰撞，所以 B 可取 $0,1,2,3$。

  共有 $2 times 4 = 8$ 种等可能情况。

  A 赢要求 $k_A < k_B$，满足的情况有：

  - $k_A=0$ 时，$k_B=1,2,3$，共 $3$ 种；
  - $k_A=1$ 时，$k_B=2,3$，共 $2$ 种。

  因此概率为
  $P = (3 + 2) / 8 = 5 / 8$。
]

(b) Suppose A wins this second backoff race. A transmits A3, and when it is finished, A and B collide again as A tries to transmit A4 and B tries once more to transmit B1. Give the probability that A wins this third backoff race immediately after the first collision.

#framed[
  此时 A 的新帧仍是第 $1$ 次碰撞后退避，所以 A 可取 $0,1$。

  B 的 B1 已经第 $3$ 次碰撞，所以 B 可取 $0,1,...,7$。

  共有 $2 times 8 = 16$ 种等可能情况。

  A 赢要求 $k_A < k_B$：

  - $k_A=0$ 时，$k_B=1,2,...,7$，共 $7$ 种；
  - $k_A=1$ 时，$k_B=2,3,...,7$，共 $6$ 种。

  因此概率为
  $P = (7 + 6) / 16 = 13 / 16$。
]

= Consider the extended LAN connected using bridges B1 and B2 in Fig. 4-1. Suppose the MAC tables in the two bridges are empty. Give the MAC tables for each of the bridges after the following transmissions:

#figure(
  image("attachments/fig-4-1.png", width: 45%)
)<fig:4-1>

(a) A sends to C.

#framed[
  A 从 B1 的端口 $1$ 进入，所以 B1 学到 $A -> 1$。

  B1 不知道 C 的位置，会泛洪到端口 $2,3,4$。B2 从端口 $4$ 收到该帧，所以 B2 学到 $A -> 4$。

  此时表项为：

  - B1：$A -> 1$
  - B2：$A -> 4$

]

(b) E sends to F.

#framed[
  E 通过 Hub 到达 B2 的端口 $2$，所以 B2 学到 $E -> 2$。

  B2 不知道 F 的位置，会泛洪到端口 $1,3,4$。B1 从端口 $4$ 收到该帧，所以 B1 学到 $E -> 4$。

  此时表项为：

  - B1：$A -> 1, E -> 4$
  - B2：$A -> 4, E -> 2$

]

(c) F sends to E.

#framed[
  F 通过 Hub 到达 B2 的端口 $2$，所以 B2 学到 $F -> 2$。

  由于 E 也在端口 $2$，B2 不再向其他端口转发。

  此时表项为：

  - B1：$A -> 1, E -> 4$
  - B2：$A -> 4, E -> 2, F -> 2$

]

(d) G sends to E.

#framed[
  G 从 B2 的端口 $3$ 进入，所以 B2 学到 $G -> 3$。

  E 已知在端口 $2$，因此 B2 只向端口 $2$ 转发。

  此时表项为：

  - B1：$A -> 1, E -> 4$
  - B2：$A -> 4, E -> 2, F -> 2, G -> 3$

]

(e) D sends to A.

#framed[
  D 从 B2 的端口 $1$ 进入，所以 B2 学到 $D -> 1$。

  A 已知在 B2 的端口 $4$，该帧转发给 B1。B1 从端口 $4$ 收到该帧，所以 B1 学到 $D -> 4$。

  此时表项为：

  - B1：$A -> 1, E -> 4, D -> 4$
  - B2：$A -> 4, E -> 2, F -> 2, G -> 3, D -> 1$

]

(f) B sends to F.

#framed[
  B 从 B1 的端口 $2$ 进入，所以 B1 学到 $B -> 2$。

  B1 还不知道 F 的位置，所以会泛洪到端口 $1,3,4$。B2 从端口 $4$ 收到该帧，所以 B2 学到 $B -> 4$。

  F 已知在 B2 的端口 $2$，因此 B2 只向端口 $2$ 转发。

  此时表项为：

  - B1：$A -> 1, E -> 4, D -> 4, B -> 2$
  - B2：$A -> 4, E -> 2, F -> 2, G -> 3, D -> 1, B -> 4$

]

= Why is collision detection more complex in wireless networks than in wired networks such as Ethernet and how can hidden terminals be detected in 802.11 networks?

#framed[
  无线网络中，节点发送时自己的信号很强，很难同时监听到其他节点较弱的信号，所以不像有线 Ethernet 那样容易边发送边检测碰撞。

  另外无线信号有覆盖范围限制，两个发送方可能彼此听不到，但都会影响同一个接收方，这就是隐藏终端问题。

  在 802.11 中，可以通过 RTS/CTS 机制发现或避免隐藏终端。发送方先发 RTS，接收方回复 CTS，其他听到 CTS 的节点就知道该接收方即将接收数据，于是暂时保持静默。
]
