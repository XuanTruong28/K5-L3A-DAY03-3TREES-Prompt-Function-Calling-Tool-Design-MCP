---
name: cross_check
track: core
kind: local_formatter
provider: local
requires_env: []
inputs: [source_a, source_b]
outputs: [tool, verdict, jaccard_similarity, shared_keywords, unique_to_a_count, unique_to_b_count]
side_effect: false
requires_confirmation: false
---

# cross_check

Đối chiếu và so sánh hai nguồn thông tin / bài viết nghiên cứu (`source_a` và `source_b`):
- Xác định mức độ tương đồng thông qua Jaccard similarity trên tập từ khoá.
- Trả về danh sách từ khoá dùng chung (`shared_keywords`) và số từ khoá riêng biệt.
- Đưa ra kết luận mức độ đồng thuận: `high_alignment`, `moderate_alignment`, hoặc `low_alignment`.

Chạy thuần local, không cần mạng ngoài.
