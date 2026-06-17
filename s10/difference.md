## CC源码

<details>
<summary>深入 CC 源码</summary>

> 以下基于 CC 源码 `constants/prompts.ts`（914 行）、`constants/systemPromptSections.ts`（68 行）、`context.ts`（189 行）、`utils/api.ts`（718 行）、`utils/systemPrompt.ts`（123 行）、`bootstrap/state.ts` 的分析。

### CC 的 system prompt 有多少 section？

数量不固定，受 feature flag、output style、KAIROS/Proactive 模式、用户类型、token 预算等影响。大致分两类：

**静态 section**（始终加载）：identity、system、doing_tasks、actions、using_tools、tone_style、output_efficiency 等。

**动态 section**（按状态加载）：session_guidance、memory、ant_model_override、env_info_simple、language、output_style、mcp_instructions、scratchpad、frc、summarize_tool_results、numeric_length_anchors、token_budget、brief 等。

`mcp_instructions` 是唯一的易失性 section（通过 `DANGEROUS_uncachedSystemPromptSection()` 创建），因为 MCP server 可以在轮次间连接和断开。

### 组装函数

```typescript
getSystemPrompt(tools, model, additionalWorkingDirs?, mcpClients?): Promise<string[]>
```

返回 `string[]`（每个元素是一个 section），由 `SYSTEM_PROMPT_DYNAMIC_BOUNDARY` 分隔静态和动态部分。

### cache scope

启用 global cache boundary 时，静态 section 合并成一个 global cache block，动态 section 不使用 global cache（`cacheScope: null`）。没有 boundary 或跳过 global cache 的路径才会走 org scope。

教学版的缓存只避免重复拼接字符串。CC 的三层缓存：

1. **lodash memoize**：`getSystemContext` 和 `getUserContext` 在会话中缓存（`context.ts`）
2. **section 注册缓存**：`STATE.systemPromptSectionCache` 缓存动态 section 结果，`/clear` 或 `/compact` 时清除
3. **API 级缓存**：`splitSysPromptPrefix()`（`api.ts`）把 prompt 按 boundary 分成不同 cache scope 的块

### getUserContext vs getSystemContext

| | getSystemContext | getUserContext |
|---|---|---|
| 内容 | gitStatus、cacheBreaker | CLAUDE.md 内容、currentDate |
| 注入方式 | 追加到 system prompt 数组 | 前置为 `<system-reminder>` 用户消息 |
| 何时跳过 | 自定义 system prompt 时 | 始终运行 |

### 模式如何改变 prompt

- **CLAUDE_CODE_SIMPLE**：整个 prompt 只有 2 行
- **Proactive/KAIROS**：用紧凑版 prompt 替换所有标准 section
- **Coordinator**：用协调器专用 prompt 完全替换
- **Agent 模式**：Agent 定义的 prompt 替换或追加到默认 prompt

### 总大小

标准交互模式下 system prompt 核心约 20-30KB 文本。CLAUDE_CODE_SIMPLE 约 150 字符。用户上下文（CLAUDE.md）和系统上下文（git status）在此基础上累加。

</details>

<!-- translation-sync: zh@v1, en@v1, ja@v1 -->