# ICE 候选收集实验记录

## 固定环境

- 实验日期：2026-07-14
- 操作系统：Microsoft Windows 10 家庭中文版，10.0.19045，64 位
- 浏览器：Google Chrome 150.0.7871.101
- 物理接入：WLAN，Intel Wi-Fi 6 AX200 160MHz
- 默认 IPv4 路由：WLAN
- 测试页面：WebRTC Trickle ICE Sample
- IceTransports：all
- 摄像头和麦克风权限：不申请
- STUN/TURN 服务：同一台临时 coturn 实例，端口 3478
- TURN 传输：UDP

## 三组配置

1. 不配置 ICE 服务器；
2. 仅配置 `stun:<server>:3478`；
3. 配置 STUN，并增加 `turn:<server>:3478?transport=udp` 与临时长期凭据。

每组重新收集三次。计时从点击 `Gather candidates` 开始，到页面显示 `gathering complete` 结束。按页面候选行中的 `typ host`、`typ srflx` 和 `typ relay` 分类，记录候选数量及传输协议。截图应遮盖公网地址和 TURN 凭据，命名为 `no-server-runN.png`、`stun-runN.png` 和 `stun-turn-runN.png`。

## 数据边界

本记录只用于验证候选收集。候选出现不代表该候选最终会被选中，也不能据此计算连接成功率、媒体时延或传输吞吐量。TURN 密码、服务器管理信息和未打码的公网地址不得写入本目录。
