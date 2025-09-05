# 本地科研智能体（零基础入门版）

这是一个**完全本地运行**的小工具集合，目标是先让你跑起来：
- **正交实验 L9 设计 + SNR 计算**（Taguchi）
- **PDF 本地解析与关键词查找**（无需联网，不用大模型）
- 简洁图形界面（Streamlit）

> 先跑通，再逐步升级为“真正的智能体”（以后可以接 LangGraph、向量库、或本地大模型）。

---

## 一、安装步骤（Windows 新手最友好）

**A. 安装 Python（推荐 Anaconda/Miniconda）**
1. 访问 https://docs.anaconda.com/miniconda/ 下载 “Miniconda for Windows (64-bit)” 并安装（一路 Next 即可）。
2. 安装完成后，开始菜单搜索 **Anaconda Prompt** 打开它。

**B. 创建并进入项目**
```bash
# 在 Anaconda Prompt 中逐行输入：
cd %USERPROFILE%
mkdir research-agent && cd research-agent
# 把你下载的 research-agent-starter.zip 解压到当前文件夹
# （Windows：右键 -> 全部提取；或使用 7-Zip）
```

**C. 创建环境并安装依赖**
```bash
conda create -n research_agent python=3.10 -y
conda activate research_agent
pip install -r requirements.txt -i https://pypi.org/simple
```

**D. 运行图形界面**
```bash
streamlit run apps/app.py
```
看到浏览器自动打开（或访问 http://localhost:8501）。

> **Mac/Linux**：打开 Terminal，替换第 2 步里的 `cd %USERPROFILE%` 为 `cd ~` 即可；其余命令相同。

---

## 二、怎么用？

### 1) DOE & SNR
- 在左侧“DOE & SNR”页：
  1. 输入三个因子及其三个水平（默认已填）
  2. 点击【生成 L9 设计】→ 得到 9 行实验计划
  3. 做完 9 组实验后，把每组的 3 次重复测试结果（响应值）填入或上传 CSV
  4. 点击【计算 SNR & 主效应】→ 自动给出每行 SNR、极差分析和主效应图

> SNR 公式（Taguchi）：
> - 越大越好：SNR = -10 * log10( mean(1/y^2) )
> - 越小越好：SNR = -10 * log10( mean(y^2) )
> - 公称最好：SNR = 10 * log10( mean(y)^2 / var(y) )

### 2) PDF 解析
- 在“PDF 解析”页上传任意 PDF：
  - 自动提取文本，显示页数与预览
  - 支持关键词搜索，高亮出现次数
  - （先用于“离线读论文”的入门体验）

---

## 三、文件说明

```
research-agent-starter/
├─ apps/app.py          # 主界面（Streamlit）
├─ core/tools/doe_tools.py
├─ core/tools/pdf_tools.py
├─ requirements.txt
└─ sample_data/demo_results.csv
```

你可以随时查看/修改 `core/tools/doe_tools.py` 里的算法，或将它替换为你自己的实验工具函数。

---

## 四、常见问题（FAQ）

- **启动后浏览器没有自动打开？** 直接手动访问 http://localhost:8501
- **安装太慢？** 可换源或多试几次，确保网络可访问 pypi.org（科学上网环境更快）。
- **PDF 无法解析？** 尝试用 `pdfplumber` 解析；或先用“另存为 PDF/A”后再上传。
- **SNR 用哪种模式？** 响应类指标选 “越大越好”；误差/噪声类选“越小越好”；接近目标值的选“公称最好”。

---

## 五、下一步升级（选做）
- 加入 LangGraph 管理“提问→调用工具→汇总”的流程（编排为智能体）
- 引入本地向量库（FAISS/Qdrant），实现论文库检索（RAG）
- 集成本地大模型（Ollama），把“读论文/写总结”自动化
```
