## CC源码

<details>
<summary>深入 CC 源码</summary>

> 以下基于 CC 源码 `query.ts`（1729 行）、`services/api/withRetry.ts`（822 行）、`query/tokenBudget.ts`（93 行）、`utils/tokenBudget.ts`（73 行）的分析。

### 一、十几种 reason/transition（不只是 3 条）

教学版讲了 3 种最常见的恢复模式。CC 实际有十几种 reason/transition，每轮 LLM 调用后都会判断：

| reason/transition | 教学版对应 | CC 行为 |
|---|---|---|
| `completed` | 正常完成 | 返回结果 |
| `next_turn` | 正常工具调用 | 继续下一轮工具执行 |
| `max_output_tokens_escalate` | 路径 1 | 8K→64K 升级 |
| `max_output_tokens_recovery` | 路径 1 续写 | 续写提示（最多 3 次） |
| `reactive_compact_retry` | 路径 2 | reactive compact → 重试 |
| `prompt_too_long` | 路径 2 | 同上 |
| `collapse_drain_retry` | 未展开 | context collapse 先提交暂存 |
| `model_error` | 未展开 | 重试 |
| `image_error` | 未展开 | `ImageSizeError` / `ImageResizeError` 专门处理 |
| `aborted_streaming` | 未展开 | 流式中止恢复 |
| `aborted_tools` | 未展开 | 工具中止 |
| `stop_hook_blocking` | 未展开 | 注入 blocking error → 模型自纠 |
| `stop_hook_prevented` | 未展开 | hooks 阻止 |
| `hook_stopped` | 未展开 | hook 停止执行 |
| `token_budget_continuation` | 未展开 | token 用量 < 90% 时继续 |
| `blocking_limit` | 未展开 | 阻塞限制 |
| `max_turns` | 未展开 | 达到最大轮次 |

教学版只展开了前 5 种（最常见的），其余各有专门处理逻辑。

### 二、指数退避的精确公式

CC 的退避延迟（`withRetry.ts:530-548`）：

```
delay = min(500 × 2^(attempt-1), 32000) + random(0~25%)
```

| 尝试 | 基础延迟 | + 抖动 |
|------|---------|--------|
| 1 | 500ms | 0-125ms |
| 2 | 1000ms | 0-250ms |
| 4 | 4000ms | 0-1000ms |
| 7+ | 32000ms（上限） | 0-8000ms |

如果服务器返回 `Retry-After` header，优先用那个值。

### 三、CONTINUATION 提示原文

CC 的续写提示（`query.ts:1225-1227`）：

```
Output token limit hit. Resume directly — no apology, no recap of what
you were doing. Pick up mid-thought if that is where the cut happened.
Break remaining work into smaller pieces.
```

Token budget 的 nudge 提示（`tokenBudget.ts:72`）：

```
Stopped at {pct}% of token target. Keep working — do not summarize.
```

### 四、流式错误处理

CC 的流式路径中，可恢复的错误（413、max_tokens、media error）在 streaming 期间**被暂扣不展示**（`query.ts:788-822`）——SDK 消费者看不到，只有恢复逻辑能看到。等 streaming 结束后才判断是否需要恢复。

### 五、529 → Fallback Model 切换

连续 3 次 529 过载错误后（`MAX_529_RETRIES = 3`），CC 自动切换到 fallback model（如 Opus → Sonnet）。切换时清除所有 pending 消息和 tool 结果，给用户展示 "Switched to {model} due to high demand"。

### 六、Diminishing Returns 检测

Token budget 的"继续"不是无限的。当连续 3 次 continuation 且 token 增量 < 500 时，系统判断"继续也没有实质性产出"，停止 continuation（`tokenBudget.ts:60-62`）。

</details>

<!-- translation-sync: zh@v1, en@v1, ja@v1 -->
