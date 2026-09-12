#!/usr/bin/env python3
"""Generate Human Audit Worksheets for Clean 32 Unexposed and Overlap 8 Clusters.

Zero API calls. Strictly loads run artifacts from local disk and produces
structured markdown worksheets marked explicitly as PENDING_HUMAN_AUDIT.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT.parent / "docs/experiments/v41_codex_audit_20260912"
OVERLAP_8 = {42, 56, 325, 345, 361, 369, 433, 501}

luna_dir = ROOT / "results/runs/20260912T074558Z_e2_confirmation_gpt-5_6-luna"
gemini_dir = ROOT / "results/runs/20260912T073141Z_e2_confirmation_gemini-3_1-flash-lite"

luna_files = sorted([f for f in luna_dir.glob("e2_clean_*.json") if not f.name.endswith("_graph.json")])


def generate_worksheet(groups, title, filename, is_overlap):
    lines = [
        f"# {title}",
        "",
        "- **审计状态**: `PENDING_HUMAN_AUDIT` (必须由人类专家独立审查，严禁自动化脚本伪造勾选)",
        f"- **组数**: {len(groups)} 组 ({len(groups)*4} 条 Utterances)",
        f"- **数据集类型**: {'开发/迁移重叠组 (旧 E2 已暴露)' if is_overlap else '真正未见纯净组 (完全排除历史暴露源)'}",
        "- **基准模型**: GPT-5.6-luna (主资产) & Gemini-3.1-flash-lite",
        "- **说明**: 本工作表列出全部指令文本、真实意图标注、候选提取结果与复核输出。重点关注语义偏差、意图幻觉与复核改坏。",
        "",
        "---",
        "",
    ]

    for g in groups:
        gid = g["group_id"]
        gf_gemini = gemini_dir / f"{gid}.json"
        g_gemini = json.loads(gf_gemini.read_text(encoding="utf-8")) if gf_gemini.exists() else None
        cid = g["utterances"][0].get("source_cluster_id")

        lines.append(f"## Group `{gid}` (Cluster `{cid}`)")
        lines.append(f"**暴露状态**: {'旧 E2 重叠簇 (42, 56, 325, 345, 361, 369, 433, 501 之一)' if is_overlap else '纯净未见簇'}")
        lines.append("")

        for idx, u in enumerate(g["utterances"]):
            uid = u["utterance_id"]
            v_type = u["variant_type"]
            text = u["text"]
            gold = u["gold_intent"]
            cands = u["candidates"]
            rev_cand = cands.get("review")

            gem_u = g_gemini["utterances"][idx] if g_gemini else None
            gem_rev_valid = bool(gem_u and gem_u["candidates"].get("review"))

            lines.append(f"### Utterance: `{uid}` ({v_type})")
            lines.append(f'- **Instruction**: "{text}"')
            lines.append(f"- **Gold Intent**: POIs={gold.get('pois')}, TimeLimit={gold.get('time_limit')}, Deps={gold.get('dependencies')}, QWeight={gold.get('quality_weight')}")
            lines.append(f"- **Luna Cand A**: POIs={cands.get('A', {}).get('pois')}, Deps={cands.get('A', {}).get('dependencies')}, QW={cands.get('A', {}).get('quality_weight')}")
            lines.append(f"- **Luna Cand B**: POIs={cands.get('B', {}).get('pois')}, Deps={cands.get('B', {}).get('dependencies')}, QW={cands.get('B', {}).get('quality_weight')}")
            lines.append(f"- **Luna Review**: POIs={rev_cand.get('pois') if rev_cand else None}, Deps={rev_cand.get('dependencies') if rev_cand else None}, QW={rev_cand.get('quality_weight') if rev_cand else None}")

            # Highlight known issues
            if uid == "e2_clean_028_v0":
                lines.append("- **⚠️ [审计焦点/改坏警报]**: Candidate A 满足所有 POI (bank, library, shopping_mall) 成功；但 Review 严重幻觉输出 supermarket，遗漏 bank 和 library，导致规划任务失败 (TSR: True -> False)！")

            lines.append(f"- **Gemini Review 状态**: {'有效 JSON 解析' if gem_rev_valid else '无效格式回退至 Candidate A (Markdown 代码块/Extra data)'}")
            lines.append("- **人工审核背书**:")
            lines.append("  - [ ] 指令语义清晰无歧义")
            lines.append("  - [ ] Gold Intent 标注准确")
            lines.append("  - [ ] 候选差异判断合理")
            lines.append("  - **审核人签署**: `____________________` | **日期**: `____-__-__`")
            lines.append("  - **审核意见/疑点记录**: `PENDING_HUMAN_AUDIT`")
            lines.append("")
        lines.append("---")
        lines.append("")

    target_path = DOCS / filename
    target_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {target_path} ({len(lines)} lines)")


def main():
    clean_groups = []
    overlap_groups = []
    for lf in luna_files:
        g = json.loads(lf.read_text(encoding="utf-8"))
        cid = g["utterances"][0].get("source_cluster_id")
        if cid in OVERLAP_8:
            overlap_groups.append(g)
        else:
            clean_groups.append(g)

    generate_worksheet(clean_groups, "E2 独立确认实验人工审核工作表 (32 个纯净未见簇)", "e2_audit_worksheet_32unexposed.md", is_overlap=False)
    generate_worksheet(overlap_groups, "E2 开发与迁移验证人工审核工作表 (8 个历史暴露重叠簇)", "e2_audit_worksheet_8overlap.md", is_overlap=True)


if __name__ == "__main__":
    main()
