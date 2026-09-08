#!/usr/bin/env python3
"""Preprocess HIPP.json, normalize schema, perform semantic clustering, and generate summary report.

Per Proposal v4 Section 5.2:
- S: Requested POI types (shopping_mall, supermarket, pharmacy, bank, library)
- T: Latest finish time in minutes, or None
- D: Directed dependency pairs, compared via transitive closure
- w: quality_weight in [0, 1]
- preference_direction: quality (w > 0.5), distance (w < 0.5), balanced (w == 0.5)
"""

import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from src.intent import category, deadline

ROOT_DIR = Path(__file__).resolve().parents[1]  # 9-AutoDriving-core
RAW_FILE = ROOT_DIR / "data" / "raw" / "HIPP.json"
REPORT_FILE = ROOT_DIR / "data" / "reports" / "hipp_clustering_summary.md"
PROCESSED_FILE = ROOT_DIR / "data" / "processed" / "hipp_clusters.json"


def normalize_time_limit(val) -> int | None:
    return deadline(val)



def compute_transitive_closure(deps: list) -> tuple[tuple[str, str], ...]:
    """Compute transitive closure of directed dependencies."""
    if not deps:
        return ()
    edges = set()
    nodes = set()
    for d in deps:
        if isinstance(d, (list, tuple)) and len(d) == 2:
            u, v = category(d[0]), category(d[1])
            edges.add((u, v))
            nodes.add(u)
            nodes.add(v)

    # Floyd-Warshall style closure
    reach = {u: set() for u in nodes}
    for u, v in edges:
        reach[u].add(v)

    for k in nodes:
        for i in nodes:
            if k in reach[i]:
                reach[i].update(reach[k])

    closure = []
    for u in sorted(nodes):
        for v in sorted(reach[u]):
            closure.append((u, v))
    return tuple(closure)


def determine_direction(quality_w: float) -> str:
    if abs(quality_w - 0.5) < 1e-4:
        return "balanced"
    elif quality_w > 0.5:
        return "quality_first"
    else:
        return "distance_first"


def main():
    print(f"Loading raw dataset from {RAW_FILE}...")
    if not RAW_FILE.exists():
        raise FileNotFoundError(f"Raw HIPP file not found at {RAW_FILE}")

    raw_records = json.loads(RAW_FILE.read_text(encoding="utf-8"))
    print(f"Loaded {len(raw_records)} records.")

    clusters = defaultdict(list)

    for idx, item in enumerate(raw_records):
        syn = item.get("synthetic_label", {})
        instruction = item.get("human_instruction", "")

        raw_pois = [category(p) for p in syn.get("pois", [])]
        norm_s = tuple(sorted(set(raw_pois)))
        norm_t = normalize_time_limit(syn.get("time_limit"))
        raw_deps = [[category(a), category(b)] for a, b in syn.get("dependencies", [])]
        norm_closure = compute_transitive_closure(raw_deps)
        qw = float(syn.get("quality_weight", 0.5))
        dw = float(syn.get("distance_weight", 0.5))
        direction = determine_direction(qw)

        cluster_key = (norm_s, norm_t, norm_closure, direction)

        parsed_record = {
            "source_index": idx,
            "instruction": instruction,
            "pois": list(norm_s),
            "poi_count": len(norm_s),
            "time_limit": norm_t,
            "has_time_limit": norm_t is not None,
            "dependencies": raw_deps,
            "dependency_closure": list(norm_closure),
            "has_dependencies": len(norm_closure) > 0,
            "quality_weight": qw,
            "distance_weight": dw,
            "direction": direction,
        }
        clusters[cluster_key].append(parsed_record)

    total_clusters = len(clusters)
    print(f"Preprocessed into {total_clusters} unique semantic intent clusters.")

    # Convert clusters to serializable list
    cluster_list = []
    for c_idx, (k, members) in enumerate(clusters.items()):
        norm_s, norm_t, norm_closure, direction = k
        cluster_list.append({
            "cluster_id": c_idx,
            "intent_key": {
                "pois": list(norm_s),
                "poi_count": len(norm_s),
                "time_limit": norm_t,
                "closure": list(norm_closure),
                "direction": direction,
            },
            "member_count": len(members),
            "sample_instruction": members[0]["instruction"],
            "records": members,
        })

    # Save processed clusters
    PROCESSED_FILE.parent.mkdir(parents=True, exist_ok=True)
    PROCESSED_FILE.write_text(json.dumps(cluster_list, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[✓] Saved clusters to {PROCESSED_FILE.relative_to(ROOT_DIR.parent)}")

    # Generate comprehensive report
    poi_count_dist = Counter(c["intent_key"]["poi_count"] for c in cluster_list)
    time_limit_dist = Counter(c["intent_key"]["time_limit"] is not None for c in cluster_list)
    dep_dist = Counter(len(c["intent_key"]["closure"]) > 0 for c in cluster_list)
    direction_dist = Counter(c["intent_key"]["direction"] for c in cluster_list)
    cluster_size_dist = Counter(c["member_count"] for c in cluster_list)

    report_lines = [
        "# HIPP 数据集预处理与语义聚类去重审计报告",
        "",
        "> 生成日期：2026-09-06  ",
        f"> 数据源：`data/raw/HIPP.json`（公开 LLMAP 冻结提交 `281f6ad95f42ca386400e5288f006aeffa2ac282`）",
        "",
        "## 1. 聚类去重核心统计",
        "",
        f"- **原始记录总数**：`{len(raw_records)}` 条",
        f"- **去重后合成标签簇（待文本语义审核）**：`{total_clusters}` 簇",
        f"- **平均每簇样本数**：`{len(raw_records) / total_clusters:.2f}` 条（簇大小分布：{dict(cluster_size_dist.most_common(5))}）",
        "- **边界**：这些簇由合成硬标签与合成权重方向分组，尚未通过文本人工审核，不能直接称为 609 个独立真实意图。正式抽样前还需核对文本偏好与近重复。",
        "",
        "---",
        "",
        "## 2. 独立意图簇属性分布",
        "",
        "### 2.1 请求 POI 数量分布",
        "| POI 数量 | 语义簇数量 | 占比 |",
        "|:---:|---:|---:|",
    ]
    for count in sorted(poi_count_dist.keys()):
        pct = poi_count_dist[count] / total_clusters * 100
        report_lines.append(f"| {count} 类 POI | {poi_count_dist[count]} | {pct:.1f}% |")

    report_lines += [
        "",
        "### 2.2 时间约束与先后依赖分布",
        "| 约束维度 | 具有该约束的簇数 | 占比 |",
        "|---|---:|---:|",
        f"| 含最晚截止时间 ($T \\neq \\text{{null}}$) | {time_limit_dist[True]} | {time_limit_dist[True] / total_clusters * 100:.1f}% |",
        f"| 无截止时间约束 | {time_limit_dist[False]} | {time_limit_dist[False] / total_clusters * 100:.1f}% |",
        f"| 含先后顺序依赖 ($D \\neq \\emptyset$) | {dep_dist[True]} | {dep_dist[True] / total_clusters * 100:.1f}% |",
        f"| 无先后顺序依赖 | {dep_dist[False]} | {dep_dist[False] / total_clusters * 100:.1f}% |",
        "",
        "### 2.3 偏好方向分布",
        "| 偏好方向 | 语义簇数量 | 占比 |",
        "|---|---:|---:|",
        f"| 质量优先 (Quality First, $w > 0.5$) | {direction_dist['quality_first']} | {direction_dist['quality_first'] / total_clusters * 100:.1f}% |",
        f"| 距离优先 (Distance First, $w < 0.5$) | {direction_dist['distance_first']} | {direction_dist['distance_first'] / total_clusters * 100:.1f}% |",
        f"| 均衡偏好 (Balanced, $w = 0.5$) | {direction_dist['balanced']} | {direction_dist['balanced'] / total_clusters * 100:.1f}% |",
        "",
        "---",
        "",
        "## 3. 代表性语义簇样例",
        "",
        "| 簇 ID | POI 集合 | 截止时间 | 依赖关系 | 偏好方向 | 样本数 | 样例指令 |",
        "|:---:|---|---|---|:---:|:---:|---|",
    ]

    for c in cluster_list[:8]:
        k = c["intent_key"]
        pois_str = ", ".join(k["pois"])
        t_str = f"{k['time_limit']} min" if k["time_limit"] else "None"
        deps_str = "; ".join(f"{u}->{v}" for u, v in k["closure"]) if k["closure"] else "None"
        inst = c["sample_instruction"].replace("|", "\\|")
        report_lines.append(f"| {c['cluster_id']} | `{pois_str}` | {t_str} | `{deps_str}` | {k['direction']} | {c['member_count']} | {inst} |")

    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    REPORT_FILE.write_text("\n".join(report_lines), encoding="utf-8")
    print(f"[✓] Generated summary report to {REPORT_FILE.relative_to(ROOT_DIR.parent)}")


if __name__ == "__main__":
    main()
