# Research Agent Starter (Full Factorial Ready)

## 快速启动（推荐：Conda）
```bat
cd <解压后的 research-agent-starter 目录>
conda env create -f environment.yml
conda run -n ra310 python -m streamlit run apps\app.py
```

## 如果你不想新建环境（已在可用环境）
```bat
python -m pip install -r requirements.txt
python -m streamlit run apps\app.py
```

## 使用说明（全因子 3×3×3）
- 在界面选择“全因子 3×3×3（27次）”，填 A/B/C 的 3 个水平；
- 设置重复次数、是否随机化、随机种子；点“生成实验表”并下载；
- 完成实验后，把每行的“重复1…重复N”填上，上传 CSV → 系统会计算 SNR 并生成主效应图。

> 提示：程序对路径更健壮了，无论从哪个目录启动都能正确工作。
