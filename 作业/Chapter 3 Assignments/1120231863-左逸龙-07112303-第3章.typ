#import "../problemst/pset.typ": pset, framed

#show: pset.with(
  class: "07112303",
  student: "左逸龙",
  title: "计算机网络第3章作业",
  date: datetime.today()
)

= A bit stream 10011101 is transmitted using the standard CRC method described in the text. The generator polynomial is $x^3 + 1$. Show the actual bit string transmitted. Suppose that the third bit from the left is inverted during transmission. Show that this error is detected at the receiver's end. Give an example of bit errors in the bit string transmitted that will not be detected by the receiver.

#framed[
  $G(x)=x^3+1$，所以 $G=1001$，校验位为 $3$ 位。

  原数据后补 $3$ 个 $0$，得到 $10011101000$。
  
  由于模 $2$ 除以 $1001$，余数为 $100$，故实际发送串为 $10011101100$。

  若第 $3$ 位出错，则接收串为 $10111101100$

  再除以 $1001$，由于余数为 $100 != 000$，所以能检测出错。

  不能检测的错误可取错误模式 $00000001001$，它能被 $1001$ 整除。
  
  此时接收串为 $10011100101$，余数为 $000$，故检测不出。
]

= A channel has a bit rate of 4 kbps and a propagation delay of 20 msec. For what range of frame sizes does stop-and-wait give an efficiency of at least 50 percent?

#framed[
  设帧长为 $L$ bit，则发送时间为 $L / 4000$ s。

  忽略 ACK 发送时间，停等协议效率为：
  $eta = (L / 4000) / (L / 4000 + 2 times 0.02)$

  由于要求 $eta >= 0.5$，则
  $(L / 4000) / (L / 4000 + 0.04) >= 1 / 2$

  解得 $L >= 160$ bit。

  故帧长范围为 $L >= 160$ bit。
]

= Suppose you are designing a sliding window protocol for a 1-Mbps point-to-point link to the stationary satellite evolving around the Earth at $3 times 10^4$ km altitude. Assuming that each frame carries 1 kB of data, what is the minimum number of bits you need for the sequence number in the following cases? Assume the speed of light is $3 times 10^8$ meters per second.
(a) Receive Window Size = 1.

#framed[
  传播时延为
  $T_p = (3 times 10^4 times 10^3) / (3 times 10^8) = 0.1$ s。

  一帧大小为 $1 k B = 8 times 10^3$ bit，发送时间为
  $T_f = (8 times 10^3) / (10^6) = 0.008$ s。

  为了连续发送，需要
  $S W S >= (T_f + 2 T_p) / T_f = (0.008 + 0.2) / 0.008 = 26$

  由于 $R W S=1$，则序号空间至少为
  $S W S + 1 = 27$

  又因为 $2^4 < 27 <= 2^5$，故至少需要 $5$ bit 序号。
]

(b) Receive Window Size = Send Window Size.

#framed[
  由上题可得 $S W S=26$。

  由于 $R W S=S W S$，则序号空间至少为
  $S W S + R W S = 26 + 26 = 52$

  又因为 $2^5 < 52 <= 2^6$，故至少需要 $6$ bit 序号。
]

= Suppose that we run the sliding window algorithm with SWS = 5 and RWS = 3, and no out-of-order arrivals.
(a) Find the smallest value for MaxSeqNum. You may assume that it suffices to find the smallest MaxSeqNum such that if DATA[MaxSeqNum] is in the receive window, then DATA[0] can no longer arrive.

#framed[
  由于 $S W S=5, R W S=3$，则序号空间至少应满足
  $M a x S e q N u m >= S W S + R W S = 5 + 3 = 8$

  故最小的 $M a x S e q N u m$ 为 $8$。
]

(b) Give an example showing that MaxSeqNum - 1 is not sufficient.

#framed[
  若取 $M a x S e q N u m=7$，序号为 $0,1,...,6$。

  发送方开始可发送 $D A T A[0]$ 到 $D A T A[4]$。

  若接收方依次收到 $D A T A[0]$ 到 $D A T A[4]$，则接收窗口变为 $D A T A[5], D A T A[6], D A T A[7]$。

  由于 $D A T A[7]$ 的序号又是 $0$，而此时旧的 $D A T A[0]$ 仍可能由于重传而到达，则接收方会把旧的 $D A T A[0]$ 当成 $D A T A[7]$。

  因此 $M a x S e q N u m=7$ 不够。
]

(c) State a general rule for the minimum MaxSeqNum in terms of SWS and RWS.

#framed[
  一般应有
  $M a x S e q N u m >= S W S + R W S$

  即最小值为
  $M a x S e q N u m = S W S + R W S$。
]
