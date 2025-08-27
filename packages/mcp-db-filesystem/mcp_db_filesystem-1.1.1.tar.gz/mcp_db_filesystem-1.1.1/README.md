# MCP Database Filesystem

[English](README_EN.md) | 中文

一个简洁高效的 MCP (Model Context Protocol) 服务器，提供多数据库访问和文件系统操作功能。

## ✨ 主要特性

### 🗄️ 多数据库支持

#### SQL Server
- **SQL 查询执行** - 支持 SELECT 查询
- **SQL 命令执行** - 支持 INSERT/UPDATE/DELETE 操作
- **表结构查询** - 获取表的详细结构信息和字段描述
- **表列表** - 列出数据库中的所有表

#### MySQL
- **MySQL 查询执行** - 支持 MySQL SELECT 查询
- **MySQL 命令执行** - 支持 INSERT/UPDATE/DELETE 操作
- **MySQL 表结构查询** - 获取 MySQL 表的详细结构信息
- **MySQL 表列表** - 列出 MySQL 数据库中的所有表

#### Redis
- **键值操作** - GET/SET/DELETE 键值对
- **键管理** - 列出匹配模式的键
- **服务器信息** - 获取 Redis 服务器状态信息
- **过期设置** - 支持键的过期时间设置

### 📁 文件系统功能
- **文件读取** - 读取文件内容
- **文件写入** - 写入内容到文件
- **目录列表** - 列出目录内容

### 🔒 安全特性
- SQL 注入防护
- 文件系统访问控制
- 环境变量配置
- 权限验证

### 🔄 容错机制
- **优雅降级** - 任何数据库连接失败时不影响其他服务
- **动态重连** - 支持运行时重新连接各种数据库
- **状态监控** - 实时监控所有数据库连接状态

## 🚀 快速开始

### 📋 前置要求

根据您要使用的数据库服务，安装相应的驱动程序：

#### 1. SQL Server (可选)
安装 ODBC Driver for SQL Server

**Windows:**
```bash
# 下载并安装 Microsoft ODBC Driver 17 for SQL Server
# 访问: https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server
# 或使用 winget 安装
winget install Microsoft.ODBCDriverforSQLServer
```

**macOS:**
```bash
# 使用 Homebrew 安装
brew tap microsoft/mssql-release https://github.com/Microsoft/homebrew-mssql-release
brew update
brew install msodbcsql17 mssql-tools
```

**Linux (Ubuntu/Debian):**
```bash
# 添加 Microsoft 仓库
curl https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -
curl https://packages.microsoft.com/config/ubuntu/20.04/prod.list | sudo tee /etc/apt/sources.list.d/msprod.list

# 安装驱动
sudo apt-get update
sudo apt-get install msodbcsql17
```

#### 2. 验证 ODBC 安装

```bash
# Windows
odbcad32.exe

# macOS/Linux
odbcinst -j
```

#### 2. MySQL (可选)
如果要使用 MySQL 功能，确保 MySQL 服务器可访问。不需要额外的客户端驱动，PyMySQL 已包含在依赖中。

#### 3. Redis (可选)
如果要使用 Redis 功能，确保 Redis 服务器可访问。不需要额外的客户端驱动，redis-py 已包含在依赖中。

### 📦 零安装使用（推荐）

```bash
# 安装 uv（如果尚未安装）
pip install uv

# 直接运行 - 无需克隆仓库！
uvx mcp-db-filesystem@latest
```

### 🔧 配置

在你的 MCP 客户端（如 Claude Desktop、AugmentCode）中添加以下配置：

```json
{
  "mcpServers": {
    "mcp-db-filesystem": {
      "command": "uvx",
      "args": ["mcp-db-filesystem@latest"],
      "env": {
        // SQL Server Configuration (可选)
        "MSSQL_SERVER": "localhost",
        "MSSQL_DATABASE": "your_database",
        "MSSQL_USERNAME": "your_username",
        "MSSQL_PASSWORD": "your_password",
        "MSSQL_USE_WINDOWS_AUTH": "true",
        "MSSQL_PORT": "1433",
        "MSSQL_DRIVER": "ODBC Driver 17 for SQL Server",
        "MSSQL_CONNECTION_TIMEOUT": "30",
        "MSSQL_COMMAND_TIMEOUT": "30",
        "MSSQL_POOL_SIZE": "5",
        "MSSQL_MAX_OVERFLOW": "10",
        "MSSQL_TRUST_SERVER_CERTIFICATE": "true",
        "MSSQL_ENCRYPT": "false",
        "MSSQL_MULTIPLE_ACTIVE_RESULT_SETS": "true",
        "MSSQL_APPLICATION_NAME": "MCP-Db-Filesystem",

        // MySQL Configuration (可选)
        "MYSQL_HOST": "localhost",
        "MYSQL_PORT": "3306",
        "MYSQL_DATABASE": "your_mysql_database",
        "MYSQL_USERNAME": "your_mysql_username",
        "MYSQL_PASSWORD": "your_mysql_password",
        "MYSQL_CHARSET": "utf8mb4",
        "MYSQL_CONNECTION_TIMEOUT": "30",
        "MYSQL_POOL_SIZE": "5",
        "MYSQL_MAX_OVERFLOW": "10",

        // Redis Configuration (可选)
        "REDIS_HOST": "localhost",
        "REDIS_PORT": "6379",
        "REDIS_DB": "0",
        "REDIS_PASSWORD": "your_redis_password",
        "REDIS_SOCKET_TIMEOUT": "30",
        "REDIS_CONNECTION_TIMEOUT": "30",
        "REDIS_MAX_CONNECTIONS": "10",

        // Filesystem Configuration
        "FS_ALLOWED_PATHS": "*",
        "FS_ALLOWED_EXTENSIONS": "*.*",
        "FS_IGNORE_FILE_LOCKS": "false",

        // Security Configuration
        "SECURITY_ENABLE_SQL_INJECTION_PROTECTION": "true",
        "SECURITY_MAX_QUERY_LENGTH": "10000",
        "SECURITY_ENABLE_QUERY_LOGGING": "true",
        "SECURITY_LOG_SENSITIVE_DATA": "false",

        // Server Configuration
        "SERVER_LOG_LEVEL": "INFO",
        "SERVER_DEBUG": "false"
      }
    }
  }
}
```

## 🛠️ 可用工具

### SQL Server 工具
- `sql_query` - 执行 SQL Server SELECT 查询
- `sql_execute` - 执行 SQL Server INSERT/UPDATE/DELETE 命令
- `list_tables` - 列出 SQL Server 数据库中的所有表
- `get_table_schema` - 获取 SQL Server 表的结构信息
- `database_reconnect` - 重新连接 SQL Server

### MySQL 工具
- `mysql_query` - 执行 MySQL SELECT 查询
- `mysql_execute` - 执行 MySQL INSERT/UPDATE/DELETE 命令
- `mysql_list_tables` - 列出 MySQL 数据库中的所有表
- `mysql_get_table_schema` - 获取 MySQL 表的结构信息
- `mysql_reconnect` - 重新连接 MySQL

### Redis 工具
- `redis_get` - 获取 Redis 键值
- `redis_set` - 设置 Redis 键值（支持过期时间）
- `redis_delete` - 删除 Redis 键
- `redis_keys` - 列出匹配模式的 Redis 键
- `redis_info` - 获取 Redis 服务器信息
- `redis_reconnect` - 重新连接 Redis

### 数据库管理工具
- `database_status` - 检查所有数据库连接状态

### 文件系统工具
- `read_file` - 读取文件内容
- `write_file` - 写入文件内容
- `list_directory` - 列出目录内容

## 📋 环境变量

### SQL Server 配置
- `MSSQL_SERVER` - SQL Server 服务器地址
- `MSSQL_DATABASE` - 数据库名称
- `MSSQL_USERNAME` - 用户名
- `MSSQL_PASSWORD` - 密码
- `MSSQL_USE_WINDOWS_AUTH` - 是否使用 Windows 身份验证
- `MSSQL_PORT` - SQL Server 端口（默认 1433）
- `MSSQL_DRIVER` - ODBC 驱动名称
- `MSSQL_CONNECTION_TIMEOUT` - 连接超时时间（秒）
- `MSSQL_COMMAND_TIMEOUT` - 命令超时时间（秒）
- `MSSQL_POOL_SIZE` - 连接池大小
- `MSSQL_MAX_OVERFLOW` - 最大溢出连接数
- `MSSQL_TRUST_SERVER_CERTIFICATE` - 是否信任服务器证书
- `MSSQL_ENCRYPT` - 是否加密连接
- `MSSQL_MULTIPLE_ACTIVE_RESULT_SETS` - 是否启用多活动结果集
- `MSSQL_APPLICATION_NAME` - 应用程序名称

### MySQL 配置
- `MYSQL_HOST` - MySQL 服务器地址
- `MYSQL_PORT` - MySQL 端口（默认 3306）
- `MYSQL_DATABASE` - MySQL 数据库名称
- `MYSQL_USERNAME` - MySQL 用户名
- `MYSQL_PASSWORD` - MySQL 密码
- `MYSQL_CHARSET` - 字符集（默认 utf8mb4）
- `MYSQL_CONNECTION_TIMEOUT` - 连接超时时间（秒）
- `MYSQL_POOL_SIZE` - 连接池大小
- `MYSQL_MAX_OVERFLOW` - 最大溢出连接数

### Redis 配置
- `REDIS_HOST` - Redis 服务器地址
- `REDIS_PORT` - Redis 端口（默认 6379）
- `REDIS_DB` - Redis 数据库编号（默认 0）
- `REDIS_PASSWORD` - Redis 密码（可选）
- `REDIS_SOCKET_TIMEOUT` - Socket 超时时间（秒）
- `REDIS_CONNECTION_TIMEOUT` - 连接超时时间（秒）
- `REDIS_MAX_CONNECTIONS` - 最大连接数

### 文件系统配置
- `FS_ALLOWED_PATHS` - 允许访问的路径（`*` 表示所有路径）
- `FS_ALLOWED_EXTENSIONS` - 允许的文件扩展名（`*.*` 表示所有文件）
- `FS_IGNORE_FILE_LOCKS` - 是否忽略文件锁

## 🔧 开发

### 本地开发

```bash
# 克隆仓库
git clone https://github.com/ppengit/mcp-db-filesystem.git
cd mcp-db-filesystem

# 安装依赖
uv sync

# 运行服务器
uv run python -m mcp_db_filesystem server
```

### 测试

```bash
# 运行测试
uv run pytest

# 运行特定测试
uv run pytest tests/test_database.py
```

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件。

## 🤝 贡献

欢迎贡献！请提交 Issue 或 Pull Request。

## ❓ 常见问题

### Q: 出现 "No module named 'pyodbc'" 错误
A: 请确保已安装 ODBC Driver for SQL Server，参见上面的前置要求部分。

### Q: 出现 "Data source name not found" 错误
A: 检查 `DB_SERVER` 配置是否正确，确保 SQL Server 服务正在运行。

### Q: 连接超时或拒绝连接
A:
1. 检查 SQL Server 是否启用了 TCP/IP 协议
2. 确认防火墙设置允许连接到 SQL Server 端口（默认1433）
3. 验证用户名和密码是否正确

### Q: 文件系统操作被拒绝
A: 检查 `FS_ALLOWED_PATHS` 和 `FS_ALLOWED_EXTENSIONS` 配置，确保路径和文件类型被允许访问。

## 📞 支持

- GitHub Issues: [https://github.com/ppengit/mcp-db-filesystem/issues](https://github.com/ppengit/mcp-db-filesystem/issues)

## 🔄 更新日志

### v1.0.1
- 🎉 首个稳定版本发布
- ✨ 完整的 SQL Server 数据库支持
- 📁 全面的文件系统操作
- 🔒 增强的安全特性
- 📝 改进的错误处理和日志记录
- 🚀 简化的架构，专注于核心功能

---

**注意**: 此版本专注于核心功能的稳定性和可靠性，提供简洁高效的MCP服务器体验。
