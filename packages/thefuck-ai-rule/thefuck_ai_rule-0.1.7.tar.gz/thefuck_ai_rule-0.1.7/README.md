# TheFuck AI Rule

TheFuck AI Rule 是一个基于 AI 的命令修正插件，为 [thefuck](https://github.com/nvbn/thefuck) 工具提供智能命令修复功能,目前仅支持硅基流动的api调用ai模型。
⚠️**注意**: 本规则的匹配条件很宽松几乎来者不拒，也就是匹配基本会优先于thefuck的所有默认规则，全部都用ai修复

## 功能特点

- 使用 AI 模型分析命令错误并提供修复建议
- 支持多种 AI 模型和 API 服务
- 自动环境检测和配置
- 简单易用的安装和设置流程

## 安装

```bash
pip install thefuck-ai-rule
```

或者使用 pipx 安装 (推荐):

```bash
pipx install git+https://github.com/DL909/thefuck.git
pipx install thefuck-ai-rule
```
⚠️**注意**:https://github.com/DL909/thefuck.git 非thefuck官方地址，但是修复了一些使用问题

## 自动安装和配置

安装后，运行以下命令完成初始化配置：

```bash
thefuck-ai-install
```

此命令将:
1. 检查是否安装了 thefuck
2. 自动识别您的操作系统
3. 将规则文件复制到适当的位置
4. 帮助您配置必要的 API 密钥和设置

## 手动配置

您可以手动设置以下环境变量：

- `THEFUCK_AI_API_URL`: AI API 的 URL (默认: https://api.siliconflow.cn/v1/chat/completions)
- `THEFUCK_AI_API_KEY`: 您的 AI API 密钥
- `THEFUCK_AI_MODEL`: 要使用的 AI 模型 (默认: Qwen/QwQ-32B)

## 使用方法

安装和配置完成后，正常使用 thefuck 命令即可。当您输入错误命令后：

### 不同操作系统的配置

#### Linux 和 macOS 用户

在 Linux 和 macOS 系统上，您需要添加 thefuck 别名到您的 shell 配置中：

```bash
# Bash 用户 (.bashrc)
eval $(thefuck --alias)

# Zsh 用户 (.zshrc)
eval $(thefuck --alias)

# Fish 用户 (config.fish)
thefuck --alias | source
```

#### Windows 用户必读

如果您在 PowerShell 中使用 thefuck，请确保正确设置别名，这对于命令正确执行至关重要：

```powershell
iex "$(thefuck --alias)"
```

如果您希望永久设置别名，可以将上面的命令添加到您的 PowerShell 配置文件中：

```powershell
# 查找您的 PowerShell 配置文件路径
echo $profile
# 编辑配置文件，添加以下行：
# iex "$(thefuck --alias)"
```

### 解决常见问题

如果您在使用 thefuck 时遇到以下错误：

```bash
(eval):2: parse error near `>'
```

这通常是由于命令中包含特殊字符（如 `>`, `<`, `|` 等）导致的。最新版本已经修复了这个问题。请确保您使用的是最新版本的 thefuck-ai-rule（0.1.5 或更高）：

```bash
pip install --upgrade thefuck-ai-rule
# 或者
pipx upgrade thefuck-ai-rule
```

### 使用示例

```bash
> 查看当前目录命令
zsh: command not found: 查看当前目录命令
> fuck
AI rule: 找到修复命令
pwd [enter/↑/↓/ctrl+c]
/home/chiyv/.config/thefuck/rules
```

## 隐私保护

TheFuck AI Rule 尊重并保护您的隐私：

- **命令和输出处理**：在将命令和输出发送到AI服务前，会自动过滤敏感信息：
  - 移除可能包含的密码和API密钥
  - 掩盖个人路径和用户名信息
  - 限制发送的输出长度
  - 替换IP地址和电子邮件地址
- **不存储命令历史**：本工具不会在本地或云端存储您的命令历史
- **API密钥保护**：您的API密钥仅存储在本地环境变量或配置文件中

## 许可证

此项目采用 MIT 许可证 - 详见 LICENSE 文件。
