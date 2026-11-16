# Báo cáo nhóm — Lab 8 LogiX-VN

**Bản cập nhật ngày 2026-11-16.** Ba shape bắt buộc và benchmark public đã hoàn tất trên code cuối. Nhóm chọn `workflow` cho C2 và B3 làm topic bonus; kết quả hidden vẫn đang chờ grader.

## 1. Thông tin nhóm

- Tên nhóm: HHTQ
- Thành viên: 4 người, chi tiết và bảng đóng góp trong `TEAM.md` (Đào Huy Hoàng — Shape A; Ngô Đức Thịnh — Shape B; Lê Hồng Quân — Shape C; Phan Trọng Hậu — baseline D + bonus B3).
- Commit chốt (trùng `report/team/decision_adr.md`): `77619d7` (nhánh `main`)

## 2. Mục tiêu và cách tiếp cận

Nhóm triển khai cùng một quy trình xử lý claim qua workflow (A), single ReAct agent (B), orchestrator (C) và swarm reference (D). Dùng cùng host để kiểm policy, approval, trần hoàn tiền theo order và idempotency. Shape D có sẵn làm baseline; nhóm chia A, B, C cho ba thành viên, Phan Trọng Hậu phụ trách baseline D cùng bonus B3.

Shape A (`workflow`, Đào Huy Hoàng), B (`single`, Ngô Đức Thịnh) và C (`orchestrator`, Lê Hồng Quân) đã qua 62/62 test student mỗi shape. Toàn bộ student suite: 248 passed. Benchmark 4 shape × 14 public claim × 5 seed đã được chạy lại trên implementation hiện tại.

## 3. Giải pháp

- **A — workflow:** chuỗi quyết định cố định trong `src/lab8/shapes/workflow.py`: đọc claim qua `get_claim_view` → thiếu `order_id` trả `needs_info` → đơn không thấy/khác principal trả `escalated` → quote từ `compute_compensation` trên order row (bỏ qua số ngày trong ticket) → quote 0 trả `denied` → quote > 0 truyền **quote đầy đủ** vào `durability.issue_refund` cùng `crash_at`; host là người duy nhất trừ tiền đã hoàn, kiểm approval và ghi ledger. MockLLM chỉ soạn chữ trả lời khách. Qua 62/62 test student.
- **B — single:** một vòng ReAct giới hạn 8 bước; quyết định nghiệp vụ và quote dùng order/compensation từ code. Model không tự quyết số tiền; host là nơi duy nhất ghi refund. Dùng các tool đọc order, refund history và compensation.
- **C — orchestrator:** orchestrator lập handoff allowlist, dùng investigator chỉ đọc, lấy quote từ dữ liệu có cấu trúc và để host ghi refund. Qua 62/62 test student.
- **D — swarm:** shape tham chiếu có sẵn; dùng làm baseline so sánh.
- **Bonus B3:** `swarm_verified` giữ baseline swarm, thêm verifier trước refund. Nếu delay trong candidate khác order có cấu trúc, quote được tính lại trên dữ liệu order. Code nằm trong `src/bonus/`, không đổi A–C.

Ba shape A/B/C đã qua ma trận student gồm các ca policy, trace, retry và crash. Trace của cả ba shape tuân theo contract v1: mọi nhánh return đều ghi trace; không ghi ticket, `parent_secret`, SĐT, địa chỉ hay ghi chú nội bộ. A, B và C đều có test riêng trong repo; B3 có test riêng kiểm tra secret và resume sau crash chỉ có một refund.

## 4. Kết quả

### Benchmark nhóm cuối (14 claim × 5 seed; nguồn `src/reports/benchmark.json`)

| Shape | Pass rate | Pass^5 | Seed min–max | Variance | Cost/success (VND mô phỏng) | Mean / p95 steps |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| workflow | 1.000 | 1.000 | 1.000–1.000 | 0.000000 | 28.78 | 3.79 / 4 |
| single | 1.000 | 1.000 | 1.000–1.000 | 0.000000 | 38.40 | 6.93 / 8 |
| orchestrator | 1.000 | 1.000 | 1.000–1.000 | 0.000000 | 36.82 | 3.43 / 4 |
| swarm | 0.986 | 0.929 | 0.929–1.000 | 0.000816 | 49.57 | 2.80 / 3 |

Cả ba shape nhóm viết đều đạt pass rate 1.000; workflow rẻ nhất (28.78) trong khi là kiến trúc ít tự chủ nhất — quyết định kiến trúc của nhóm: chọn **workflow** (chi tiết lập luận trong `decision_adr.md`). Swarm là shape duy nhất có variance khác 0 vì điểm yếu cố ý ở seed 55.

Cổng `python -m pytest -q`: **129 passed** (gồm cổng host + test nhóm thêm). Ma trận student: **248 passed** (62 test × 4 shape). Crash suite: **20/20** (`src/reports/crash.json`).

### Bonus B3 (nguồn `src/reports/bonus_*.json`, 5 seed 11, 22, 33, 44, 55)

| Bộ dữ liệu | Shape | Pass rate | Pass^5 | Seed min–max | Variance | Cost/success | Mean / p95 steps |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Public, 14 claim | swarm | 0.986 | 0.929 | 0.929–1.000 | 0.000816 | 49.57 | 2.80 / 3 |
| Public, 14 claim | swarm_verified | 1.000 | 1.000 | 1.000–1.000 | 0.000000 | 48.86 | 3.66 / 4 |
| Public, 14 claim | workflow | 1.000 | 1.000 | 1.000–1.000 | 0.000000 | 28.78 | 3.79 / 4 |
| Tự viết, 8 claim | swarm | 0.850 | 0.250 | 0.250–1.000 | 0.090000 | 63.39 | 3.18 / 4 |
| Tự viết, 8 claim | swarm_verified | 1.000 | 1.000 | 1.000–1.000 | 0.000000 | 53.88 | 4.18 / 5 |
| Tự viết, 8 claim | workflow | 1.000 | 1.000 | 1.000–1.000 | 0.000000 | 30.93 | 4.00 / 4 |

Nguồn: `src/reports/bonus_benchmark_public.json`, `src/reports/bonus_benchmark_adversarial.json` và `src/reports/bonus_analysis.json`. Test bonus: 22 passed. Verifier can thiệp 1/70 trial public, 7/40 trial đối kháng. Trên public T02 seed 55, swarm tin ticket báo trễ 5 ngày thay vì order 2 ngày; B3 đối chiếu order, quote 0 và từ chối. Benchmark B3 so sánh với Shape A chính thức.

Repo còn có code/report B1 (parallel orchestrator) do thành viên khác thêm, nhưng theo quyết định của nhóm trong ADR, **chỉ chọn B3** để được chấm bonus. B1 không phải topic bonus nộp.

### Kết quả nhóm còn thiếu

Đã chọn `workflow` trong `decision_adr.md` dựa trên benchmark public và đã điền `research_card.md` với ablation R1 (timing đo thật). `python -m lab8.check_submission` hiện cho **0 FAIL** (có WARN tạm thời khi còn thay đổi chưa commit). Chưa có `student_drop/` hoặc hidden grade, nên C2 và must-pass hidden chưa được xác nhận.

## 5. Khó khăn và cách xử lý

- Môi trường ban đầu chưa có pytest; tạo `src/.venv` và cài dependencies từ `src/requirements.txt`.
- Lệnh lọc test student có thể lấy cả tham số shape khác do tên test chứa từ `single`; dùng biểu thức lọc loại `workflow`, `orchestrator`, `swarm` để chỉ chạy B.
- Push bị từ chối non-fast-forward khi hai nhánh lịch sử tách nhau (một máy push Shape B/C từ clone cũ trong khi máy khác đã push Shape A); xử lý bằng `git pull --rebase`, giải xung đột `TEAM.md` (giữ dòng đóng góp của cả hai thành viên), không force-push.
- Swarm có sai khác chủ ý ở seed 55. B3 xử lý bằng kiểm chứng trên order có cấu trúc; benchmark trên case tự viết cũng cho thấy biến thiên theo seed của baseline.

## 6. Tổng hợp đóng góp

- **Đào Huy Hoàng** — Shape A (workflow): chuỗi quyết định 8 bước, truyền quote đầy đủ + `crash_at`, trace bảo mật; 62/62 test student; test riêng `test_workflow_extra.py`.
- **Ngô Đức Thịnh** — Shape B (single): vòng ReAct ≤ 8 bước; test riêng `test_single_extra.py` (3 test).
- **Lê Hồng Quân** — Shape C (orchestrator): handoff allowlist + investigator chỉ đọc; test riêng `test_orchestrator_shape.py` (7 test), `test_orchestrator_extra.py`, ablation R1 đo timing.
- **Phan Trọng Hậu** — baseline D, biến thể B3, tám case đối kháng, test và benchmark bonus.
- Chi tiết commit + test của từng người: bảng đóng góp trong `TEAM.md`; báo cáo cá nhân từng người trong `report/team/`. B1 là artifact không chọn để chấm.

## 7. Hạn chế và hướng cải thiện

MockLLM không phải model sản xuất và cost là giá mô phỏng; benchmark không đo latency. Bộ case B3 tự viết chỉ có tám claim nên không đại diện cho phân bố production. Chưa tự kiểm trên bộ hidden vì chưa nhận `student_drop/` — cần hidden pack để xác nhận C2 và must-pass (workflow phải đạt pass rate ≥ 0.75; ≥ 0.80 để giữ điều kiện nhận bonus B3). Nếu nghiệp vụ sau này yêu cầu điều tra đa bước (nhiều nguồn dữ liệu, ticket mơ hồ cần hỏi lại), orchestrator là ứng viên nâng cấp đầu tiên vì handoff giữ cổng ghi duy nhất ở host.

## 8. Tài liệu tham khảo

- `README.md`, `docs/business_rules.md`, `docs/contracts.md`, `docs/architecture.md`, `docs/metrics.md`.
- `docs/bonus_topics.md`, topic B3: verifier/aggregator chống khuếch đại lỗi.
- Google Research, 2026, *Towards a Science of Scaling Agent Systems* — nguồn của research card R1.
- Cemri et al., "Why Do Multi-Agent LLM Systems Fail?" (MAST), 2025, https://arxiv.org/abs/2503.13657 — tham chiếu phân loại lỗi cho phân tích swarm seed 55.
