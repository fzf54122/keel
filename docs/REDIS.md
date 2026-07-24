# Redis 策略

| 场景 | `REDIS_REQUIRED=false`（默认） | `REDIS_REQUIRED=true` |
| --- | --- | --- |
| 连接失败 | 降级：缓存/黑名单失效，服务可启动 | 启动失败 / 关键路径 503 |
| login 写 refresh | 尽力写入，失败不阻断登录 | 写入失败 → 503 |
| refresh 校验 | 有值则强校验；无值（Redis 挂）则放行 JWT 本身 | 无缓存 → 503 |
| logout 黑名单 | 尽力写入 | 失败 → 503 |

生产若依赖“登出立即失效”，请设：

```bash
REDIS_REQUIRED=true
```
