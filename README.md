# CC-Structure
## 每一章都是在永不改变的 while True 循环之上叠加一种新机制, 循环属于 Agent，而机制属于框架
## 全部 20 章的核心要义，就是教你如何在这个循环外围构建一切
s01 | Agent Loop | 核心循环 | messages / while True / stop_reason | 一个循环与 Bash 足矣 |
s02 | Tool Use | 工具分发 | TOOL_HANDLERS / 分发映射 / 并发 | 添加工具即添加处理器 |
s03 | Permission | 安全边界 | PermissionRule / 审批管线 | 先设边界，后予自由 |
s04 | Hooks | 扩展性 | PreToolUse / PostToolUse | 在循环外围挂钩，永不重写循环 |
s05 | TodoWrite | 规划 | TodoItem / 计划后执行 | 缺乏规划的 Agent 会迷失方向 |
s06 | Subagent | 上下文隔离 | fresh messages[] / 仅返回结果 | 大任务拆小，各自保持纯净上下文 |
s07 | Skill Loading | 按需获取知识 | SkillManifest / 惰性注入 | 按需加载知识，而非预先加载 |
s08 | Context Compact | 长会话 | snipCompact / microCompact / autoCompact | 上下文总会填满——需腾出空间 |
s09 | Memory | 持久化 | 选择 / 提取 / 合并 | 铭记要事，遗忘冗余 |
s10 | System Prompt | 组装 | 运行时拼接 / 分区加载 | 提示词是组装出来的，非硬编码 |
s11 | Error Recovery | 鲁棒性 | 重试 / token 升级 / 降级模型 | 错误非终点——而是重试的起点 |
s12 | Task System | 编排 | TaskRecord / blockedBy / 磁盘持久化 | 宏大目标：拆解为有序且持久的小任务 |
s13 | Background Tasks | 非阻塞 | 多线程执行 / 通知队列 | 耗时操作转后台，Agent 保持思考 |
s14 | Cron Scheduler | 时间触发 | 持久化调度 / 会话级作用域 | 定时触发，无需人工干预 |
s15 | Agent Teams | 多 Agent | MessageBus / 收件箱 / 权限传递 | 单兵力有不逮——委派给队友 |
s16 | Team Protocols | 协同 | 关闭握手 / 方案审批 | 队友需要共享的沟通规则 |
s17 | Autonomous Agents | 自组织 | 空闲周期 / 自动认领 / 任务看板 | 队友检视看板，主动认领工作 |
s18 | Worktree Isolation | 并行安全 | WorktreeRecord / 任务目录绑定 | 各自在独立目录中工作 |
s19 | MCP Plugin | 外部能力 | 多传输层 / 信道路由 | 能力不足？通过 MCP 插入 |
s20 | Comprehensive | 集成 | 所有机制围绕一个循环 | 多重机制，单一循环 |