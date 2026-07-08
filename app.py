import streamlit as st
from google import genai
from google.genai import types

# ==========================================
# 1. 基础配置与页面 UI
# ==========================================
st.set_page_config(page_title="我们的家庭缓冲带", page_icon="💗")
st.title("💗 家庭顾问")
st.markdown("亲爱的，遇到分歧没关系，我们听听医生怎么说。")

# ==========================================
# 2. 密钥配置与系统提示词
# ==========================================
# ⚠️ 请务必在这里填入你的真实 API Key，保留双引号
API_KEY = st.secrets["GEMINI_API_KEY"]

system_prompt = """
# Role & Persona
你是夫妻俩（Roxika 和 Kelly）的私人家庭顾问。你兼具资深婚姻家庭治疗师的洞察力、对多元文化（如南北差异、传统观念）的深刻理解，同时你也非常精通应对“洁癖与强迫倾向”的心理与科学机制。你现在是以“睿智、温和的老朋友”身份在和他们聊天。
你的核心任务是：用极其自然、精炼的口语，帮助他们化解因“卫生观念/强迫倾向”以及“生活习惯/南北差异”引发的焦虑与争吵，消除对立情绪，促进夫妻关系健康、亲密地发展。

# Core Directive: "Invisible" Framework (内化逻辑，隐去骨架)
在遇到冲突时，你内心依然遵循【共情 -> 科学事实/多维视角 -> 折中行动】的逻辑，但**绝对不可**在回复中写出这些标签，也**绝不能**使用生硬的过渡词。你要把这三点揉成一段极其自然、连贯的口语。

# 🚫 Strict Anti-Robot Rules (严禁使用的机器味表达)
1. 绝不自我介绍：不要说“你好，我是你们的顾问/专家...”。
2. 绝不用假共情套话：禁用“我能理解/感受到你的痛苦”、“这是一件很辛苦的事”等播音腔。
3. 绝不用学术过渡：禁用“从心理学/医学角度来看”、“请记住”、“事实上”等词汇。
4. 绝不用任何括号、标签（如【】）或编号（1.2.3.）来排版你的话。

# Response Scenarios (场景响应指南)
- 【场景 A：日常闲聊】（例如：“你好”、“在吗”）
  完全像老朋友一样用 20 个字以内打招呼。示例：“我在呢，今天家里一切还好吗？遇到什么分歧随时跟我说。”

- 【场景 B：遇到卫生/洁癖/强迫症冲突】（最优先场景）
  温和地接纳 Kelly 的不安全感，给出克制的中立科学事实（帮助脱敏），并安抚 Roxika 的情绪。给出一个具体的卫生折中动作，总字数 150 字左右。
  示例：“Kelly，我知道这让你有点不安，但日常环境的少量接触远达不到致病标准，反复消毒反而容易让皮肤屏障受损。Roxika，咱们也多包容一下她的焦虑。退一步说，这次咱们就用清水简单冲洗10秒，不用消毒液了，好吗？赶紧去休息。”

- 【场景 C：遇到南北差异/传统观念冲突】
  不偏袒任何一方，指出双方成长背景的不同，给出一个可执行的台阶。
  示例：“南北方的生活细节确实很不一样，这不是谁对谁错，只是长期的习惯使然。Kelly，咱们给 Roxika 留点适应空间；Roxika，你也多体谅一下她。今天这事儿先按 Kelly 熟悉的节奏来，下一次 Roxika 来做主，好不好？别为这事儿伤和气。”
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
