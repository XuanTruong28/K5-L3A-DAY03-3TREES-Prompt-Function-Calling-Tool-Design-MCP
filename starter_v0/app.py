from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

from env_loader import load_lab_env
from providers import make_provider
from providers.base import ToolCall
from tools import TOOL_FUNCTIONS, load_tool_declarations, to_openai_tools
from versioning import build_artifact_version


ROOT = Path(__file__).parent
ARTIFACTS_DIR = ROOT / "artifacts"
load_lab_env(ROOT)

st.set_page_config(
    page_title="AI Research Agent — Day 03 Lab",
    page_icon="🤖",
    layout="wide",
)


def execute_tool_call(call: ToolCall) -> dict:
    func = TOOL_FUNCTIONS.get(call.name)
    if not func:
        return {
            "tool": call.name,
            "args": call.args,
            "result": {"error": "unknown_tool", "message": f"No implementation for {call.name}"},
        }
    try:
        res = func(**call.args)
    except Exception as exc:
        res = {"error": type(exc).__name__, "message": str(exc)}
    return {"tool": call.name, "args": call.args, "result": res}


def init_session():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []


init_session()

# --- Sidebar Configuration ---
with st.sidebar:
    st.title("⚙️ Cấu hình Agent")
    provider_name = st.selectbox("Model Provider", ["openai", "openrouter", "gemini", "anthropic"], index=0)
    model_name = st.text_input("Model Name (để trống nếu dùng mặc định)", value="")
    max_rounds = st.slider("Max Tool Rounds", min_value=1, max_value=8, value=4)

    prompt_file = ARTIFACTS_DIR / "system_prompt.md"
    tools_file = ARTIFACTS_DIR / "tools.yaml"
    version_tag = build_artifact_version("v1", prompt_file, tools_file)
    st.caption(f"🔖 **Artifact Version**: `{version_tag}`")

    st.markdown("---")
    st.markdown("### 🛠️ Danh sách Tools sẵn có")
    declarations = load_tool_declarations(tools_file)
    for t in declarations:
        with st.expander(f"🔧 {t['name']}"):
            st.caption(t.get("description", ""))

    st.markdown("---")
    if st.button("🗑️ Xóa lịch sử chat"):
        st.session_state.messages = []
        st.session_state.chat_history = []
        st.rerun()

# --- Main App Header ---
st.title("🤖 AI Research Agent Demo")
st.markdown("Hệ thống **Research Agent** tự động gọi công cụ tra cứu, đọc web, tính toán số liệu và lưu báo cáo.")

# Sample prompt buttons
st.markdown("**Gợi ý câu hỏi thử nghiệm:**")
col1, col2, col3 = st.columns(3)
sample_prompt = None
if col1.button("📈 Tính tăng trưởng 50 tỷ lên 85 tỷ"):
    sample_prompt = "Doanh thu năm ngoái là 50 tỷ, năm nay là 85 tỷ. Tính giúp mình tốc độ tăng trưởng phần trăm."
if col2.button("📰 Tin tức AI hôm nay có gì?"):
    sample_prompt = "Tin tức AI hôm nay có gì nổi bật?"
if col3.button("🐦 Tweet mới nhất của Elon Musk"):
    sample_prompt = "Lấy 5 tweet mới nhất của Elon Musk."

# Render chat history
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        if msg.get("tool_calls"):
            with st.expander("🛠️ Chi tiết Tool Calls", expanded=False):
                st.json(msg["tool_calls"])
        st.markdown(msg["content"])

user_input = st.chat_input("Nhập câu hỏi nghiên cứu của bạn...") or sample_prompt

if user_input:
    # Display user query
    with st.chat_message("user"):
        st.markdown(user_input)

    st.session_state.chat_history.append({"role": "user", "content": user_input})

    # Prepare agent message context
    system_prompt_text = prompt_file.read_text(encoding="utf-8")
    openai_tools = to_openai_tools(declarations)

    working_messages = [{"role": "system", "content": system_prompt_text}]
    for msg in st.session_state.messages:
        working_messages.append(msg)
    working_messages.append({"role": "user", "content": user_input})
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("assistant"):
        with st.spinner("Agent đang suy nghĩ và gọi tools..."):
            try:
                provider = make_provider(provider_name)
                final_answer = ""
                all_recorded_calls = []

                for round_idx in range(1, max_rounds + 1):
                    model_arg = model_name.strip() if model_name.strip() else None
                    resp = provider.complete(working_messages, openai_tools, model=model_arg, temperature=0.0)
                    calls = resp.tool_calls

                    if not calls:
                        final_answer = resp.text or "Đã hoàn thành xử lý."
                        break

                    round_calls = [{"name": c.name, "args": c.args} for c in calls]
                    all_recorded_calls.extend(round_calls)

                    with st.status(f"Vòng {round_idx}: Gọi {len(calls)} công cụ...", expanded=True) as status:
                        tool_events = []
                        for c in calls:
                            st.write(f"🔧 **{c.name}** `{json.dumps(c.args, ensure_ascii=False)}`")
                            event = execute_tool_call(c)
                            tool_events.append(event)
                            res = event.get("result", {})
                            st.json(res)

                        status.update(label=f"Vòng {round_idx} hoàn tất!", state="complete")

                    # Check for clarify tool
                    clarify_event = next((e for e in tool_events if isinstance(e.get("result"), dict) and e["result"].get("awaiting_user")), None)
                    if clarify_event:
                        res = clarify_event["result"]
                        final_answer = res.get("question") or clarify_event["args"].get("question") or "Vui lòng cung cấp thêm thông tin."
                        break

                    working_messages.append({
                        "role": "assistant",
                        "content": (resp.text or "") + f"\nTOOL_CALLS_JSON:\n{json.dumps(round_calls, ensure_ascii=False)}",
                    })
                    working_messages.append({
                        "role": "user",
                        "content": f"TOOL_RESULTS_JSON:\n{json.dumps(tool_events, ensure_ascii=False, indent=2)}\n\nHãy tổng hợp kết quả trả lời người dùng ngắn gọn, trích nguồn rõ ràng.",
                    })

                st.markdown(final_answer)
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": final_answer,
                    "tool_calls": all_recorded_calls if all_recorded_calls else None,
                })
                st.session_state.messages.append({"role": "assistant", "content": final_answer})

            except Exception as e:
                st.error(f"Đã xảy ra lỗi: {e}")
