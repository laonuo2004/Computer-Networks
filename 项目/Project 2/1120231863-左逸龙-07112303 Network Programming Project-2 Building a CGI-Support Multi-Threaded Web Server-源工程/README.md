# CGI-Support Multi-Threaded Web Server

本项目是北京理工大学《计算机网络》Network Programming Project 2。服务器不使用 `http.server`、Flask 等 HTTP 框架，而是在 TCP socket 上自行完成 HTTP 报文解析、固定线程池、连接上限管理、静态资源响应、CGI 子进程调用和访问日志。

## 已实现功能

- HTTP/1.0，并兼容浏览器常用的基础 HTTP/1.1 请求；
- GET、POST、HEAD；
- 200、400、403、404、500 状态与自定义错误页；
- 启动时预创建的固定 worker 线程池；
- 请求多于 worker 时排队，连接达到上限后关闭接受时间最早的连接；
- HTTP/1.0 显式 keep-alive 和 HTTP/1.1 默认 keep-alive；
- HTML、CSS、SVG 等静态资源与安全的 webroot 路径解析；
- 通过环境变量、stdin、stdout 连接的真实 CGI 子进程；
- 四则运算 CGI 与 SQLite 学生信息查询 CGI；
- 线程安全的 Common Log 风格访问日志；
- 单元、端到端、40客户端并发、连接淘汰和独立 EXE 测试；
- 1～20 个 worker 的可复现性能实验。

运行时只使用 Python 标准库。Python 3.13 已移除旧 `cgi` 模块，本项目按照 CGI/1.1 的数据传递方式自行实现服务器与 CGI 程序之间的接口。

## 工程结构

```text
.
|-- web_server.py              # 统一入口和命令行参数
|-- server/                    # HTTP、线程池、路由、CGI、日志
|-- cgi_apps/                  # 计算器和 SQLite 查询逻辑
|-- webroot/                   # 页面、静态资源、CGI 包装脚本、数据和日志
|-- tests/                     # unittest 自动测试
|-- tools/                     # 性能实验和打包烟雾测试
|-- results/                   # 性能 CSV、Markdown 和 SVG
|-- packaging/README.txt       # EXE 使用说明
|-- pyproject.toml / uv.lock   # uv 环境与开发依赖锁定
`-- 1120231863CGIMultiThreadedWebServer.spec
```

## 环境

- Python 3.13.3
- uv 0.7.1 或更新版本
- Windows 10/11；源码也可在 Linux 上运行

项目已有 `.venv` 时直接使用。重新创建环境可执行：

```powershell
uv sync --dev
```

运行时没有第三方依赖，`--dev` 只安装构建 Windows 程序所需的 PyInstaller 6.21.0。

## 启动源码服务器

在本目录打开 PowerShell：

```powershell
.\.venv\Scripts\python.exe web_server.py
```

默认地址为 <http://127.0.0.1:8888/>，默认8个 worker、最多32个同时打开的连接。自定义参数示例：

```powershell
.\.venv\Scripts\python.exe web_server.py `
  --host 127.0.0.1 `
  --port 8888 `
  --workers 4 `
  --max-connections 32
```

如需从局域网其他机器访问，可改用 `--host 0.0.0.0`，并按 Windows 防火墙提示允许对应端口。按 Ctrl+C 可关闭 listener、客户端 socket、worker 和日志。

## 页面和 CGI

- `/`：静态首页；
- `/calculator.html`：计算器表单；
- `/query.html`：学生信息查询表单；
- `/cgi-bin/calculator.py`：支持 `add/sub/mul/div`；
- `/cgi-bin/query.py`：按学号参数化查询 SQLite。

首次启动会根据 `webroot/data/students.csv` 原子生成 `students.db`。服务器不会通过 HTTP 返回 `data/`、`log/` 或 CGI 源文件。

命令行手测：

```powershell
curl.exe -i http://127.0.0.1:8888/
curl.exe -I http://127.0.0.1:8888/index.html
curl.exe -i -X POST -d "a=6&b=7&op=mul" http://127.0.0.1:8888/cgi-bin/calculator.py
curl.exe -i -X POST -d "student_id=1120231863" http://127.0.0.1:8888/cgi-bin/query.py
```

## 自动测试

```powershell
.\.venv\Scripts\python.exe -W error::ResourceWarning `
  -m unittest discover -s tests -p "test_*.py" -v
```

测试覆盖分片 HTTP 报文、Content-Length、连续请求、HEAD、状态码、目录穿越、CGI 超时/异常输出、SQLite 注入字符串、并发日志、40客户端并发、最老连接淘汰和优雅关闭。

## 性能实验

正式实验命令：

```powershell
.\.venv\Scripts\python.exe tools\performance_suite.py `
  --workers 1 2 4 8 12 16 20 `
  --requests 500 `
  --concurrency 40 `
  --repetitions 3 `
  --warmup 20 `
  --output-dir results
```

每个客户端请求都新建 TCP 连接并发送 HTTP/1.0 请求。工具校验 `/index.html` 的完整响应，记录吞吐量、平均/中位/P95 延迟和错误数，并生成：

- `results/performance.csv`
- `results/performance.md`
- `results/throughput.svg`
- `results/latency.svg`

性能结果取三轮中位数，不要求 worker 越多吞吐量越高；线程调度、TCP 建连和本机负载都可能导致超过最佳线程数后性能下降。

## 构建和验证 Windows 程序

```powershell
uv sync --dev
.\.venv\Scripts\pyinstaller.exe --clean --noconfirm 1120231863CGIMultiThreadedWebServer.spec
```

输出目录：

```text
dist\1120231863CGIMultiThreadedWebServer\
|-- 1120231863CGIMultiThreadedWebServer.exe
|-- _internal\
|-- webroot\
`-- README.txt
```

不要单独移动 EXE。验证工具会把整个目录复制到系统临时目录，在未激活虚拟环境的情况下测试静态页、HEAD、CGI、SQLite、40并发和日志：

```powershell
.\.venv\Scripts\python.exe tools\package_smoke.py `
  dist\1120231863CGIMultiThreadedWebServer\1120231863CGIMultiThreadedWebServer.exe
```

PyInstaller 不是交叉编译器；Windows EXE 必须在 Windows 构建。如果需要原生 Linux 可执行文件，应在 Linux 环境中用同一 spec 重新构建。

## 访问日志

每次启动会创建 `webroot/log/access-YYYYMMDD-HHMMSS-ffffff.log`。每行记录客户端 IP、时间、请求行、状态码、资源大小、Referer 和 User-Agent。HTML 页面引用 CSS/SVG 时，每个资源请求各产生一行记录。

## 实现边界

本项目聚焦课程要求，没有实现 HTTPS、HTTP chunked transfer、Range、缓存、上传、认证或任意 CGI 程序执行。CGI 只允许计算器和查询脚本，子进程有5秒超时和1 MiB输出上限。
