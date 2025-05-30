# ⚡ AstrBot x 郊狼: 一键开火插件 ⚡

嗯，这是一款给 [AstrBot](https://github.com/SkywalkerJi/AstrBot) 用的“小玩具”插件！

它能让你通过聊天控制 [DG-Lab Coyote Game Hub](https://github.com/hyperzlib/DG-Lab-Coyote-Game-Hub) 这个神奇的玩意儿，实现远程“一键开火”（你懂的 😉）。

## 功能就一个: `fire_action` 工具

*   **作用**: 给配置文件里指定的那个倒霉蛋（或者所有蛋）来一下！
*   **参数**:
    *   `strength` (必需): 剂量多大，你说了算 (API说最高40)。
    *   `time` (可选): 持续多久，单位毫秒 (API默认5000ms)。
    *   `override` (可选): 是不是要推倒重来 (true)，还是温柔叠加 (false，API默认这个)。

## 咋配置呢？

在 AstrBot 的插件配置里填上这两项就行：

1.  `base_url`: 你的郊狼 Hub 服务器地址，比如 `http://localhost:8920`。
2.  `default_client_id`: 默认调教对象是谁？填上TA的ID，或者用 `"all"` 来个雨露均沾。

搞定！现在可以让你的 LLM 助手帮你“操作”了。

**玩得开心，注意安全！** 😈
