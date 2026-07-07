import streamlit as st
from google import genai
from google.genai import types

# ==========================================
# 1. 基础配置与页面 UI
# ==========================================
st.set_page_config(page_title="我们的家庭缓冲带", page_icon="💗")
st.title("💗 家庭专属心理与卫生顾问")
st.markdown("亲爱的，遇到分歧没关系，我们听听医生怎么说。")

# ==========================================
# 2. 密钥配置与系统提示词
# ==========================================
# ⚠️ 请务必在这里填入你的真实 API Key，保留双引号
API_KEY = st.secrets["GEMINI_API_KEY"]

system_prompt = """
# Role
你是一位拥有20年临床经验的资深婚姻家庭治疗师与临床微生物学专家。你的目标是帮助一对因“卫生观念差异与强迫洁癖倾向”而深陷争吵的夫妻（丈夫与妻子）。

# Background
妻子有因疫情创伤和遗传导致的强迫性洁癖（表现为过度洗手导致指纹变淡、恐惧触摸）。丈夫深感疲惫，两人频繁争吵。双方都希望能改善婚姻，找到科学卫生与心理舒适的平衡点。

# Core Principles
1. 绝对中立：共情妻子的生理/心理痛苦，肯定丈夫的疲惫与包容。
2. 科学折中：强调“无菌不存在，适度清洁保护皮肤屏障”。
3. 极简高效：在夫妻争吵的当下，需要快速灭火，拒绝啰嗦和长篇大论说教。

# Response Framework (严格约束)
每次收到用户的输入，你的回复总字数必须控制在 150 - 300 字以内。请严格按照以下三步输出，每步一两句话即可：
1. 【一语共情】：用极其简短、温和的话，精准接住双方当下的情绪。
2. 【科学定调】：用一句话给出中立的医学事实，打破僵局。
3. 【折中行动】：直接给出一个当下双方各退半步的“微操作”。

# Tone
温暖、客观、精炼。像一位经验丰富、说话言简意赅但句句切中要害的主治医师。不使用复杂的专业术语，不说废话。
"""

# ==========================================
# 3. 对话与客户端记忆管理
# ==========================================
if "client" not in st.session_state:
    st.session_state.client = genai.Client(api_key=API_KEY)
    
    # 融合了 AI Studio 导出的精确配置
    st.session_state.chat_session = st.session_state.client.chats.create(
        # 💡 如果你嫌 3.1 Pro 太慢且容易被限制频率（报错429），请把这里改为 "gemini-1.5-flash"
        model="gemini-3-flash-preview", 
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.6,
            top_p=0.95
        )
    )

if "messages" not in st.session_state:
    st.session_state.messages = []

# 渲染历史聊天记录
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ==========================================
# 4. 接收输入并生成回复 (带防崩溃保护)
# ==========================================
if user_input := st.chat_input("说点什么吧，比如：医生，我们今天因为..."):
    
    # 显示用户输入
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # 调用大模型生成回复
    with st.chat_message("assistant"):
        with st.spinner("医生正在思考中..."):
            try:
                response = st.session_state.chat_session.send_message(user_input)
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                error_msg = str(e)
                if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                    st.warning("⚠️ 医生刚刚接诊了太多消息，需要喝口水休息一下。请等待大约 1 分钟后再试，或者在代码里把模型换成 gemini-1.5-flash。")
                else:
                    st.error(f"真实报错细节：{error_msg}")