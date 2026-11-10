---
name: calculate_stats
track: core
kind: local_formatter
provider: local
requires_env: []
inputs: [numbers, operation]
outputs: [tool, operation, result, count]
side_effect: false
requires_confirmation: false
---

# calculate_stats

Tính toán các chỉ số thống kê cơ bản từ danh sách số liệu nghiên cứu:
- `summary`: Tổng hợp `count`, `sum`, `average`, `min`, `max`.
- `average`: Tính giá trị trung bình.
- `sum`: Tính tổng các phần tử.
- `growth_rate`: Tính tỷ lệ tăng trưởng % từ số đầu đến số cuối: `((final - initial) / |initial|) * 100`.

Chạy thuần local, không cần mạng hay API key ngoài.
