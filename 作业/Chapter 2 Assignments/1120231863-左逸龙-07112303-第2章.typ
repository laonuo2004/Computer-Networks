#import "../problemst/pset.typ": pset, framed

#show: pset.with(
  class: "07112303",
  student: "左逸龙",
  title: "计算机网络第2章作业",
  date: datetime.today()
)

= A noiseless 4-kHz channel is sampled every 1 msec. What is the maximum data rate? How does the maximum data rate change if the channel is noisy, with a signal-to-noise ratio of 30 dB?

#framed[
  由题意，信道每 $1 "ms"$ 采样一次，即采样率 $f_s = 1 / (1 "ms") = 1000 "Hz"$。
  根据数据率公式 $R = f_s log_2 V$，
  由于信道无噪声，信号电平数 $V$ 理论上可无限增大，
  所以最大数据率理论上无上限。

  若信道有噪声且信噪比为 $30 "dB"$，则
  $10 log_10(S/N) = 30$，
  得 $S/N = 1000$。

  由 Shannon 公式，最大数据率为：
  $R = H log_2(1 + S/N) = 4000 times log_2(1001) approx 39868 "bps"$

  即约 $39.9 "kbps"$。
]

= Show the NRZ, NRZI, Manchester, and Differential Manchester encodings for the bit pattern shown in @fig:encoding-pattern. Assuming that the 0 in Manchester encoding is encoded as a high-to-low transition and 1 being encoded as a low-to-high transition, and that the signals of NRZI and Differential Manchester start out low.

#framed[
  #figure(
  image("attachments/line_encoding.svg", width: 85%)
  )<fig:encoding-pattern>
]

= What are the disadvantages of Manchester Encoding?

#framed[
  曼彻斯特编码的主要缺点在于带宽利用率低（只有 $50%$ 左右）。

  因为每比特时间内至少有一次跳变，这导致它的波特率会达到 NRZ 的两倍，因此要达到相同比特率所需要的带宽也会更宽一些。
]

= A total of four stations perform code division multiple access CDMA communication. The chip sequences of the four stations are:

A: `(-1 -1 -1 +1 +1 -1 +1 +1)`

B: `(-1 -1 +1 -1 +1 +1 +1 -1)`

C: `(-1 +1 -1 +1 +1 +1 -1 -1)`

D: `(-1 +1 -1 -1 -1 -1 +1 -1)`

Station X now receives such a chip sequence: `(-1 +1 -3 +1 -1 -3 +1 +1)`. Which stations transmitted, and which bits did each one send?

#framed[
  A：$A dot S = (1 - 1 + 3 + 1 - 1 + 3 + 1 + 1) / 8 = 1$，说明 A 站发送了比特 1。

  B：$B dot S = (1 - 1 - 3 - 1 - 1 - 3 + 1 - 1) / 8 = -1$，说明 B 站发送了比特 0。

  C：$C dot S = (1 + 1 + 3 + 1 - 1 - 3 - 1 - 1) / 8 = 0$，说明 C 站未发送数据。

  D：$D dot S = (1 + 1 + 3 - 1 + 1 + 3 + 1 - 1) / 8 = 1$，说明 D 站发送了比特 1。

  综上所述，A、B、D 站进行了发送，其中 A、D 站发送了比特 1，B 站发送了比特 0。
]
