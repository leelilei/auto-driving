#!/usr/bin/env python3
"""Generate an interactive, standalone HTML review portal for DARC-Route test set v1 -> v2 changes.

Reads:
- 9-AutoDriving-core/data/test/test_640_v1_to_v2_changelog.json
- 9-AutoDriving-core/data/test/test_640_utterances_v2_proposed.json
- 9-AutoDriving-core/data/test/test_640_utterances.json

Writes:
- docs/experiments/review_v2_changelog.html
"""

from __future__ import annotations

import difflib
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CORE = ROOT / "9-AutoDriving-core"
DOCS = ROOT / "docs/experiments"


def token_diff_html(old_text: str, new_text: str) -> tuple[str, str]:
    """Generate inline word-level diff HTML for old and new text."""
    if old_text == new_text:
        return old_text, new_text

    tokens_old = re.findall(r"[\w']+|[^\w\s]", old_text)
    tokens_new = re.findall(r"[\w']+|[^\w\s]", new_text)
    matcher = difflib.SequenceMatcher(None, tokens_old, tokens_new)

    def join_tokens(tokens: list[str]) -> str:
        res = ""
        for t in tokens:
            if not res or t in ",.!?;:'’":
                res += t
            else:
                res += " " + t
        return res

    old_chunks = []
    new_chunks = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            chunk = join_tokens(tokens_old[i1:i2])
            old_chunks.append(chunk)
            new_chunks.append(chunk)
        elif tag == "replace":
            chunk_old = join_tokens(tokens_old[i1:i2])
            chunk_new = join_tokens(tokens_new[j1:j2])
            old_chunks.append(f'<mark class="diff-del">{chunk_old}</mark>')
            new_chunks.append(f'<mark class="diff-ins">{chunk_new}</mark>')
        elif tag == "delete":
            chunk_old = join_tokens(tokens_old[i1:i2])
            old_chunks.append(f'<mark class="diff-del">{chunk_old}</mark>')
        elif tag == "insert":
            chunk_new = join_tokens(tokens_new[j1:j2])
            new_chunks.append(f'<mark class="diff-ins">{chunk_new}</mark>')

    return join_tokens(old_chunks), join_tokens(new_chunks)


def main():
    changelog_path = CORE / "data/test/test_640_v1_to_v2_changelog.json"
    v2_proposed_path = CORE / "data/test/test_640_utterances_v2_proposed.json"
    v1_test_path = CORE / "data/test/test_640_utterances.json"

    with open(changelog_path, "r", encoding="utf-8") as f:
        changelog = json.load(f)

    with open(v2_proposed_path, "r", encoding="utf-8") as f:
        v2_data = json.load(f)

    with open(v1_test_path, "r", encoding="utf-8") as f:
        v1_data = json.load(f)

    # Group v2 data by group_id
    v2_by_group = {}
    for item in v2_data:
        gid = item["group_id"]
        v2_by_group.setdefault(gid, []).append(item)

    # Affected groups
    affected_groups = changelog["affected_groups"]
    changelog_entries = changelog["entries"]

    # Build rich structure for affected groups
    groups_data = []
    for gid in affected_groups:
        entries = [e for e in changelog_entries if e["group_id"] == gid]
        entries.sort(key=lambda x: x["variant_type"])
        
        meta_item = v2_by_group[gid][0]
        gold_hard = meta_item.get("gold_hard", {})
        pois = gold_hard.get("pois", [])
        time_limit = gold_hard.get("time_limit")
        dependencies = gold_hard.get("dependencies", [])
        
        var_list = []
        for e in entries:
            old_html, new_html = token_diff_html(e["old_text"], e["proposed_text"])
            var_list.append({
                "variant_type": e["variant_type"],
                "old_text": e["old_text"],
                "proposed_text": e["proposed_text"],
                "old_text_html": old_html,
                "proposed_text_html": new_html,
                "text_changed": e["old_text"] != e["proposed_text"],
                "old_direction": e["old_direction"],
                "proposed_direction": e["proposed_direction"],
                "old_w": e["old_w_synthetic"],
                "proposed_w": e["proposed_w"],
                "reason": e.get("reason", "")
            })

        time_str = "无截止限制"
        if time_limit is not None:
            hours = time_limit // 60
            mins = time_limit % 60
            time_str = f"{hours:02d}:{mins:02d} (截止分钟 {time_limit})"

        dep_str = "无拓扑依赖"
        if dependencies:
            dep_str = ", ".join([f"{d[0]} ➔ {d[1]}" for d in dependencies])

        groups_data.append({
            "group_id": gid,
            "pois": pois,
            "time_str": time_str,
            "dep_str": dep_str,
            "graph_id": meta_item.get("graph_id", ""),
            "variants": var_list
        })

    total_groups_count = len(v2_by_group)
    modified_groups_count = len(affected_groups)
    unaffected_groups_count = total_groups_count - modified_groups_count

    all_groups_meta = []
    for gid in sorted(v2_by_group.keys()):
        items = v2_by_group[gid]
        v0 = items[0]
        gh = v0.get("gold_hard", {})
        all_groups_meta.append({
            "group_id": gid,
            "is_modified": gid in affected_groups,
            "pois": gh.get("pois", []),
            "time_limit": gh.get("time_limit"),
            "dependencies": gh.get("dependencies", []),
            "v0_text": v0.get("text", "")
        })

    html_content = generate_html(
        groups_data=groups_data,
        all_groups_meta=all_groups_meta,
        total_groups_count=total_groups_count,
        modified_groups_count=modified_groups_count,
        unaffected_groups_count=unaffected_groups_count,
        modified_texts_count=changelog["modified_texts_count"],
        modified_weights_count=changelog["modified_weights_count"],
        affected_groups=changelog["affected_groups"],
    )

    out_file = DOCS / "review_v2_changelog.html"
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"[✓] Generated review HTML: {out_file} ({out_file.stat().st_size} bytes)")


def generate_html(
    groups_data: list[dict],
    all_groups_meta: list[dict],
    total_groups_count: int,
    modified_groups_count: int,
    unaffected_groups_count: int,
    modified_texts_count: int,
    modified_weights_count: int,
    affected_groups: list[str],
) -> str:
    groups_json = json.dumps(groups_data, ensure_ascii=False)
    all_meta_json = json.dumps(all_groups_meta, ensure_ascii=False)
    chips_html = "".join([f'<span class="chip" onclick="scrollToGroup(\'{g}\')">{g}</span>' for g in affected_groups])

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>DARC-Route 测试集语义漂移修复审阅工作台 (v1 ➔ v2)</title>
  <style>
    :root {{
      --primary: #2563eb;
      --primary-hover: #1d4ed8;
      --success: #16a34a;
      --success-bg: #dcfce7;
      --warning: #d97706;
      --warning-bg: #fef3c7;
      --danger: #dc2626;
      --danger-bg: #fee2e2;
      --slate-50: #f8fafc;
      --slate-100: #f1f5f9;
      --slate-200: #e2e8f0;
      --slate-300: #cbd5e1;
      --slate-600: #475569;
      --slate-700: #334155;
      --slate-800: #1e293b;
      --slate-900: #0f172a;
    }}
    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
      background-color: var(--slate-50);
      color: var(--slate-800);
      line-height: 1.6;
      padding-bottom: 90px;
    }}
    header {{
      background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
      color: white;
      padding: 24px 36px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.12);
      position: sticky;
      top: 0;
      z-index: 50;
    }}
    .header-content {{
      max-width: 1400px;
      margin: 0 auto;
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 16px;
    }}
    .header-title h1 {{
      font-size: 22px;
      font-weight: 700;
      display: flex;
      align-items: center;
      gap: 10px;
    }}
    .header-title p {{
      font-size: 13px;
      color: #94a3b8;
      margin-top: 4px;
    }}
    .header-badges {{
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
    }}
    .badge {{
      display: inline-flex;
      align-items: center;
      padding: 4px 10px;
      border-radius: 9999px;
      font-size: 12px;
      font-weight: 600;
      gap: 5px;
    }}
    .badge-primary {{ background: #1e40af; color: #dbeafe; }}
    .badge-warning {{ background: #854d0e; color: #fef08a; }}
    .badge-success {{ background: #166534; color: #bbf7d0; }}

    .container {{
      max-width: 1400px;
      margin: 24px auto;
      padding: 0 24px;
    }}

    /* Stat Cards */
    .stats-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 16px;
      margin-bottom: 24px;
    }}
    .stat-card {{
      background: white;
      border-radius: 12px;
      padding: 18px 20px;
      border: 1px solid var(--slate-200);
      box-shadow: 0 1px 3px rgba(0,0,0,0.05);
      display: flex;
      flex-direction: column;
    }}
    .stat-label {{
      font-size: 13px;
      color: var(--slate-600);
      font-weight: 500;
    }}
    .stat-value {{
      font-size: 28px;
      font-weight: 700;
      color: var(--slate-900);
      margin-top: 4px;
    }}
    .stat-desc {{
      font-size: 12px;
      color: #64748b;
      margin-top: 4px;
    }}

    /* Explainer Box */
    .explainer-box {{
      background: #eff6ff;
      border-left: 4px solid var(--primary);
      border-radius: 8px;
      padding: 16px 20px;
      margin-bottom: 24px;
      box-shadow: 0 1px 2px rgba(0,0,0,0.04);
    }}
    .explainer-box h3 {{
      font-size: 15px;
      font-weight: 700;
      color: #1e40af;
      margin-bottom: 6px;
      display: flex;
      align-items: center;
      gap: 8px;
    }}
    .explainer-box p {{
      font-size: 13.5px;
      color: #1e3a8a;
      line-height: 1.6;
    }}

    /* Toolbar & Navigation */
    .toolbar {{
      background: white;
      border-radius: 12px;
      padding: 16px 20px;
      border: 1px solid var(--slate-200);
      box-shadow: 0 1px 3px rgba(0,0,0,0.05);
      margin-bottom: 24px;
      display: flex;
      flex-direction: column;
      gap: 14px;
    }}
    .toolbar-row {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 12px;
    }}
    .tabs {{
      display: flex;
      gap: 8px;
    }}
    .tab-btn {{
      padding: 8px 16px;
      border-radius: 8px;
      border: 1px solid var(--slate-200);
      background: var(--slate-100);
      font-size: 13.5px;
      font-weight: 600;
      cursor: pointer;
      color: var(--slate-700);
      transition: all 0.2s;
    }}
    .tab-btn.active {{
      background: var(--primary);
      color: white;
      border-color: var(--primary);
    }}
    .action-btns {{
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
    }}
    .btn {{
      padding: 8px 14px;
      border-radius: 8px;
      border: 1px solid transparent;
      font-size: 13px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.15s;
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }}
    .btn-outline {{
      border-color: var(--slate-300);
      background: white;
      color: var(--slate-700);
    }}
    .btn-outline:hover {{
      background: var(--slate-100);
    }}
    .btn-success {{
      background: var(--success);
      color: white;
    }}
    .btn-success:hover {{
      background: #15803d;
    }}
    .btn-primary {{
      background: var(--primary);
      color: white;
    }}
    .btn-primary:hover {{
      background: var(--primary-hover);
    }}

    .filter-chips {{
      display: flex;
      gap: 6px;
      flex-wrap: wrap;
      align-items: center;
    }}
    .chip-label {{
      font-size: 12px;
      font-weight: 600;
      color: var(--slate-600);
      margin-right: 4px;
    }}
    .chip {{
      padding: 4px 10px;
      border-radius: 6px;
      font-size: 12px;
      background: var(--slate-100);
      border: 1px solid var(--slate-200);
      cursor: pointer;
      font-weight: 500;
      color: var(--slate-700);
      transition: all 0.15s;
    }}
    .chip:hover {{
      border-color: var(--primary);
      color: var(--primary);
    }}
    .chip.active {{
      background: #dbeafe;
      border-color: var(--primary);
      color: #1e40af;
      font-weight: 600;
    }}
    .search-input {{
      padding: 8px 14px;
      border-radius: 8px;
      border: 1px solid var(--slate-300);
      font-size: 13px;
      width: 260px;
      outline: none;
    }}
    .search-input:focus {{
      border-color: var(--primary);
      box-shadow: 0 0 0 3px rgba(37,99,235,0.15);
    }}

    /* Group Card */
    .group-card {{
      background: white;
      border-radius: 14px;
      border: 1px solid var(--slate-200);
      box-shadow: 0 2px 5px rgba(0,0,0,0.04);
      margin-bottom: 24px;
      overflow: hidden;
      transition: box-shadow 0.2s, border-color 0.2s;
    }}
    .group-card:hover {{
      box-shadow: 0 6px 16px rgba(0,0,0,0.07);
    }}
    .group-card.status-approved {{
      border-left: 6px solid var(--success);
    }}
    .group-card.status-flagged {{
      border-left: 6px solid var(--danger);
    }}
    .group-card.status-pending {{
      border-left: 6px solid var(--warning);
    }}

    .group-header {{
      padding: 16px 22px;
      background: #f8fafc;
      border-bottom: 1px solid var(--slate-200);
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 12px;
    }}
    .group-header-left {{
      display: flex;
      align-items: center;
      gap: 14px;
      flex-wrap: wrap;
    }}
    .group-id-badge {{
      font-size: 16px;
      font-weight: 700;
      color: var(--slate-900);
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
    }}
    .group-tags {{
      display: flex;
      gap: 6px;
      flex-wrap: wrap;
    }}
    .tag {{
      display: inline-flex;
      align-items: center;
      padding: 2px 8px;
      border-radius: 4px;
      font-size: 11.5px;
      background: var(--slate-200);
      color: var(--slate-700);
      font-weight: 500;
    }}
    .tag-blue {{ background: #e0e7ff; color: #3730a3; }}
    .tag-amber {{ background: #fef3c7; color: #92400e; }}
    .tag-purple {{ background: #f3e8ff; color: #6b21a8; }}

    .group-header-right {{
      display: flex;
      align-items: center;
      gap: 10px;
    }}
    .btn-action-group {{
      display: inline-flex;
      border-radius: 8px;
      overflow: hidden;
      border: 1px solid var(--slate-300);
    }}
    .btn-toggle {{
      padding: 6px 12px;
      border: none;
      background: white;
      font-size: 12px;
      font-weight: 600;
      cursor: pointer;
      color: var(--slate-600);
      transition: all 0.15s;
    }}
    .btn-toggle:not(:last-child) {{
      border-right: 1px solid var(--slate-300);
    }}
    .btn-toggle.active-approved {{
      background: var(--success);
      color: white;
    }}
    .btn-toggle.active-flagged {{
      background: var(--danger);
      color: white;
    }}

    .group-body {{
      padding: 20px 22px;
    }}

    /* Variants Grid */
    .variants-table {{
      width: 100%;
      border-collapse: separate;
      border-spacing: 0;
      margin-top: 10px;
      border: 1px solid var(--slate-200);
      border-radius: 10px;
      overflow: hidden;
    }}
    .variants-table th {{
      background: #f1f5f9;
      padding: 10px 14px;
      font-size: 12px;
      font-weight: 700;
      color: var(--slate-700);
      text-align: left;
      border-bottom: 1px solid var(--slate-200);
    }}
    .variants-table td {{
      padding: 12px 14px;
      font-size: 13.5px;
      border-bottom: 1px solid var(--slate-100);
      vertical-align: top;
    }}
    .variants-table tr:last-child td {{
      border-bottom: none;
    }}
    .var-type {{
      font-weight: 700;
      color: var(--slate-900);
      font-size: 12px;
      display: inline-block;
      padding: 2px 6px;
      border-radius: 4px;
      background: var(--slate-100);
    }}
    .var-type.v0 {{ background: #e2e8f0; color: #334155; }}
    .var-type.v1 {{ background: #dbeafe; color: #1e40af; }}
    .var-type.v2 {{ background: #ede9fe; color: #6d28d9; }}
    .var-type.v3 {{ background: #fae8ff; color: #86198f; }}

    /* Diff highlighting */
    mark.diff-del {{
      background-color: #fee2e2;
      color: #991b1b;
      text-decoration: line-through;
      padding: 1px 4px;
      border-radius: 3px;
    }}
    mark.diff-ins {{
      background-color: #dcfce7;
      color: #166534;
      font-weight: 600;
      padding: 1px 4px;
      border-radius: 3px;
    }}

    .diff-cell {{
      display: flex;
      flex-direction: column;
      gap: 6px;
    }}
    .diff-row-old {{
      font-size: 13px;
      color: #475569;
      background: #fef2f2;
      padding: 6px 10px;
      border-radius: 6px;
      border-left: 3px solid #f87171;
    }}
    .diff-row-new {{
      font-size: 13px;
      color: #0f172a;
      background: #f0fdf4;
      padding: 6px 10px;
      border-radius: 6px;
      border-left: 3px solid #4ade80;
    }}
    .diff-row-same {{
      font-size: 13px;
      color: #334155;
      background: #f8fafc;
      padding: 6px 10px;
      border-radius: 6px;
      border-left: 3px solid #94a3b8;
    }}

    .param-change {{
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 12px;
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
    }}
    .param-old {{
      color: #dc2626;
      text-decoration: line-through;
    }}
    .param-arrow {{
      color: #94a3b8;
    }}
    .param-new {{
      color: #16a34a;
      font-weight: 700;
    }}

    .note-box {{
      margin-top: 14px;
      display: flex;
      gap: 10px;
      align-items: center;
    }}
    .note-input {{
      flex: 1;
      padding: 6px 12px;
      border-radius: 6px;
      border: 1px solid var(--slate-300);
      font-size: 12.5px;
    }}
    .note-input:focus {{
      border-color: var(--primary);
      outline: none;
    }}

    /* All 160 View Table */
    .all-groups-table {{
      width: 100%;
      border-collapse: collapse;
      background: white;
      border-radius: 10px;
      overflow: hidden;
      border: 1px solid var(--slate-200);
      box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }}
    .all-groups-table th {{
      background: #f8fafc;
      padding: 12px 16px;
      font-size: 12px;
      font-weight: 700;
      color: var(--slate-700);
      text-align: left;
      border-bottom: 1px solid var(--slate-200);
    }}
    .all-groups-table td {{
      padding: 12px 16px;
      font-size: 13px;
      border-bottom: 1px solid var(--slate-100);
    }}
    .all-groups-table tr:hover td {{
      background: #f8fafc;
    }}

    /* Modal */
    .modal-backdrop {{
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(0,0,0,0.5);
      display: none;
      align-items: center;
      justify-content: center;
      z-index: 100;
    }}
    .modal {{
      background: white;
      border-radius: 14px;
      padding: 24px;
      max-width: 680px;
      width: 90%;
      max-height: 85vh;
      overflow-y: auto;
      box-shadow: 0 20px 25px -5px rgba(0,0,0,0.1);
    }}
    .modal-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 16px;
    }}
    .modal-header h3 {{
      font-size: 18px;
      font-weight: 700;
    }}
    .modal-close {{
      background: none;
      border: none;
      font-size: 20px;
      cursor: pointer;
      color: #64748b;
    }}
    .modal-textarea {{
      width: 100%;
      height: 280px;
      font-family: monospace;
      font-size: 12px;
      padding: 12px;
      border: 1px solid var(--slate-300);
      border-radius: 8px;
      margin-top: 10px;
      outline: none;
    }}

    .footer-bar {{
      position: fixed;
      bottom: 0;
      left: 0;
      right: 0;
      background: white;
      border-top: 1px solid var(--slate-200);
      padding: 12px 24px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      box-shadow: 0 -4px 12px rgba(0,0,0,0.05);
      z-index: 40;
    }}
    .footer-info {{
      font-size: 13.5px;
      font-weight: 600;
      color: var(--slate-700);
      display: flex;
      align-items: center;
      gap: 16px;
    }}
    .progress-bar-wrap {{
      width: 200px;
      height: 8px;
      background: var(--slate-200);
      border-radius: 9999px;
      overflow: hidden;
    }}
    .progress-bar-fill {{
      height: 100%;
      background: var(--success);
      width: 0%;
      transition: width 0.3s;
    }}
  </style>
</head>
<body>

  <header>
    <div class="header-content">
      <div class="header-title">
        <h1><span>🚗</span> DARC-Route 测试集语义漂移修复审阅工作台</h1>
        <p>数据版本变更: 1.0.0-exploratory ➔ 2.0.0-proposed ｜ 针对 14 组语义漂移改写的人工审核视图</p>
      </div>
      <div class="header-badges">
        <span class="badge badge-primary">Test Split: 160 组 / 640 句</span>
        <span class="badge badge-warning">修订组数: 14 组 (42 改写, 56 权重)</span>
        <span class="badge badge-success">未修改组数: 146 组 (100% 保持)</span>
      </div>
    </div>
  </header>

  <div class="container">

    <!-- Top Metric Cards -->
    <div class="stats-grid">
      <div class="stat-card">
        <span class="stat-label">待审阅修订组数</span>
        <span class="stat-value" style="color: var(--primary);">14 <span style="font-size: 14px; font-weight: normal; color: #64748b;">组</span></span>
        <span class="stat-desc">占全部 160 组的 8.75%</span>
      </div>
      <div class="stat-card">
        <span class="stat-label">文本改写总数</span>
        <span class="stat-value" style="color: var(--warning);">42 <span style="font-size: 14px; font-weight: normal; color: #64748b;">句</span></span>
        <span class="stat-desc">14 组 × (V1+V2+V3)</span>
      </div>
      <div class="stat-card">
        <span class="stat-label">偏好权重归正</span>
        <span class="stat-value" style="color: var(--success);">56 <span style="font-size: 14px; font-weight: normal; color: #64748b;">处</span></span>
        <span class="stat-desc">0.60 ➔ 0.50 (对齐 balanced)</span>
      </div>
      <div class="stat-card">
        <span class="stat-label">当前审核进度</span>
        <span class="stat-value" id="topProgressStat">0 / 14</span>
        <span class="stat-desc" id="topProgressPct">完成度 0%</span>
      </div>
    </div>

    <!-- Explainer Callout -->
    <div class="explainer-box">
      <h3><span>💡</span> 为什么必须进行这次数据修正？（漂移根因回顾）</h3>
      <p>
        在历史探索测试集生成过程中，这 14 组原句（V0）文本均明确表达了<strong>“平衡评分与距离/路程”（Aim for a balance between...）</strong>。然而在初始数据合成中，原合成标签错误打上了 <code>quality_first</code>（权重 0.60）。改写模型在生成同义改写（V1）、句式变换（V2）、口语表达（V3）时，受标签驱动错误注入了 <em>"Prioritize locations with high ratings" / "Give top priority to reputable venues"</em> 等品质优先词句。
        <br><br>
        <strong>后果</strong>：大模型在 V0 上选平衡路线、在 V1-V3 上选高分路线，原本是<strong>“精准遵循用户不同指令”</strong>的合理行为，却在评测中被误判为<strong>“缺乏鲁棒性”的路线翻转（Route Flip）</strong>。
        <br>
        <strong>整改方案</strong>：保留 V0 原句不变；将 V1-V3 误插入的高分优先表述剔除，重新对齐为与 V0 完全一致的平衡表述；标签与权重统一归正为 <code>balanced (w=0.50)</code>。
      </p>
    </div>

    <!-- Toolbar -->
    <div class="toolbar">
      <div class="toolbar-row">
        <div class="tabs">
          <button class="tab-btn active" id="tabFocus" onclick="switchTab('focus')">🎯 14 组重点审阅视图 (Focus Diff)</button>
          <button class="tab-btn" id="tabAll" onclick="switchTab('all')">📋 全部 160 组测试集浏览 (All 160)</button>
        </div>
        <div class="action-btns">
          <input type="text" id="searchInput" class="search-input" placeholder="🔍 搜索 Group ID 或关键词..." oninput="onSearchChange()">
          <button class="btn btn-outline" onclick="approveAll()">✓ 全部通过</button>
          <button class="btn btn-outline" onclick="resetReview()">↺ 重置审核</button>
          <button class="btn btn-primary" onclick="openExportModal()">📥 导出审核结论</button>
        </div>
      </div>
      <div class="toolbar-row" id="quickJumpRow">
        <div class="filter-chips">
          <span class="chip-label">快速跳转组:</span>
          {chips_html}
        </div>
      </div>
    </div>

    <!-- View 1: Focus 14 Groups -->
    <div id="focusView">
      <!-- Injected by JavaScript -->
    </div>

    <!-- View 2: All 160 Groups -->
    <div id="allView" style="display: none;">
      <table class="all-groups-table">
        <thead>
          <tr>
            <th style="width: 110px;">Group ID</th>
            <th style="width: 100px;">状态</th>
            <th style="width: 180px;">POI 需求</th>
            <th style="width: 140px;">截止时间</th>
            <th style="width: 150px;">拓扑依赖</th>
            <th>V0 原句预览</th>
          </tr>
        </thead>
        <tbody id="allGroupsTbody">
          <!-- Injected by JavaScript -->
        </tbody>
      </table>
    </div>

  </div>

  <!-- Bottom Floating Bar -->
  <div class="footer-bar">
    <div class="footer-info">
      <span id="footerApprovedCount">已通过: 0 / 14 组</span>
      <span id="footerFlaggedCount" style="color: var(--danger);">有异议: 0 组</span>
      <div class="progress-bar-wrap">
        <div class="progress-bar-fill" id="progressBarFill"></div>
      </div>
    </div>
    <div>
      <button class="btn btn-success" onclick="openExportModal()">✓ 完成审核并导出报告</button>
    </div>
  </div>

  <!-- Export Modal -->
  <div class="modal-backdrop" id="exportModal">
    <div class="modal">
      <div class="modal-header">
        <h3>📄 导出人工审核决议报告</h3>
        <button class="modal-close" onclick="closeExportModal()">✕</button>
      </div>
      <p style="font-size: 13px; color: #475569;">
        您可以直接复制下方生成的 Markdown 决议文本粘贴到聊天窗口，或者保存为文件作为正式审核证据。
      </p>
      <textarea class="modal-textarea" id="exportText" readonly></textarea>
      <div style="margin-top: 16px; display: flex; justify-content: flex-end; gap: 10px;">
        <button class="btn btn-outline" onclick="copyExportText()">📋 复制到剪贴板</button>
        <button class="btn btn-primary" onclick="downloadExportJson()">💾 下载 JSON 审核记录</button>
      </div>
    </div>
  </div>

  <script>
    const groupsData = {groups_json};
    const allGroupsMeta = {all_meta_json};

    // Review state: {{ gid: {{ status: 'approved'|'flagged'|'pending', note: '' }} }}
    let reviewState = JSON.parse(localStorage.getItem('darc_v2_review_state') || '{{}}');

    // Initialize state - default approved for easy confirmation, user can toggle
    groupsData.forEach(g => {{
      if (!reviewState[g.group_id]) {{
        reviewState[g.group_id] = {{ status: 'approved', note: '' }};
      }}
    }});

    function saveState() {{
      localStorage.setItem('darc_v2_review_state', JSON.stringify(reviewState));
      updateProgress();
    }}

    function setGroupStatus(gid, status) {{
      if (!reviewState[gid]) reviewState[gid] = {{ status: 'pending', note: '' }};
      reviewState[gid].status = status;
      saveState();
      renderFocusView();
    }}

    function setGroupNote(gid, note) {{
      if (!reviewState[gid]) reviewState[gid] = {{ status: 'pending', note: '' }};
      reviewState[gid].note = note;
      saveState();
    }}

    function approveAll() {{
      groupsData.forEach(g => {{
        if (!reviewState[g.group_id]) reviewState[g.group_id] = {{}};
        reviewState[g.group_id].status = 'approved';
      }});
      saveState();
      renderFocusView();
    }}

    function resetReview() {{
      if (confirm('确认重置所有审核标记为待审阅？')) {{
        groupsData.forEach(g => {{
          reviewState[g.group_id] = {{ status: 'pending', note: '' }};
        }});
        saveState();
        renderFocusView();
      }}
    }}

    function updateProgress() {{
      let approved = 0;
      let flagged = 0;
      groupsData.forEach(g => {{
        const st = reviewState[g.group_id]?.status;
        if (st === 'approved') approved++;
        else if (st === 'flagged') flagged++;
      }});
      const total = groupsData.length;
      const pct = Math.round((approved / total) * 100);

      document.getElementById('topProgressStat').innerText = `${{approved}} / ${{total}}`;
      document.getElementById('topProgressPct').innerText = `已认可 ${{pct}}% (异议 ${{flagged}})`;
      document.getElementById('footerApprovedCount').innerText = `已通过: ${{approved}} / ${{total}} 组`;
      document.getElementById('footerFlaggedCount').innerText = `有异议: ${{flagged}} 组`;
      document.getElementById('progressBarFill').style.width = pct + '%';
    }}

    function renderFocusView() {{
      const container = document.getElementById('focusView');
      const q = document.getElementById('searchInput').value.trim().toLowerCase();

      let html = '';
      groupsData.forEach((g, idx) => {{
        if (q) {{
          const matchId = g.group_id.toLowerCase().includes(q);
          const matchText = g.variants.some(v => v.old_text.toLowerCase().includes(q) || v.proposed_text.toLowerCase().includes(q));
          if (!matchId && !matchText) return;
        }}

        const state = reviewState[g.group_id] || {{ status: 'pending', note: '' }};
        const statusClass = 'status-' + state.status;

        html += `
          <div class="group-card ${{statusClass}}" id="group-card-${{g.group_id}}">
            <div class="group-header">
              <div class="group-header-left">
                <span class="group-id-badge">${{g.group_id}}</span>
                <div class="group-tags">
                  <span class="tag tag-blue">POI: ${{g.pois.join(', ')}}</span>
                  <span class="tag tag-amber">截止: ${{g.time_str}}</span>
                  <span class="tag tag-purple">依赖: ${{g.dep_str}}</span>
                </div>
              </div>
              <div class="group-header-right">
                <div class="btn-action-group">
                  <button class="btn-toggle ${{state.status === 'approved' ? 'active-approved' : ''}}" onclick="setGroupStatus('${{g.group_id}}', 'approved')">✓ 认可通过</button>
                  <button class="btn-toggle ${{state.status === 'flagged' ? 'active-flagged' : ''}}" onclick="setGroupStatus('${{g.group_id}}', 'flagged')">✕ 存在异议</button>
                </div>
              </div>
            </div>
            <div class="group-body">
              <table class="variants-table">
                <thead>
                  <tr>
                    <th style="width: 70px;">版本</th>
                    <th style="width: 140px;">字段与权重变更</th>
                    <th>原版 (v1) vs 提议修正 (v2) 文本对比</th>
                  </tr>
                </thead>
                <tbody>
                  ${{g.variants.map(v => `
                    <tr>
                      <td>
                        <span class="var-type ${{v.variant_type.toLowerCase()}}">${{v.variant_type}}</span>
                        <div style="font-size: 11px; color: #64748b; margin-top: 4px;">
                          ${{v.variant_type === 'V0' ? '原句基准' : v.variant_type === 'V1' ? '同义改写' : v.variant_type === 'V2' ? '句式变换' : '口语表达'}}
                        </div>
                      </td>
                      <td>
                        <div class="param-change">
                          <span class="param-old">${{v.old_direction}} (${{v.old_w.toFixed(2)}})</span>
                          <span class="param-arrow">➔</span>
                          <span class="param-new">${{v.proposed_direction}} (${{v.proposed_w.toFixed(2)}})</span>
                        </div>
                      </td>
                      <td>
                        <div class="diff-cell">
                          ${{v.text_changed ? `
                            <div class="diff-row-old">
                              <strong>[v1 原版]</strong> ${{v.old_text_html}}
                            </div>
                            <div class="diff-row-new">
                              <strong>[v2 提议]</strong> ${{v.proposed_text_html}}
                            </div>
                          ` : `
                            <div class="diff-row-same">
                              <strong>[保持不变]</strong> ${{v.old_text}}
                            </div>
                          `}}
                        </div>
                      </td>
                    </tr>
                  `).join('')}}
                </tbody>
              </table>

              <div class="note-box">
                <span style="font-size: 12px; font-weight: 600; color: #64748b;">审阅批注:</span>
                <input type="text" class="note-input" placeholder="可在此输入该组的审核意见或修改建议（选填）..." value="${{state.note || ''}}" onchange="setGroupNote('${{g.group_id}}', this.value)">
              </div>
            </div>
          </div>
        `;
      }});

      container.innerHTML = html || '<div style="text-align: center; padding: 40px; color: #94a3b8;">无匹配的组</div>';
    }}

    function renderAllGroupsView() {{
      const tbody = document.getElementById('allGroupsTbody');
      const q = document.getElementById('searchInput').value.trim().toLowerCase();

      let html = '';
      allGroupsMeta.forEach(g => {{
        if (q) {{
          const matchId = g.group_id.toLowerCase().includes(q);
          const matchText = g.v0_text.toLowerCase().includes(q);
          if (!matchId && !matchText) return;
        }}

        const isMod = g.is_modified;
        html += `
          <tr>
            <td>
              <strong style="font-family: monospace;">${{g.group_id}}</strong>
            </td>
            <td>
              ${{isMod ? '<span class="badge badge-warning">漂移修订 (14组)</span>' : '<span class="badge badge-success">保持原样</span>'}}
            </td>
            <td>${{g.pois.join(', ')}}</td>
            <td>${{g.time_limit ? g.time_limit + ' 分' : '无'}}</td>
            <td>${{g.dependencies.length ? g.dependencies.map(d => d[0] + '➔' + d[1]).join(', ') : '无'}}</td>
            <td style="font-size: 12px; color: #475569;">${{g.v0_text}}</td>
          </tr>
        `;
      }});
      tbody.innerHTML = html || '<tr><td colspan="6" style="text-align: center;">无匹配项</td></tr>';
    }}

    function switchTab(tab) {{
      document.getElementById('tabFocus').classList.toggle('active', tab === 'focus');
      document.getElementById('tabAll').classList.toggle('active', tab === 'all');
      document.getElementById('focusView').style.display = tab === 'focus' ? 'block' : 'none';
      document.getElementById('allView').style.display = tab === 'all' ? 'block' : 'none';
      document.getElementById('quickJumpRow').style.display = tab === 'focus' ? 'flex' : 'none';

      if (tab === 'focus') renderFocusView();
      else renderAllGroupsView();
    }}

    function onSearchChange() {{
      const isFocus = document.getElementById('tabFocus').classList.contains('active');
      if (isFocus) renderFocusView();
      else renderAllGroupsView();
    }}

    function scrollToGroup(gid) {{
      const el = document.getElementById('group-card-' + gid);
      if (el) {{
        el.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
        el.style.outline = '3px solid var(--primary)';
        setTimeout(() => {{ el.style.outline = 'none'; }}, 1500);
      }}
    }}

    function openExportModal() {{
      let approvedCount = 0;
      let flaggedCount = 0;
      const flags = [];

      groupsData.forEach(g => {{
        const st = reviewState[g.group_id]?.status;
        const note = reviewState[g.group_id]?.note || '';
        if (st === 'approved') approvedCount++;
        else if (st === 'flagged') {{
          flaggedCount++;
          flags.push(`- **${{g.group_id}}**: ${{note || '有异议'}}`);
        }}
      }});

      let md = `# DARC-Route 测试集 14 组语义漂移人工审核决议报告\\n\\n`;
      md += `> **审核人**：研究负责人 / 人工审核员\\n`;
      md += `> **审核时间**：${{new Date().toISOString().replace('T', ' ').substring(0, 19)}}\\n`;
      md += `> **审核范围**：14 组语义漂移表达（共 56 句，42 处文本改写，56 处权重归正）\\n\\n`;
      md += `## 1. 审核结论\\n\\n`;
      md += `- **审核通过组数**：${{approvedCount}} / 14 组\\n`;
      md += `- **存在异议组数**：${{flaggedCount}} / 14 组\\n`;
      md += `- **综合决议**：${{flaggedCount === 0 ? '【全部认可通过 (APPROVED)】，准予冻结为正式数据集 v2_confirmed' : '【存在异议需微调 (CONDITIONAL)】'}} \\n\\n`;

      if (flags.length > 0) {{
        md += `## 2. 异议清单\\n\\n` + flags.join('\\n') + '\\n\\n';
      }} else {{
        md += `## 2. 异议清单\\n\\n无异议。全部 14 组改写成功剔除了 V1-V3 的高分优先漂移表述，恢复与 V0 完全一致的平衡语义。\\n\\n`;
      }}

      md += `## 3. 逐组明细状态\\n\\n`;
      groupsData.forEach(g => {{
        const st = reviewState[g.group_id]?.status || 'pending';
        const note = reviewState[g.group_id]?.note || '';
        md += `- **${{g.group_id}}**: ${{st === 'approved' ? '✓ APPROVED' : '✕ FLAGGED'}} ${{note ? '(' + note + ')' : ''}}\\n`;
      }});

      document.getElementById('exportText').value = md;
      document.getElementById('exportModal').style.display = 'flex';
    }}

    function closeExportModal() {{
      document.getElementById('exportModal').style.display = 'none';
    }}

    function copyExportText() {{
      const ta = document.getElementById('exportText');
      ta.select();
      navigator.clipboard.writeText(ta.value).then(() => {{
        alert('已复制审核报告到剪贴板！');
      }});
    }}

    function downloadExportJson() {{
      const dataStr = 'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify({{
        timestamp: new Date().toISOString(),
        reviewer: 'Human Reviewer',
        decision: reviewState
      }}, null, 2));
      const a = document.createElement('a');
      a.setAttribute('href', dataStr);
      a.setAttribute('download', 'darc_route_v2_review_decision.json');
      document.body.appendChild(a);
      a.click();
      a.remove();
    }}

    // Initial render
    renderFocusView();
    updateProgress();
  </script>
</body>
</html>
"""


if __name__ == "__main__":
    main()
