# ⚡ AstrBot x DG-Lab 郊狼控制插件 ⚡

[![AstrBot](https://img.shields.io/badge/AstrBot-Plugin-blue.svg)](https://github.com/AstrBotDevs/AstrBot/) 
[![DG-Lab](https://img.shields.io/badge/DG--Lab-Coyote--Game--Hub-orange.svg)](https://github.com/hyperzlib/DG-Lab-Coyote-Game-Hub/)

这是一款为 [AstrBot](https://github.com/AstrBotDevs/AstrBot/) 量身定制的“小玩具”插件！

它能让你通过聊天控制 [DG-Lab Coyote Game Hub](https://github.com/hyperzlib/DG-Lab-Coyote-Game-Hub/) 这个神奇的玩意儿，实现远程强度控制、波形切换、以及一键开火！（你懂的 😉）✨


这是酪灰基于原作者 [RC-CHN](https://github.com/RC-CHN/astrbot_dg_lab_plugin/) 的修改增强版。

---

## 🛠️ 核心功能

*   🤖 **AI 智能控电**：赋予你的 AI 助手操作郊狼的能力（如：当对话触发惩罚条件时，AI 能直接调大基础强度并下发“一键开火”）。
*   🔧 **多维操作接口**：大模型可随时调用获取受控者信息、调整 A/B 通道强度与倍率、指定跳跃随机波形等高阶玩法。
*   ⚙️ **热更新与动态绑定**：支持在聊天中通过指令直接切换受控目标、实时更新目标 Client ID。
*   🔒 **安全丰富的权限系统**：
    *   动态多维度的身份鉴权，不仅能全局控制对其他用户的允许状态，也支持在特定群聊中被@唤醒。
    *   受控者本人与管理员具有最高权限。

---

## 🚀 常用交互指令

> ⚠️ 这些指令只能由**被设定的受控者本人**或 **AstrBot 管理员** 在**私聊**中触发。

### 📡 目标与设备管理

- **`/郊狼客户端 [client_id]`**
  热修改郊狼要控制的 `client_id`。
  例如：`/郊狼客户端 all` 或 `/郊狼客户端 123456...`

### 🛡️ 权限与授权管理

- **`/郊狼授权`**
  不带参数可以直接查看当前的整体授权情况（生效的用户与群聊）。
  
- **`/郊狼授权 用户 <用户ID>`**
  一键切换授权该用户的郊狼控制权限。
  
- **`/郊狼授权 用户开关`**
  全局切换：是否允许所有人随意召唤 AI 对你发起控制。

- **`/郊狼授权 群聊 <群号>`**
  将某个群组加入白名单，允许群友在里面通过 `@Bot` 来下发电击请求。
  
- **`/郊狼授权 群聊开关`**
  全局切换：启用或关闭整个群聊唤醒郊狼的能力。

### 🛠️ 传统文字开发控制

如果你不想借助 AI，也可以使用硬指令操作（比如开发调试用）：
- **`/郊狼指令 <动作> <目标或值> [附加参数...]`**
  例如：`/郊狼指令 开火 30 5000`（一键 30 强度开火，持续 5000 毫秒）。

---

## ⚙️ 如何配置？

在 AstrBot 的主控面板中找到该插件，进行以下配置：

1.  **`game_api` (API 链接与设备)**
    *   **`base_url`**: 你的郊狼 Hub 服务器地址，例如 `http://localhost:8920` 或者穿透后的域名。
    *   **`default_client_id`**:  默认调教对象是谁？填上TA的ID，或者用 `"all"` 来个雨露均沾。

2.  **`target_info` (AI 认知增强)**
    *   让 AI 更好代入角色！填上受控者的 **名字 (user_name)** 和 **标识/QQ号 (user_id)**。AI 在获取信息时会明确“现在被控者是谁”。

3.  **高级权限设定**
    也可以随时在面板中通过 `authorized_settings` 与 `group_settings` 进行修改！

4. **选择性指引**
    在人格设定或其它方式，诱导 Bot 调用 `dglab_get_target_info` 函数。
    例如 `你可以在 AstrBot 上使用 dglab_get_target_info 等函数来控制 ** 的郊狼。` ，这里写的不怎么好，自行设定喔！

---

## 💡 使用建议

* **安全第一**：虽然郊狼设备自身具备上限约束功能，但在把“生杀大权”交由 AI 时请务必通过 Hub 页面**提前锁好安全上限强度**！

祝你们玩得开心！🎉
