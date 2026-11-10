---
name: save_note
track: core
kind: action
provider: local
requires_env: []
inputs: [title, content, tags]
outputs: [tool, status, filename, path, title, tags, bytes_written]
side_effect: local_file_write
requires_confirmation: false
---

# save_note

Lưu kết quả nghiên cứu, trích dẫn hoặc tổng hợp vào file ghi chú Markdown cục bộ trong thư mục `artifacts/notes/`.
Chạy thuần local, không cần mạng ngoài.
