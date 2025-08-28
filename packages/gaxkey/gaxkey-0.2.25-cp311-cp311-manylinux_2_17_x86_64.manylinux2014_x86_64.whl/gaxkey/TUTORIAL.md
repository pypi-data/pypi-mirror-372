# GAXKey 使用教程

## 概述

GAXKey 是 GAX 产品的激活工具，用于管理和验证 GAX 系列产品的许可证。它包含两个主要组件：
- **客户端(gaxkey)**：用于激活产品、检查许可证状态、申请和续约许可证
- **服务器端(gaxkeyServer)**：提供许可证管理服务，负责验证和分发许可证

## 快速入门
### 安装
**系统&软件要求**
1. Linux系统；
2. glibc版本 >= 2.31 （可使用 ldd --version 命令查看glibc版本）;
3. python版本 >= 3.8;
**安装python**
```bash
sudo apt update
sudo apt install python3 python3-pip
```
**安装gaxkey软件**
```bash
pip3 install gaxkey
# 如果网络连接不上，可指定国内源安装：
pip install gaxkey -i https://pypi.tuna.tsinghua.edu.cn/simple
```
### 单机许可模式
**激活**
```bash
gaxkey --gaxkcompiler eyJhbGciOiJIUzUxMiJ9.eyJwcm9kdWN0SWQiOjQsImV4cGlyYXRpb25EYXRlIjoxNzQ3MDY1NjAwMDAwLCJ0aW1lc3RhbXAiOjE3NDcwNDk0NjkzMzl9.KmzDFvpQQqDRabuhrxe0dDmSZ3knZs_C2dljTR_KU_H2sgd3mx_t-aao8J3vZs3mVVJTc9jtGS4rLoYbhes7Kw

# gaxkcompiler successfully activated! the license file is written to /home/user/.config/gax/gaxkcompiler_0.lic
```
**检查是否成功激活**
```bash
gaxkey --check
```
### 集群许可模式
**激活**
```bash
gaxkey --gaxkcompiler --cluster eyJhbGciOiJIUzUxMiJ9.eyJwcm9kdWN0SWQiOjQsImV4cGlyYXRpb25EYXRlIjoxNzQ3MDY1NjAwMDAwLCJ0aW1lc3RhbXAiOjE3NDcwMzE4MDcwOTN9._-Q4NKzSjByj6w_7tMVGcyuVBrDZgTJr9fgd-QBavps6EyNSJ8ulquBnMsXdo67FcSKuLDcZJaCjnHnuiIs_PQ

# gaxkcompiler successfully activated! the license file is written to /home/user/.config/gax/gaxkcompiler_1.lic
```
**启动授权服务端**
```bash
gaxkeyServer

# Starting GAXKey License Server...
# [2025-05-12 11:58:22] [INFO] [SERVER] License server started at http://127.0.0.1:15200 ...
```
**设置授权服务器地址**
```bash
gaxkey --server http://127.0.0.1:15200

# License Server Configuration Results:
# --------------------------------
# http://127.0.0.1:15200: Success
# --------------------------------
```
**申请授权**
```bash
gaxkey --apply gaxkcompiler

# apply success, clientId: 9638f5e40f96a38601c8967dc278977d, server address: http://127.0.0.1:15200
```
**批准授权**
```bash
gaxkeyServer --approve 9638f5e40f96a38601c8967dc278977d

# Application approved for clientID: 9638f5e40f96a38601c8967dc278977d product: gaxkcompiler
```

**检查许可证是否有效**
```bash
gaxkey --check

# gaxkcompiler successfully activated! the license file is written to /home/user/.config/gax/gaxkcompiler_0.lic
# ClientID:9638f5e40f96a38601c8967dc278977d
# Activated:true
# ExpireTime:2025-05-30 00:00:00
```
#### 集群模式在docker中使用
**方案一：绑定server地址配置文件**
1. 在主机上执行: gaxkey --server http://192.168.1.101:15200
2. 在docker-compose.yml中添加配置文件映射：
```yaml
version: '3'
services:
  gax-app:
    image: your-gax-app-image
    container_name: gax-app
    restart: always
    volumes:
      - /home/gant/.config/gax/licenseServer.txt:/opt/gax/licenseServer.txt
```

**方案二：在docker-compose.yml中设置环境变量**
```yaml
version: '3'
services:
  gax-app:
    image: your-gax-app-image
    container_name: gax-app
    restart: always
    environment:
      - LICENSE_SERVER=http://192.168.1.101:15200
```

## 客户端使用指南

### 基本命令

```bash
gaxkey [选项] [激活码]
```

### 常用选项

- `--gaxkcompiler`：激活 GAXKCompiler 产品
- `--server <服务器地址>`：设置许可证服务器地址，例如 `http://127.0.0.1:15200,http://192.168.1.1:15200`
- `--server-health`: 检查许可证服务器连接状态
- `--check`：检查产品许可证是否有效
- `--apply`：申请许可证
- `--cluster`：启用集群模式（与 `--gaxkcompiler` 或 `--check` 一起使用）

### 使用示例

#### 设置许可证服务器

**方式一：使用gaxkey命令设置**
```bash
gaxkey --server http://192.168.1.1:15200,http://127.0.0.1:15200

# License Server Configuration Results:
# --------------------------------
# http://192.168.1.1:15200: Failed: Connection timed out
# http://127.0.0.1:15200: Success
# --------------------------------
```
**方式二：设置环境变量**
1. 临时生效：`export LICENSE_SERVER=http://127.0.0.1:15200`
2. 永久生效: 
    1. 修改 `~/.bashrc` 文件，添加内容：`export LICENSE_SERVER=http://127.0.0.1:15200`
    2. 生效：`source ~/.bashrc`

#### 检查许可证服务器状态
```bash
gaxkey --server-health

# +------------------------+-----------+
# | Server                 | Status    |
# +------------------------+-----------+
# | http://127.0.0.1:15200 | Available |
# +------------------------+-----------+
```
#### 检查许可证状态

```bash
gaxkey --check
```

集群模式下检查集群许可证状态：

```bash
gaxkey --check --cluster
```

#### 申请许可证

```bash
gaxkey --apply
```

#### 使用激活码激活产品

```bash
gaxkey --gaxkcompiler YOUR_ACTIVATION_CODE
```

集群模式下激活产品：

```bash
gaxkey --gaxkcompiler YOUR_ACTIVATION_CODE --cluster
```

## 服务器端使用指南

### 基本命令

```bash
gaxkeyServer [选项]
```

### 常用选项

- 无参数：启动许可证服务器
- `--list-apps`：列出客户端应用信息
- `--query-app <客户端ID>`：查询特定客户端应用信息
- `--approve <客户端ID> [时长(秒)]`：批准客户端应用，可选设置许可时长
- `--set-renewable <客户端ID> <enable|disable>`：设置许可证是否可续约

### 使用示例

#### 启动许可证服务器

```bash
gaxkeyServer
```

#### 列出所有客户端证书申请信息

```bash
gaxkeyServer --list-apps
```

#### 查询特定客户端证书申请信息

```bash
gaxkeyServer --query-app client_xxxx
```

#### 批准客户端证书申请

默认有效时长限制：
```bash
gaxkeyServer --approve client_xxxx
```

指定有效期（例如7天）：
```bash
gaxkeyServer --approve client_xxxx 604800
```

#### 设置许可证续约状态

启用续约：
```bash
gaxkeyServer --set-renewable client_xxxx enable
```

禁用续约：
```bash
gaxkeyServer --set-renewable client_xxxx disable
```

## 注意事项

1. 确保网络连接稳定，特别是在连接远程许可证服务器时
2. 集群模式适用于分布式环境下的许可证管理
3. 服务器地址可以设置多个，以逗号分隔，提高可用性
