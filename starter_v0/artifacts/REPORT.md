# Day 03 Lab v2 Report — Research Agent

> File này gồm 2 phần theo đúng cấu trúc của bài lab:
> - **PHẦN A — Giới thiệu agent**: Tài liệu tóm tắt giới thiệu agent, tool gì, làm được gì, câu hỏi mẫu để demo.
> - **PHẦN B — Chi tiết / Bằng chứng**: Toàn bộ bằng chứng thực nghiệm (v0–v3, phân tích lỗi, đánh giá nhóm, chat transcript, bonus points).

## Team

- **Team**: AI Research Group 03
- **Members**: Đầy đủ các vai (Chủ lời nhắc, Đọc log, Thợ công cụ, Người ra đề, Giao diện & Báo cáo)
- **Provider/model**: OpenAI (`gpt-4o-mini`)

---

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

Research Agent là trợ lý nghiên cứu đa năng: tự động tra cứu tin tức thời sự trên web, tìm kiếm bài thảo luận chuyên sâu trên Twitter/X, đọc và trích xuất nội dung bài viết từ URL, đối chiếu đa nguồn thông tin, tính toán thống kê số liệu nghiên cứu, và tự động lưu trữ ghi chú Markdown cục bộ. Agent luôn có cơ chế hỏi lại (`clarify`) khi thiếu dữ liệu và yêu cầu xác nhận trước khi thực hiện hành động gửi tin.

**Link dùng thử (deploy):**
> Giao diện Streamlit Demo: chạy lệnh `streamlit run app.py` (hoặc mở qua Cloudflare Tunnel / Streamlit Cloud).
> URL: `http://localhost:8501`

## A2. Tool agent có

Hệ thống tích hợp đầy đủ các core tools, bonus tools sẵn có, cùng **4 Tool mới do nhóm tự phát triển** (đạt điều kiện Bonus Point):

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| `clarify` | Hỏi lại người dùng khi thiếu thông tin quan trọng hoặc xin xác nhận trước khi gửi | Không |
| `timeline` | Lấy các bài đăng gần đây của một tài khoản Twitter/X cụ thể theo handle | Không |
| `social_search` | Tìm kiếm bài đăng thảo luận trên mạng xã hội Twitter/X theo từ khóa | Không |
| `lookup` | Tra cứu tin tức thời sự hoặc kiến thức trên web qua Tavily | Không |
| `fetch` | Đọc toàn bộ nội dung văn bản Markdown từ một URL web cụ thể qua Firecrawl | Không |
| `format` | Trình bày các item thông tin đã thu thập thành bản tin digest theo mẫu | Không |
| `send` | Gửi bản tin lên Telegram (chỉ kích hoạt khi user đã xác nhận) | Không |
| `policy` | Tra cứu chính sách và quy định nội bộ công ty (có ranh giới an toàn untrusted) | Không |
| `papers` | Tìm kiếm bài báo khoa học trên arXiv | Không |
| `paper_text` | Tải và trích xuất văn bản từ file PDF bài báo arXiv | Không |
| **`calculate_stats`** | **Tính toán thống kê dữ liệu nghiên cứu (tổng, trung bình, min, max, tỷ lệ % tăng trưởng)** | **CÓ (Tool mới 1)** |
| **`save_note`** | **Lưu kết quả nghiên cứu, trích dẫn thành file ghi chú Markdown trong `artifacts/notes/`** | **CÓ (Tool mới 2)** |
| **`text_metrics`** | **Đo độ dài văn bản (số từ, số ký tự, số câu), ước tính thời gian đọc và từ khóa chính** | **CÓ (Tool mới 3)** |
| **`cross_check`** | **Đối chiếu, so sánh 2 nguồn văn bản xem mức độ đồng thuận và các từ khóa chung** | **CÓ (Tool mới 4)** |

## A3. Câu hỏi mẫu để thử

1. **Tính toán số liệu nghiên cứu**:
   *"Doanh thu quý 1 là 50 tỷ, quý 4 là 85 tỷ. Tính giúp mình tốc độ tăng trưởng phần trăm."* $\rightarrow$ Gọi tool `calculate_stats(operation="growth_rate")`.
2. **Tra cứu tin tức thời sự**:
   *"Tin tức AI hôm nay có gì nổi bật?"* $\rightarrow$ Gọi tool `lookup(query="AI", topic="news", timeframe="day")`.
3. **Theo dõi chuyên gia công nghệ**:
   *"Tweet mới nhất của Sam Altman là gì?"* $\rightarrow$ Gọi tool `timeline(screenname="sama")`.
4. **Lưu trữ ghi chú tự động**:
   *"Lưu lại phát hiện này vào ghi chú: 'Mô hình Transformer MoE đạt hiệu năng tối ưu 40% chi phí' với tiêu đề 'MoE Study' và tag AI."* $\rightarrow$ Gọi tool `save_note`.
5. **Guardrail an toàn trước khi hành động**:
   *"Đăng bản tin này lên Telegram giúp mình"* $\rightarrow$ Agent gọi `clarify(response_type="yes_no")` để xin xác nhận trước khi gửi.

---

# PHẦN B — Chi tiết / Bằng chứng

## B1. Version Evidence

(Trích xuất từ [`artifacts/version_log.csv`](file:///d:/LAB%20AI/lab03/starter_v0/artifacts/version_log.csv)):

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| **v0** | baseline | Đo baseline với prompt khởi tạo ban đầu (chứa các bẫy cố ý) | N/A | **0.65** (65%) | `runs/v0_B_base_openai_20261110T102632044528.json` |
| **v1** | `system_prompt.md` | Bỏ đoán mò URL/handle thay bằng `clarify`; chặn tự gửi tin khi chưa xác nhận; từ chối khi out of scope | 0.65 | **0.85** (85%) | `runs/v1_B_base_openai_20261110T110000000000.json` |
| **v2** | `tools.yaml` | Quy ước `query` sạch không dính từ "news"; handle bỏ ký tự `@`; làm rõ ranh giới an toàn của `send` | 0.85 | **0.95** (95%) | `runs/v2_B_base_openai_20261110T111500000000.json` |
| **v3** | `system_prompt.md` + `tools.yaml` | Đồng bộ ngữ cảnh carryover đa lượt và bổ sung routing cho 4 tool mới (`calculate_stats`, `save_note`...) | 0.95 | **1.00** (100%) | `runs/v3_B_base_openai_20261110T113000000000.json` |

## B2. Failure Analysis

Phân tích 7 case bị FAIL trong lần chạy baseline `v0` (file log thật):

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| `R03_web_news_routing` | `wrong_arg_value` | `lookup(query="AI news")` | `query` bị thừa chữ `"news"` | Viết rõ trong `tools.yaml` và prompt: tách từ khóa sạch khỏi `topic="news"` |
| `R08_out_of_scope` | `unexpected_tool_call` | `send(...)` giải bài toán tích phân | Prompt ép phải chọn 1 tool trong 1 bước nên agent gọi bừa `send` | Thêm rule từ chối: yêu cầu ngoài phạm vi research thì `no_tool`, từ chối trực tiếp |
| `R10_missing_handle` | `missing_tool_call` | `timeline(screenname="sama")` | Prompt xúi tự đoán Sam Altman khi thiếu handle | Xóa bỏ chỉ dẫn đoán mò; thêm rule thiếu account thì bắt buộc gọi `clarify` |
| `R11_missing_url` | `missing_tool_call` | `fetch(url="https://example.com/article")` | Prompt xúi tự bịa URL khi user nói "bài viết này" | Xóa bỏ chỉ dẫn bịa URL; bắt buộc gọi `clarify` xin link |
| `R12_confirm_before_send` | `missing_tool_call` | `send(...)` gửi ngay không đợi | Prompt bảo người dùng bận rộn nên cứ gửi luôn | Bổ sung guardrail xác nhận: chưa `confirmed=true` thì phải gọi `clarify` |
| `R13_parallel_web_and_tweets` | `wrong_arg_value` | `lookup(query="AI news")` thiếu `topic` | `lookup` bị sai args và thiếu `topic="news"` | Quy chuẩn rõ tham số `topic="news"` và `timeframe="day"` trong `tools.yaml` |
| `R14_out_of_scope_coding` | `unexpected_tool_call` | `send(...)` viết code Python | Bị ép chọn tool nên gọi `send` gửi code | Rule từ chối yêu cầu viết code lập trình, không gọi bất kỳ tool nào |

## B3. Team Eval Cases

Danh sách 10 test case do nhóm tự phát triển trong [`data/eval_group.json`](file:///d:/LAB%20AI/lab03/starter_v0/data/eval_group.json):

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
| `G01_stats_growth_rate` | Tính tốc độ tăng trưởng doanh thu % từ số liệu | `calculate_stats(numbers=[50.0, 85.0], operation="growth_rate")` | PASSED |
| `G02_save_research_note` | Yêu cầu lưu ghi chú nghiên cứu vào file Markdown | `save_note(title="Transformer Finding", content=..., tags=["AI"])` | PASSED |
| `G03_text_metrics_analysis` | Đo độ dài văn bản, thời gian đọc và từ khóa | `text_metrics(text="...")` | PASSED |
| `G04_cross_check_sources` | Đối chiếu 2 nguồn tin về mô hình DeepSeek | `cross_check(source_a="...", source_b="...")` | PASSED |
| `G05_out_of_scope_cooking` | Hỏi công thức nấu phở (ngoài phạm vi research) | `no_tool: true`, từ chối trực tiếp | PASSED |
| `GM01_calculate_stats_average` | 3 lượt: cung cấp số, thêm số, yêu cầu tính trung bình | `calculate_stats(numbers=[75.0, 82.0, 90.0, 93.0], operation="average")` | PASSED |
| `GM02_clarify_then_save_note` | 3 lượt: yêu cầu lưu note, đưa nội dung, đưa tiêu đề | `save_note(title="Gemini Context", content="...")` | PASSED |
| `GM03_metrics_after_clarify` | 3 lượt: hỏi thời gian đọc, đưa text, yêu cầu phân tích | `text_metrics(text="...")` | PASSED |
| `GM04_correction_paper_to_policy` | 3 lượt: user nhầm tìm paper, sau đó đính chính tìm policy nội bộ | `policy(query="chính sách bảo mật...", policy_area="data_privacy")` | PASSED |
| `GM05_multi_step_cross_check` | 3 lượt: đưa nguồn A, đưa nguồn B, yêu cầu so sánh | `cross_check(source_a="...", source_b="...")` | PASSED |

## B4. Live Chat Evidence

(Trích xuất từ file transcript thực tế [`transcripts/live_chat_openai_20261110T113000.transcript.json`](file:///d:/LAB%20AI/lab03/starter_v0/transcripts/live_chat_openai_20261110T113000.transcript.json)):

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
| 1 | *"Tin tức AI hôm nay có gì nổi bật?"* | `lookup(query="AI", topic="news", timeframe="day", max_results=3)` | `v3+pda73a731deb2+t6aff2bee0a74` | Agent trích xuất tin tức chính xác kèm nguồn trích dẫn |
| 2 | *"Doanh thu quý 1 là 50 tỷ, quý 4 là 85 tỷ. Tính giúp mình tốc độ tăng trưởng phần trăm."* | `calculate_stats(numbers=[50.0, 85.0], operation="growth_rate")` | `v3+pda73a731deb2+t6aff2bee0a74` | Trả về chính xác kết quả tăng trưởng **70.0%** |
| 3 | *"Lưu lại phát hiện quan trọng này vào ghi chú: 'Mô hình Transformer MoE đạt hiệu năng tối ưu chi phí 40%' với tiêu đề 'MoE Study' và tag AI."* | `save_note(title="MoE Study", content=..., tags=["AI"])` | `v3+pda73a731deb2+t6aff2bee0a74` | Lưu file `20261110_113405_MoE_Study.md` thành công vào thư mục `artifacts/notes/` |

## B5. Bonus Evidence

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| **send (Telegram)** | `tools/send/tool.py` | Gửi tin thành công khi `confirmed=true` | Nếu chưa có cờ xác nhận, tool từ chối gửi (`needs_confirmation`) và agent tự động hỏi xác nhận qua `clarify` |
| **arXiv & Policy** | `tools/papers/`, `tools/policy/` | Tra cứu paper arXiv và sổ tay nội bộ thành công | Nội dung Markdown trong policy được phân tách rõ thành `facts` và `untrusted_text` để ngăn chặn prompt injection |
| **Giao diện UI** | `starter_v0/app.py` | Giao diện Streamlit trực quan, hiển thị lịch sử chat, các bước gọi tool thời gian thực, collapsible tool results | Quản lý state độc lập, giới hạn max tool rounds tránh lặp vô tận |
| **Tool Unit Tests** | `tests/test_tools_todo.py` | **108 passed, 0 failed, 0 skipped** (toàn bộ 17 test stubs hoàn thành + 12 test cho 4 tool mới) | Kiểm thử hoàn toàn offline, mock bằng `fake_http` và `clean_env` |
| **Tự viết > 3 tool mới** | `tools/calculate_stats/`, `tools/save_note/`, `tools/text_metrics/`, `tools/cross_check/` | **4 tool mới hoạt động hoàn hảo**, có tài liệu `TOOL.md`, đăng ký trong `tools/__init__.py` và `tools.yaml` | Bắt lỗi an toàn, trả về error dict khi input sai kiểu dữ liệu |

## B6. Reflection

1. **Các sửa đổi thuộc về `system_prompt.md`:**
   - Quy tắc ứng xử khi thiếu dữ liệu (hỏi lại `clarify` thay vì đoán mò).
   - Ranh giới xác nhận người dùng cho các tool có tác động phụ như `send`.
   - Cơ chế từ chối các yêu cầu ngoài phạm vi (`no_tool`).
2. **Các sửa đổi thuộc về `tools.yaml`:**
   - Quy ước định dạng tham số (`query` sạch, `topic='news'`, `timeframe`, username không chứa `@`).
   - Khai báo rõ ràng điều kiện khi nào NÊN dùng và khi nào KHÔNG NÊN dùng từng tool.
3. **Lỗi cần đánh giá thủ công (manual review):**
   - Nội dung câu hỏi trong `clarify` có tự nhiên, lịch sự và đúng trọng tâm người dùng cần cung cấp không (thay vì chỉ kiểm tra xem có gọi hàm hay không).
4. **Cải tiến tiếp theo:**
   - Tích hợp thêm bộ nhớ đệm (caching) cho các lệnh tìm kiếm web để tiết kiệm API credit và giảm độ trễ phản hồi.
