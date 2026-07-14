// ==================== 论文信息（请先修改这里） ====================
#let paper-title = "你的论文名称"
#let english-title = "Your English Paper Title"
#let author-name = "左逸龙"
#let student-id = "1120231863"
#let class-name = "07112303"
#let school-name = "计算机学院"
#let english-author = "Yilong Zuo"
#let email = "cs.yilong.zuo@bit.edu.cn"
#let semester = "2025-2026-2"
#let postal-code = "100081"

#set document(title: paper-title, author: author-name)
#set text(
  font: ("Times New Roman", "Source Han Serif SC"),
  size: 10.5pt,
  weight: 400,
  lang: "zh",
  region: "CN",
)
#set par(
  justify: true,
  first-line-indent: 2em,
  leading: 5pt,
  spacing: 0pt,
)
#set heading(numbering: "1.1")
#set math.equation(numbering: "(1)")

// 页眉、页脚和页码均由 Typst 自动生成。
#set page(
  paper: "a4",
  margin: (top: 22mm, bottom: 15mm, left: 17mm, right: 17mm),
  header-ascent: 7mm,
  footer-descent: 8mm,
  numbering: "1",
  header: context {
    set text(
      font: ("Times New Roman", "Source Han Serif SC"),
      size: 9pt,
      weight: 400,
    )
    block(width: 100%)[
      #grid(
        columns: (1fr, auto),
        align(left, paper-title),
        align(right, [#semester #h(0.8em) 计算机网络]),
      )
      #v(2pt)
      #line(length: 100%, stroke: 0.6pt)
    ]
  },
  footer: context {
    set text(font: "Times New Roman", size: 9pt)
    align(center, counter(page).display("1"))
  },
)

// 只调整原生标题的显示样式；层级、编号、书签与引用仍由 heading 负责。
#show heading.where(level: 1): set text(
  font: "SimHei",
  size: 12pt,
  weight: "bold",
)
#show heading.where(level: 2): set text(
  font: "SimHei",
  size: 10.5pt,
  weight: "bold",
)
#show heading.where(level: 3): set text(
  font: "SimHei",
  size: 10.5pt,
  weight: "bold",
)

// 图表题注沿用 Typst 的原生编号和 label 引用。
#show figure.caption: set text(
  font: ("Times New Roman", "Source Han Serif SC"),
  size: 9pt,
  weight: 400,
)

// ==================== 单栏：题目、作者与摘要 ====================
#align(left)[
  #set par(first-line-indent: 0pt)
  #text(font: "SimHei", size: 16pt, weight: "bold", paper-title)

  #v(14pt)
  #text(font: "FangSong", size: 14pt, weight: 400)[
    #student-id #h(2em) #author-name
  ]

  #v(8pt)
  #text(
    font: ("Times New Roman", "Source Han Serif SC"),
    size: 9pt,
    weight: 400,
  )[北京理工大学 #school-name #class-name 班，北京 #postal-code]

  #v(6pt)
  #text(size: 9pt, email)

  #v(20pt)
  #text(font: "Times New Roman", size: 14pt, weight: "bold", english-title)

  #v(12pt)
  #text(font: "Times New Roman", size: 10.5pt, english-author)

  #v(7pt)
  #text(font: "Times New Roman", size: 9pt)[
    (Class #class-name, School of Computer Science,
    Beijing Institute of Technology, Beijing #postal-code)
  ]
]

#v(12pt)

#block[
  #set text(font: "Times New Roman", size: 9pt, weight: 400)
  #set par(first-line-indent: 0pt)
  *Abstract* #h(0.5em) [Write an English abstract of at least 200 words here. It should state the research problem, the main method, the principal results, and the conclusion. Delete this instruction when the abstract is complete.]
]

#v(6pt)

#block[
  #set text(font: "Times New Roman", size: 9pt, weight: 400)
  #set par(first-line-indent: 0pt)
  *Key words* #h(0.5em) keyword one; keyword two; keyword three; keyword four
]

#v(10pt)

#block[
  #set text(font: "KaiTi", size: 10.5pt, weight: 400)
  #set par(first-line-indent: 0pt)
  #text(font: "SimHei", size: 9pt, weight: "bold")[摘要]
  #h(0.5em) [在此填写约 300 字的中文摘要。摘要应交代研究问题、采用的方法、主要结果和结论，完成后删除本段提示。]
]

#v(6pt)

#block[
  #set text(font: "KaiTi", size: 10.5pt, weight: 400)
  #set par(first-line-indent: 0pt)
  #text(font: "SimHei", size: 9pt, weight: "bold")[关键词]
  #h(0.5em) 关键词一；关键词二；关键词三；关键词四
]

// ==================== 双栏：正文 ====================
// 原 Word 模板不含目录，因此这里直接进入正文。
#v(8pt)
#columns(2, gutter: 7.5mm)[
  本文从这里开始撰写正文。引言一般说明研究背景、需要解决的问题、相关工作以及全文结构。正式论文不少于 4000 字，并应在正文中引用至少 5 篇参考文献。文献引用示例见 @tanenbaum2021。

  正文中的章节、公式、图和表均可使用标签交叉引用。例如，@sec-method 给出章节引用示例；@eq-example、@fig-example 和 @tab-example 分别展示公式、图片和表格引用方式。

  = 方法与原理 <sec-method>

  本节介绍论文采用的方法及其基本原理，并说明各部分之间的关系。调整章节顺序后，相关编号与引用会同步更新。

  == 核心机制 <sec-mechanism>

  在此说明方案的关键流程、协议交互或算法设计。需要使用公式时，可以直接使用原生数学公式环境：

  $ y = f(x) + epsilon $ <eq-example>

  该式给出一个简化的函数关系。正式写作时，应在公式后解释符号含义及其适用条件。

  === 实现要点 <sec-details>

  在此补充实现细节、参数设置和必要的设计理由。三级标题同样参与自动编号和 PDF 书签生成。

  #figure(
    rect(
      width: 100%,
      height: 36mm,
      stroke: 0.7pt + gray,
      fill: luma(245),
      align(center + horizon)[
        #text(font: "Source Han Serif SC", size: 7.5pt)[在此插入图片]
      ],
    ),
    kind: "image",
    supplement: [图],
    caption: [示例图片占位符 \ Example figure placeholder],
  ) <fig-example>

  #v(8pt)

  @fig-example 展示了图片、双语题注与正文引用的写法。

  #figure(
    text(
      font: ("Times New Roman", "Source Han Serif SC"),
      size: 7.5pt,
      weight: 400,
    )[
      #table(
        columns: (1fr, 1fr, 1fr),
        align: center + horizon,
        stroke: 0.5pt,
        table.header([指标], [方案 A], [方案 B]),
        [时延], [10 ms], [8 ms],
        [吞吐量], [80 Mbit/s], [95 Mbit/s],
      )
    ],
    kind: table,
    supplement: [表],
    caption: [示例实验结果 \ Example experimental results],
  ) <tab-example>

  #v(8pt)

  @tab-example 用于展示数据对比。表内文字、数值和单位应保持一致的精度与书写方式。

  = 结果与分析 <sec-results>

  在此给出实验环境、测试方法和结果，并结合图表解释结果产生的原因。除平均值外，还应说明边界情况或异常现象，以便判断结论是否稳定。

  = 结论 <sec-conclusion>

  在此概括论文的主要工作、得到的结论以及仍可继续研究的问题。结论应与正文分析对应，不引入尚未讨论的新结果。

  #heading(numbering: none)[参考文献] <sec-references>

  // 正式论文至少列出 5 篇文献，并保证每篇文献均在正文中通过 @文献键 引用。
  #show bibliography: set text(
    font: ("Times New Roman", "Source Han Serif SC"),
    size: 7.5pt,
    weight: 400,
  )
  #bibliography("references.bib", style: "ieee", title: none)
]
