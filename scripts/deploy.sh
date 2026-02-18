#!/bin/bash
# AiDocPlus-DocTemplates deploy.sh
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"
PARENT_DIR="$(dirname "$REPO_DIR")"
TARGET_DIR="${PARENT_DIR}/AiDocPlus"
DIST_DIR="${REPO_DIR}/dist"
DATA_DIR="${REPO_DIR}/data"

echo "[deploy] AiDocPlus-DocTemplates -> ${TARGET_DIR}"

# 1. 部署 generated TypeScript 文件
GENERATED_DIR="${TARGET_DIR}/packages/shared-types/src/generated"
mkdir -p "$GENERATED_DIR"

for f in ppt-themes.generated.ts doc-template-categories.generated.ts doc-templates.generated.ts; do
  if [ -f "${DIST_DIR}/${f}" ]; then
    cp "${DIST_DIR}/${f}" "${GENERATED_DIR}/"
    echo "   [ok] ${f} -> generated/"
  fi
done

# 2. 部署模板数据到 bundled-resources
BUNDLED_DIR="${TARGET_DIR}/apps/desktop/src-tauri/bundled-resources/document-templates"
mkdir -p "$BUNDLED_DIR"

if [ -f "${DATA_DIR}/_meta.json" ]; then
  cp "${DATA_DIR}/_meta.json" "${BUNDLED_DIR}/"
fi

find "$DATA_DIR" -name "manifest.json" -not -path "*/_meta.json" | while read -r manifest_file; do
  tmpl_dir="$(dirname "$manifest_file")"
  rel_path="${tmpl_dir#${DATA_DIR}/}"
  target_dir="${BUNDLED_DIR}/${rel_path}"
  mkdir -p "$target_dir"
  cp "${tmpl_dir}/manifest.json" "$target_dir/"
  # 复制可选的 content.json
  [ -f "${tmpl_dir}/content.json" ] && cp "${tmpl_dir}/content.json" "$target_dir/" || true
done

TOTAL=$(find "$DATA_DIR" -name "manifest.json" -not -path "*/_meta.json" | wc -l | tr -d ' ')
echo "   [ok] ${TOTAL} 个文档模板资源 -> bundled-resources/document-templates/"
echo "[done] AiDocPlus-DocTemplates 部署完成"
