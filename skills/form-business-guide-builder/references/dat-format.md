# DAT 格式与脚本

## 适用前提

以下 DAT 结构和脚本仅针对金政软件开发的内控系统 P1 版本业务助手配置。不得把这里记录的字段结构视为其他系统或其他版本的通用标准。

P1 业务助手 DAT 采用固定结构，已内置于 `assets/p1-dat-template.json`。正常生成时不要求用户重复提供 DAT 样例。

## 已验证结构

业务助手 DAT 通常是无 BOM 的 UTF-8 JSON，根节点含 `cfgEntity`。四个富文本字段为：

- `content`：业务助手内容
- `wfGuide`：业务流程指引
- `bizFillingGuide`：业务填报指引
- `attachmentGuide`：附件清单说明

内容使用 HTML 保存。转换脚本把 Excel 单元格中的每一行转换为一个 `<p>`，并进行 HTML 转义。

`cfgEntity.accountSetId` 是目标单位的账套ID，也是能否成功导入的重要条件。生成最终 DAT 前必须由用户准确提供；不得留空、使用占位值、猜测或复用其他项目的值。

## 生成命令

```powershell
python scripts/xlsx_to_dat.py 审阅确认版.xlsx --account-set-id 目标账套ID --output-dir 输出目录
```

脚本默认使用内置 P1 固定模板，并强制要求 `--account-set-id`。`--template` 仅用于导入异常时的结构差异排查，不是日常必需参数。

## 校验命令

```powershell
python scripts/validate_dat.py 输出目录 --xlsx 审阅确认版.xlsx --account-set-id 目标账套ID
```

校验包括：文件数量、UTF-8 JSON、`cfgEntity`、`accountSetId` 非空且与提供值一致、四字段非空、文件名与表单名一致，以及 Excel 与 DAT 四段内容逐字段一致。

## 导入失败排查顺序

1. 核对 `accountSetId` 是否确实属于目标单位当前账套；
2. 检查文件是否为无 BOM 的 UTF-8 JSON；
3. 检查 `cfgEntity` 和固定字段是否完整；
4. 检查表单名称及四个富文本字段是否有效；
5. 上述均无异常时，再让用户提供目标环境导出的 DAT 样例，与固定模板比对结构差异。

## 注意事项

- 不覆盖用户原始 DAT。
- 内置模板只能保留 `accountSetId` 占位符，不得写入任何真实单位账套信息。
- `formId`、`id` 等字段使用固定空值，不要求用户逐表提供。
- 仅在用户反馈无法导入时，才把目标环境 DAT 结构差异作为排查点。
