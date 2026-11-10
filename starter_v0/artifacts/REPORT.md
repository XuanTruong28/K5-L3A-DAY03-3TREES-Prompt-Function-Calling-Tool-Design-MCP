# Day 03 Lab v2 Report — Research Agent

> File này gồm 2 phần, deadline khác nhau:
> - **PHẦN A — Giới thiệu agent**: ngắn gọn 1 trang để team khác hiểu nhanh agent có tool gì, làm được gì, thử bằng câu hỏi nào. **Xong trước 16:30** để làm tài liệu phụ trợ khi demo. Có thể làm thành poster HTML/SVG (`artifacts/poster.html` / `poster.svg`) để show cho team cùng zone.
> - **PHẦN B — Chi tiết / Bằng chứng**: bảng đầy đủ (v0–v3, failure, eval, chat) dựa trên log thật. **Có thể hoàn thiện sau buổi debate để nộp bài.**

## Team

- Team: 3TREES
- Members: 2A202603605_NguyenHaAnh ,2A202603617_TranXuanTruong, 2A202603641_NguyenSyHuyKien
- Provider/model: openai
 
---

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

> 1–2 câu mô tả agent dùng để làm gì (cho team khác hiểu nhanh).

Ví dụ: "Research agent: tìm tin theo từ khóa / theo tài khoản, đọc URL, tổng hợp thành digest, và gửi lên Telegram khi được xác nhận."

**Link dùng thử (deploy):**

> Dán link public để team khác mở thử ngay. Cách deploy nhanh bằng Cloudflare Tunnel xem README. Nếu deploy Vercel/Streamlit Cloud thì dán link đó.
>
> URL: [https://tabs-elect-character-cherry.trycloudflare.com ](https://logo-leon-floppy-heat.trycloudflare.com/)

## A2. Tool agent có

> Liệt kê các tool agent đang dùng (gồm tool mới nhóm tự thêm). Mỗi tool 1 dòng: tên + làm được gì.

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | hỏi lại người dùng khi thiếu thông tin | không |
|  |  |  |
|  |  |  |

## A3. Câu hỏi mẫu để thử

> 3–5 câu hỏi/yêu cầu mẫu để team khác tự thử agent ngay.

1.
2.
3.

---

# PHẦN B — Chi tiết / Bằng chứng

## B1. Version Evidence

Fill from `artifacts/version_log.csv` and `runs/*.json`.

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline |Prompt & tool declaration mặc định (cố ý ép đoán, ép 1 step, gửi không xác nhận)  |-  |65% (13/20 pass)  |  |
| v1 |  |  |  |  |  |
| v2 |  |  |  |  |  |
| v3 |  |  |  |  |  |

## B2. Failure Analysis

Use actual failures from `results[*].result.failures`.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
|R03_web_news_routing  |wrong_tool  |  |Nhầm tool khi tìm tin tức AI  |Bổ sung quy tắc routing rõ ràng trong prompt  |
|R08_out_of_scope  |out_of_scope  |  |Câu ngoài phạm vi nhưng agent vẫn cố gọi tool  |Thêm rule từ chối/không gọi tool với câu ngoài lề  |
|R10_missing_handle  |missing_info  |  |Thiếu tên tài khoản nhưng agent tự đoán mò  |Xóa câu xúi đoán mò trong prompt, bắt buộc gọi clarify  |
|R11_missing_url  |missing_info  |  |Bảo tóm tắt nhưng không đưa link, agent tự bịa link  |Bắt buộc gọi clarify khi thiếu URL bài viết  |
|R12_confirm_before_send  |wrong_boundary  |  |Tự ý gửi tin Telegram khi chưa có xác nhận  |Đặt quy tắc chỉ gọi send khi confirmed=true  |
|R13_parallel_web_and_tweets  |wrong_tool  |  |Nhầm lẫn giữa tìm web và tìm tweet  |Phân định rõ lookup vs social_search  |
|R14_out_of_scope_coding  |out_of_scope  |  |Yêu cầu viết code, agent vẫn gọi tool nghiên cứu  |Hướng dẫn agent trả lời trực tiếp khi không cần tool  |

## B3. Team Eval Cases

List the 10 cases added to `data/eval_group.json` (5 single turn + 5 multi turn).

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
|G01_stats_growth_rate  |Tính tốc độ tăng trưởng doanh thu  |Gọi calculate_stats với operation=growth_rate  |PASS  |
|G02_stats_average  |	Tính điểm trung bình cộng dãy số  |Gọi calculate_stats với operation=average  |PASS  |
|G03_arxiv_papers_search  |Tìm kiếm bài báo khoa học trên arXiv  |Gọi tool papers  |FAIL wrong_tool  |
|G04_company_policy_privacy  |Tra cứu quy định nội bộ về bảo mật dữ liệu  |Gọi tool policy (data_privacy)  |FAIL wrong_tool  |
|G05_out_of_scope_cooking  |Hỏi công thức nấu ăn ngoài phạm vi  |	Từ chối, không gọi tool (no_tool)  |PASS  |
|GM01_multiturn_stats_carryover  |Đa lượt: bổ sung thêm số liệu rồi tính trung bình  |Gọi calculate_stats với danh sách số gộp  |PASS  |
|GM02_multiturn_clarify_then_timeline  |Đa lượt: hỏi thiếu tên người, sau đó bổ sung tên  |Gọi timeline với screenname=sama  |PASS  |
|GM03_multiturn_switch_topic_news  |Đa lượt: đổi chủ đề tìm kiếm từ chứng khoán sang AI  |Gọi lookup với query=AI, topic=news  |FAIL wrong_tool  |
|GM04_multiturn_paper_to_paper_text  |Đa lượt: tìm bài báo rồi chuyển sang đọc chi tiết  |Gọi paper_text  |PASS  |
|GM05_multiturn_confirm_telegram_send  |Đa lượt: người dùng đồng ý xác nhận gửi tin  |Gọi send với confirmed=true  |PASS  |
## B4. Live Chat Evidence

Use `transcripts/*.transcript.json`.

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
|  |  |  |  |  |

## B5. Bonus Evidence

Only fill if your team did bonus.

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| send (Telegram) |  |  |  |
| arXiv/company policy |  |  |  |
| UI |  |  |  |
| Tool unit tests (`tests/`) | `pytest` output |  |  |

Tool unit tests: số test đã viết, số bug tìm được trong tool có sẵn (nếu có), và một ví dụ lỗi mà unit test bắt được nhưng eval không bắt được.

## B6. Reflection

- Which fixes belonged in `system_prompt.md`?
- Which fixes belonged in `tools.yaml`?
- Which failure needed manual review instead of automatic grading?
- What would you improve next?

## B7. Small Local Model Challenge (bonus)

Only fill if your team did the local model challenge.

| Version | Model (provider) | Prompt/Tools | case_accuracy | tool_routing | argument | multiturn | Run File |
|---|---|---|---|---|---|---|---|
| v3 | (cloud) | v3 |  |  |  |  |  |
| v3-... | (ollama) | v3 |  |  |  |  |  |
| v3-... | (ollama) | v3 |  |  |  |  |  |
| v4-local |  |  |  |  |  |  |  |
| v5-local |  |  |  |  |  |  |  |

Lỗi đặc thù của model nhỏ (đếm từ run JSON):

| Failure Pattern | Count | Example Case | Fix Tried | Helped? |
|---|---|---|---|---|
| wrong / hallucinated tool |  |  |  |  |
| invalid JSON args (`_invalid_json_arguments`) |  |  |  |  |
| no tool call / answered directly |  |  |  |  |
| missed `clarify` |  |  |  |  |
| repeated / unnecessary calls |  |  |  |  |

- Cái gì giúp model nhỏ gọi tool đúng hơn nhất? Bằng chứng?
- Bản prompt tối ưu cho local chạy trên model cloud thì sao?
- Khi nào nhóm sẽ chọn model local thay vì cloud cho agent này?
