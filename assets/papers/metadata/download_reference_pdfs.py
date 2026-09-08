#!/usr/bin/env python3
"""Download reference PDFs based on reference_screening_matrix_v3.xlsx and extended core papers.

Follows the 0-Tools/research-standard layout:
- Assets stored in assets/papers/pdf/<category>/
- Manifest recorded in assets/papers/metadata/pdf_download_manifest.json
- Literature report recorded in assets/papers/metadata/reference-report.md
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[3]
EXCEL_PATH = ROOT_DIR / "docs" / "project" / "reference_screening_matrix_v3.xlsx"
PDF_BASE_DIR = ROOT_DIR / "assets" / "papers" / "pdf"
MANIFEST_PATH = ROOT_DIR / "assets" / "papers" / "metadata" / "pdf_download_manifest.json"
REPORT_PATH = ROOT_DIR / "assets" / "papers" / "metadata" / "reference-report.md"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 DARC-RouteLiteratureCollector/1.0"
}

# Manual overrides / direct open-access PDF links for known papers
DIRECT_PDF_MAP: dict[int, str] = {
    1: "https://aclanthology.org/2025.findings-emnlp.416.pdf",
    2: "https://arxiv.org/pdf/2510.06078.pdf",
    3: "https://arxiv.org/pdf/2504.05846.pdf",
    4: "https://arxiv.org/pdf/2412.07207.pdf",  # MAPLE arXiv
    5: "https://aclanthology.org/2025.acl-long.1339.pdf",
    6: "https://arxiv.org/pdf/2402.01622.pdf",  # TravelPlanner arXiv
    7: "https://aclanthology.org/2024.emnlp-industry.37.pdf",
    8: "https://arxiv.org/pdf/2409.08069.pdf",
    9: "https://aclanthology.org/2025.naacl-long.176.pdf",
    10: "https://arxiv.org/pdf/2410.12112.pdf",
    11: "https://arxiv.org/pdf/2510.07043.pdf",
    12: "https://arxiv.org/pdf/2512.14138.pdf",  # LAPPI arXiv
    13: "https://arxiv.org/pdf/2410.19656.pdf",  # APRICOT arXiv
    14: "https://arxiv.org/pdf/2607.04670.pdf",
    15: "https://aclanthology.org/2026.wassa-1.5.pdf",
    16: "https://aclanthology.org/2025.emnlp-main.1595.pdf",
    17: "https://aclanthology.org/2026.findings-acl.1929.pdf",
    18: "https://arxiv.org/pdf/2603.28301.pdf",
    19: "https://arxiv.org/pdf/2411.01679.pdf",  # Autoformulation arXiv
    20: "https://arxiv.org/pdf/2503.22674.pdf",
    21: "https://openaccess.thecvf.com/content/CVPR2026W/WDFM-EAI/papers/Hamid_ICR-Drive_Instruction_Counterfactual_Robustness_for_End-to-End_Language-Driven_Autonomous_Driving_CVPRW_2026_paper.pdf",
    22: "https://proceedings.neurips.cc/paper_files/paper/2023/file/a2cf225ba392627529efef14dc857e22-Paper-Conference.pdf",
    23: "https://arxiv.org/pdf/2607.22554.pdf",
    24: "https://arxiv.org/pdf/2608.03091.pdf",
    25: "https://arxiv.org/pdf/2412.03338.pdf",  # Agentic LLMs Day-to-Day Route Choices (preprint)
    26: "",  # TR-Part E (paywalled Elsevier)
    27: "https://eprints.whiterose.ac.uk/162141/1/Path%20planning%20with%20user%20route%20preference....pdf",
    28: "https://arxiv.org/pdf/2603.19257.pdf",
    29: "https://arxiv.org/pdf/2406.10857.pdf",
    30: "https://arxiv.org/pdf/2601.08064.pdf",
}

# High-value Extension Papers for DARC-Route v4
EXTENSION_PAPERS: list[dict] = [
    {
        "id": 101,
        "category": "03_verification_and_spo",
        "title": "Smart “Predict, then Optimize”",
        "short_title": "SPO_Elmachtoub",
        "author": "Adam N. Elmachtoub; Paul Grigas",
        "year": 2022,
        "venue": "Management Science",
        "priority": "必引（理论基石）",
        "url": "https://arxiv.org/pdf/1710.08005.pdf",
        "rationale": "决策损失与预测误差严格区分的理论基石，支撑本项目‘规划差异作为复核门控’的核心依据。"
    },
    {
        "id": 102,
        "category": "03_verification_and_spo",
        "title": "Large Language Models Cannot Self-Correct Reasoning Yet",
        "short_title": "SelfCorrection_Huang",
        "author": "Jie Huang; Xinyun Chen; Swaroop Mishra; et al.",
        "year": 2024,
        "venue": "ICLR 2024",
        "priority": "必引（方法机理）",
        "url": "https://arxiv.org/pdf/2310.01798.pdf",
        "rationale": "论证为什么无外部/决策反馈的盲目自纠错往往降低准确率，论证 DARC-Route 选择性门控的必要性。"
    },
    {
        "id": 103,
        "category": "03_verification_and_spo",
        "title": "Self-Consistency Improves Chain of Thought Reasoning in Language Models",
        "short_title": "SelfConsistency_Wang",
        "author": "Xuezhi Wang; Jason Wei; Dale Schuurmans; et al.",
        "year": 2023,
        "venue": "ICLR 2023",
        "priority": "必引（基线对照）",
        "url": "https://arxiv.org/pdf/2203.11171.pdf",
        "rationale": "本方案基线 B1（3次自一致性完整候选选择）的直接源头与采样对比基线。"
    },
    {
        "id": 104,
        "category": "03_verification_and_spo",
        "title": "FrugalGPT: How to Use Large Language Models While Reducing Cost and Improving Performance",
        "short_title": "FrugalGPT_Chen",
        "author": "Lingjiao Chen; Matei Zaharia; James Zou",
        "year": 2023,
        "venue": "NeurIPS 2023",
        "priority": "强烈建议（成本调度）",
        "url": "https://arxiv.org/pdf/2305.05176.pdf",
        "rationale": "LLM 级联与有限预算选择性调度的经典之作，支撑质量-Token 权衡分析的叙事框架。"
    },
    {
        "id": 105,
        "category": "03_verification_and_spo",
        "title": "RouteLLM: Learning to Route LLMs with Preference Data",
        "short_title": "RouteLLM_Ong",
        "author": "Isaac Ong; Amjad Almahairi; Vincent Tao; et al.",
        "year": 2024,
        "venue": "LMSYS / arXiv",
        "priority": "强烈建议（模型路由）",
        "url": "https://arxiv.org/pdf/2406.18665.pdf",
        "rationale": "大模型路由领域的 RouteLLM，用于在正文中与路线推荐领域的同名工作做清晰区分，并对比路由逻辑。"
    },
    {
        "id": 106,
        "category": "03_verification_and_spo",
        "title": "Decision-Focused Learning: Foundations, State of the Art, Benchmark and Future Opportunities",
        "short_title": "DFL_Survey_Mandi",
        "author": "Jayanta Mandi; et al.",
        "year": 2023,
        "venue": "IJCAI 2023 Survey",
        "priority": "建议（综述背景）",
        "url": "https://arxiv.org/pdf/2307.13565.pdf",
        "rationale": "决策导向学习的系统综述，为在优化环路中利用下游解差异提供坚实文献背景。"
    },
    {
        "id": 107,
        "category": "01_route_preference",
        "title": "TransitLM: A Benchmark for Transit Route Planning with Language Models",
        "short_title": "TransitLM",
        "author": "TransitLM Contributors",
        "year": 2025,
        "venue": "arXiv preprint",
        "priority": "建议（后续扩展）",
        "url": "https://arxiv.org/pdf/2412.06201.pdf",
        "rationale": "公共交通路线规划 benchmark，Proposal v4 §15 明确列为后续外推验证的重要邻近工作。"
    },
    {
        "id": 108,
        "category": "03_verification_and_spo",
        "title": "CRITIC: Large Language Models Can Self-Correct with Tool-Interactive Critiquing",
        "short_title": "CRITIC_Gou",
        "author": "Zhibin Gou; Zhihong Shao; Yeyun Gong; et al.",
        "year": 2024,
        "venue": "ICLR 2024",
        "priority": "必引（工具反馈）",
        "url": "https://arxiv.org/pdf/2305.11738.pdf",
        "rationale": "论证必须结合外部工具/环境客观事实反馈才能有效纠错，支撑路线求解器作为判定证据的立论。"
    },
    {
        "id": 109,
        "category": "03_verification_and_spo",
        "title": "Self-Refine: Iterative Refinement with Self-Feedback",
        "short_title": "SelfRefine_Madaan",
        "author": "Aman Madaan; Niket Tandon; Prakhar Gupta; et al.",
        "year": 2023,
        "venue": "NeurIPS 2023",
        "priority": "强烈建议（对比参照）",
        "url": "https://arxiv.org/pdf/2303.17651.pdf",
        "rationale": "多轮无外部指导自迭代的代表作，正文中用于对比本方案严格最多复核 1 次的成本控制优势。"
    },
    {
        "id": 110,
        "category": "03_verification_and_spo",
        "title": "CriticBench: Benchmarking Large Language Models as Critics for Multimodal and Reasoning Tasks",
        "short_title": "CriticBench_Lan",
        "author": "Tian Lan; Deng Cai; Yan Wang; et al.",
        "year": 2024,
        "venue": "Findings of ACL 2024",
        "priority": "强烈建议（评判模型）",
        "url": "https://arxiv.org/pdf/2402.14808.pdf",
        "rationale": "LLM 作为 Critic 评判者的权威基准，支撑对复核器纠错/改坏能力边界的分析。"
    },
    {
        "id": 111,
        "category": "03_verification_and_spo",
        "title": "Language Model Cascades",
        "short_title": "LMCascades_Dohan",
        "author": "David Dohan; Winnie Xu; Aida Amini; et al.",
        "year": 2022,
        "venue": "arXiv preprint",
        "priority": "强烈建议（级联理论）",
        "url": "https://arxiv.org/pdf/2207.10342.pdf",
        "rationale": "建立语言模型级联与条件调度的理论框架，为双路 A/B 低成本生成到高成本复核提供理论基石。"
    },
    {
        "id": 112,
        "category": "03_verification_and_spo",
        "title": "Let’s Verify Step by Step",
        "short_title": "VerifyStepByStep_OpenAI",
        "author": "Hunter Lightman; Vineet Kosaraju; Yura Burda; et al.",
        "year": 2024,
        "venue": "ICLR 2024",
        "priority": "强烈建议（分层验证）",
        "url": "https://arxiv.org/pdf/2305.20050.pdf",
        "rationale": "过程监督与步骤验证代表作，支撑硬约束先验检查与路线效用后验评估的分层门控设计。"
    },
    {
        "id": 113,
        "category": "03_verification_and_spo",
        "title": "Melding the Data-Decisions Pipeline: Decision-Focused Learning for Combinatorial Optimization",
        "short_title": "CombinatorialDFL_Wilder",
        "author": "Bryan Wilder; Bistra Dilkina; Milind Tambe",
        "year": 2019,
        "venue": "AAAI 2019",
        "priority": "必引（图决策优化）",
        "url": "https://arxiv.org/pdf/1809.05504.pdf",
        "rationale": "将预测与离散图组合优化融为一体的经典之作，直接证明下游路线解变动对误差评估的决定性作用。"
    },
    {
        "id": 114,
        "category": "01_route_preference",
        "title": "CityBench: Evaluating the Capabilities of Large Language Models for Urban Problem Solving",
        "short_title": "CityBench_Jin",
        "author": "Chengyan Jin; et al.",
        "year": 2024,
        "venue": "NeurIPS 2024",
        "priority": "必引（城市空间基准）",
        "url": "https://arxiv.org/pdf/2406.13945.pdf",
        "rationale": "NeurIPS 2024 最新城市 LLM 规划与移动评测基准，确立 POI 规划在空间计算中的核心学术地位。"
    },
    {
        "id": 115,
        "category": "02_linguistic_robustness",
        "title": "PromptBench: Towards Evaluating the Robustness of Large Language Models on Adversarial and Natural Prompts",
        "short_title": "PromptBench_Zhu",
        "author": "Kaijie Zhu; Jindong Wang; Jiaheng Zhou; et al.",
        "year": 2023,
        "venue": "IEEE T-AI / arXiv 2023",
        "priority": "强烈建议（鲁棒性基准）",
        "url": "https://arxiv.org/pdf/2306.04528.pdf",
        "rationale": "大模型提示词自然变体（Natural Perturbation）鲁棒性基准，为 HIPP-Robust 构建协议提供权威分类依据。"
    }
]


def sanitize_filename(name: str) -> str:
    name = re.sub(r"[^\w\-\.]", "_", name)
    name = re.sub(r"_+", "_", name).strip("_")
    return name[:60]


def download_file(url: str, dest_path: Path, max_retries: int = 3) -> bool:
    if dest_path.exists() and dest_path.stat().st_size > 1000:
        return True  # Already downloaded

    dest_path.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers=HEADERS)

    for attempt in range(max_retries):
        try:
            with urllib.request.urlopen(req, timeout=25) as response:
                content = response.read()
                # Check for PDF signature or minimum length
                if len(content) < 1000:
                    return False
                if not content.startswith(b"%PDF"):
                    # Some servers return html redirect or cloudflare challenge
                    if b"%PDF" in content[:1024]:
                        pass
                    else:
                        print(f"    [!] Downloaded content does not appear to be a PDF for {url}")
                        return False
                dest_path.write_bytes(content)
                return True
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2)
            else:
                print(f"    [X] Failed after {max_retries} attempts: {e}")
                return False
    return False


def get_sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def load_matrix_papers() -> list[dict]:
    import openpyxl

    if not EXCEL_PATH.exists():
        print(f"Excel file not found at {EXCEL_PATH}")
        return []

    wb = openpyxl.load_workbook(EXCEL_PATH)
    papers = []

    # Sheet 1: Reference Matrix
    s1 = wb["Reference Matrix"]
    for r in range(5, s1.max_row + 1):
        pid = s1.cell(r, 1).value
        title = s1.cell(r, 5).value
        if not title:
            continue
        short_title = s1.cell(r, 6).value or f"Paper_{pid}"
        priority = s1.cell(r, 4).value or "建议"
        threat = s1.cell(r, 3).value or 0
        venue = s1.cell(r, 9).value or ""
        author = s1.cell(r, 7).value or ""
        year = s1.cell(r, 8).value or ""
        pdf_url = DIRECT_PDF_MAP.get(int(pid), "")

        # Categorize
        if int(pid) in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 19, 20]:
            cat = "01_route_preference"
        else:
            cat = "02_linguistic_robustness"

        papers.append({
            "id": int(pid),
            "category": cat,
            "title": str(title).strip(),
            "short_title": str(short_title).strip(),
            "threat": int(threat),
            "priority": str(priority).strip(),
            "author": str(author).strip(),
            "year_venue": f"{year} {venue}".strip(),
            "url": pdf_url,
            "source": "Reference Matrix"
        })

    # Sheet 2: Round 3 Search
    s2 = wb["Round 3 Search"]
    for r in range(5, s2.max_row + 1):
        pid = s2.cell(r, 1).value
        title = s2.cell(r, 5).value
        if not title:
            continue
        short_title = f"R3_Paper_{pid}"
        priority = s2.cell(r, 4).value or "建议"
        threat = s2.cell(r, 3).value or 0
        year_venue = s2.cell(r, 6).value or ""
        pdf_url = DIRECT_PDF_MAP.get(int(pid), "")

        if int(pid) in [25, 26, 27]:
            cat = "01_route_preference"
        else:
            cat = "02_linguistic_robustness"

        papers.append({
            "id": int(pid),
            "category": cat,
            "title": str(title).strip(),
            "short_title": str(short_title).strip(),
            "threat": int(threat),
            "priority": str(priority).strip(),
            "author": "",
            "year_venue": str(year_venue).strip(),
            "url": pdf_url,
            "source": "Round 3 Search"
        })

    return papers


def main():
    print("=== DARC-Route Reference PDF Collector ===")
    matrix_papers = load_matrix_papers()
    all_papers = matrix_papers + EXTENSION_PAPERS

    print(f"Total papers to process: {len(all_papers)} (30 from Matrix + {len(EXTENSION_PAPERS)} Extensions)\n")

    manifest = []
    success_count = 0
    fail_count = 0
    paywall_count = 0

    for p in all_papers:
        pid = p["id"]
        title = p["title"]
        short = p["short_title"]
        cat = p["category"]
        url = p["url"]
        prio = p.get("priority", "建议")

        print(f"[{pid:03d}] {title[:50]}... ({prio})")

        if not url:
            print("    [-] Status: PAYWALLED or No direct open-access link")
            manifest.append({
                "id": pid,
                "title": title,
                "category": cat,
                "status": "paywalled_or_manual",
                "priority": prio,
                "local_path": None,
                "source_url": None,
                "size_bytes": 0,
                "sha256": None
            })
            paywall_count += 1
            continue

        filename = f"{pid:03d}_{sanitize_filename(short)}.pdf"
        dest_file = PDF_BASE_DIR / cat / filename

        success = download_file(url, dest_file)
        if success:
            size_kb = dest_file.stat().st_size / 1024
            sha256 = get_sha256(dest_file)
            rel_path = str(dest_file.relative_to(ROOT_DIR))
            print(f"    [✓] Saved to {rel_path} ({size_kb:.1f} KB)")
            manifest.append({
                "id": pid,
                "title": title,
                "category": cat,
                "status": "downloaded",
                "priority": prio,
                "local_path": rel_path,
                "source_url": url,
                "size_bytes": dest_file.stat().st_size,
                "sha256": sha256
            })
            success_count += 1
        else:
            print(f"    [X] Download failed for {url}")
            manifest.append({
                "id": pid,
                "title": title,
                "category": cat,
                "status": "download_failed",
                "priority": prio,
                "local_path": None,
                "source_url": url,
                "size_bytes": 0,
                "sha256": None
            })
            fail_count += 1

        time.sleep(0.5)  # Polite request rate

    # Save manifest
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nManifest saved to {MANIFEST_PATH.relative_to(ROOT_DIR)}")

    # Generate Markdown summary report
    generate_report(manifest)
    print(f"Report saved to {REPORT_PATH.relative_to(ROOT_DIR)}")
    print(f"\nSummary: Total={len(all_papers)}, Downloaded={success_count}, Paywalled/Manual={paywall_count}, Failed={fail_count}")


def generate_report(manifest: list[dict]):
    lines = [
        "# DARC-Route 文献下载与索引台账 (Reference Literature Report)",
        "",
        f"> 生成时间：{time.strftime('%Y-%m-%d %H:%M:%S')}  ",
        f"> 本台账由 `assets/papers/metadata/download_reference_pdfs.py` 自动生成，对应 `reference_screening_matrix_v3.xlsx` 与核心扩展文献。",
        "",
        "## 1. 概览统计",
        "",
        f"- **总计收录文献**：{len(manifest)} 篇",
        f"- **成功下载 PDF**：{sum(1 for m in manifest if m['status'] == 'downloaded')} 篇",
        f"- **商业数据库/需手动获取**：{sum(1 for m in manifest if m['status'] == 'paywalled_or_manual')} 篇",
        f"- **下载异常**：{sum(1 for m in manifest if m['status'] == 'download_failed')} 篇",
        "",
        "---",
        "",
        "## 2. 已下载文献清单 (Categorized Local PDFs)",
        "",
        "### 01_route_preference（路线规划、偏好建模与旅行规划）",
        "",
        "| ID | 引用优先级 | 论文题目 | 本地路径 | 大小 |",
        "|:---:|:---:|---|---|---:|",
    ]

    for m in manifest:
        if m["category"] == "01_route_preference" and m["status"] == "downloaded":
            kb = m["size_bytes"] / 1024
            lines.append(f"| {m['id']} | **{m['priority']}** | {m['title']} | [{Path(m['local_path']).name}]({m['local_path']}) | {kb:.1f} KB |")

    lines += [
        "",
        "### 02_linguistic_robustness（语言扰动、等义表达与下游鲁棒性）",
        "",
        "| ID | 引用优先级 | 论文题目 | 本地路径 | 大小 |",
        "|:---:|:---:|---|---|---:|",
    ]

    for m in manifest:
        if m["category"] == "02_linguistic_robustness" and m["status"] == "downloaded":
            kb = m["size_bytes"] / 1024
            lines.append(f"| {m['id']} | **{m['priority']}** | {m['title']} | [{Path(m['local_path']).name}]({m['local_path']}) | {kb:.1f} KB |")

    lines += [
        "",
        "### 03_verification_and_spo（选择性复核、自纠错机理与决策优化 SPO）",
        "",
        "| ID | 引用优先级 | 论文题目 | 本地路径 | 大小 |",
        "|:---:|:---:|---|---|---:|",
    ]

    for m in manifest:
        if m["category"] == "03_verification_and_spo" and m["status"] == "downloaded":
            kb = m["size_bytes"] / 1024
            lines.append(f"| {m['id']} | **{m['priority']}** | {m['title']} | [{Path(m['local_path']).name}]({m['local_path']}) | {kb:.1f} KB |")

    lines += [
        "",
        "---",
        "",
        "## 3. 需手动获取或商业版权文献",
        "",
        "| ID | 优先级 | 论文题目 | 来源渠道 / 说明 |",
        "|:---:|:---:|---|---|",
    ]

    for m in manifest:
        if m["status"] != "downloaded":
            lines.append(f"| {m['id']} | {m['priority']} | {m['title']} | Elsevier ScienceDirect / 建议走学校图书馆权限下载至 shared-library |")

    lines.append("")
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
