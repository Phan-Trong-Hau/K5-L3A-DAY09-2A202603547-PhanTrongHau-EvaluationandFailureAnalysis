# Báo cáo nhóm — Lab 8 LogiX-VN

**Bản tiến độ ngày 2026-11-16.** Đây là bản làm việc; cập nhật các mục kết quả sau khi hoàn tất ba shape bắt buộc và có benchmark nhóm cuối.

## 1. Thông tin nhóm

- Tên nhóm: chưa điền.
- Thành viên: xem `TEAM.md` (hiện bảng thành viên chưa được điền đầy đủ).
- Commit chốt (trùng `report/team/decision_adr.md`): chưa có.

## 2. Mục tiêu và cách tiếp cận

Nhóm triển khai cùng một quy trình xử lý claim qua workflow (A), single ReAct agent (B), orchestrator (C) và swarm reference (D). Dùng cùng host để kiểm policy, approval, trần hoàn tiền theo order và idempotency. Shape D có sẵn để làm baseline; nhóm chia A, B, C cho ba thành viên và Phan Trọng Hậu phụ trách baseline D cùng bonus B3.

Hiện Shape B đã hoàn thành và qua 62/62 test student. Shape A và C vẫn là stub trong workspace tại thời điểm cập nhật báo cáo này, nên phần benchmark 4 shape và quyết định kiến trúc chưa thể kết luận.

## 3. Giải pháp

- **A — workflow:** chưa triển khai; hiện `workflow.py` còn trả `not_implemented`.
- **B — single:** một vòng ReAct giới hạn 8 bước; quyết định nghiệp vụ và quote dùng order/compensation từ code. Model không tự quyết số tiền; host là nơi duy nhất ghi refund. Dùng các tool đọc order, refund history và compensation.
- **C — orchestrator:** chưa triển khai; hiện `orchestrator.py` còn trả `not_implemented`. Khi làm cần handoff allowlist và investigator chỉ có quyền đọc.
- **D — swarm:** shape tham chiếu có sẵn; dùng làm baseline so sánh.
- **Bonus B3:** `swarm_verified` giữ baseline swarm, thêm verifier trước refund. Nếu delay trong candidate khác order có cấu trúc, quote được tính lại trên dữ liệu order. Code nằm trong `src/bonus/`, không đổi A–C.

Trace và approval của A/C chưa được rà soát vì hai shape chưa hoàn thành. Shape B và B3 ghi trace theo contract; test bonus hiện kiểm tra không lộ parent secret và resume sau crash chỉ có một refund.

## 4. Kết quả

### Shape B

Lệnh `python -m pytest -q -m student -o addopts= tests/test_public_matrix.py -k 'single and not workflow and not orchestrator and not swarm'` cho kết quả **62 passed, 186 deselected**.

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

Chưa có `src/reports/benchmark.json` cho đủ bốn shape hay hidden selfcheck/grade. Vì A/C chưa xong, chưa điền so sánh đủ bốn shape hoặc khuyến nghị shape chính. Sau khi có số liệu, ghi quyết định tại `decision_adr.md` và nghiên cứu/ablation tại `research_card.md`.

## 5. Khó khăn và cách xử lý

- Môi trường ban đầu chưa có pytest; tạo `src/.venv` và cài dependencies từ `src/requirements.txt`.
- Lệnh lọc test student có thể lấy cả tham số shape khác do tên test chứa từ `single`; dùng biểu thức lọc loại `workflow`, `orchestrator`, `swarm` để chỉ chạy B.
- Swarm có sai khác chủ ý ở seed 55. B3 xử lý bằng kiểm chứng trên order có cấu trúc; benchmark trên case tự viết cũng cho thấy biến thiên theo seed của baseline.

## 6. Tổng hợp đóng góp

Shape B đã qua test student. Phan Trọng Hậu làm baseline D, biến thể B3, tám case đối kháng, test và benchmark bonus. Thành viên phụ trách A/C và commit/test tương ứng cần cập nhật trong `TEAM.md` và báo cáo cá nhân từng người.

## 7. Hạn chế và hướng cải thiện

MockLLM không phải model sản xuất và cost là giá mô phỏng; benchmark không đo latency. Bộ case B3 tự viết chỉ có tám claim nên không đại diện cho phân bố production. Cần hoàn tất A/C, benchmark cùng workflow, chạy crash suite, kiểm hidden và chọn shape chính theo số liệu trước khi kết luận cuối.

## 8. Tài liệu tham khảo

- `README.md`, `docs/business_rules.md`, `docs/contracts.md`, `docs/architecture.md`, `docs/metrics.md`.
- `docs/bonus_topics.md`, topic B3: verifier/aggregator chống khuếch đại lỗi.
