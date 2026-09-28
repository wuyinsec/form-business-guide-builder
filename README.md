# 表单业务指引生成工具

面向金政软件内控系统 P1 版本实施场景的 Codex Skill。它可以根据当前项目提供的表单截图、制度文件、附件清单、需求文档、操作手册和实施说明，整理每张表单的四个业务助手板块，并在人工审阅后生成和校验系统可导入的 DAT 文件。

> 适用范围：本工具的 DAT 字段、转换和导入结论仅针对金政软件内控系统 P1 版本。其他厂商、产品或版本可以参考资料整理方法，但不得直接套用 DAT 结构。

## 核心能力

- 从 DOCX、XLSX、截图和实施说明中整理项目规则；
- 按“业务助手内容、业务流程指引、业务填报指引、附件清单说明”四个板块生成初稿；
- 对没有依据的金额、时限、审批条件和必传附件进行拦截或标记待确认；
- 生成供实施人员和业务人员审阅的 Excel；
- 使用内置的 P1 固定 DAT 结构，按目标 `accountSetId`（账套ID）批量生成各表单 DAT；
- 校验 DAT 结构及其与确认版 Excel 的逐字段一致性。
- 提供纯本地 DAT 富文本编辑器，便于导入、审阅和重新导出单个 DAT。

## 安装

### 通过 Codex 安装

把下面的 GitHub 子目录地址交给 Codex，并要求使用 `$skill-installer` 安装：

```text
https://github.com/wuyinsec/form-business-guide-builder/tree/main/skills/form-business-guide-builder
```

安装完成后，在新的 Codex 任务中使用：

```text
使用 $form-business-guide-builder，根据当前项目资料整理业务助手，先生成审阅表，确认后再生成并校验 DAT。
```

### 手动安装

克隆仓库后，将 `skills/form-business-guide-builder` 整个目录复制到：

```text
~/.codex/skills/form-business-guide-builder
```

Windows 通常对应：

```text
C:\Users\你的用户名\.codex\skills\form-business-guide-builder
```

重新打开 Codex 任务后即可发现该 Skill。

## 仓库结构

```text
form-business-guide-builder/                    # GitHub 仓库
├─ README.md                                    # 项目介绍及安装说明
├─ LICENSE                                      # MIT 开源许可证
├─ CHANGELOG.md                                 # 版本更新记录
├─ .gitignore                                   # 排除业务资料和生成文件
├─ .github/                                     # GitHub 自动检查配置
├─ tools/business-assistant-editor/             # 纯本地 DAT 富文本编辑器
└─ skills/                                      # 可安装的 Skill
   └─ form-business-guide-builder/              # 表单业务指引生成工具
      ├─ SKILL.md                               # Skill 核心入口
      ├─ README.md                              # 详细使用说明
      ├─ agents/                                # 显示名称和默认提示词
      ├─ references/                            # 资料边界、四板块及审校规范
      ├─ assets/                                # 脱敏审阅表示例
      └─ scripts/                               # Office、Excel 和 DAT 工具
```

## 使用原则

- 只使用当前项目资料、系统实际表现和用户明确确认的信息；
- 默认不联网补充规章制度，不引用其他单位或其他项目规则；
- 金额、比例、人数、时限、审批条件和必传附件必须有当前项目依据；
- 资料不明确时使用中性表述或列为待确认，不得猜测；
- DAT 只能根据用户确认后的 Excel 生成，转换时不得再次润色。

## 环境要求

- Python 3.10 或更高版本；
- 脚本仅使用 Python 标准库，无需安装第三方依赖；
- 生成 DAT 前需确认使用金政内控系统 P1 版本，并由项目人员提供目标单位准确的 `accountSetId`；正常情况下无需提供 DAT 样例。

## 本地 DAT 编辑器

进入 `tools/business-assistant-editor`，双击“打开业务助手编辑器.bat”即可使用。编辑器不上传文件，能够修改四个富文本板块和目标账套 ID，并保留导入 DAT 中其他字段。跨单位使用时必须核对并改为目标单位的账套 ID。

## 数据安全

请勿向公开仓库提交单位制度原件、真实业务数据、账套信息、组织或用户信息、表单 ID、真实 DAT 和审阅结果。仓库中的示例均应保持脱敏。

## 许可证

本项目使用 [MIT License](LICENSE)。
