# TheFuck AI Rule

TheFuck AI Rule 是一个基于 AI 的命令修正插件，为 [thefuck](https://github.com/nvbn/thefuck) 工具提供智能命令修复功能。

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
pipx install thefuck
pipx install thefuck-ai-rule
```

或者直接从 GitHub 安装:

```bash
pip install git+https://github.com/huchiyv/thefuckAiRule.git
```

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

### 正确设置 PowerShell 别名 (Windows 用户必读)

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

### 使用示例

```bash
$ cd /nonexistent-directory
bash: cd: /nonexistent-directory: No such file or directory

$ fuck
✨✨✨ AI 提示 ✨✨✨
>>> 这是 AI 生成的修复命令 <<<
✨✨✨✨✨✨✨✨✨✨

mkdir -p /nonexistent-directory && cd /nonexistent-directory

$ mkdir -p /nonexistent-directory && cd /nonexistent-directory
```

## 许可证

此项目采用 MIT 许可证 - 详见 LICENSE 文件。
