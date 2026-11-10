---
name: text_metrics
track: core
kind: local_formatter
provider: local
requires_env: []
inputs: [text]
outputs: [tool, char_count, word_count, sentence_count, reading_time_minutes, top_words]
side_effect: false
requires_confirmation: false
---

# text_metrics

Phân tích số liệu văn bản nghiên cứu:
- Đếm số ký tự (`char_count`), số từ (`word_count`), số câu (`sentence_count`).
- Ước tính thời gian đọc (`reading_time_minutes` với tốc độ đọc chuẩn 200 từ/phút).
- Trích xuất top 5 từ khoá xuất hiện nhiều nhất.

Chạy thuần local, không cần mạng ngoài.
