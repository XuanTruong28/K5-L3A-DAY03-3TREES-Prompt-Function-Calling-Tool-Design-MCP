import streamlit as st

from chat import ARTIFACTS_DIR, run_model_tool_loop, trim_history
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools

st.set_page_config(page_title="Research Agent", page_icon="🔎")
st.title("🔎 Research Agent")

with st.sidebar:
    provider_name = st.selectbox("Provider", ["openai", "openrouter", "anthropic", "gemini", "ollama"])
    if st.button("Xoá hội thoại"):
        st.session_state.messages = []
        st.rerun()


@st.cache_resource
def get_provider(name):
    return make_provider(name)


if "messages" not in st.session_state:
    st.session_state.messages = []

# Hiện lại lịch sử chat
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])
        if m.get("tools"):
            with st.expander("🔧 Tool đã gọi"):
                st.json(m["tools"])

user_text = st.chat_input("Hỏi agent...")
if user_text:
    st.session_state.messages.append({"role": "user", "content": user_text})
    with st.chat_message("user"):
        st.markdown(user_text)

    # Đọc lại prompt/tools mỗi lần để sửa file là có hiệu lực ngay
    system_prompt = (ARTIFACTS_DIR / "system_prompt.md").read_text(encoding="utf-8")
    tools = to_openai_tools(load_tool_declarations(ARTIFACTS_DIR / "tools.yaml"))

    history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[:-1]]
    messages = [
        {"role": "system", "content": system_prompt},
        *trim_history(history, 5),
        {"role": "user", "content": user_text},
    ]

    with st.chat_message("assistant"):
        with st.spinner("Đang xử lý..."):
            try:
                result = run_model_tool_loop(
                    provider=get_provider(provider_name),
                    messages=messages,
                    tools=tools,
                    model=None,
                    max_tool_rounds=4,
                )
                answer = result["assistant_text"]
                tool_log = [{"tool": e["tool"], "args": e["args"]} for e in result["tool_events"]]
            except Exception as exc:
                answer, tool_log = f"Lỗi: {type(exc).__name__}: {exc}", []
        st.markdown(answer)
        if tool_log:
            with st.expander("🔧 Tool đã gọi"):
                st.json(tool_log)

    st.session_state.messages.append({"role": "assistant", "content": answer, "tools": tool_log})