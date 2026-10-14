# STATUS — qcnn_protocol（Bot B）

更新：2026-10-13 17:22 Asia/Shanghai

## 总态
**本轮交付完成（未 push）。** 负结果：CNN 在 8/8 全参数对照中测试准确率更高。

## 完成清单
| 项 | 状态 |
|----|------|
| `scripts/` 固定种子可重跑 | 有（`config.py`, `run_protocol.py`, `make_figs.py`, `regenerate.sh`） |
| `data/summary.json` | 有；`verdict=cnn_better_on_average`，`mean_delta=-0.3385` |
| `data/histories.json` / `examples.npz` | 有 |
| `paper/README.md` | 有（含强制口径） |
| `paper/main_zh.md` | 有；数字指 json 键 |
| `paper/non_claims.md` | 有 |
| `paper/params_table.md` | 有（文献\|本轮\|假设） |
| `paper/fig/*.png+pdf` | 6 组 |
| `prior_bib.md` | 文献包已放；正文只作框架引用，**未**抄其准确率进结果表 |
| `verify/` | **无** |
| GitHub push | **未做**（按指示） |

## 种子
data=2408 · init=8701 · train=2026 · split=42

## 已跑完扫参
encodings: angle4, amplitude · losses: mse, bce · batch: 16, 32  
优化器：SPSA · 模拟器：`numpy_statevector_v1` · n_qubits=4 · epochs=20 · n_train=96 · n_test=48

## 结局一句话
QCNN **未**优于参数量对齐 CNN（平均 Δ 测试准确率 −0.3385）；剪枝至 9 参后仍全部 `winner=cnn`。标题保持协议对照。

## 阻塞 / 未做
- 无 Tidy3D/硬件无关本轨；本轨无量子硬件、无 HEP 数据、无 PennyLane/Qiskit/PyTorch（numpy 栈）。
- 未推 `xinleichen666/tfln-data` 或其它仓。
- DEA 为敏感性方差代理，非 Elhag 原文逐行复现。

## 重跑
`bash /workspace/qcnn_protocol/scripts/regenerate.sh`
