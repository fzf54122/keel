# Keel 错误码

响应信封：

```json
{ "code": 200, "status": "success", "data": {}, "msg": "OK" }
```

| code | 含义 |
| --- | --- |
| 200 | 成功 |
| 20010 | 对象已存在 (`ObjectExistException`) |
| 20020 | 对象不存在 (`ObjectNotFoundException`) |
| 40000 | 通用业务错误 (`KeelException`) |
| 401 | 未认证 / Token 无效（HTTP） |
| 403 | 无权限（HTTP） |
| 422 | 请求参数校验失败 |
| 500 | 未处理服务端错误 |

业务模块请优先抛 `KeelException` 子类，而不是裸 `HTTPException`。
