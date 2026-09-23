from __future__ import annotations

import argparse
import json
from pathlib import Path

from office_data import write_review_xlsx


HEADERS = ["表单名称", "业务助手内容", "业务流程指引", "业务填报指引", "附件清单说明", "待确认事项", "依据摘要"]


def main() -> None:
    parser = argparse.ArgumentParser(description="从结构化JSON生成业务助手审阅Excel")
    parser.add_argument("input_json", type=Path)
    parser.add_argument("output_xlsx", type=Path)
    args = parser.parse_args()

    data = json.loads(args.input_json.read_text(encoding="utf-8"))
    forms = data.get("forms", [])
    if not forms:
        raise SystemExit("输入JSON中没有forms")

    rows = [HEADERS]
    names: set[str] = set()
    for form in forms:
        name = str(form.get("form_name", "")).strip()
        if not name:
            raise SystemExit("存在空白表单名称")
        if name in names:
            raise SystemExit(f"表单名称重复：{name}")
        names.add(name)
        rows.append([
            name,
            form.get("content", ""),
            form.get("workflow", ""),
            form.get("filling", ""),
            form.get("attachments", ""),
            form.get("pending_questions", ""),
            form.get("evidence_summary", ""),
        ])

    write_review_xlsx(args.output_xlsx, rows)
    print(args.output_xlsx.resolve())


if __name__ == "__main__":
    main()
