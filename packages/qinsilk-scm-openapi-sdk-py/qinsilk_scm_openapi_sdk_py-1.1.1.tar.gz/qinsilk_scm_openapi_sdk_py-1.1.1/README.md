# Qinsilk SCM OpenAPI SDK (Python)

本项目是 `qinsilk-scm-openapi-sdk` 提供了一个用于与 秦丝生产 ERP 开放平台 交互的客户端。

## 最近更新

### v0.1.1 - 签名传递修复

🔧 **重要修复**: 修复了与 Java SDK 签名不一致的问题

- **修复内容**:

  - 修复了`access_token`在签名计算中缺失的问题
  - 改进了签名算法以完全匹配 Java 版本的逻辑
  - 优化了 POST 请求中`access_token`的处理，避免重复传递
  - 确保`timestamp`正确保留在 POST 请求体中
  - 修复了请求体为空的问题，确保包含完整的参数信息
  - 改进了 null 值和空白字符串的处理逻辑

- **影响**: 确保 Python SDK 与 Java SDK 生成相同的签名，提高 API 调用成功率
- **向后兼容**: 此修复不影响现有的 API 调用接口

## 支持的 API 模块

本 SDK 支持以下 API 模块：

### 基础数据模块

- **商品管理** (`goods`): 商品的增删改查操作
- **颜色管理** (`color`): 颜色和颜色分组的管理
- **尺码管理** (`size`): 尺码和尺码分组的管理
- **供应商管理** (`supplier`): 供应商信息管理
- **仓库管理** (`storehouse`): 仓库信息管理
- **物料管理** (`material`): 物料信息管理
- **品牌管理** (`brand`): 品牌信息管理 🆕
- **用户管理** (`user`): 用户信息管理 🆕
- **波段管理** (`ranges`): 波段信息管理 🆕
- **物料类型管理** (`material_type`): 物料类型管理 🆕

### 单据模块

- **生产订单** (`order`): 生产订单的创建和管理 🆕

### 报表模块

- **生产报表** (`report`): 各种生产相关报表查询 🆕
  - 生产单明细报表
  - 生产单工序报表
  - 商品工序明细报表
  - 薪资计件报表
  - 采购单明细报表
  - 领料单明细报表

### 对象存储模块

- **OSS** (`oss`): 文件上传临时 URL 申请 🆕

> 🆕 标记表示最近更新同步的新功能模块

## 安装

您可以通过 pip 直接安装本 SDK：

```bash
pip install qinsilk-scm-openapi-sdk-py
```

## 使用方法

### 初始化客户端

SDK 的核心是 `OpenClient`。您需要使用包含您的凭据的 `OpenConfig` 对象来初始化它。

```python
from qinsilk_scm_openapi_sdk_py import OpenClient, OpenConfig

# 配置您的客户端ID、密钥和服务器地址
config = OpenConfig(
    client_id="your_client_id",
    client_secret="your_client_secret",
    server_url="https://your.api.server/"
)

client = OpenClient(config)
```

> **建议**：您也可以通过环境变量来配置 `OpenConfig`，以避免在代码中硬编码敏感信息。
> `OpenConfig` 会自动从环境变量中读取这些值。
>
> - `SCM_CLIENT_ID`: 您的客户端 ID
> - `SCM_CLIENT_SECRET`: 您的客户端密钥
> - `SCM_SERVER_URL`: 您的 API 服务器地址

### 发起 API 调用

要发起一个 API 调用，您需要创建一个继承自 `BaseRequest` 的请求对象。

例如，要获取商品列表，您可以创建一个 `GetProductListRequest` 类：

```python
from dataclasses import dataclass
from qinsilk_scm_openapi_sdk_py import BaseRequest, BaseResponse, OpenException
from typing import Type, List

@dataclass
class Product:
    id: str
    name: str

@dataclass
class GetProductListResponse(BaseResponse):
    products: List[Product]

@dataclass
class GetProductListRequest(BaseRequest[GetProductListResponse]):
    page: int = 1
    page_size: int = 10

    @property
    def response_class(self) -> Type[GetProductListResponse]:
        return GetProductListResponse

    @property
    def api_url(self) -> str:
        return "api/products/list"

    def get_request_type(self) -> str:
        return "GET"

# 执行请求
try:
    product_request = GetProductListRequest(page=1)
    _, response = client.execute(product_request)

    if response.is_success():
        for product in response.products:
            print(f"商品: {product.name}")

except OpenException as e:
    print(f"发生错误: {e}")

```

`GetProductListRequest` 只是一个示例，您可以根据需要为其他接口扩展 SDK。

## 项目结构

- `qinsilk_scm_openapi_sdk_py/` (项目根目录)
  - `qinsilk_scm_openapi_sdk_py/`: Python 包目录。
    - `client.py`: 包含 `OpenClient` 和 `OpenConfig`。
    - `models/`: 包含 `BaseRequest`, `BaseResponse` 以及其他数据模型。
    - `signing.py`: 处理 API 请求签名。
    - `exceptions.py`: 自定义异常。
  - `examples/`: 用法示例脚本。
    - `example_brand.py`: 品牌管理示例
    - `example_user.py`: 用户管理示例
    - `example_ranges.py`: 波段管理示例
    - `example_oss.py`: OSS 文件上传示例
    - `example_material_type.py`: 物料类型管理示例
    - `example_produce_order.py`: 生产订单管理示例
    - `example_report.py`: 报表查询示例
    - `example_storehouse.py`: 仓库管理示例（已更新）
    - 以及其他基础模块示例文件...
  - `README.md`: 本文档。

## 打包命令

```
python -m pip install --upgrade setuptools wheel twine
python setup.py sdist bdist_wheel
```

## 上传命令

```
 twine upload dist/*
```
