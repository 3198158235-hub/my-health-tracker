import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import google.generativeai as genai
from datetime import datetime

# === 1. 初始化设置 ===
st.set_page_config(page_title="Gemini健康追踪", page_icon="🧬")

# 从 secrets 读取配置
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=GEMINI_API_KEY)
    # 连接 Google Sheets
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error(f"配置读取失败，请检查 .streamlit/secrets.toml 文件。\n错误详情: {e}")
    st.stop()

st.title('🧬 身体炎症追踪 (云端版)')

# === 2. 数据录入区 ===
with st.form("entry_form"):
    st.caption("📅 随时随地记录，无需开电脑")
    date = st.date_input("日期", datetime.now(), label_visibility="collapsed")
    
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        sleep_score = st.slider("💤 睡眠质量", 1, 10, 6)
        stress_level = st.slider("🧠 心理压力 (10=无压)", 1, 10, 7)
        nose_status = st.slider("👃 呼吸道", 1, 10, 9)
    with col2:
        energy_level = st.slider("🔋 精力值", 1, 10, 6)
        skin_score = st.slider("🧖‍♀️ 皮肤状态", 1, 10, 8)

    st.markdown("---")
    # 为了方便存表格，多选框的内容会被拼成字符串
    skin_symptoms = st.multiselect("🚑 具体症状", ["唇炎", "毛囊炎", "皮炎", "荨麻疹", "痘痘", "泛红", "关节痛"])
    
    col_diet, col_env = st.columns(2)
    with col_diet:
        diet_tags = st.multiselect("🍔 饮食", ["咖啡因", "乳制品", "牛/羊肉", "海鲜", "高糖", "辛辣", "麸质", "酒精"])
    with col_env:
        env_tags = st.multiselect("🌍 环境/行为", ["新环境", "换季", "熬夜", "失眠", "剧烈运动", "久坐", "猫狗接触"])
    
    note = st.text_input("📝 备注")

    # 提交按钮
    if st.form_submit_button("💾 同步到 Google Sheets", use_container_width=True):
        try:
            # 1. 读取现有数据 (ttl=0 表示不缓存，强制读最新的)
            df = conn.read(worksheet="Sheet1", ttl=0)
            
            # 2. 准备新的一行数据
            new_data = pd.DataFrame([{
                "日期": str(date),
                "睡眠": sleep_score, "压力": stress_level, "鼻子": nose_status,
                "精力": energy_level, "皮肤": skin_score,
                "症状": ",".join(skin_symptoms),
                "标签": ",".join(diet_tags + env_tags),
                "备注": note,
                "记录时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }])
            
            # 3. 合并并写回
            # 注意：如果表是空的，concat 可能会有点警告，这里做了简单处理
            if df.empty:
                updated_df = new_data
            else:
                updated_df = pd.concat([df, new_data], ignore_index=True)
                
            conn.update(worksheet="Sheet1", data=updated_df)
            st.success("✅ 云端同步成功！去 Google Sheets 看看吧")
            
        except Exception as e:
            st.error(f"同步失败: {e}")

# === 3. Gemini 智能分析区 ===
st.markdown("### 🤖 每周分析 (Gemini)")

if st.button("✨ 生成分析报告"):
    try:
        # 拉取最新数据
        df = conn.read(worksheet="Sheet1", ttl=0)
        
        if not df.empty:
            recent_data = df.tail(7) # 取最后7行
            data_text = recent_data.to_string(index=False)
            
            prompt = f"""
            你是我（Zhong Qingyang）的健康助理。这是我存在 Google Sheets 里的最近身体数据：
            {data_text}

            请帮我分析：
            1. **模式识别**：在皮肤或精力变差的前1-2天，我通常做了什么（饮食/行为）？
            2. **本周总结**：我的整体炎症水平趋势如何？
            3. **下周建议**：给我 3 条基于数据的调整建议。
            """
            
            with st.spinner("Gemini 正在读取表格并思考..."):
                model = genai.GenerativeModel('gemini-pro')
                response = model.generate_content(prompt)
                st.markdown(response.text)
        else:
            st.warning("表格里还没数据呢，先记一条吧！")
    except Exception as e:
        st.error(f"分析失败: {e}")
