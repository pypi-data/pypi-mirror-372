# Karma MVP - 多域智能助手

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-0.1.0-orange.svg)](https://github.com/karma-ai/karma-mvp)

Karma MVP 是一个多域智能 AI 助手，采用三层记忆架构（全局-工作区-会话），为用户提供个性化的、上下文感知的对话体验。

## ✨ 主要特性

- 🧠 **三层记忆架构**: 全局用户偏好、工作区项目知识、会话实时上下文
- 🎯 **多域适应**: 自动识别技术开发、学术研究、创意设计、商业规划、个人管理五大领域
- 🔧 **多LLM支持**: OpenAI GPT、Claude、自定义API等多种LLM提供商
- 💾 **本地数据存储**: 所有数据存储在本地，保护隐私安全
- 🎨 **丰富的CLI界面**: 使用 Rich 库打造美观的命令行交互体验
- 📊 **调试分析模式**: 提供详细的系统行为分析和对话效果调试

## 🚀 快速安装

### 方式一：pip 安装 (推荐普通用户)

```bash
pip install karma-mvp
```

### 方式二：Poetry 安装 (推荐开发者)

```bash
# 克隆仓库
git clone https://github.com/karma-ai/karma-mvp.git
cd karma-mvp

# 安装依赖
poetry install

# 激活虚拟环境
poetry shell
```

### 方式三：一键安装脚本

**Linux/macOS:**
```bash
curl -sSL https://raw.githubusercontent.com/karma-ai/karma-mvp/main/install.sh | bash
```

**Windows (PowerShell):**
```powershell
iex ((New-Object System.Net.WebClient).DownloadString('https://raw.githubusercontent.com/karma-ai/karma-mvp/main/install.ps1'))
```

### 方式四：从源码安装

```bash
# 克隆仓库
git clone https://github.com/karma-ai/karma-mvp.git
cd karma-mvp

# 安装依赖
pip install -r requirements.txt

# 以开发模式安装
pip install -e .
```

## 📋 系统要求

- Python 3.8 或更高版本
- pip 或 Poetry 包管理器
- 2GB+ 可用磁盘空间
- 网络连接（用于LLM API调用）

## 🎯 快速开始

### 1. 首次配置

```bash
# 设置 API 密钥
chatbot config api-key --provider openai

# 或使用 karma 命令 (两个命令等效)
karma config api-key --provider openai

# 配置模型
chatbot config set llm.model gpt-4
chatbot config set llm.temperature 0.7
```

### 2. 创建工作区

```bash
# 创建技术开发工作区
chatbot workspace create my-project --domain technology --tech-stack "python,fastapi,postgresql"

# 创建学术研究工作区
chatbot workspace create research --domain academic --research-area "machine learning"

# 创建创意设计工作区
chatbot workspace create art-project --domain creative --creative-medium "digital illustration"
```

### 3. 开始对话

```bash
# 交互式聊天
chatbot chat

# 单次提问
chatbot ask "如何优化Python代码性能？"

# 启用调试模式查看系统行为
chatbot ask "设计一个REST API架构" --debug
```

## 📚 主要命令

### 对话交互
- `chatbot chat [PROMPT]` - 启动交互式聊天或发送单条消息
- `chatbot ask <PROMPT>` - 发送单个问题

### 工作区管理
- `chatbot workspace create <NAME>` - 创建新工作区
- `chatbot workspace switch <NAME>` - 切换工作区
- `chatbot workspace list` - 列出所有工作区
- `chatbot workspace info [NAME]` - 显示工作区信息

### 记忆管理
- `chatbot memory show` - 显示记忆信息
- `chatbot memory clean` - 清理旧记忆数据

### 历史记录
- `chatbot history list` - 列出对话会话
- `chatbot history show <SESSION_ID>` - 显示特定会话
- `chatbot history search <QUERY>` - 搜索历史消息

### 配置管理
- `chatbot config show` - 显示配置信息
- `chatbot config set <KEY> <VALUE>` - 设置配置值
- `chatbot config models` - 列出支持的模型

查看完整命令文档：[CLI_COMMANDS.md](docs/CLI_COMMANDS.md)

## 💡 使用示例

### 技术开发场景
```bash
# 创建技术工作区
chatbot workspace create backend --domain technology --tech-stack "python,fastapi,redis,postgresql"

# 切换到工作区
chatbot workspace switch backend

# 开始技术咨询 (系统会自动适应技术领域)
chatbot ask "如何设计用户认证系统？"
```

### 学术研究场景
```bash
# 创建学术工作区
chatbot workspace create ml-research --domain academic --research-area "深度学习"

# 学术讨论 (系统会使用学术语言风格)
chatbot ask "解释Transformer架构的注意力机制"
```

### 创意设计场景
```bash
# 创建创意工作区
chatbot workspace create design --domain creative --creative-medium "UI设计"

# 创意咨询 (系统会激发创意思维)
chatbot ask "为移动应用设计简洁的登录界面"
```

## 🔧 高级配置

### 自定义 API 配置
```bash
# 使用自定义API端点
chatbot config set llm.base_url https://api.custom-provider.com/v1
chatbot config set llm.model custom-model-name

# 配置组织ID (OpenAI)
chatbot config set llm.organization org-xxxxx
```

### 个性化偏好
```bash
# 设置全局偏好
chatbot config set global.communication_style detailed
chatbot config set global.technical_depth expert
chatbot config set global.code_examples always
chatbot config set global.response_length long
```

## 🐛 故障排除

### 常见问题

**Q: 命令未找到 (command not found)**
```bash
# 确认 Python 包安装路径在 PATH 中
export PATH="$HOME/.local/bin:$PATH"
# 或重新安装
pip install --user karma-mvp
```

**Q: API 调用失败**
```bash
# 检查 API 密钥配置
chatbot config show --llm

# 测试网络连接
chatbot config models --provider openai --available
```

**Q: 权限错误 (Permission denied)**
```bash
# 使用 --user 标志安装
pip install --user karma-mvp

# 或使用虚拟环境
python -m venv karma-env
source karma-env/bin/activate  # Linux/macOS
# karma-env\Scripts\activate  # Windows
pip install karma-mvp
```

**Q: 内存或存储问题**
```bash
# 清理旧数据
chatbot memory clean --sessions --older-than 30

# 查看存储使用情况
du -sh ~/.memory-chatbot/
```

### 调试模式
```bash
# 启用调试模式查看详细信息
chatbot ask "test question" --debug

# 查看系统配置
chatbot config show

# 检查工作区状态
chatbot workspace info
```

## 📖 更多文档

- [详细安装指南](docs/INSTALLATION.md)
- [CLI 命令参考](docs/CLI_COMMANDS.md)
- [部署文档](docs/DEPLOYMENT.md)
- [API 文档](docs/API.md)
- [开发指南](docs/DEVELOPMENT.md)

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 💬 支持

- 📧 Email: team@karma-ai.com
- 🐛 Issues: [GitHub Issues](https://github.com/karma-ai/karma-mvp/issues)
- 📖 文档: [项目文档](https://github.com/karma-ai/karma-mvp/blob/main/docs/)

---

⭐ 如果这个项目对你有帮助，请给我们一个 Star！
