import json
from pathlib import Path
import streamlit as st

from env_loader import load_lab_env
from providers import make_provider
from tools import TOOL_FUNCTIONS, load_tool_declarations, to_openai_tools
from agent import ResearchAgent

# 1. Cấu hình trang & nạp môi trường
ROOT = Path(__file__).parent
load_lab_env(ROOT)

st.set_page_config(
    page_title="AI Research Assistant — 3TREES Lab",
    page_icon="🌲",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS cho phong cách Card hiện đại, sạch sẽ và hoàn toàn không có JSON
st.markdown("""
<style>
    /* Card công cụ chính */
    .tool-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 18px;
        margin-top: 10px;
        margin-bottom: 14px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.04);
    }
    .tool-header {
        display: flex;
        align-items: center;
        gap: 8px;
        font-weight: 700;
        font-size: 0.95rem;
        color: #1e293b;
        margin-bottom: 12px;
        padding-bottom: 8px;
        border-bottom: 1px dashed #cbd5e1;
    }
    /* Sub-card cho từng mẩu tin tức / bài báo */
    .item-card {
        background: #f8fafc;
        border-left: 4px solid #10b981;
        border-radius: 6px;
        padding: 12px 14px;
        margin-bottom: 10px;
    }
    .item-title {
        font-weight: 600;
        font-size: 0.95rem;
        color: #0f172a;
        text-decoration: none;
    }
    .item-title:hover {
        text-decoration: underline;
        color: #059669;
    }
    .item-source {
        font-size: 0.78rem;
        color: #64748b;
        margin-top: 2px;
        margin-bottom: 6px;
    }
    .item-summary {
        font-size: 0.88rem;
        color: #334155;
        line-height: 1.4;
    }
    /* Card cảnh báo / xác nhận */
    .warning-card {
        background: #fffbeb;
        border-left: 4px solid #f59e0b;
        padding: 12px 14px;
        border-radius: 6px;
        color: #92400e;
        font-size: 0.9rem;
    }
    .success-card {
        background: #f0fdf4;
        border-left: 4px solid #10b981;
        padding: 12px 14px;
        border-radius: 6px;
        color: #065f46;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# 2. Khởi tạo Agent trong session_state
if "agent" not in st.session_state:
    tools_schema = to_openai_tools(load_tool_declarations(ROOT / "artifacts" / "tools.yaml"))
    system_prompt = (ROOT / "artifacts" / "system_prompt.md").read_text(encoding="utf-8")
    provider = make_provider("openai")  # Hoặc "openrouter" tùy theo key bạn dùng
    st.session_state.agent = ResearchAgent(provider=provider, system_prompt=system_prompt, tools=tools_schema)
    st.session_state.messages = []

# Tên & Icon hiển thị cho từng công cụ
TOOL_INFO = {
    "lookup": {"icon": "🔍", "name": "Tra Cứu Thông Tin Trực Tuyến (Tavily)"},
    "fetch": {"icon": "🌐", "name": "Trích Xuất Nội Dung Trang Web (Firecrawl)"},
    "timeline": {"icon": "🐦", "name": "Bài Đăng Tài Khoản Mạng Xã Hội (Twitter)"},
    "social_search": {"icon": "💬", "name": "Tìm Kiếm Mạng Xã Hội (Twitter)"},
    "clarify": {"icon": "❓", "name": "Làm Rõ Thông Tin Yêu Cầu"},
    "format": {"icon": "📝", "name": "Định Dạng Bản Tin Tóm Tắt"},
    "send": {"icon": "🚀", "name": "Kênh Phân Phối Tin Nhắn (Telegram)"},
    "policy": {"icon": "📜", "name": "Chính Sách & Quy Định Nội Bộ"},
    "papers": {"icon": "📚", "name": "Tra Cứu Báo Cáo Khoa Học (arXiv)"},
    "paper_text": {"icon": "📑", "name": "Đọc Nội Dung Báo Cáo Chi Tiết"},
    "calculate_stats": {"icon": "📊", "name": "Thống Kê & Phân Tích Dữ Liệu Số"},
    "save_note": {"icon": "💾", "name": "Lưu Trữ Ghi Chú Nghiên Cứu"},
    "text_metrics": {"icon": "📏", "name": "Đo Lường Chỉ Số Văn Bản"},
    "cross_check": {"icon": "⚖️", "name": "Đối Chiếu Nguồn Tin"},
}

def render_tool_as_cards(tool_name: str, args: dict, result: any):
    """Vẽ toàn bộ kết quả của tool thành Card trực quan, thân thiện (100% không dùng JSON)."""
    info = TOOL_INFO.get(tool_name, {"icon": "⚙️", "name": tool_name.title()})
    
    st.markdown(f"""
    <div class="tool-card">
        <div class="tool-header">
            <span>{info['icon']}</span>
            <span>{info['name']}</span>
        </div>
    """, unsafe_allow_html=True)

    # 1. Tool Thống kê: calculate_stats
    if tool_name == "calculate_stats":
        if isinstance(result, dict) and "result" in result:
            col1, col2, col3 = st.columns([1, 1, 2])
            with col1:
                st.metric(
                    label=f"Phép tính: {result.get('operation', 'summary').upper()}",
                    value=f"{result.get('result')}"
                )
            with col2:
                st.metric(
                    label="Số lượng mẫu tính",
                    value=f"{len(args.get('numbers', []))} phần tử"
                )
            with col3:
                st.markdown(f"**Dãy số đầu vào:** `{args.get('numbers', [])}`")
        else:
            st.info(f"Kết quả phân tích: {result}")

    # 2. Tool Tìm kiếm Web: lookup
    elif tool_name == "lookup":
        items = result.get("items", []) if isinstance(result, dict) else []
        st.markdown(f"**Từ khóa tìm kiếm:** *'{args.get('query')}'* ({len(items)} kết quả)")
        if items:
            for item in items[:4]:  # Hiển thị tối đa 4 card bài viết
                title = item.get("title", "Không có tiêu đề")
                url = item.get("url", "#")
                source = item.get("source", "Nguồn tin tức")
                summary = item.get("summary", "Không có bản tóm tắt.")
                st.markdown(f"""
                <div class="item-card">
                    <a class="item-title" href="{url}" target="_blank">🔗 {title}</a>
                    <div class="item-source">Nguồn: {source}</div>
                    <div class="item-summary">{summary}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.caption("Không tìm thấy bài viết nào phù hợp.")

    # 3. Tool Đọc URL: fetch
    elif tool_name == "fetch":
        title = result.get("title") or "Trang nội dung" if isinstance(result, dict) else "Trang Web"
        summary = result.get("summary") or result.get("text") or str(result)
        st.markdown(f"""
        <div class="item-card">
            <div class="item-title">📄 {title}</div>
            <div class="item-source">Địa chỉ: <a href="{args.get('url')}" target="_blank">{args.get('url')}</a></div>
            <div class="item-summary">{summary[:400]}...</div>
        </div>
        """, unsafe_allow_html=True)

    # 4. Tool Bài báo khoa học: papers & paper_text
    elif tool_name in ["papers", "paper_text"]:
        papers_list = result.get("papers", []) if isinstance(result, dict) else []
        if papers_list:
            for p in papers_list[:3]:
                st.markdown(f"""
                <div class="item-card">
                    <div class="item-title">📚 {p.get('title', 'Paper')}</div>
                    <div class="item-source">Tác giả: {p.get('authors', 'Đang cập nhật')} | ID: {p.get('id', '')}</div>
                    <div class="item-summary">{p.get('summary', '')[:300]}...</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="item-card">
                <div class="item-title">📑 Trích xuất nội dung arXiv</div>
                <div class="item-summary">{str(result)[:350]}...</div>
            </div>
            """, unsafe_allow_html=True)

    # 5. Tool Chính sách nội bộ: policy
    elif tool_name == "policy":
        results = result.get("results", []) if isinstance(result, dict) else []
        if results:
            for r in results:
                st.markdown(f"""
                <div class="item-card">
                    <div class="item-title">📜 {r.get('title', 'Điều khoản chính sách')}</div>
                    <div class="item-source">Phân loại: {r.get('policy_area', 'Chung')}</div>
                    <div class="item-summary">{"<br>• ".join(r.get('facts', []))}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.caption("Không tìm thấy điều khoản liên quan trong chính sách công ty.")

    # 6. Tool Mạng xã hội: timeline / social_search
    elif tool_name in ["timeline", "social_search"]:
        tweets = result.get("items", []) if isinstance(result, dict) else []
        for tw in tweets[:3]:
            st.markdown(f"""
            <div class="item-card">
                <div class="item-title">💬 @{tw.get('author', args.get('screenname', 'user'))}</div>
                <div class="item-summary">{tw.get('text', '')}</div>
                <div class="item-source"><a href="{tw.get('url', '#')}" target="_blank">Xem bài đăng gốc</a></div>
            </div>
            """, unsafe_allow_html=True)

    # 7. Tool Xác nhận gửi: send
    elif tool_name == "send":
        if args.get("confirmed"):
            st.markdown("""
            <div class="success-card">
                ✅ <b>Đã phát hành tin nhắn thành công</b> lên kênh Telegram an toàn.
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="warning-card">
                ⚠️ <b>Chặn bảo mật:</b> Yêu cầu gửi tin chưa có xác nhận từ người dùng. Hệ thống đang giữ lại.
            </div>
            """, unsafe_allow_html=True)

    # 8. Tool Hỏi lại: clarify
    elif tool_name == "clarify":
        st.markdown(f"""
        <div class="warning-card">
            ❓ <b>Cần làm rõ thêm:</b> {args.get('question', '')}
        </div>
        """, unsafe_allow_html=True)

    # Mặc định thân thiện cho các tool khác
    else:
        st.markdown(f"""
        <div class="item-card">
            <div class="item-summary">{str(result)[:300]}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


# 3. Sidebar: Thông tin & Câu hỏi mẫu 1-click
with st.sidebar:
    # Logo thương hiệu nhóm 3TREES
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 6px; padding: 4px 0;">
        <span style="font-size: 2rem; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.15));">🌲</span>
        <div>
            <span style="font-size: 1.55rem; font-weight: 900; letter-spacing: 2px; background: linear-gradient(135deg, #059669 0%, #10b981 50%, #34d399 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">3TREES</span>
            <span style="display: block; font-size: 0.72rem; color: #64748b; font-weight: 600; letter-spacing: 1px; text-transform: uppercase;">Research Lab</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.header("🔬 AI Research Agent")
    st.markdown("**Hệ thống trợ lý nghiên cứu đa công cụ**")
    
    st.divider()
    st.subheader("💡 Câu hỏi mẫu trải nghiệm")
    
    sample_queries = [
        ("📊 Thống kê tăng trưởng", "Doanh thu năm ngoái là 50 tỷ, năm nay là 85 tỷ. Tính giúp mình tốc độ tăng trưởng phần trăm."),
        ("🔍 Tin tức AI hôm nay", "Tin tức AI hôm nay có gì mới nổi bật?"),
        ("📜 Chính sách bảo mật", "Quy định công ty về bảo mật dữ liệu khách hàng khi dùng AI?"),
        ("📚 Nghiên cứu arXiv", "Tìm bài báo mới nhất về Transformer trên arXiv"),
        ("❓ Câu hỏi thiếu URL", "Tóm tắt bài viết này giúp mình với"),
    ]
    
    for label, query in sample_queries:
        if st.button(label, use_container_width=True):
            st.session_state.pending_input = query

    st.divider()
    if st.button("🗑️ Xóa lịch sử trò chuyện", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# 4. Khu vực trò chuyện chính
st.subheader("💬 Trò chuyện cùng Research Assistant")
st.caption("Agent tự động nhận diện ý định, phân tích dữ liệu và kích hoạt công cụ nghiên cứu phù hợp.")

# Hiển thị lịch sử tin nhắn
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        # Hiển thị các công cụ đã chạy thành các Card trực quan
        if msg.get("tool_executions"):
            for item in msg["tool_executions"]:
                render_tool_as_cards(
                    tool_name=item.get("tool", ""),
                    args=item.get("args", {}),
                    result=item.get("result")
                )

        # Hiển thị phản hồi văn bản
        if msg.get("content"):
            st.markdown(msg["content"])

# 5. Xử lý tin nhắn người dùng nhập hoặc bấm từ câu hỏi mẫu
active_input = st.chat_input("Nhập yêu cầu nghiên cứu của bạn...")
if "pending_input" in st.session_state and st.session_state.pending_input:
    active_input = st.session_state.pending_input
    del st.session_state["pending_input"]

if active_input:
    # 1. Thêm tin nhắn user vào lịch sử
    st.session_state.messages.append({"role": "user", "content": active_input})
    with st.chat_message("user"):
        st.markdown(active_input)

    # 2. Xử lý và gọi Agent
    with st.chat_message("assistant"):
        with st.spinner("🤖 Đang phân tích yêu cầu và kích hoạt công cụ phù hợp..."):
            history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
            try:
                run = st.session_state.agent.run(history)
                
                executed_tools = []
                if run.tool_calls:
                    for call, res in zip(run.tool_calls, run.tool_results):
                        tool_name = call.name
                        raw_res = res.get("result")
                        
                        # Render Card ngay lập tức
                        render_tool_as_cards(tool_name, call.args, raw_res)

                        executed_tools.append({
                            "tool": tool_name,
                            "args": call.args,
                            "result": raw_res
                        })

                # Hiển thị câu phản hồi tổng kết của agent
                response_text = run.text or "*(Đã hoàn tất trích xuất dữ liệu từ công cụ)*"
                st.markdown(response_text)

                # Lưu vào lịch sử phiên làm việc
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response_text,
                    "tool_executions": executed_tools
                })

            except Exception as e:
                st.error(f"❌ Đã xảy ra lỗi trong quá trình thực thi: {e}")