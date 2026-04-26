#import "../problemst/pset.typ": pset, framed

#show: pset.with(
  class: "07112303",
  student: "左逸龙",
  lab_number: 1,
  title: "Lab-1 (3) STP Configuration and Verification(E)",
  date: datetime.today()
)

= BROADCAT STORM AND MAC ADDRESS TABLE INSTABILITY ANALYSIS

== Paste the screenshot of the created topology.

#framed[
  // 用于填写我的回答
]

== Have you observed broadcast storm in Wireshark? What is the phenomenon of broadcast storm? Please paste the screenshot of the broadcast storm communications in Wireshark and mark the broadcast storm communications in it.

#framed[
  // 用于填写我的回答
]

== Wait for a while, then view the log information output by the switch LSW1 and LSW2 in the configuration window. Are the CPUs of LSW1 and LSW2 overloaded? What are the CPU usages of the two switches?

#framed[
  // 用于填写我的回答
]

== Which MAC address is reported being flapping on the switch LSW1? On which ports does the MAC address flap? Paste the screenshot of the report in the log.

#framed[
  // 用于填写我的回答
]


= STP CONFIGURATION

== Paste the screenshot of the created topology.

#framed[
  // 用于填写我的回答
]

== Fill in Tables 1-9, 1-10, and 1-11 based on the STP status output of each switch and its ports.

#framed[
  // 用于填写我的回答
  
  #align(center)[
    *Table 1-9 STP Status and Roles on switch LSW1*
    #table(
      columns: 5,
      align: center + horizon,[Bridge ID], [], table.cell(colspan: 3)[#sym.square Root Bridge #h(2em) #sym.square Designated Bridge],
      [Bridge ID priority], table.cell(colspan: 4)[],
      [Switch MAC Address], table.cell(colspan: 4)[],
      [*Interface*],[*STP Role*], [*STP Status*], [*Port ID*], [*Path Cost*],[GE 0/0/9], [], [], [], [],
      [GE 0/0/21], [], [], [], [],
      [GE 0/0/22], [], [], [], [],[GE 0/0/23], [], [], [], [],
      [GE 0/0/24], [], [],[],[]
    )

    #v(1em)
    
    *Table 1-10 STP Status and Roles on switch LSW2*
    #table(
      columns: 5,
      align: center + horizon,
      [Bridge ID], [], table.cell(colspan: 3)[#sym.square Root Bridge #h(2em) #sym.square Designated Bridge],
      [Bridge ID priority], table.cell(colspan: 4)[],
      [Switch MAC Address], table.cell(colspan: 4)[],
      [*Interface*], [*STP Role*], [*STP Status*],[*Port ID*], [*Path Cost*],
      [GE 0/0/9], [], [], [], [],[GE 0/0/21], [], [], [], [],[GE 0/0/22], [], [], [], [],
      [GE 0/0/23], [], [], [], [],[GE 0/0/24], [], [], [],[]
    )

    #v(1em)

    *Table 1-11 STP Status and Roles on switch LSW3*
    #table(
      columns: 5,
      align: center + horizon,
      [Bridge ID],[], table.cell(colspan: 3)[#sym.square Root Bridge #h(2em) #sym.square Designated Bridge],
      [Bridge ID priority], table.cell(colspan: 4)[],[Switch MAC Address], table.cell(colspan: 4)[],
      [*Interface*], [*STP Role*], [*STP Status*], [*Port ID*], [*Path Cost*],[GE 0/0/9], [], [], [], [],
      [GE 0/0/21], [], [], [],[],
      [GE 0/0/22], [], [], [], [],[GE 0/0/23], [], [], [], [],
      [GE 0/0/24], [], [], [],[]
    )
  ]
]

== Draw the spanning tree of this network and mark the root bridge, designated bridge, root port, and designated port.

#framed[
  // 用于填写我的回答
]

== How many types of BPDUs are captured?

#framed[
  // 用于填写我的回答
]

== A BPDU is encapsulated in an Ethernet frame. What is the destination MAC address of the frame encapsulating these BPDUs?

#framed[
  // 用于填写我的回答
]

== Expand the Topology Change Notification BPDU in Wireshark, and paste the screenshot of this expanded BPDU. From which interface of which switch is the BPDU sent? Is the switch the Root Bridge? Is the interface the Root Port? To which switch is this notification sent?

#framed[
  // 用于填写我的回答
]

== Expand the Configuration BPDU indicating topology change in Wireshark, and paste the screenshot of this expanded BPDU. Which type of switch can send this type of BPDU, Root Bridge or Non-Root Bridge?

#framed[
  // 用于填写我的回答
]

== Expand the Configuration BPDU indicating topology change acknowledgement in Wireshark, and paste the screenshot of this expanded BPDU. Which type of switch can send this type of BPDU, Root Bridge or Non-Root Bridge?

#framed[
  // 用于填写我的回答
]

== After STP is converged, what are the majority of BPDUs? Is the topology change and topology change acknowledgement flag set?

#framed[
  // 用于填写我的回答
]

== Describe how TCN BPDUs work with Configuration BPDUs.

#framed[
  // 用于填写我的回答
]

== Have you observed broadcast storm in Wireshark?

#framed[
  // 用于填写我的回答
]

== On which ports of the switch have you captured the ping communication?

#framed[
  // 用于填写我的回答
]


= ROOT BRIDGE CONFIGURATION

== Paste the screenshot of the created topology.

#framed[
  // 用于填写我的回答
]

== Fill in Tables 1-13, 1-14, and 1-15 based on the STP status output of each switch and its ports.

#framed[
  // 用于填写我的回答

  #align(center)[
    *Table 1-13 STP Status and Roles on switch LSW1*
    #table(
      columns: 5,
      align: center + horizon,
      [Bridge ID],[], table.cell(colspan: 3)[#sym.square Root Bridge #h(2em) #sym.square Designated Bridge],
      [Bridge ID priority], table.cell(colspan: 4)[],[Switch MAC Address], table.cell(colspan: 4)[],
      [*Interface*], [*STP Role*], [*STP Status*], [*Port ID*], [*Path Cost*],[GE 0/0/9], [], [], [], [],
      [GE 0/0/21], [], [], [],[],
      [GE 0/0/22], [], [], [], [],[GE 0/0/23], [], [], [], [],
      [GE 0/0/24], [], [], [],[]
    )

    #v(1em)

    *Table 1-14 STP Status and Roles on switch LSW2*
    #table(
      columns: 5,
      align: center + horizon,
      [Bridge ID], [], table.cell(colspan: 3)[#sym.square Root Bridge #h(2em) #sym.square Designated Bridge],
      [Bridge ID priority], table.cell(colspan: 4)[],
      [Switch MAC Address], table.cell(colspan: 4)[],
      [*Interface*], [*STP Role*], [*STP Status*], [*Port ID*],[*Path Cost*],
      [GE 0/0/9], [], [], [], [],[GE 0/0/21], [], [], [], [],
      [GE 0/0/22], [], [],[], [],
      [GE 0/0/23], [], [], [], [],[GE 0/0/24], [], [], [],[]
    )

    #v(1em)

    *Table 1-15 STP Status and Roles on switch LSW3*
    #table(
      columns: 5,
      align: center + horizon,
      [Bridge ID],[], table.cell(colspan: 3)[#sym.square Root Bridge #h(2em) #sym.square Designated Bridge],
      [Bridge ID priority], table.cell(colspan: 4)[],
      [Switch MAC Address], table.cell(colspan: 4)[],
      [*Interface*], [*STP Role*],[*STP Status*], [*Port ID*], [*Path Cost*],
      [GE 0/0/9],[], [], [], [],
      [GE 0/0/21], [], [], [], [],[GE 0/0/22], [], [], [], [],
      [GE 0/0/23],[], [], [], [],
      [GE 0/0/24], [], [], [],[]
    )
  ]
]

== Draw the spanning tree of the network and mark the root bridge, designated bridge, root port, and designated port.

#framed[
  // 用于填写我的回答
]
