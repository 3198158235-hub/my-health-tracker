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
    
    # --- 核心指标 ---
    st.info("💡 提示：所有滑块 10 分代表状态最好，1 分代表状态最差")
    
    col1, col2 = st.columns(2)
    with col1:
        sleep_score = st.slider("💤 昨晚睡眠质量", 1, 10, 6)
        stress_level = st.slider("🧠 心理压力 (反向:10=无压)", 1, 10, 7) # 注意：这里建议统一逻辑，10是好的
        nose_status = st.slider("👃 呼吸道状态", 1, 10, 9)
        
    with col2:
        energy_level = st.slider("🔋 精力/体能", 1, 10, 6)
        skin_score = st.slider("🧖‍♀️ 皮肤总体状态", 1, 10, 8)

    # --- 症状细节 ---
    st.markdown("---")
    st.markdown("### 🚑 症状细节 (多选)")
    skin_symptoms = st.multiselect(
        "具体哪里不舒服？",
        ["唇炎", "毛囊炎", "皮炎", "荨麻疹", "痘痘/闭口", "泛红", "关节痛", "偏头痛"]
    )

    # --- 干扰因素 (逻辑分类版) ---
    st.markdown("---")
    st.markdown("### 🕵️‍♀️ 变量控制与追踪")
    
    col_diet, col_env = st.columns(2)
    
    with col_diet:
        st.markdown("**🍔 饮食摄入**")
        diet_tags = st.multiselect(
            "吃了什么特殊的？",
            ["咖啡因", "牛奶/乳制品", "牛肉/红肉", "羊肉", "海鲜", 
             "高糖/甜食", "辛辣", "麸质/面食", "酒精", "加工食品"],
            key="diet"
        )
        
    with col_env:
        st.markdown("**🌍 环境与行为**")
        env_tags = st.multiselect(
            "做了什么特殊的？",
            ["到了新环境", "换季/气温剧变", "熬夜(晚于12点)", "失眠", 
             "剧烈运动", "久坐不动", "接触尘螨/猫狗", "忘记吃补充剂"],
             key="env"
        )
    
    note = st.text_input("📝 备注", placeholder="例如：今天心情特别好，因为...")

    # 提交按钮
    submitted = st.form_submit_button("💾 保存记录")

    if submitted:
        # === 核心逻辑：合并标签 ===
        # 把饮食标签和环境标签拼起来，中间用逗号隔开，方便存进 CSV
        all_tags_list = diet_tags + env_tags
        final_tags_str = ",".join(all_tags_list)
        
        new_data = {
            "日期": date,
            "睡眠质量": sleep_score,
            "心理压力": stress_level,
            "鼻子状态": nose_status,
            "精力水平": energy_level,
            "皮肤总分": skin_score,
            "皮肤症状": ",".join(skin_symptoms),
            "干扰标签": final_tags_str, # 存的是合并后的
            "备注": note,
            "记录时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        if os.path.exists(DATA_FILE):
            df = pd.read_csv(DATA_FILE)
            df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
        else:
            df = pd.DataFrame([new_data])
            
        df.to_csv(DATA_FILE, index=False)
        st.success(f"✅ 保存成功！今日追踪变量：{final_tags_str if final_tags_str else '无'}")

# === 3. 历史回显 ===
if os.path.exists(DATA_FILE):
    st.markdown("---")
    with st.expander("📊 查看历史数据 (最近 5 条)"):
        df = pd.read_csv(DATA_FILE)
        st.dataframe(df.sort_values("日期", ascending=False).head(5))

# === 4. 数据管理区 ===
    with st.expander("🛠️ 数据修正/删除"):
        st.write("输入左侧行号 (Index) 删除误录数据")
        if os.path.exists(DATA_FILE):
            df_manager = pd.read_csv(DATA_FILE)
            st.dataframe(df_manager)
            
            col_del1, col_del2 = st.columns([3, 1])
            with col_del1:
                del_index = st.number_input("行号", min_value=0, step=1, label_visibility="collapsed")
            with col_del2:
                if st.button("🗑️ 删除"):
                    if del_index in df_manager.index:
                        df_manager = df_manager.drop(del_index)
                        df_manager.to_csv(DATA_FILE, index=False)
                        st.success("已删除！")
                        st.rerun()
                    else:
                        st.error("行号不存在")
