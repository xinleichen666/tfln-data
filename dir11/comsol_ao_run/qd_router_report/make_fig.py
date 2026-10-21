# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle, Circle
from matplotlib import font_manager

font_manager.fontManager.addfont(r"C:\Windows\Fonts\msyh.ttc")
plt.rcParams["font.family"] = "Microsoft YaHei"
plt.rcParams["axes.unicode_minus"] = False

fig, ax = plt.subplots(figsize=(10.6, 4.6), dpi=200)
ax.set_xlim(0, 106)
ax.set_ylim(0, 46)
ax.axis("off")
fig.patch.set_facecolor("white")

def box(x, y, w, h, fc, ec, t, fs=9):
    p = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.2,rounding_size=0.6",
                       facecolor=fc, edgecolor=ec, linewidth=1.1)
    ax.add_patch(p)
    ax.text(x + w / 2, y + h / 2, t, ha="center", va="center", fontsize=fs, color="#1a1a1a")

box(2, 28, 22, 14, "#F4F7FB", "#4C6A92", "泵浦\n785 nm", 9)
box(28, 30, 34, 12, "#E7F2EA", "#2E7D4F", "腔区\n砷化镓只盖一小段\n应变调量子点，电光调腔", 8.5)
box(66, 30, 36, 12, "#F8F1E3", "#8A5A12", "路由区\n910 nm 透明高折射率层\n相位与结构一起优化", 8.5)

ax.annotate("", xy=(28, 36), xytext=(24, 36),
            arrowprops=dict(arrowstyle="-|>", color="#333", lw=1.1))
ax.annotate("", xy=(66, 36), xytext=(62, 36),
            arrowprops=dict(arrowstyle="-|>", color="#333", lw=1.1))

# ring sketch
ax.add_patch(FancyBboxPatch((32, 8), 26, 16, boxstyle="round,pad=0.15,rounding_size=2",
                            facecolor="none", edgecolor="#2E7D4F", linewidth=1.6))
ax.add_patch(Rectangle((40, 20.2), 8, 2.2, facecolor="#6B4C9A", edgecolor="none"))
ax.text(44, 24.2, "量子点 / GaAs", ha="center", fontsize=7.5, color="#6B4C9A")
ax.text(45, 12.2, "铌酸锂跑道环", ha="center", fontsize=8, color="#2E7D4F")

ax.annotate("", xy=(78, 16), xytext=(58, 16),
            arrowprops=dict(arrowstyle="-|>", color="#333", lw=1.1))
ax.text(68, 18.2, "准 TE0", ha="center", fontsize=8)

box(78, 8, 24, 16, "#F8F1E3", "#8A5A12", "两路收成\n同一个 TE0\n再干涉", 8.5)

ax.text(2, 43.2, "图 1  分区结构。硅不进入腔区；路由层工作在量子点发光波长。",
        fontsize=8.5, color="#333", ha="left")

fig.tight_layout()
fig.savefig(r"D:\comsol_ao_run\qd_router_report\fig1.png", bbox_inches="tight", facecolor="white")
print("fig ok")
