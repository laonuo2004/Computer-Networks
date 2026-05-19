#let course-code = "100071011"
#let course-name = "Computer Networks"
#let term = "2025-2026-2"
#let project-no = "Project-1"
#let project-title = "Reliable File Transfer using Go-Back-N protocol"
#let report-kind = "Project Report"

#let student-id = "1120231863"
#let student-name = "左逸龙"
#let class-no = "07112303"
#let instructor = "宿红毅"
#let report-date = datetime.today().display("[month repr:long] [day], [year]")

#set document(
  title: project-no + ": " + project-title,
  author: student-name,
)

#set page(
  paper: "a4",
  margin: (top: 2.2cm, bottom: 2cm, left: 2.45cm, right: 2.45cm),
)

#set text(
  font: ("Times New Roman", "Source Han Serif SC"),
  size: 11pt,
  lang: "en",
)

#set par(
  justify: true,
  first-line-indent: 2em,
  leading: 0.52em,
)

#show heading: it => {
  set par(first-line-indent: 0pt)
  block(above: 1.15em, below: 0.75em)[#it]
}

#let info-row(label, value) = (
  text(weight: "bold")[#label],
  if value == "" { [] } else { [#value] },
)

#let answer(body) = block(
  width: 100%,
  inset: (x: 0.8em, y: 0.55em),
  stroke: 0.5pt + gray,
  radius: 0pt,
  breakable: true,
)[#body]

#let placeholder(label) = text(fill: gray)[#label]

#align(center)[
  #v(3.3cm)

  #text(size: 15pt, weight: "bold")[
    #course-code #course-name #term \
    #project-no \
    #project-title \
    #report-kind
  ]

  #v(2.35cm)

  #table(
    columns: (6.2cm, 6.2cm),
    rows: 4 * (0.78cm,),
    align: (center + horizon, left + horizon),
    stroke: 0.75pt,
    inset: (x: 0.35em, y: 0.15em),
    ..info-row("学号 (Student ID)", student-id),
    ..info-row("姓名 (Name)", student-name),
    ..info-row("班号 (Class No.)", class-no),
    ..info-row("授课教师 (Instructor)", instructor),
  )

  #v(2.55cm)

  #text(size: 15pt, weight: "bold")[
    School of Computer \
    Beijing Institute of Technology \
    #report-date
  ]
]

#pagebreak()
#counter(page).update(1)

#set page(
  paper: "a4",
  margin: (top: 2.05cm, bottom: 1.75cm, left: 2.45cm, right: 2.45cm),
  header: context [
    #set text(size: 7.5pt)
    #grid(
      columns: (1fr, 1fr),
      align: (left, right),
      [#course-code #course-name #term],
      [#project-no: #project-title],
    )
    #line(length: 100%, stroke: 0.65pt)
  ],
  footer: context [
    #set text(size: 8.5pt)
    #align(center)[#counter(page).display("1") / #numbering("1", ..counter(page).final())]
  ],
)

#set heading(numbering: "1.")
#set par(
  justify: true,
  first-line-indent: 2em,
  leading: 0.52em,
)

= Requirement Analysis

Understanding and analysis of project requirements. Explain why Go-Back-N can be used to transfer files reliably, and describe the main issues, key functions, expected input/output, and reliability goals.

#answer[
  #placeholder("Write the requirement analysis here.")
]

= Design

Frame structure, checksum generation and checking, sliding window settings and controls, buffering, sequence spaces and numbers, acknowledgement rules, retransmission strategy, timeout timer maintenance, UDP socket design, system model, functions or classes, flow charts, state diagrams, time-sequence diagrams, possible errors and simulations, logging, configuration file and parameters, and system initialization.

#answer[
  #placeholder("Write the design details here. Add diagrams, tables, and protocol formats as needed.")
]

= Development and Implementation

Development tools, operating system, language, database or framework if any, libraries, project structure, critical functions or classes, data structures, code organization, and samples of important code.

#answer[
  #placeholder("Write the implementation details here.")
]

= System Deployment, Startup, and Use

Describe how to build, configure, start, and use the sender and receiver. Include command-line examples, configuration file examples, and notes about required runtime environment.

#answer[
  #placeholder("Write the deployment and usage instructions here.")
]

= System Test

Unit tests, integrated tests, test cases, screenshots, expected results, actual results, and analysis of failed or abnormal cases.

#answer[
  #placeholder("Write the test plan and results here.")
]

= Performance and Analysis

Performance and result analysis. Show results in data sheets and figures, such as transfer time, throughput, retransmission count, packet loss rate, window size comparison, and timeout setting comparison.

#answer[
  #placeholder("Write the performance analysis here.")
]

= Summary or Conclusions

Summarize what was studied and analyzed, what problems were solved, what technical solution was used to implement the system, how the problems were solved, what results were obtained, how well the system performed, and the main features of the system.

#answer[
  #placeholder("Write the summary or conclusions here.")
]

= References

List 5 or more references.

#answer[
  #placeholder("Add references here.")
]

= Comments

Your comments and/or suggestions on the course and the project.

#answer[
  #placeholder("Write comments here.")
]
