#import "../problemst/pset.typ": pset, framed

#show: pset.with(
  class: "07112303",
  student: "左逸龙",
  title: "计算机网络第7章作业",
  date: datetime.today()
)

#let underline-blank(width) = box(width: width, stroke: (bottom: 1pt), outset: (bottom: 2pt))

= File Transfer Protocol (FTP) uses #underline-blank(3em) for control connection and #underline-blank(4em) for data connection.

A. Stateless connection. Non persistent TCP connection

B. Persistent TCP connection, non-persistent TCP connection

C. Non-persistent TCP connection, persistent TCP connection

D. FTP is a connection less protocol

#framed[
  FTP 控制连接在整个会话期间保持，因此是 persistent TCP connection。

  数据连接通常按传输需要临时建立，用完关闭，因此是 non-persistent TCP connection。

  所以选 B。
]

= Consider different activities related to email.

s1: Send an email from a mail client to a mail server

s2: Download an email from mailbox server to a mail client

s3: Checking email in a web browser

#underline-blank(3em) is the application level protocol used in each activity.

A. s1: HTTP, s2: SMTP, s3: POP

B. s1: SMTP, s2: FTP, s3: HTTP

C. s1: SMTP, s2: POP, s3: HTTP

D. s1: POP, s2: SMTP, s3: IMAP

#framed[
  客户端向邮件服务器发送邮件一般使用 SMTP。

  从邮箱服务器下载邮件到客户端可使用 POP。

  在浏览器中查看邮件属于 Web 访问，使用 HTTP。

  所以选 C。
]

= Suppose within your Web browser you click on a link to obtain a Web page. The IP address for the associated URL is not cached in your local host, so a DNS lookup is necessary to obtain the IP address. Suppose that $n$ DNS servers are visited before your host receives the IP address from DNS; the successive visits incur an RTT of $R T T_1, ..., R T T_n$. Further suppose that the Web page associated with the link contains exactly one object, consisting of a small amount of HTML text. Let $R T T$ denote the RTT between the local host and the server containing the object. Assuming zero transmission time of the object, how much time elapses from when the client clicks on the link until the client receives the object? <prob:dns-http>

#framed[
  DNS 查询需要依次访问 $n$ 个 DNS 服务器，耗时为
  $R T T_1 + R T T_2 + ... + R T T_n$。

  得到 IP 后，浏览器还需要 $1$ 个 RTT 建立 TCP 连接，再用 $1$ 个 RTT 发送 HTTP 请求并收到对象。

  因此总时间为
  $sum_(i=1)^n R T T_i + 2 R T T$。
]

= Referring to @prob:dns-http, suppose the HTML file references eight very small objects on the same server. Neglecting transmission times, how much time elapses with

== Non-persistent HTTP with no parallel TCP connections?

#framed[
  先 DNS 查询，再取回 HTML 文件本身，需要
  $sum_(i=1)^n R T T_i + 2 R T T$。

  之后 $8$ 个小对象都用非持久连接，且没有并行连接，每个对象需要 $2 R T T$。

  因此总时间为
  $sum_(i=1)^n R T T_i + 2 R T T + 8 times 2 R T T = sum_(i=1)^n R T T_i + 18 R T T$。
]

== Non-persistent HTTP with the browser configured for 5 parallel connections?

#framed[
  HTML 文件本身仍需要
  $sum_(i=1)^n R T T_i + 2 R T T$。

  后面的 $8$ 个对象用非持久连接，但最多 $5$ 个并行，所以分成两批获取。

  每批需要 $2 R T T$，两批共 $4 R T T$。

  因此总时间为
  $sum_(i=1)^n R T T_i + 6 R T T$。
]

== Persistent HTTP?

#framed[
  HTML 文件本身需要建立 TCP 连接并取回，共 $2 R T T$。

  使用 persistent HTTP 时，后续 $8$ 个小对象可复用同一个 TCP 连接，因此再需要约 $1 R T T$。

  因此总时间为
  $sum_(i=1)^n R T T_i + 3 R T T$。
]
