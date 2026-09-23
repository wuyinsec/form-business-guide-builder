# DAT 格式与脚本

## 适用前提

以下 DAT 结构和脚本仅针对金政软件开发的内控系统 P1 版本业务助手配置。不得把这里记录的字段结构视为其他系统或其他版本的通用标准。

即使同为 P1 版本，也应使用目标项目当前系统导出的有效 DAT 样例作为模板，并在正式导入前完成验证。

## 已验证结构

业务助手 DAT 通常是无 BOM 的 UTF-8 JSON，根节点含 `cfgEntity`。四个富文本字段为：

- `content`：业务助手内容
- `wfGuide`：业务流程指引
- `bizFillingGuide`：业务填报指引
- `attachmentGuide`：附件清单说明

内容使用 HTML 保存。转换脚本把 Excel 单元格中的每一行转换为一个 `<p>`，并进行 HTML 转义。

## 生成命令

```powershell
python scripts/xlsx_to_dat.py 审阅确认版.xlsx --template 系统导出样例.dat --output-dir 输出目录
```

模板 DAT 用于保留当前系统需要的外层结构。若系统版本或导入机制未知，应优先让用户提供任意表单导出的有效 DAT 样例。

## 校验命令

```powershell
python scripts/validate_dat.py 输出目录 --xlsx 审阅确认版.xlsx
```

校验包括：文件数量、UTF-8 JSON、`cfgEntity`、四字段非空、文件名与表单名一致，以及 Excel 与 DAT 四段内容逐字段一致。

## 注意事项

- 不覆盖用户原始 DAT。
- 不把项目资料或真实账套信息制作成通用模板资产。
- 如果系统明确忽略 `formId`、`id` 等字段，可复用一个模板批量生成；否则应为每张表单使用对应导出模板。
- 该判断必须来自当前系统验证或用户确认，不能自行假设。
