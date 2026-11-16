# Báo cáo nhóm — Lab 8 LogiX-VN

**Bản tiến độ ngày 2026-11-16.** Đây là bản làm việc; cập nhật các mục kết quả sau khi hoàn tất ba shape bắt buộc và có benchmark nhóm cuối.

## 1. Thông tin nhóm

- Tên nhóm: chưa điền.
- Thành viên: xem `TEAM.md` (hiện bảng thành viên chưa được điền đầy đủ).
- Commit chốt (trùng `report/team/decision_adr.md`): chưa có.

## 2. Mục tiêu và cách tiếp cận

Nhóm triển khai cùng một quy trình xử lý claim qua workflow (A), single ReAct agent (B), orchestrator (C) và swarm reference (D). Dùng cùng host để kiểm policy, approval, trần hoàn tiền theo order và idempotency. Shape D có sẵn để làm baseline; nhóm chia A, B, C cho ba thành viên và Phan Trọng Hậu phụ trách baseline D cùng bonus B3.

Shape B (`single`) và Shape C (`orchestrator`) đã qua 62/62 test student mỗi shape. Shape A (`workflow`) vẫn là stub, nên benchmark đã chạy nhưng hàng workflow chưa có ý nghĩa đánh giá; cần triển khai A rồi chạy lại trước khi chọn kiến trúc cuối.

## 3. Giải pháp

- **A — workflow:** chưa triển khai; hiện `workflow.py` còn trả `not_implemented`.
- **B — single:** một vòng ReAct giới hạn 8 bước; quyết định nghiệp vụ và quote dùng order/compensation từ code. Model không tự quyết số tiền; host là nơi duy nhất ghi refund. Dùng các tool đọc order, refund history và compensation.
- **C — orchestrator:** orchestrator lập handoff allowlist, dùng investigator chỉ đọc, lấy quote từ dữ liệu có cấu trúc và để host ghi refund. Đã qua 62/62 test student.
- **D — swarm:** shape tham chiếu có sẵn; dùng làm baseline so sánh.
- **Bonus B3:** `swarm_verified` giữ baseline swarm, thêm verifier trước refund. Nếu delay trong candidate khác order có cấu trúc, quote được tính lại trên dữ liệu order. Code nằm trong `src/bonus/`, không đổi A–C.

Trace của A chưa được rà soát vì shape còn là stub. Shape B và C đã qua ma trận student gồm các ca policy, retry và crash; B3 có test riêng kiểm tra secret và resume sau crash chỉ có một refund.

## 4. Kết quả

### Benchmark hiện tại

Benchmark cùng 14 claim × 5 seed; nguồn `src/reports/benchmark.json`. Workflow vẫn là stub nên kết quả 0.000 phản ánh `not_implemented`, không phải hiệu năng của workflow hoàn chỉnh.

| Shape | Pass rate | Pass^5 | Seed min–max | Variance | Cost/success (VND mô phỏng) | Mean / p95 steps |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| workflow (stub) | 0.000 | 0.000 | 0.000–0.000 | 0.000000 | — | 1.00 / 1 |
| single | 1.000 | 1.000 | 1.000–1.000 | 0.000000 | 38.40 | 6.93 / 8 |
| orchestrator | 1.000 | 1.000 | 1.000–1.000 | 0.000000 | 36.82 | 3.43 / 4 |
| swarm | 0.986 | 0.929 | 0.929–1.000 | 0.000816 | 49.57 | 2.80 / 3 |

Shape B và C mỗi shape qua **62/62 test student**. Cổng `python -m pytest -q`: **76 passed, 248 deselected**. Crash suite: **20/20** (`src/reports/crash.json`).

### Bonus B3 (kết quả hiện tại, chưa phải benchmark nhóm)

Số dưới đây lấy từ JSON benchmark do công cụ sinh ra, với 5 seed (11, 22, 33, 44, 55). Chi phí là VND mô phỏng; độ trễ không được đo.

| Bộ dữ liệu | Shape | Pass rate | Pass^5 | Seed min–max | Variance | Cost/success | Mean / p95 steps |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Public, 14 claim | swarm | 0.986 | 0.929 | 0.929–1.000 | 0.000816 | 49.57 | 2.80 / 3 |
| Public, 14 claim | swarm_verified | 1.000 | 1.000 | 1.000–1.000 | 0.000000 | 48.86 | 3.66 / 4 |
| Public, 14 claim | workflow baseline | 1.000 | 1.000 | 1.000–1.000 | 0.000000 | 27.86 | 1.86 / 2 |
| Tự viết, 8 claim | swarm | 0.850 | 0.250 | 0.250–1.000 | 0.090000 | 63.39 | 3.18 / 4 |
| Tự viết, 8 claim | swarm_verified | 1.000 | 1.000 | 1.000–1.000 | 0.000000 | 53.88 | 4.18 / 5 |
| Tự viết, 8 claim | workflow baseline | 1.000 | 1.000 | 1.000–1.000 | 0.000000 | 30.00 | 2.00 / 2 |

Nguồn: `src/reports/bonus_benchmark_public.json`, `src/reports/bonus_benchmark_adversarial.json` và `src/reports/bonus_analysis.json`. Test bonus: 22 passed. Toàn bộ cổng hiện tại `python -m pytest -q`: **76 passed, 248 deselected**. Crash suite: **20/20** (`src/reports/crash.json`). Verifier can thiệp 1/70 trial public, 7/40 trial đối kháng. Trên public T02 seed 55, swarm tin ticket báo trễ 5 ngày thay vì order 2 ngày; B3 đối chiếu order, quote 0 và từ chối. Workflow baseline là bản deterministic bonus-local bám theo hợp đồng Shape A; cần chạy lại với `workflow.py` chính thức sau khi thành viên phụ trách A hoàn tất.

### Kết quả nhóm còn thiếu

Benchmark bốn shape đã có nhưng cần chạy lại sau khi triển khai A. Chưa có hidden selfcheck/grade, chưa chọn shape chính và chưa chốt ADR/research card. Workflow baseline trong benchmark B3 là module bonus-local, không thay cho A chính thức.

## 5. Khó khăn và cách xử lý

- Môi trường ban đầu chưa có pytest; tạo `src/.venv` và cài dependencies từ `src/requirements.txt`.
- Lệnh lọc test student có thể lấy cả tham số shape khác do tên test chứa từ `single`; dùng biểu thức lọc loại `workflow`, `orchestrator`, `swarm` để chỉ chạy B.
- Swarm có sai khác chủ ý ở seed 55. B3 xử lý bằng kiểm chứng trên order có cấu trúc; benchmark trên case tự viết cũng cho thấy biến thiên theo seed của baseline.

## 6. Tổng hợp đóng góp

Shape B và C đã qua test student. Phan Trọng Hậu làm baseline D, biến thể B3, tám case đối kháng, test và benchmark bonus. Thành viên phụ trách A và commit/test tương ứng cần cập nhật trong `TEAM.md` và báo cáo cá nhân.

## 7. Hạn chế và hướng cải thiện

MockLLM không phải model sản xuất và cost là giá mô phỏng; benchmark không đo latency. Bộ case B3 tự viết chỉ có tám claim nên không đại diện cho phân bố production. Cần hoàn tất A/C, benchmark cùng workflow, chạy crash suite, kiểm hidden và chọn shape chính theo số liệu trước khi kết luận cuối.

## 8. Tài liệu tham khảo

- `README.md`, `docs/business_rules.md`, `docs/contracts.md`, `docs/architecture.md`, `docs/metrics.md`.
- `docs/bonus_topics.md`, topic B3: verifier/aggregator chống khuếch đại lỗi.
