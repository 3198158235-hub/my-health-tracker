import streamlit as st
import pandas as pd
import os
from datetime import datetime

# === 1. 设置文件保存路径 ===
DATA_FILE = "my_health_data.csv"

st.title('我的身体炎症与过敏源追踪 🧬')

# === 2. 数据录入区 ===
with st.form("entry_form"):
    st.subheader("📅 今日记录")
    date = st.date_input("日期", datetime.now())
    
    # 核心指标 (1-10分)
    col1, col2 = st.columns(2)
    with col1:
        sleep_score = st.slider("昨晚睡眠质量 (1=很差, 10=完美)", 1, 10, 6)
        stress_level = st.slider("今日心理压力 (1=无压力, 10=崩溃)", 1, 10, 3)
    with col2:
        energy_level = st.slider("精力/身体感受 (1=生病/极累, 10=满血)", 1, 10, 6)
        skin_status = st.slider("皮肤/过敏状态 (1=严重起疹, 10=光滑)", 1, 10, 8)

    # 过敏源侦探 (你刚才提到的需求)
    st.markdown("---")
    st.subheader("🕵️‍♀️ 潜在干扰因素")
    tags = st.multiselect(
        "今天接触了哪些嫌疑对象？",
        ["喝了牛奶", "吃了牛肉", "到了新环境", "换季/天气剧变", "吃了高糖", "熬夜", "剧烈运动"]
    )
    
    note = st.text_input("备注 (选填)", placeholder="例如：今天膝盖有点痛...")

    # 提交按钮
    submitted = st.form_submit_button("💾 保存今天的记录")

    if submitted:
        # 整理数据
        new_data = {
            "日期": date,
            "睡眠质量": sleep_score,
            "心理压力": stress_level,
            "精力水平": energy_level,
            "皮肤状态": skin_status,
            "标签": ",".join(tags), # 把列表变成字符串保存
            "备注": note,
            "记录时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # 保存到 CSV 文件
        if os.path.exists(DATA_FILE):
            df = pd.read_csv(DATA_FILE)
            df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
        else:
            df = pd.DataFrame([new_data])
            
        df.to_csv(DATA_FILE, index=False)
        st.success("✅ 记录已保存！明天继续加油！")

# === 3. 简单的历史回显 ===
if os.path.exists(DATA_FILE):
    st.markdown("---")
    st.subheader("📊 历史数据概览")
    df = pd.read_csv(DATA_FILE)
    # 按日期倒序显示最近 5 条
    st.dataframe(df.sort_values("日期", ascending=False).head(5))