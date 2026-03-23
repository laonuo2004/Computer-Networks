#let pset(
  class: "07112303",
  title: "计算机网络 第X章作业",
  student: "左逸龙",
  student_id: "1120231863",
  date: datetime.today(),
  subproblems: "1.1.a.i",
  collaborators: (),
  doc,
) = {
  [
    /* Convert collaborators to a string if necessary */
    #let collaborators = if type(collaborators) == array { collaborators.join(", ") } else { collaborators }

    /* Global settings for beautiful typography */
    #set text(font: ("Libertinus Serif", "Times New Roman", "Source Han Serif SC", "SimSun"), size: 11pt)
    #set par(leading: 1.2em, justify: true)

    /* Problem + subproblem headings */
    #set heading(
      numbering: (..nums) => {
        nums = nums.pos()
        if nums.len() == 1 {
          [Problem #nums.at(0):]
        } else {
          numbering(subproblems, ..nums)
        }
      },
    )

    /* Set metadata */
    #set document(title: title, author: student, date: date)

    /* Set up page numbering and continued page headers */
    #set page(
      numbering: "1",
      header: context {
        if counter(page).get().first() > 1 [
          #set text(style: "italic")
          #title
          #h(1fr)
          #date.display("[year]-[month]-[day]")
          #block(line(length: 100%, stroke: 0.5pt), above: 0.6em)
        ]
      },
    )

    /* Add numbering and some color to code blocks */
    #show raw.where(block: true): it => {
      block(width: 100% - 0.5em, radius: 0.3em, stroke: luma(50%), inset: 1em, fill: luma(98%))[
        #show raw.line: l => context {
          box(width: measure([#it.lines.last().count]).width, align(right, text(fill: luma(50%))[#l.number]))
          h(0.5em)
          l.body
        }
        #it
      ]
    }

    /* Make the title */
    #align(
      center,
      {
        text(size: 1.8em, weight: "bold")[#title]
        // v(1.2em)
        block(width: 100%)[
          #grid(
            columns: (auto, 20%, auto),
            align: (left, center, right),
            text(size: 1.15em)[#class],
            text(size: 1.15em)[#student],
            text(size: 1.15em)[#student_id]
          )
        ]
        // v(0.8em)
        text(size: 1.05em, style: "italic", fill: luma(30%))[
          #date.display("[year]-[month]-[day]")
          #if collaborators != none {
            [
              \ Collaborators: #collaborators
            ]
          }
        ]
        v(0.6em)
        box(line(length: 100%, stroke: 0.8pt))
        v(1.2em)
      },
    )

    #doc
  ]
}
