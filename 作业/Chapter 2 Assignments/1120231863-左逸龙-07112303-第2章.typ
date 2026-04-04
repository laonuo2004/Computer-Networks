#import "../problemst/pset.typ": pset, framed

#show: pset.with(
  class: "07112303",
  student: "左逸龙",
  title: "计算机网络第2章作业",
  date: datetime.today()
)

= A noiseless 4-kHz channel is sampled every 1 msec. What is the maximum data rate? How does the maximum data rate change if the channel is noisy, with a signal-to-noise ratio of 30 dB?

#framed[
]

= Show the NRZ, NRZI, Manchester, and Differential Manchester encodings for the bit pattern shown in @fig:encoding-pattern. Assuming that the 0 in Manchester encoding is encoded as a high-to-low transition and 1 being encoded as a low-to-high transition, and that the signals of NRZI and Differential Manchester start out low.

#figure(
  image("attachments/Figure2.png", width: 85%)
)<fig:encoding-pattern>

#framed[
]

= What are the disadvantages of Manchester Encoding?

#framed[
]

= A total of four stations perform code division multiple access CDMA communication. The chip sequences of the four stations are:

A: `(-1 -1 -1 +1 +1 -1 +1 +1)`

B: `(-1 -1 +1 -1 +1 +1 +1 -1)`

C: `(-1 +1 -1 +1 +1 +1 -1 -1)`

D: `(-1 +1 -1 -1 -1 +1 +1 -1)`

Station X now receives such a chip sequence: `(-1 +1 -3 +1 -1 -3 +1 +1)`. Which stations transmitted, and which bits did each one send?

#framed[
]
