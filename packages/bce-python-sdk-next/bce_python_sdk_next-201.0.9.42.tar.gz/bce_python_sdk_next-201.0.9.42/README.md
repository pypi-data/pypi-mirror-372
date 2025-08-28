# bce-python-sdk三方版

## 简介

bce-python-sdk三方版，适配官方尚未支持的某些产品API，例如AIHC

## 安装

- 本地安装

```
python setup.py install
```

- pip安装

```
pip install bce-python-sdk-next
```

## AIHC服务详细使用指南

### 模块化结构说明

AIHC SDK采用模块化结构设计，将不同功能划分为独立的模块，提高了代码的可维护性和可扩展性。最新版本修复了IDE类型提示问题，确保开发体验更加友好。

项目结构：
```
baidubce/services/aihc/
├── base/                          # 基础模块
│   ├── __init__.py
│   ├── aihc_base_client.py       # 基础客户端类
│   └── aihc_common.py            # 公共工具函数
├── modules/                       # 业务模块目录
│   ├── __init__.py
│   ├── job/                      # 任务模块
│   │   ├── __init__.py
│   │   └── job_client.py         # 任务相关接口
│   ├── dataset/                  # 数据集模块
│   │   ├── __init__.py
│   │   └── dataset_client.py     # 数据集相关接口
│   ├── model/                    # 模型模块
│   │   ├── __init__.py
│   │   └── model_client.py       # 模型相关接口
│   ├── service/                  # 在线服务模块
│   │   ├── __init__.py
│   │   └── service_client.py     # 服务相关接口
│   └── dev_instance/             # 开发机模块
│       ├── __init__.py
│       └── dev_instance_client.py # 开发机相关接口
├── aihc_client.py                # 重构后的主客户端文件
├── aihc_model.py                 # 保留原有模型文件
├── aihc_handler.py               # 保留原有处理器文件
├── aihc_client_original.py       # 原始文件备份
└── __init__.py                   # 主入口文件
```

### 客户端初始化

AIHC SDK提供了多种客户端初始化方式，您可以根据需要选择最适合的方式：

#### 1. 使用主客户端（推荐）
```python
from baidubce.services.aihc.aihc_client import AihcClient
from baidubce.bce_client_configuration import BceClientConfiguration
from baidubce.auth.bce_credentials import BceCredentials

# 创建配置
config = BceClientConfiguration(
    credentials=BceCredentials('your-access-key-id', 'your-secret-access-key'),
    endpoint='https://aihc.bj.baidubce.com'
)

# 创建客户端
client = AihcClient(config)

# 使用各种接口
client.DescribeJobs(resourcePoolId='your-pool-id')
client.DescribeDatasets()
client.DescribeModels()
```

#### 2. 使用独立模块客户端
```python
from baidubce.services.aihc.modules.job import JobClient
from baidubce.services.aihc.modules.dataset import DatasetClient
from baidubce.bce_client_configuration import BceClientConfiguration
from baidubce.auth.bce_credentials import BceCredentials

# 创建配置
config = BceClientConfiguration(
    credentials=BceCredentials('your-access-key-id', 'your-secret-access-key'),
    endpoint='https://aihc.bj.baidubce.com'
)

# 使用特定模块
job_client = JobClient(config)
dataset_client = DatasetClient(config)

# 调用模块特定方法
job_client.DescribeJobs(resourcePoolId='your-pool-id')
dataset_client.DescribeDatasets()
```

#### 3. 直接访问子模块（新特性）
```python
from baidubce.services.aihc.aihc_client import AihcClient

# 创建客户端
client = AihcClient(config)

# 直接访问子模块
client.job.DescribeJobs(resourcePoolId='your-pool-id')
client.dataset.DescribeDatasets()
client.model.DescribeModels()
client.service.DescribeServices()
client.dev_instance.DescribeDevInstances()
```

### 主要功能模块API说明

#### 1. 任务管理模块 (job)
任务模块提供了对AI训练任务的完整管理功能：

- `DescribeJobs()`: 查询训练任务列表
- `DescribeJob()`: 查询训练任务详情
- `CreateJob()`: 创建训练任务
- `DeleteJob()`: 删除训练任务
- `StopJob()`: 停止训练任务
- `UpdateJob()`: 更新训练任务
- `DescribeJobEvents()`: 查询训练任务事件
- `DescribeJobLogs()`: 查询训练任务日志
- `DescribeJobPodEvents()`: 查询训练任务Pod事件
- `DescribeJobNodeNames()`: 查询训练任务所在节点列表
- `GetJobWebTerminalUrl()`: 获取训练任务WebTerminal地址

#### 2. 数据集管理模块 (dataset)
数据集模块提供了对AI训练数据集的管理功能：

- `DescribeDatasets()`: 获取数据集列表
- `DescribeDataset()`: 获取数据集详情
- `CreateDataset()`: 创建数据集
- `ModifyDataset()`: 修改数据集
- `DeleteDataset()`: 删除数据集
- `DescribeDatasetVersions()`: 获取数据集版本列表
- `DescribeDatasetVersion()`: 获取数据集版本详情
- `CreateDatasetVersion()`: 创建数据集版本
- `DeleteDatasetVersion()`: 删除数据集版本

#### 3. 模型管理模块 (model)
模型模块提供了对AI模型的管理功能：

- `DescribeModels()`: 获取模型列表
- `CreateModel()`: 创建模型
- `DeleteModel()`: 删除模型
- `ModifyModel()`: 修改模型
- `DescribeModel()`: 获取模型详情
- `DescribeModelVersions()`: 获取模型版本列表
- `DescribeModelVersion()`: 获取模型版本详情
- `CreateModelVersion()`: 新建模型版本
- `DeleteModelVersion()`: 删除模型版本

#### 4. 在线服务模块 (service)
在线服务模块提供了对AI模型在线部署服务的管理功能：

- `DescribeServices()`: 拉取服务列表
- `DescribeService()`: 查询服务详情
- `DescribeServiceStatus()`: 获取服务状态

#### 5. 开发机模块 (dev_instance)
开发机模块提供了对AI开发环境的管理功能：

- `DescribeDevInstances()`: 查询开发机列表
- `DescribeDevInstance()`: 查询开发机详情
- `StartDevInstance()`: 开启开发机实例
- `StopDevInstance()`: 停止开发机实例

#### 6. 资源池模块 (resource_pool)
资源池模块提供了对计算资源池的管理功能：

- `DescribeResourcePools()`: 获取资源池列表
- `DescribeResourcePool()`: 获取资源池详情

#### 7. 队列模块 (queue)
队列模块提供了对任务队列的管理功能：

- `DescribeQueues()`: 获取队列列表
- `DescribeQueue()`: 获取队列详情

## 示例代码说明

AIHC SDK提供了丰富的示例代码，帮助您快速上手使用各种功能。

### 环境准备

- 准备 Python 3.8+ 运行环境（建议使用虚拟环境）。
- 在仓库根目录执行示例，或确保已将仓库根目录加入 `PYTHONPATH`。

### 配置

编辑 `sample/aihc/aihc_sample_conf.py`，设置以下参数为你自己的值：

- `HOST`: AIHC 服务接入域名，例如 `aihc.bj.baidubce.com`
- `AK`: 访问密钥 AccessKey
- `SK`: 访问密钥 SecretKey

### 运行示例

#### 推荐方式（模块方式，优先使用本地源码）

```
cd /Users/luyuchao/Documents/GitHub/bce-sdk-python
python -m sample.aihc.aihc_model_sample
```

#### 备用方式（显式指定本地源码路径）

```
export PYTHONPATH=/Users/luyuchao/Documents/GitHub/bce-sdk-python
python /Users/luyuchao/Documents/GitHub/bce-sdk-python/sample/aihc/aihc_model_sample.py
```

#### 其他示例

```
python -m sample.aihc.aihc_dataset_sample
python -m sample.aihc.aihc_job_sample
python -m sample.aihc.aihc_service_sample
python -m sample.aihc.aihc_devinstance_sample
python -m sample.aihc.aihc_base_sample
python -m sample.aihc.aihc_pool_sample
```

## 常见问题解答

### ImportError: cannot import name 'AihcClient'
- **原因**: 命中了环境中已安装的旧版 `baidubce` 包（不包含 `AihcClient`），而非当前仓库源码。
- **解决**: 使用"模块方式运行"或设置 `PYTHONPATH` 指向仓库根目录；或在当前环境卸载旧版包后重试：

```
pip uninstall baidubce
```

## 故障排除

### IDE类型提示问题
如果IDE仍然显示 `any`，请尝试：
1. 重启IDE
2. 清除IDE缓存
3. 重新加载项目
4. 检查Python语言服务器状态

### 模块导入问题
确保正确导入模块：
```python
# 正确的导入方式
from baidubce.services.aihc import AihcClient
```