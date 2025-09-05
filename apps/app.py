import io
import re
import sys
from pathlib import Path
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

# 确保项目根目录可被导入（无论从哪里启动）
BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from core.tools.doe_tools import l9_table_from_factors, taguchi_snr, full_factorial_table
from core.tools.pdf_tools import extract_text_by_page, keyword_hits

st.set_page_config(page_title="本地科研助手（入门）", layout="wide")
st.title("🧪 本地科研助手（入门版）")
st.caption("DOE 正交/全因子 + SNR 计算、PDF 本地解析（纯离线）")


tabs = st.tabs(["DOE & SNR", "PDF 解析"])

# -------- Tab 1: DOE & SNR --------
with tabs[0]:
    st.subheader("实验设计")
    design_type = st.radio("选择设计类型", ["L9(3^4) 正交（9次）", "全因子 3×3×3（27次）"], horizontal=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        a_name = st.text_input("因子A 名称", value="因子A")
        a_levels = st.text_input("A 的三个水平（逗号分隔）", value="L1,L2,L3").split(",")
        a_levels = [x.strip() for x in a_levels if x.strip()]
    with col2:
        b_name = st.text_input("因子B 名称", value="因子B")
        b_levels = st.text_input("B 的三个水平", value="L1,L2,L3").split(",")
        b_levels = [x.strip() for x in b_levels if x.strip()]
    with col3:
        c_name = st.text_input("因子C 名称", value="因子C")
        c_levels = st.text_input("C 的三个水平", value="L1,L2,L3").split(",")
        c_levels = [x.strip() for x in c_levels if x.strip()]

    if design_type.startswith("全因子"):
        st.markdown("— **全因子选项** —")
        c1, c2, c3 = st.columns(3)
        with c1:
            replicates = st.number_input("每个组合的重复次数", min_value=1, max_value=10, value=3, step=1)
        with c2:
            randomize = st.checkbox("随机化实施顺序", value=True)
        with c3:
            seed = st.number_input("随机种子（可选）", min_value=0, max_value=999999, value=42, step=1)

    if st.button("✅ 生成实验表"):
        if not (len(a_levels)==len(b_levels)==len(c_levels)==3):
            st.error("每个因子必须恰好 3 个水平。")
        else:
            factors = {a_name:a_levels, b_name:b_levels, c_name:c_levels}
            if design_type.startswith("全因子"):
                df_plan = full_factorial_table(factors, replicates=replicates, randomize=randomize, seed=int(seed), add_replicate_columns=True)
            else:
                df_plan = l9_table_from_factors(factors)

            st.success("已生成实验计划")
            st.dataframe(df_plan, use_container_width=True)
            csv = df_plan.to_csv(index=False).encode("utf-8")
            st.download_button("下载实验计划 CSV", data=csv, file_name="experiment_plan.csv", mime="text/csv")

    st.markdown("---")
    st.subheader("SNR 计算与主效应分析")

    st.markdown("**方式 1：上传结果 CSV（推荐）**")
    st.caption("CSV 建议包含：试验号、因子列，以及一组或多组“重复N”列（如 重复1/重复2/重复3）。系统会自动识别以“重复”开头的列。")

    uploaded = st.file_uploader("上传你的 CSV 结果文件", type=["csv"])

    mode = st.selectbox("SNR 模式", ["larger", "smaller", "nominal"], index=0,
                        help="larger=越大越好；smaller=越小越好；nominal=接近目标最好")

    def find_replicate_cols(columns):
        repl = [c for c in columns if re.fullmatch(r"重复\d+", str(c))]
        import re as _re
        repl_sorted = sorted(repl, key=lambda x: int(_re.findall(r"\d+", x)[0]))
        return repl_sorted

    if uploaded is not None:
        df = pd.read_csv(uploaded)
        repl_cols = find_replicate_cols(df.columns)
        if not repl_cols:
            st.error("未检测到“重复N”列，例如：重复1、重复2、重复3。请在 CSV 中加入这些列。")
        else:
            df["SNR"] = df.apply(lambda row: taguchi_snr([row[c] for c in repl_cols], mode=mode), axis=1)
            st.dataframe(df, use_container_width=True)
            csv2 = df.to_csv(index=False).encode("utf-8")
            st.download_button("下载含 SNR 的结果 CSV", data=csv2, file_name="results_with_snr.csv", mime="text/csv")

            st.markdown("### 主效应图")
            factors_cols = [c for c in df.columns if c not in (["试验号","实施顺序","SNR"] + repl_cols)]
            for f in factors_cols:
                means = df.groupby(f)["SNR"].mean()
                fig, ax = plt.subplots()
                means.plot(ax=ax, marker="o")
                ax.set_title(f"主效应图 - {f}")
                ax.set_xlabel(f)
                ax.set_ylabel("平均 SNR (dB)")
                st.pyplot(fig)

    st.markdown("**方式 2：手动录入**（小样本快速试用）")
    with st.form("manual_input"):
        st.caption("填写若干行的重复值。列名请用“重复1/重复2/...”，系统会自动识别计算 SNR。")
        df_manual = pd.DataFrame({
            "试验号":[f"Run{i:02d}" for i in range(1,10)],
            "重复1":[None]*9,
            "重复2":[None]*9,
            "重复3":[None]*9,
        })
        edited = st.data_editor(df_manual, num_rows="dynamic", use_container_width=True)
        submit = st.form_submit_button("计算 SNR（手动）")
        if submit:
            repl_cols = [c for c in edited.columns if re.fullmatch(r"重复\d+", str(c))]
            if not repl_cols:
                st.error("请添加至少一个“重复N”列，例如：重复1")
            else:
                edited["SNR"] = edited.apply(lambda r: taguchi_snr([r[c] for c in repl_cols], mode=mode), axis=1)
                st.dataframe(edited, use_container_width=True)

# -------- Tab 2: PDF 解析 --------
with tabs[1]:
    st.subheader("本地 PDF 解析（纯离线）")
    pdf = st.file_uploader("上传 PDF", type=["pdf"])
    if pdf is not None:
        # 保存到项目根，避免工作目录差异
        bytes_data = pdf.read()
        tmp_path = BASE_DIR / ".tmp_upload.pdf"
        with open(tmp_path,"wb") as f: f.write(bytes_data)
        pages = extract_text_by_page(str(tmp_path))
        st.success(f"解析完成：共 {len(pages)} 页")
        kw = st.text_input("关键词（可中文/英文）", value="NH3")
        if kw:
            hits = keyword_hits(pages, kw)
            if hits:
                st.info("命中页（页码: 次数）：" + ", ".join([f"{p}:{c}" for p,c in hits]))
            else:
                st.warning("未找到关键词。")
        sel = st.number_input("预览页码", min_value=1, max_value=max(1,len(pages)), value=1, step=1)
        st.text_area("页面文本预览", pages[sel-1] if pages else "", height=300)
