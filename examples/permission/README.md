
来自 mirai-console

## 权限

每个权限都由 PermissionId 对象表示。

一个 PermissionId 拥有这些信息：
```python
class PermissionId(BaseModel):
    id: str # 唯一识别ID
    description: str = "" # 描述信息
    parent: Optional["PermissionId"] = None # 父权限 （除ROOT_PERMISSION外都应该有父权限）
```

「权限」表示的意义是 “做一项工作的能力”。如 “执行指令 /stop”，“操作数据库” 都叫作权限。

id 是 PermissionId 的唯一标识符。知道 id 就可以获取到对应的 PermissionId。
使用 `async def get_permission(permission: str) -> PermissionId` 


#### 根权限

RootPermission 是所有权限的父权限。其 ID 为 "\*"

## 被许可人ID

```python
class PermitteeId(BaseModel):
    id: str # 被许可人id
    directParents: Sequence["PermitteeId"] # 直接父对象
```

PermitteeId 表示一个可被赋予权限的对象，即 '被许可人'。

提供函数 `def str_to_permittee(permittee_str: str) -> PermitteeId` 来获取 PermitteeId 对象

被许可人自身不持有拥有的权限列表，而是拥有 PermitteeId，标识自己的身份，供 check_permission 处理。

**注意**：请不要自主实现 PermitteeId。

一个这样的标识符即可代表特定的单个 PermitteeId, 也可以表示多个同类 PermitteeId.

#### `directParents`
PermitteeId 允许拥有多个父对象。在检查权限时会首先检查自己, 再递归检查父类。

#### 字符串表示

当使用 `PermitteeId.id` 时, 不同的类型的返回值如下表所示. 
区分大小写, 不区分 Bot

|    被许可人类型    | 字符串表示示例 | 备注                                 |
|:----------------:|:-----------:|:------------------------------------|
|      控制台       |   console   |                                     |
|   任意其他客户端    |   client*   | 即 Bot 自己发消息给自己                |
|      精确群       |   g123456   | 表示群, 而不表示群成员                  |
|      精确好友      |   f123456   | 必须通过好友消息                       |
|   精确群临时会话    | t123456.789 | 群 123456 内的成员 789. 必须通过临时会话 |
|     精确群成员     | m123456.789 | 群 123456 内的成员 789. 同时包含临时会话 |
|      精确用户      |   u123456   | 同时包含群成员, 好友, 临时会话           |
|      任意群       |     g\*     | g 意为 group                         |
|  任意群的任意群员   |     m\*     | m 意为 member                        |
|  精确群的任意群员   | m123456.\*  | 群 123456 内的任意成员. 同时包含临时会话  |
|    任意临时会话    |     t\*      | t 意为 temp. 必须通过临时会话          |
| 精确群的任意临时会话 | t123456.\*  | 群 123456 内的任意成员. 必须通过临时会话  |
|      任意好友      |     f\*     | f 意为 friend                       |
|      任意用户      |     u\*     | u 意为 user. 任何人在任何环境           |
|     任意陌生人     |     s\*     | s 意为 stranger. 任何人在任何环境       |
|    任意联系对象    |      \*      | 即任何人, 任何群. 不包括控制台           |


### 注册权限

每一条指令都会默认自动创建一个权限，父权限为 ROOT_PERMISSION 。

提供 `async def get_permission(permission_id: str) -> PermissionId` 获取权限对象,也可以用于申请一个新的权限对象

提供 `async def set_permission(permission: PermissionId) -> NoReturn` 来设置权限对象

提供 `async def set_permission_with_permittee(permission: str, permittee: str)` 来给被许可人某个权限

### 快速使用

1. 将 `PermissionConfig-example.py` 重命名为 `Permission-Config.py` 然后将

2. 注册一个 `ApplicationLaunched` 的事件，并初始化数据库

```python
@bcc.receiver(ApplicationLaunched)
async def __init_database():
    await permission_custom.init_database()
```

3. 那就可以用了。可以在 `headless_decorator` 中使用 `MessagePermissionCheckDecorator`，也可以在 `dispatcher` 中
使用 `MessagePermissionCheckDispatcher`

3. 其余请参考