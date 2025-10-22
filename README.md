# OpenJudge - 面向教育和自主学习的在线判题平台


## 项目简介

OpenJudge是一个专为教育设计的在线判题平台，致力于解决现有竞赛编程平台不利于使用者自我检查和纠正的特性。与LeetCode、Codeforces等传统平台不同，这些平台为了防作弊而隐藏测试用例，而我们的系统**完全公开所有测试用例**，让学生能够清楚看到每个测试点的具体情况。目前这个MVP版本仅支持**Python**编程。

这种完全透明的设计让学生能够：
- **从失败中学习** - 清楚看到哪些测试用例没有通过
- **高效调试** - 对比期望输出与实际输出，快速定位问题
- **提升解题能力** - 通过详细的反馈不断改进代码
- **掌握边界情况** - 了解可能遗漏的特殊情况

平台延续了经典的在线判题模式，但更注重学习效果而非竞技排名。

## 🚀 在线体验

**平台地址**: [http://coughoverflow-alb-1348614147.us-east-1.elb.amazonaws.com/](http://coughoverflow-alb-1348614147.us-east-1.elb.amazonaws.com/)

**体验账号:**
- **用户名**: `CSSE6400`
- **密码**: `qimojiayou`

使用上述账号即可体验平台功能，提交代码解题，感受这个以教学和自我学习及纠正为核心的在线判题环境。

## 📁 项目结构

```
2025_P4_OpenJudge/
├── OpenJudge/                    # 主程序目录
│   ├── app/                      # Flask应用核心
│   │   ├── models/              # 数据模型 (用户、题目、提交)
│   │   ├── routes/              # API接口和路由处理
│   │   ├── tasks.py             # Celery异步判题任务
│   │   ├── utils/               # 工具函数
│   │   └── __init__.py          # Flask应用工厂
│   ├── test/                    # 测试套件
│   │   ├── test_basic.py        # 基础功能测试
│   │   ├── test_judge_integration.py  # 判题系统集成测试
│   │   ├── test_validation.py   # 参数验证和安全测试
│   │   ├── k6_performance_test.js     # k6性能测试
│   │   ├── run_performance_test.sh    # 性能测试运行器
│   │   ├── test.sh              # 一键测试脚本
│   │   └── auth_helper.py       # 认证测试工具
│   ├── instance/                # 实例配置
│   ├── *.tf                     # Terraform基础设施文件
│   │   ├── main.tf              # AWS核心基础设施 (ECS, ALB, VPC)
│   │   ├── rds.tf               # PostgreSQL数据库配置
│   │   ├── sqs.tf               # SQS消息队列配置
│   │   ├── celery.tf            # Celery工作器配置
│   │   └── autoscaling.tf       # 自动扩缩容配置
│   ├── deploy.sh                # 一键部署脚本
│   ├── dockerfile               # 容器镜像配置
│   ├── docker-compose.yml       # 本地开发环境
│   ├── pyproject.toml           # Python依赖配置
│   └── credentials              # AWS认证信息 (需手动创建)
└── README.md                    # 项目说明文档
```

**核心模块:**
- **`app/`**: 采用MVC架构的Flask主应用
- **`test/`**: 包含云部署验证和安全测试的完整测试套件
- **`*.tf`**: 基于Terraform的AWS基础设施代码
- **`deploy.sh`**: 自动化部署流程
- **`docker-compose.yml`**: 本地开发环境 (主分支为云版本，不使用此配置)

## 部署说明

### 技术架构
- **后端框架**: Flask (REST API)
- **身份认证**: JSON Web Token (JWT)
- **任务队列**: Celery 
- **消息中间件**: AWS SQS
- **数据存储**: PostgreSQL (AWS RDS)
- **负载均衡**: AWS应用负载均衡器 (ALB)
- **弹性伸缩**: ECS服务自动扩缩容
- **基础设施**: Terraform + Docker + AWS服务

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
**注意**: 与本地版本不同，云版本中我们移除了判题沙箱机制。原本计划通过ECS RunTask实现容器化判题来隔离用户代码，但在实际部署中发现，每次提交都启动新容器会带来无法接受的延迟。因此，我们改为直接在Celery工作进程中执行判题，在安全性和性能之间找到了平衡点。详细的技术决策分析请参考项目报告。若未来迁移到ec2，可使用其他更好方式（如linux自带隔离机制）实现隔离。

### 分支管理
考虑到本地和云端环境的配置差异，我们采用双分支策略：
- **`main` 分支**: 云部署的生产版本，包含完整的AWS基础设施和端点测试 （英文说明）
- **`CN` 分支**: 云部署的生产版本，包含完整的AWS基础设施和端点测试（中文版说明）
- **`local` 分支**: 暂未上传github

### 云端部署 (main分支)

1. **进入项目目录:**
   ```bash
   cd OpenJudge/
   ```

2. **配置AWS认证:**
   创建`credentials`文件，填入您的AWS认证信息:
   ```ini
   [default]
   aws_access_key_id=YOUR_KEY
   aws_secret_access_key=YOUR_SECRET
   aws_session_token=YOUR_SESSION_TOKEN
   ```

3. **一键部署:**
   ```bash
   ./deploy.sh
   ```

部署脚本会自动完成:
- 初始化并更新Terraform模块
- 部署完整的AWS基础设施
- 部署完成后输出API访问地址

**建议使用Ubuntu系统进行AWS部署，避免潜在的兼容性问题。** 

## 使用指南

### 平台特色

OpenJudge采用经典的ACM/ICPC在线判题模式，与LeetCode等平台有明显区别：
- 学生需要为编程题目提交完整的源代码
- 系统会运行多个测试用例来验证代码
- 每个测试用例都会给出详细的结果(PASS/FAIL/ERROR)和输出对比
- **代码必须从标准输入读取数据，向标准输出打印结果**
- **目前仅支持Python语言**


### 题目示例

**题目1: 奇偶判断**

**题目描述**: 给定一个整数，判断它是奇数还是偶数。如果是偶数输出'even'，奇数输出'odd'。

**输入样例:**
```
3
```

**输出样例:**
```
odd
```

**参考代码 (Python):**
```python
n = int(input())
print('even' if n % 2 == 0 else 'odd')
```

**题目2: 阿姆斯特朗数**

**题目描述**: 判断一个3位数是否为阿姆斯特朗数。如果是输出'yes'，否则输出'no'。

**输入样例:**
```
153
```

**输出样例:**
```
yes
```

**参考代码 (Python):**
```python
def is_armstrong_number(n):
    # 检查是否为3位数
    if not (100 <= n <= 999):
        return "no"

    # 转换为字符串便于处理各位数字
    s_n = str(n)

    # 计算各位数字的立方和
    sum_of_cubes = int(s_n[0]) ** 3 + int(s_n[1]) ** 3 + int(s_n[2]) ** 3

    # 判断是否为阿姆斯特朗数
    if sum_of_cubes == n:
        return "yes"
    else:
        return "no"

# 读取输入并输出结果
n = int(input())
print(is_armstrong_number(n))
```

![Successful Test Result](/model/frontend_result.jpg)


## 测试体系

### 云端测试 (main分支)
`OpenJudge/test/`目录包含了完整的测试套件，涵盖端点集成、参数验证和性能测试:
- API身份认证和权限控制
- 题目提交完整流程  
- 判题执行和结果反馈
- 数据持久化和查询
- 用户隔离和访问控制
- 输入验证和安全防护
- 系统性能和负载测试

**测试文件说明:**
- **`test_basic.py`**: 基础功能测试，包括系统健康检查和用户认证
- **`test_judge_integration.py`**: 判题系统集成测试，覆盖各种代码场景
- **`test_validation.py`**: 安全验证测试，包含:
  - 用户注册/登录字段验证
  - 必填字段缺失检测
  - 数据类型错误处理
  - 代码长度限制 (50KB)
  - 危险代码模式识别 (import os, eval, exec等)
  - JSON格式错误处理
  - 未授权访问拦截
- **`k6_performance_test.js`**: k6负载测试脚本
- **`run_performance_test.sh`**: 性能测试执行器
- **`test.sh`**: 一键运行所有测试套件
- **`auth_helper.py`**: 认证测试辅助工具

**三层测试架构:**
1. **基础层**: 系统健康检查和用户认证
2. **集成层**: 完整的判题流程验证  
3. **安全层**: 输入验证和安全防护

详细测试说明请查看测试目录中的README.md。如需更深入的内部测试，请切换到local分支。

#### k6性能测试
我们使用k6工具进行全面的性能测试，模拟真实的学术使用场景，验证系统在高并发情况下的稳定性。

**执行性能测试:**
```bash
cd OpenJudge/test

# 安装k6 (如未安装)
# macOS: brew install k6
# Ubuntu: sudo apt-get install k6
# Windows: choco install k6

# 执行性能测试并保存结果
./run_performance_test.sh
```

**执行功能测试:**
```bash
cd OpenJudge/test
./test.sh
```
如需自行部署服务，请替换测试脚本中的URL地址，并安装requests库。

测试脚本会自动执行基础功能和集成测试，全面验证云端部署的稳定性。

### 本地测试 (local分支)
考虑到本地和云端环境的配置差异，我们采用双分支策略。local分支专门用于本地开发，支持更全面的内部功能测试。本地开发时，可执行以下命令进行内部测试：
```bash
./build_and_test.sh
```
该命令会自动构建Docker镜像，并在本地环境中运行所有单元测试和集成测试。

所有测试脚本和说明文档位于OpenJudge/localtest目录：
```bash
cd OpenJudge/localtest 
```

该命令会运行完整的测试套件，包括核心功能的单元测试和本地环境的集成测试，内部会调用OpenJudge/test/目录中的测试脚本。



---


## 🔒 安全防护

OpenJudge平台采用多层安全防护机制，确保用户数据安全和系统稳定运行：

### 身份认证与会话管理
- **HTTP-only Cookies**: JWT令牌存储在HTTP-only cookies中，有效防止XSS攻击
- **安全Cookie策略**: 设置`SameSite=Lax`属性，防范CSRF攻击
- **密码加密**: 采用bcrypt算法和独立盐值对用户密码进行加密存储
- **令牌时效**: 认证令牌24小时自动失效，确保安全性

### 代码执行安全
- **输入验证**: 所有用户输入都经过严格验证和过滤
- **危险代码检测**: 自动识别并拦截潜在的安全风险代码:
  - 文件系统操作 (`import os`, `open()`, `file()`)
  - 网络通信 (`import socket`, `import requests`)
  - 系统调用 (`import subprocess`, `eval()`, `exec()`)
  - 文件删除操作 (`rmdir`, `remove`, `delete`)

### API接口安全
- **请求校验**: 所有API接口都进行JSON格式和参数类型验证
- **权限控制**: 受保护接口需要有效的JWT令牌认证
- **错误处理**: 采用安全的错误信息，避免泄露系统敏感信息

**安全说明**: 虽然为了性能考虑移除了容器化沙箱，但我们通过全面的输入验证和危险代码检测机制来保障系统安全。







