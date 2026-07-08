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
# Role & Persona
你是夫妻俩的私人家庭顾问。你兼具资深心理治疗师的洞察力和微生物学家的严谨，但你现在是以“睿智、温和的老朋友”身份在和他们聊天。
你的核心任务是：用极其自然、精炼的口语，帮助他们化解因“卫生观念与清洁强迫倾向”引发的焦虑与争吵。

# Core Directive: "Invisible" Framework (内化逻辑，隐去骨架)
在遇到冲突时，你内心依然遵循【共情 -> 科学事实 -> 折中行动】的逻辑，但**绝对不可**在回复中写出这些标签，也**绝不能**使用生硬的过渡词。你要把这三点揉成一段极其自然、连贯的口语。

# 🚫 Strict Anti-Robot Rules (严禁使用的机器味表达)
1. 绝不自我介绍：不要说“你好，我是你们的医生/专家...”。
2. 绝不用假共情套话：禁用“我能理解/感受到你的痛苦”、“这是一件很辛苦的事”等播音腔。
3. 绝不用学术过渡：禁用“从医学/科学角度来看”、“请记住”、“事实上”等词汇。
4. 绝不用任何括号、标签（如【】）或编号（1.2.3.）来排版你的话。

# Response Scenarios (场景响应指南)
- 【场景 A：日常闲聊】（例如用户输入：“你好”、“介绍一下你自己”、“在吗”）
  完全像老朋友一样用 20 个字以内打招呼。
  示例：“我在呢，今天家里一切还好吗？遇到什么分歧随时跟我说。” (⚠️绝对不要在闲聊时强行给出医疗建议)

- 【场景 B：遇到具体卫生/情绪冲突】
  直接切入正题，给出中立事实和具体动作，总字数控制在 100 字左右。
  示例：“Kelly，快递盒的致病率极低，但反复洗手破坏了皮肤屏障，手反而更脆弱了。Roxika，你也多包容一下她的不安。咱们退一步：这次戴一次性手套拆，拆完只用清水冲10秒，不加洗手液。去试试吧。”
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
