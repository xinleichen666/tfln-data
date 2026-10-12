# 方向一 · 参考文献（与共用表一致）

机器可读：同目录 `refs.bib`（条目自 `/workspace/dir11/paperB/paper/refs.bib` 裁剪）。  
核对状态见 `/workspace/tfln_review/ao_shared_params_v1.md`。

## 正文主引

1. **Shao2020** — L. Shao *et al.*, “Integrated microwave acousto-optic frequency shifter on thin-film lithium niobate,” *Opt. Express* **28**, 23728–23738 (2020). DOI: [10.1364/OE.397138](https://doi.org/10.1364/OE.397138); arXiv:[2005.03794](https://arxiv.org/abs/2005.03794). **全文已核。** 甲类器件模型（η=3.5%@30 dBm、CSR≈31 dB、SSR>40 dB、IL≈−15 dB）。
2. **Shao2019** — L. Shao *et al.*, “Microwave-to-optical conversion using lithium niobate thin-film acoustic resonators,” *Optica* **6**, 1498–1505 (2019). DOI: [10.1364/OPTICA.6.001498](https://doi.org/10.1364/OPTICA.6.001498); arXiv:[1907.08593](https://arxiv.org/abs/1907.08593). **全文已核。** 乙类锁定 Table S2（含 \(\Omega/2\pi=2.007\,\mathrm{GHz}\)）；**不混用** 2.17 GHz 跑道环 \(g_0\) 行。
3. **Zhu2025ao** — Z.-X. Zhu *et al.*, “Acoustically control of integrated optical microrings: from photonic molecule to Möbius strip,” arXiv:[2511.22585](https://arxiv.org/abs/2511.22585) (2025). **全文已核。** 丙类只取 \(C/P_a\)、κ、\(R\) 等标定；**不做**双环光子分子 / Möbius 结构叙事。

## 旁列（效率定义不同，不比胜负）

4. **Hu2021** — Y. Hu *et al.*, “On-chip electro-optic frequency shifters and beam splitters,” *Nature* **599**, 587–593 (2021). DOI: [10.1038/s41586-021-03999-x](https://doi.org/10.1038/s41586-021-03999-x); arXiv:[2005.09621](https://arxiv.org/abs/2005.09621). 电光双环 ~99% 转换效率；与 Shao 3.5% **分列**。

## 参数表旁列（正文不引 Xu 4.03 / Ni）

5. **Xu2025b** — X.-B. Xu *et al.*, “Magnetic-free optical mode degeneracy lifting in lithium niobate microring resonators,” arXiv:[2509.01940](https://arxiv.org/abs/2509.01940) (2025). **全文已核（HTML）。** 仅出现在 `params_table.md`（α、RF→acoustic≈10%）；**方向一正文不引用** Xu *et al.* arXiv:2510.26596 的 4.03 rad/W（方向二锚）。
6. **Ni / Bhave** arXiv:[2606.05337](https://arxiv.org/abs/2606.05337) — **方向一不引用**（方向二非悬空 \(V_\pi L\) 锚）。

## 台面 datasheet（非文献）

- Gooch & Housego Fiber-Q series (e.g. T-M080-…-F2P @ 80 MHz, ~1550 nm) + A35 driver — 型号已锁；实测格待测。手册 on/off 消光 ≥50 dB **≠** 已测 \(R_c\)。
