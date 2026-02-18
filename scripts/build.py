#!/usr/bin/env python3
"""
AiDocPlus-DocTemplates 构建脚本
扫描 data/ 目录，生成 ppt-themes.generated.ts 和 doc-template-categories.generated.ts
"""
import json
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(REPO_DIR, "data")
DIST_DIR = os.path.join(REPO_DIR, "dist")

os.makedirs(DIST_DIR, exist_ok=True)


def ts_string(s: str) -> str:
    return json.dumps(s, ensure_ascii=False)


def find_ppt_themes(data_dir: str):
    themes = []
    ppt_dir = os.path.join(data_dir, "ppt-theme")
    if not os.path.isdir(ppt_dir):
        return themes
    for root, dirs, files in os.walk(ppt_dir):
        if "manifest.json" in files:
            with open(os.path.join(root, "manifest.json"), "r", encoding="utf-8") as f:
                manifest = json.load(f)
            themes.append(manifest)
    themes.sort(key=lambda t: t.get("order", 0))
    return themes


def load_categories(data_dir: str):
    meta_path = os.path.join(data_dir, "_meta.json")
    if not os.path.exists(meta_path):
        return []
    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)
    return meta.get("categories", [])


def generate_ppt_themes_ts(themes):
    entries = []
    for t in themes:
        colors = t.get("colors", {})
        fonts = t.get("fonts", {})
        lines = []
        lines.append("  {")
        lines.append(f"    id: {ts_string(t['id'])},")
        lines.append(f"    name: {ts_string(t['name'])},")
        # colors
        color_parts = []
        for k in ["primary", "secondary", "background", "text", "accent"]:
            color_parts.append(f"{k}: {ts_string(colors.get(k, ''))}")
        lines.append(f"    colors: {{ {', '.join(color_parts)} }},")
        # fonts
        font_parts = []
        for k in ["title", "body"]:
            font_parts.append(f"{k}: {ts_string(fonts.get(k, ''))}")
        lines.append(f"    fonts: {{ {', '.join(font_parts)} }},")
        lines.append("  },")
        entries.append("\n".join(lines))

    return f"""/**
 * 自动生成文件 — 请勿手动编辑
 * 由 AiDocPlus-DocTemplates/scripts/build.py 生成
 */
import type {{ PptTheme }} from '../index';

export const BUILT_IN_PPT_THEMES: PptTheme[] = [
{chr(10).join(entries)}
];

export const DEFAULT_PPT_THEME: PptTheme = BUILT_IN_PPT_THEMES[0];
"""


def generate_doc_categories_ts(categories):
    entries = []
    for cat in categories:
        key = cat["key"]
        label = cat["name"]
        order = cat.get("order", 0)
        cat_type = "builtin"
        entries.append(
            f'  {{ key: {ts_string(key)}, label: {ts_string(label)}, order: {order}, category_type: {ts_string(cat_type)} }},'
        )

    return f"""/**
 * 自动生成文件 — 请勿手动编辑
 * 由 AiDocPlus-DocTemplates/scripts/build.py 生成
 */

export interface DocTemplateCategory {{
  key: string;
  label: string;
  order: number;
  category_type: string;
}}

export const DEFAULT_DOC_TEMPLATE_CATEGORIES: DocTemplateCategory[] = [
{chr(10).join(entries)}
];
"""


def main():
    print("🔨 构建文档模板数据...")
    themes = find_ppt_themes(DATA_DIR)
    categories = load_categories(DATA_DIR)

    # 生成 PPT 主题
    if themes:
        ts_content = generate_ppt_themes_ts(themes)
        output_path = os.path.join(DIST_DIR, "ppt-themes.generated.ts")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(ts_content)
        print(f"   ✅ {len(themes)} 个 PPT 主题 → ppt-themes.generated.ts")
    else:
        print("   ⚠️  未找到 PPT 主题")

    # 生成文档模板分类
    if categories:
        cat_content = generate_doc_categories_ts(categories)
        cat_output = os.path.join(DIST_DIR, "doc-template-categories.generated.ts")
        with open(cat_output, "w", encoding="utf-8") as f:
            f.write(cat_content)
        print(f"   ✅ {len(categories)} 个分类 → doc-template-categories.generated.ts")

    print(f"✅ 构建完成")


if __name__ == "__main__":
    main()
