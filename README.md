# 2025_P4_OpenJudge - 教育在线判题平台


## 项目概述

OpenJudge是一个教育在线判题平台，旨在解决现有竞赛编程平台的关键限制。与LeetCode或Codeforces等传统在线判题平台隐藏测试用例以防止学生利用测试用例不同，我们的系统专门为教育目的而构建，**所有测试用例对学生完全可见**。目前，这个MVP版本仅支持使用**Python**解决问题。

这种透明度使学生能够：
- **从错误中学习**，通过准确看到哪些测试用例失败
- **更有效地调试**，完全了解预期输出与实际输出的对比
- **通过基于清晰反馈的迭代改进来提高问题解决技能**
- **理解他们可能没有考虑到的边缘情况**

该平台保持熟悉的在线判题模型，同时优先考虑学习和理解而非竞赛评估。

## 🚀 在线演示

**访问部署的平台**: [http://coughoverflow-alb-1348614147.us-east-1.elb.amazonaws.com/](http://coughoverflow-alb-1348614147.us-east-1.elb.amazonaws.com/)

**默认登录凭据:**
- **用户名**: `CSSE6400`
- **密码**: `qimojiayou`

使用这些凭据探索平台功能、提交代码解决方案，并体验以教育为重点的在线判题环境。

## 📁 仓库结构

```
2025_P4_OpenJudge/
├── OpenJudge/                    # 主应用程序目录
│   ├── app/                      # Flask应用程序核心
│   │   ├── models/              # 数据库模型 (User, Problem, Submission)
│   │   ├── routes/              # API端点和路由处理器
│   │   ├── tasks.py             # Celery异步判题任务定义
│   │   ├── utils/               # 辅助函数和工具
│   │   └── __init__.py          # Flask应用工厂
│   ├── test/                    # 综合测试套件
│   │   ├── test_basic.py        # 基本功能测试
│   │   ├── test_judge_integration.py  # 判题系统集成测试
│   │   ├── test_validation.py   # 参数验证和安全测试
│   │   ├── k6_performance_test.js     # k6性能测试脚本
│   │   ├── run_performance_test.sh    # 性能测试运行器
│   │   ├── test.sh              # 一键测试执行脚本
│   │   └── auth_helper.py       # 认证测试工具
│   ├── instance/                # 实例特定配置
│   ├── *.tf                     # Terraform基础设施文件
│   │   ├── main.tf              # 核心AWS基础设施 (ECS, ALB, VPC)
│   │   ├── rds.tf               # PostgreSQL数据库配置
│   │   ├── sqs.tf               # SQS消息队列设置
│   │   ├── celery.tf            # Celery工作器基础设施
│   │   └── autoscaling.tf       # 自动扩缩容策略
│   ├── deploy.sh                # 一键部署脚本
│   ├── dockerfile               # 容器镜像定义
│   ├── docker-compose.yml       # 本地开发环境
│   ├── pyproject.toml           # Python依赖和项目元数据
│   └── credentials              # AWS凭据 (手动创建)
└── README.md                    # 项目文档 (本文件)
```

**关键组件:**
- **`app/`**: 采用MVC架构的核心Flask应用程序
- **`test/`**: 包括云部署验证和安全测试的综合端点级测试
- **`*.tf`**: 使用Terraform的完整AWS基础设施即代码
- **`deploy.sh`**: 自动化部署管道
- **`docker-compose.yml`**: 本地开发环境设置 (主分支中不使用，这是云版本)

## 部署

### 架构栈
- **后端**: Flask (REST API)
- **认证**: JSON Web Token (JWT)
- **任务队列**: Celery 
- **消息代理**: AWS SQS
- **数据库**: PostgreSQL (AWS RDS)
- **负载均衡**: AWS应用负载均衡器 (ALB)
- **自动扩缩容**: API和工作器的ECS服务自动扩缩容
- **基础设施**: Terraform, Docker, AWS服务

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Flask Web     │    │  SQS Message    │    │ Celery Worker   │
│      API        │◄──►│     Broker      │◄──►│   (Async)       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                                              
         │                                              
         ▼                                              
┌─────────────────┐                          
│ PostgreSQL (RDS)│                          
│   (Database)    │                          
└─────────────────┘                          
```
**沙箱移除**: 与本地版本不同，我们在云版本中移除了判题沙箱。我们原本计划使用ECS RunTask通过boto3实现沙箱化容器判题来隔离用户代码执行。然而，在实施过程中我们发现，每次提交启动新容器在云环境中引入了不可接受的延迟。因此，我们移除了沙箱组件，现在直接在Celery工作器进程中执行判题逻辑。此决策的安全性和性能权衡在我们的最终项目报告中详细记录。

### 分支结构
由于配置差异，我使用主分支支持云部署版本和端点测试，而本地分支用于本地开发和内部测试。
- **`main` 分支**: 使用AWS基础设施的云部署生产版本（目前在上面的URL上运行）包含端点和性能测试。
- **`local` 分支**: 本地开发和内部测试环境

### 云部署 (main分支)

1. **导航到项目目录:**
   ```bash
   cd OpenJudge/
   ```

2. **配置AWS凭据:**
   创建名为`credentials`的文件，包含您的AWS凭据:
   ```ini
   [default]
   aws_access_key_id=YOUR_KEY
   aws_secret_access_key=YOUR_SECRET
   aws_session_token=YOUR_SESSION_TOKEN
   ```

3. **部署基础设施:**
   ```bash
   ./deploy.sh
   ```

部署脚本将:
- 初始化和升级Terraform模块
- 应用完整的AWS基础设施配置
- 成功完成后输出API端点URL

**建议您使用Ubuntu部署到AWS，以防出现一些奇怪的问题。** 

## 使用

### 使用模式

OpenJudge遵循传统的在线判题范式，类似于ACM/ICPC风格的在线判题模型，这与leetcode模式不同
- 学生为预定义的编程问题提交源代码解决方案
- 系统针对多个测试用例执行提交
- 每个测试用例接收判决结果(PASS/FAIL/ERROR)以及详细的输出比较
- **提交必须从标准输入读取输入并打印输出到标准输出**
- **仅支持python代码**


### 示例问题

**问题1: 奇数或偶数**

**描述**: 给定一个整数，如果是偶数则打印'even'，如果是奇数则打印'odd'。

**示例输入:**
```
3
```

**期望输出:**
```
odd
```

**正确提交 (Python):**
```python
n = int(input())
print('even' if n % 2 == 0 else 'odd')
```
**问题2: 阿姆斯特朗数**

**描述**: 检查一个3位数是否为阿姆斯特朗数。打印'yes'或'no'。

**示例输入:**
```
153
```

**期望输出:**
```
yes
```

**正确提交 (Python):**
```python
def is_armstrong_number(n):
    # 检查数字是否为3位数
    if not (100 <= n <= 999):
        return "no"

    # 将数字转换为字符串以便轻松访问其数字
    s_n = str(n)

    # 计算其数字的立方和
    sum_of_cubes = int(s_n[0]) ** 3 + int(s_n[1]) ** 3 + int(
        s_n[2]) ** 3

    # 检查是否为阿姆斯特朗数
    if sum_of_cubes == n:
        return "yes"
    else:
        return "no"


# 读取输入
n = int(input())

# 调用函数并打印结果
print(is_armstrong_number(n))
```

![Successful Test Result](/model/frontend_result.jpg)


## 测试策略

### 云测试 (main分支)
端点级集成测试、参数验证测试和性能测试(k6)位于`OpenJudge/test/`目录中。这些测试包括:
- API认证和授权
- 问题提交工作流  
- 判题执行和判决报告
- 数据库持久化和检索
- 用户隔离和访问控制
- 参数验证和安全测试
- 性能和负载测试

**测试文件:**
- **`test_basic.py`**: 核心功能测试，包括健康检查、认证和基本判题操作
- **`test_judge_integration.py`**: 各种代码场景的综合判题系统集成测试
- **`test_validation.py`**: 参数验证和安全测试，包括:
  - 认证字段验证 (注册/登录)
  - 缺失必需字段检测
  - 无效数据类型处理
  - 代码长度限制执行 (50KB)
  - 危险代码模式检测 (import os, eval, exec等)
  - 格式错误的JSON处理
  - 未授权访问防护
- **`k6_performance_test.js`**: 用于负载测试的k6性能测试脚本
- **`run_performance_test.sh`**: 性能测试运行器脚本
- **`test.sh`**: 运行所有三个测试套件(基本、集成、验证)的一键测试执行脚本
- **`auth_helper.py`**: 认证工具和测试辅助函数

**三阶段测试策略:**
1. **阶段1: 基本功能测试** - 核心系统健康和认证
2. **阶段2: 系统集成测试** - 端到端判题工作流验证  
3. **阶段3: 参数验证测试** - 安全和输入验证验证

更多信息请参考测试文件夹中的README.md。如果要进行更多测试，请切换到本地分支进行内部测试。

#### 使用k6进行性能测试
我们使用k6进行综合性能测试，模拟真实的学术工作负载并验证系统在峰值使用条件下的可扩展性。

**运行性能测试:**
```bash
cd OpenJudge/test

# 安装k6 (如果尚未安装)
# macOS: brew install k6
# Ubuntu: sudo apt-get install k6
# Windows: choco install k6

# 运行性能测试并自动保存结果
./run_performance_test.sh
```


**运行端点功能测试:**
```bash
cd OpenJudge/test
./test.sh
```
如果您选择自己部署服务，请将请求URL替换为您自己的URL，并通过pip安装requests库。

测试脚本将自动运行基本和集成测试套件，提供云部署的综合验证。

### 本地测试 (local分支)
由于本地和云环境之间的配置差异，我将代码库分为两个分支：local和main。local分支支持本地开发期间的内部功能测试(内部测试比端点测试全面得多！)。对于本地开发，可以使用以下命令执行内部功能和单元测试：
```bash
./build_and_test.sh
```
此命令将自动构建Docker镜像并在本地开发环境中运行所有内部单元和集成测试。

所有带描述的测试脚本都位于OpenJudge/localtest中
```bash
   cd OpenJudge/localtest 
```

此命令运行完整的测试套件，包括核心功能的单元测试和本地开发环境的集成测试。它内部调用位于OpenJudge/test/目录中的测试脚本。



---


## 🔒 安全功能

我们的OpenJudge平台实现了多项安全措施来保护用户数据并防止常见的Web漏洞：

### 认证和会话管理
- **HTTP-only Cookies**: JWT令牌存储在HTTP-only cookies中，以防止XSS攻击访问认证令牌
- **安全Cookie配置**: Cookies包含`SameSite=Lax`保护，防止CSRF攻击
- **密码安全**: 用户密码使用bcrypt和独立盐值进行哈希处理
- **JWT令牌过期**: 认证令牌在24小时后自动过期

### 代码执行安全
- **输入清理**: 所有用户输入在处理前都经过验证和清理
- **危险模式检测**: 代码提交会扫描潜在的不安全模式，包括:
  - 文件系统操作 (`import os`, `open()`, `file()`)
  - 网络操作 (`import socket`, `import requests`)
  - 系统操作 (`import subprocess`, `eval()`, `exec()`)
  - 破坏性操作 (`rmdir`, `remove`, `delete`)

### API安全
- **请求验证**: 所有API端点都验证JSON负载和参数类型
- **需要认证**: 受保护的端点需要通过HTTP-only cookies提供有效的JWT令牌
- **错误处理**: 不暴露敏感系统信息的安全错误消息

**注意**: 虽然我们出于性能原因移除了容器化沙箱，但直接执行方法包括全面的输入验证和危险代码模式检测以维护安全性。



