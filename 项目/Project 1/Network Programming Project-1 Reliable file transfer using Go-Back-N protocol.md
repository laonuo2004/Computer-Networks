# Project 1: Reliable file transfer using Go-Back-N protocol

Network Programming Project 1 - Reliable file transfer using Go-Back-N protocol

假设 Host1 和 Host2 分别向对方发送大文件。要求采用 GBN（Go-Back-N）协议实现可靠的文件传输。可以参考 *Computer Networks (A.S.Tanenbaum, 5th Edition)* 书第 3 章中 Protocol 5。

## 一、基本功能要求（必须实现）：

1.  **自行定义帧（PDU）结构**。需要在 PDU 末尾增加 checksum 字段。checksum 采用 CRC-CCITT 标准。可以不考虑帧的起始和结束标识。
2.  **采用 UDP Socket API 模拟并实现 PDU 的发送和接收**，每个 UDP 数据报封装一个 PDU。注意：UDP Socket 仅用于 PDU 的发送和接收，其使用的 IP 地址和端口与传输的 PDU 无关。需要处理的是 UDP 数据报中的 PDU。
3.  可以参考 *Computer Networks (A.S.Tanenbaum, 5th Edition)* 书第 3 章中 Protocol 5 定义的 PDU。
4.  PDU 中数据部分的长度不要超过 **4KB**，以保证传输足够多的 PDU。
5.  所实现的 GBN 协议应支持**全双工**，实现双向文件传输。
6.  实现一个生成器或方法，允许根据配置文件中给出的百分比（n%）**随机产生 PDU 错误和 PDU 丢失**。
7.  准备一个 **3MB 以上**的文件用于测试。
8.  文件传输完毕后，接收并保存的文件应与发送的原始文件一模一样。
9.  通过配置文件配置通信或协议参数。
10. **记录通信状态**。写到日志文件中。
11. **编写一个程序读取日志文件**，对通信状态记录数据进行统计分析，从多个维度分析比较不同的数据大小、窗口大小、PDU 错误率、PDU 丢失率和超时值时的通信效率，例如：文件划分的 PDU 总数量，通信总次数，超时次数，重传 PDU 的数量、总耗时等，可以用图表表示，并得出分析结论。

## 二、增强的功能要求（可选）：

12. **支持多台主机之间的文件传输**。不仅支持 Host1 与 Host2 一对主机之间的文件传输，还支持与其他 Hosts，例如 Host1 同时与 Host2、Host3、Host4 等多对主机之间同时相互发送文件。
13. 考虑采用多进程、多线程、队列等技术实现并发文件传输。

## 三、配置文件

配置文件关键要点（包括但不限于）：

*   **UDPPort**：UDP 端口。例如：UDPPort=8888。建议使用的 Port 为 4xxxx，其中 xxxx 为你的学号的最后 4 位数。
*   **DataSize**：PDU 中数据字段的长度，单位为字节。例如：DataSize=1024，表示 PDU 中数据字段的长度为 1KB。
*   **ErrorRate**：PDU 错误率。例如：ErrorRate=10，表示每 10 帧中一帧出错。
*   **LostRate**：PDU 丢失率。例如：LostRate=10，表示每 10 帧丢一帧。
*   **SWSize**：发送窗口大小。例如：SWSize=4，表示发送窗口大小为 4。注意：最大窗口大小与序号所占二进制位数的关系。
*   **InitSeqNo**：起始 PDU 的序号。例如：InitSeqNo=1，表示开始文件传输时，发送和接收的第 1 个 PDU 的序号为 1。
*   **Timeout**：超时定时器值，单位为毫秒。例如：Timeout =1000，表示超时时间为 1 秒。

## 四、日志文件

记录在每一次文件传输中，发送方和接收方每发送和接收一个 PDU 时的通信状态记录与统计信息，包括：

*   **发送**：顺序编号（反映第几次发送，从 1 开始）或时间戳，本次发出的 PDU 的序号和状态（新 New，超时重传 TO，重传 RT），当前已被确认的 PDU 的序号。
    *   格式：`1, pdu_to_send=1, status=New, ackedNo=1`
    *   可以记录其他你认为必要的状态信息。
*   **接收**：顺序编号（反映第几次接收，从 1 开始）或时间戳，期望接收的 PDU 的序号，当前接收到的 PDU 的序号和状态（数据错误 DataErr，序号错误 NoErr，正确 OK）。
    *   格式：`1, pdu_exp=1, pdu_recv=1, status=OK`
    *   可以记录其他你认为必要的状态信息。

每次文件传输生成一个日志文件，每次发送和接收一个 PDU 在日志文件中记录一条日志，便于事后查看和分析。