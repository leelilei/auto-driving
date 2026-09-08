#!/usr/bin/env python3
"""Generate publication-quality figures for CCEAI 2027 paper.

Outputs PDF and PNG formats to paper/figures/:
1. fig1_framework: Conceptual diagram of Decision-Aware Selective Verification
2. fig2_baseline_comparison: Route Flip & Deployment Cost across B0-B6 + Ours
3. fig3_pareto_curve: Equal-Quota Pareto Curve (Route Flip vs Budget)
4. fig4_contrast_sensitivity: Sensitivity on Contrast Set (Appropriate Response vs Adaptation)
"""

from __future__ import annotations

import json
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
FIG_DIR = ROOT / "paper" / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

# Publication styling
plt.rcParams.update({
    "font.size": 11,
    "font.family": "serif",
    "axes.labelsize": 12,
    "axes.titlesize": 13,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.fontsize": 10,
    "figure.titlesize": 14,
    "axes.grid": True,
    "grid.alpha": 0.3,
    "grid.linestyle": "--",
})


def plot_fig1_framework():
    """Figure 1: Architectural framework diagram."""
    fig, ax = plt.subplots(figsize=(8.5, 4.2), dpi=300)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5)
    ax.axis("off")

    def box(x, y, w, h, text, color="#EBF3FB", ec="#2B6CB0", lw=1.5, bold=False):
        rect = patches.FancyBboxPatch(
            (x, y), w, h, boxstyle="round,pad=0.15",
            facecolor=color, edgecolor=ec, linewidth=lw
        )
        ax.add_patch(rect)
        weight = "bold" if bold else "normal"
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
                fontsize=9.5, fontweight=weight, color="#1A202C", wrap=True)

    def arrow(x1, y1, x2, y2, label=""):
        ax.annotate(
            label, xy=(x2, y2), xytext=(x1, y1),
            arrowprops=dict(facecolor="#4A5568", edgecolor="#4A5568", arrowstyle="-|>", lw=1.2),
            ha="center", va="center", fontsize=8.5, color="#2D3748"
        )

    # Inputs
    box(0.3, 2.0, 1.4, 1.0, "Instruction\n$x$", color="#EDF2F7", ec="#718096")

    # Stage 1: Dual Extraction
    box(2.2, 3.2, 1.8, 0.9, "Direct Prompt\n(Candidate $A$)", color="#EBF8FF", ec="#3182CE")
    box(2.2, 0.9, 1.8, 0.9, "Evidence Prompt\n(Candidate $B$)", color="#EBF8FF", ec="#3182CE")
    arrow(1.7, 2.6, 2.2, 3.5)
    arrow(1.7, 2.4, 2.2, 1.4)

    # Route Solving
    box(4.5, 2.0, 1.6, 1.0, "Shared Exact\nRoute Solver\n$r_A, r_B$", color="#FEEBC8", ec="#DD6B20")
    arrow(4.0, 3.5, 4.5, 2.7)
    arrow(4.0, 1.4, 4.5, 2.3)

    # Stage 2: Gating
    box(6.5, 2.0, 1.7, 1.1, "Decision Gate:\n$h \\vee (\\Delta_U > \\tau)$", color="#FED7D7", ec="#E53E3E", bold=True)
    arrow(6.1, 2.5, 6.5, 2.5)

    # Branching
    box(8.5, 3.3, 1.3, 0.8, "Single Review\n(Arbitration)", color="#E9D8FD", ec="#805AD5")
    box(8.5, 0.9, 1.3, 0.8, "Adopt\nCandidate $A$", color="#C6F6D5", ec="#38A169")

    arrow(7.4, 3.0, 8.5, 3.6, "Triggered\n($4.2\\%$)")
    arrow(7.4, 2.0, 8.5, 1.4, "Pass\n($95.8\\%$)")

    plt.tight_layout()
    fig.savefig(FIG_DIR / "fig1_framework.pdf", bbox_inches="tight")
    fig.savefig(FIG_DIR / "fig1_framework.png", bbox_inches="tight")
    plt.close(fig)
    print("  [✓] Generated fig1_framework")


def plot_fig2_baseline_comparison():
    """Figure 2: Route Flip rate across all baselines with 95% bootstrap CI & calls."""
    fig, ax1 = plt.subplots(figsize=(8.0, 4.5), dpi=300)

    methods = ["B0", "B2", "B5", "B4", "B1", "B3", "Ours", "B6"]
    labels = [
        "B0\n(Single)",
        "B2\n(A+B)",
        "B5\n(Prot $h$)",
        "B4\n(Semantic)",
        "B1\n(Self-Cons)",
        "B3\n(Random)",
        "Ours\n(DARC)",
        "B6\n(Always)",
    ]
    flips = [0.2385, 0.2385, 0.2385, 0.2271, 0.2188, 0.1896, 0.2031, 0.1635]
    calls = [1.00, 2.00, 2.00, 2.08, 3.00, 2.51, 2.04, 3.00]

    # Colors: DARC highlighted in royal blue, baselines in soft colors
    colors = ["#CBD5E0", "#CBD5E0", "#CBD5E0", "#CBD5E0", "#F6AD55", "#CBD5E0", "#2B6CB0", "#4A5568"]

    x = np.arange(len(methods))
    width = 0.55

    bars = ax1.bar(x, [f * 100 for f in flips], width, color=colors, edgecolor="#2D3748", lw=1.2, zorder=3)
    ax1.set_ylabel("Route Flip Rate (%)", fontsize=12, fontweight="bold", color="#1A202C")
    ax1.set_ylim(0, 30)
    ax1.set_xticks(x)
    ax1.set_xticklabels(labels)

    # Annotate Flip % and Calls on top of bars
    for bar, f, c in zip(bars, flips, calls):
        yval = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width() / 2.0, yval + 0.6,
                 f"{f*100:.1f}%\n({c:.2f} calls)", ha="center", va="bottom", fontsize=8.5, fontweight="semibold")

    # Add a horizontal dashed line at B0 baseline
    ax1.axhline(0.2385 * 100, color="#E53E3E", linestyle=":", lw=1.5, alpha=0.8, label="B0 Baseline (23.8%)")

    # Annotate DARC drop
    ax1.annotate(
        "-14.8% (p < 0.05)\nvs B0",
        xy=(6, 20.31), xytext=(6, 26.5),
        arrowprops=dict(facecolor="#2B6CB0", edgecolor="#2B6CB0", arrowstyle="->", lw=1.5),
        ha="center", fontsize=9.5, fontweight="bold", color="#2B6CB0",
        bbox=dict(boxstyle="round,pad=0.2", facecolor="#EBF8FF", edgecolor="#3182CE")
    )

    ax1.legend(loc="upper right")
    plt.title("Route Instability under Paraphrase Across Baselines (Test N=640)", fontsize=12, fontweight="bold", pad=12)
    plt.tight_layout()
    fig.savefig(FIG_DIR / "fig2_baseline_comparison.pdf", bbox_inches="tight")
    fig.savefig(FIG_DIR / "fig2_baseline_comparison.png", bbox_inches="tight")
    plt.close(fig)
    print("  [✓] Generated fig2_baseline_comparison")


def plot_fig3_pareto_curve():
    """Figure 3: Equal-Quota Pareto Curve (Route Flip vs Budget)."""
    fig, ax = plt.subplots(figsize=(7.2, 4.4), dpi=300)

    budgets = [2, 4, 6, 8, 10, 15, 20]
    # Data from Table in ablation_experiment_report.md
    flip_darc = [0.2281, 0.2031, 0.1875, 0.1760, 0.1656, 0.1635, 0.1635]
    flip_b4 = [0.2354, 0.2312, 0.2271, 0.2250, 0.2188, 0.2104, 0.1979]
    flip_b3 = [0.2365, 0.2333, 0.2302, 0.2271, 0.2240, 0.2188, 0.2125]

    ax.plot(budgets, [f * 100 for f in flip_darc], marker="o", lw=2.4, color="#2B6CB0", label="DARC Gating (ΔU)")
    ax.plot(budgets, [f * 100 for f in flip_b4], marker="s", lw=1.8, linestyle="--", color="#DD6B20", label="Semantic Gating B4 (|Δw|)")
    ax.plot(budgets, [f * 100 for f in flip_b3], marker="^", lw=1.8, linestyle=":", color="#718096", label="Random Gating B3")

    ax.set_xlabel("Review Budget Quota (%)", fontsize=11, fontweight="bold")
    ax.set_ylabel("Route Flip Rate (%)", fontsize=11, fontweight="bold")
    ax.set_title("Equal-Quota Pareto Frontier (Route Flip vs Review Budget)", fontsize=12, fontweight="bold")
    ax.set_xlim(1, 21)
    ax.set_ylim(15, 25)

    # Highlight optimal frozen point
    ax.scatter([4.2], [20.31], color="#E53E3E", s=100, zorder=5)
    ax.annotate(
        "Frozen Config τ*=0.02\n(4.2% Review, Flip 20.3%)",
        xy=(4.2, 20.31), xytext=(8.0, 22.0),
        arrowprops=dict(facecolor="#E53E3E", edgecolor="#E53E3E", arrowstyle="->", lw=1.5),
        fontsize=9, fontweight="semibold", color="#C53030",
        bbox=dict(boxstyle="round,pad=0.2", facecolor="#FFF5F5", edgecolor="#FEB2B2")
    )

    ax.legend(loc="upper right", framealpha=0.95)
    plt.tight_layout()
    fig.savefig(FIG_DIR / "fig3_pareto_budget_curve.pdf", bbox_inches="tight")
    fig.savefig(FIG_DIR / "fig3_pareto_budget_curve.png", bbox_inches="tight")
    plt.close(fig)
    print("  [✓] Generated fig3_pareto_budget_curve")


def plot_fig4_contrast_sensitivity():
    """Figure 4: Contrast Set Sensitivity (Appropriate Response vs Route Adaptation)."""
    fig, ax = plt.subplots(figsize=(6.8, 4.2), dpi=300)

    methods = ["Single (B0)", "Always (B6)", "DARC (Ours)"]
    x = np.arange(len(methods))
    width = 0.35

    # Data from contrast_experiment_report.md
    adaptation = [42.5, 45.0, 42.5]
    appropriate = [70.0, 72.5, 75.0]

    bars1 = ax.bar(x - width / 2, adaptation, width, label="Route Adaptation Rate", color="#CBD5E0", edgecolor="#4A5568")
    bars2 = ax.bar(x + width / 2, appropriate, width, label="Appropriate Response Rate", color="#2B6CB0", edgecolor="#1A365D")

    ax.set_ylabel("Rate on Contrast Set (%)", fontsize=11, fontweight="bold")
    ax.set_ylim(0, 100)
    ax.set_xticks(x)
    ax.set_xticklabels(methods, fontweight="semibold")
    ax.set_title("Sensitivity to Genuine Semantic Changes (Contrast N=40 Pairs)", fontsize=12, fontweight="bold")

    for bar in bars1:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2.0, yval + 1.5, f"{yval:.1f}%", ha="center", va="bottom", fontsize=8.5)

    for bar in bars2:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2.0, yval + 1.5, f"{yval:.1f}%", ha="center", va="bottom", fontsize=8.5, fontweight="bold")

    ax.annotate(
        "Highest Appropriate Response\n(No Over-Smoothing)",
        xy=(2 + width / 2, 75.0), xytext=(1.2, 88.0),
        arrowprops=dict(facecolor="#2B6CB0", edgecolor="#2B6CB0", arrowstyle="->", lw=1.5),
        fontsize=9, fontweight="bold", color="#2B6CB0",
        bbox=dict(boxstyle="round,pad=0.2", facecolor="#EBF8FF", edgecolor="#3182CE")
    )

    ax.legend(loc="upper left")
    plt.tight_layout()
    fig.savefig(FIG_DIR / "fig4_contrast_sensitivity.pdf", bbox_inches="tight")
    fig.savefig(FIG_DIR / "fig4_contrast_sensitivity.png", bbox_inches="tight")
    plt.close(fig)
    print("  [✓] Generated fig4_contrast_sensitivity")


if __name__ == "__main__":
    plot_fig1_framework()
    plot_fig2_baseline_comparison()
    plot_fig3_pareto_curve()
    plot_fig4_contrast_sensitivity()
    print("All figures successfully generated in paper/figures/")
