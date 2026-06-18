# Trae 悬浮球助手

一个桌面级的AI编程助手，通过悬浮球界面为用户提供即时的编程帮助。

## 功能特性

### 🎯 核心功能
- **悬浮球界面** - 永远置顶的圆形悬浮球，可拖动到屏幕任意位置
- **AI智能问答** - 支持多种AI服务提供商（OpenAI、Claude等）
- **截图提问** - 一键截图，框选区域后自动复制到剪贴板
- **历史记录** - 自动保存对话历史，支持清空和查看
- **配置管理** - 可自定义悬浮球大小、颜色、AI设置等

### 🖱️ 操作说明
| 操作 | 效果 |
|------|------|
| 左键点击悬浮球主体 | 打开聊天窗口 |
| 左键点击左上角绿色按钮 | 打开 Trae 主应用 |
| 右键点击右下角按钮 | 打开功能菜单 |
| 按住拖动悬浮球 | 移动悬浮球位置 |

### 📋 功能菜单
- 💬 打开聊天 - 打开AI聊天窗口
- 📷 截图提问 - 启动截图工具
- ⚙️ 设置 - 打开设置窗口
- 🗑️ 清空历史 - 清空对话历史记录
- 🚪 退出 - 退出应用

## 安装与运行

### 1. 安装依赖
```bash
cd trae-floating-ball
pip install -r requirements.txt
```

### 2. 运行程序
```bash
python main.py
```

### 3. 配置AI服务（可选）
如需使用真实AI服务，请在设置窗口中配置API密钥：
- 打开悬浮球菜单 → 设置 → AI设置
- 选择AI服务提供商（OpenAI或Anthropic）
- 输入对应的API密钥

## 项目结构

```
trae-floating-ball/
├── main.py                 # 主程序入口
├── requirements.txt        # 依赖列表
├── config/
│   └── settings.py         # 默认配置
├── modules/
│   ├── floating_ball.py    # 悬浮球模块
│   ├── chat_window.py      # 聊天窗口模块
│   ├── ai_service.py       # AI服务模块
│   ├── screen_capture.py   # 截图模块
│   ├── history_manager.py  # 历史记录管理
│   └── settings_window.py  # 设置窗口
└── utils/
    ├── common.py           # 通用工具函数
    └── config_manager.py   # 配置管理器
```

## AI服务配置

### OpenAI配置
```python
# 在 config/settings.py 中配置
AI_CONFIG = {
    'provider': 'openai',
    'openai': {
        'api_key': 'your-api-key',
        'model': 'gpt-3.5-turbo',
        'base_url': 'https://api.openai.com/v1',
        'temperature': 0.7,
        'max_tokens': 2000
    }
}
```

### Anthropic (Claude)配置
```python
AI_CONFIG = {
    'provider': 'anthropic',
    'anthropic': {
        'api_key': 'your-api-key',
        'model': 'claude-3-sonnet-20240229',
        'max_tokens': 2000
    }
}
```

### 模拟模式（测试）
默认使用模拟模式，无需API密钥即可测试功能：
```python
AI_CONFIG = {
    'provider': 'mock'
}
```

## 使用示例

### 快速问答
```
用户: Python列表怎么用？
AI: Python列表是常用的数据结构，主要操作包括：
    - 创建: my_list = [1, 2, 3]
    - 添加: my_list.append(4)
    - 访问: my_list[0]
    - 删除: my_list.remove(2)
```

### 代码问题诊断
```
用户: 我遇到了一个错误：TypeError: 'NoneType' object is not subscriptable
AI: 这个错误通常发生在尝试对None值进行索引访问时。
    解决方法：
    1. 检查变量是否为None
    2. 添加None值检查
    3. 确保函数返回值不为None
```

### 截图提问
1. 点击悬浮球菜单中的"📷 截图提问"
2. 框选需要截图的区域
3. 截图自动复制到剪贴板
4. 在聊天窗口粘贴截图进行分析

## 技术特性

- **永远置顶** - 悬浮球始终显示在所有窗口之上
- **透明背景** - 圆形透明设计，不遮挡内容
- **可拖动** - 支持拖动到屏幕任意位置
- **一键截图** - 点击按钮自动触发框选截图
- **快速启动** - 点击绿色按钮快速打开 Trae 主应用
- **配置持久化** - 用户设置自动保存到本地文件

## 开发说明

### 扩展AI服务
如需添加新的AI服务提供商，请在 `modules/ai_service.py` 中添加新的调用方法：

```python
def _call_new_provider(self, message):
    """调用新的AI服务"""
    # 实现API调用逻辑
    pass
```

### 自定义UI
修改 `config/settings.py` 中的UI配置：

```python
FLOATING_BALL_SIZE = 60        # 悬浮球大小
FLOATING_BALL_COLOR = '#667eea' # 悬浮球颜色
CHAT_WINDOW_WIDTH = 400        # 聊天窗口宽度
CHAT_WINDOW_HEIGHT = 600       # 聊天窗口高度
```

## 系统要求

- Python 3.8+
- Windows/Linux/MacOS
- 必需依赖：Pillow, pyperclip
- 可选依赖：openai, anthropic

## 许可证

本项目仅供学习和研究使用。

## 联系方式

如有问题或建议，请通过Trae主应用联系开发者。