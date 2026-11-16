# Báo cáo nhóm — Lab 8 LogiX-VN

**Bản tiến độ ngày 2026-11-16.** Ba shape bắt buộc đã hoàn thành và benchmark public đã chạy. Báo cáo còn thiếu quyết định kiến trúc cuối và kết quả hidden.

## 1. Thông tin nhóm

- Tên nhóm: chưa điền.
- Thành viên: xem `TEAM.md` (hiện bảng thành viên chưa được điền đầy đủ).
- Commit chốt (trùng `report/team/decision_adr.md`): chưa có.

## 2. Mục tiêu và cách tiếp cận

Nhóm triển khai cùng một quy trình xử lý claim qua workflow (A), single ReAct agent (B), orchestrator (C) và swarm reference (D). Dùng cùng host để kiểm policy, approval, trần hoàn tiền theo order và idempotency. Shape D có sẵn để làm baseline; nhóm chia A, B, C cho ba thành viên và Phan Trọng Hậu phụ trách baseline D cùng bonus B3.

Shape A (`workflow`, Đào Huy Hoàng), B (`single`, Ngô Đức Thịnh) và C (`orchestrator`, Lê Hồng Quân) đã qua 62/62 test student mỗi shape. Toàn bộ student suite: 248 passed. Benchmark 4 shape × 14 public claim × 5 seed cũng đã được chạy lại trên implementation hiện tại.

## 3. Giải pháp

- **A — workflow:** chuỗi quyết định Python cố định; lấy order qua allowlist, quote bằng compensation code và giao refund cho host. Qua 62/62 test student.
- **B — single:** một vòng ReAct giới hạn 8 bước; quyết định nghiệp vụ và quote dùng order/compensation từ code. Model không tự quyết số tiền; host là nơi duy nhất ghi refund. Dùng các tool đọc order, refund history và compensation.
- **C — orchestrator:** orchestrator lập handoff allowlist, dùng investigator chỉ đọc, lấy quote từ dữ liệu có cấu trúc và để host ghi refund. Qua 62/62 test student.
- **D — swarm:** shape tham chiếu có sẵn; dùng làm baseline so sánh.
- **Bonus B3:** `swarm_verified` giữ baseline swarm, thêm verifier trước refund. Nếu delay trong candidate khác order có cấu trúc, quote được tính lại trên dữ liệu order. Code nằm trong `src/bonus/`, không đổi A–C.

Ba shape A/B/C đã qua ma trận student gồm các ca policy, trace, retry và crash. B3 có test riêng kiểm tra secret và resume sau crash chỉ có một refund. Các commit B/C không thêm test mới; cần bổ sung test do thành viên phụ trách viết để đáp ứng checklist đóng góp cá nhân.

## 4. Kết quả

### Benchmark hiện tại

Benchmark cùng 14 claim × 5 seed; nguồn `src/reports/benchmark.json`. Chi phí là VND mô phỏng, latency không có trong MockLLM.

| Shape | Pass rate | Pass^5 | Seed min–max | Variance | Cost/success (VND mô phỏng) | Mean / p95 steps |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| workflow | 1.000 | 1.000 | 1.000–1.000 | 0.000000 | 28.78 | 3.79 / 4 |
| single | 1.000 | 1.000 | 1.000–1.000 | 0.000000 | 38.40 | 6.93 / 8 |
| orchestrator | 1.000 | 1.000 | 1.000–1.000 | 0.000000 | 36.82 | 3.43 / 4 |
| swarm | 0.986 | 0.929 | 0.929–1.000 | 0.000816 | 49.57 | 2.80 / 3 |

Mỗi shape A/B/C qua **62/62 test student**; toàn ma trận **248 passed**. Cổng `python -m pytest -q`: **78 passed, 248 deselected**. Crash suite: **20/20** (`src/reports/crash.json`). Smoke pass.

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

Nguồn: `src/reports/bonus_benchmark_public.json`, `src/reports/bonus_benchmark_adversarial.json` và `src/reports/bonus_analysis.json`. Test bonus: 22 passed. Verifier can thiệp 1/70 trial public, 7/40 trial đối kháng. Trên public T02 seed 55, swarm tin ticket báo trễ 5 ngày thay vì order 2 ngày; B3 đối chiếu order, quote 0 và từ chối. Workflow baseline trong B3 là module deterministic bonus-local theo hợp đồng Shape A; benchmark chính hiện đã có kết quả Shape A chính thức.

### Kết quả nhóm còn thiếu

Đã có benchmark public bốn shape, nhưng chưa có `student_drop/` để tự kiểm hidden. Chưa chọn shape chính; `decision_adr.md` và `research_card.md` còn trống. `python -m lab8.check_submission` xác nhận shapes, benchmark, crash report, contribution table và bonus report; hiện báo **8 FAIL** ở ADR và research card.

## 5. Khó khăn và cách xử lý

- Môi trường ban đầu chưa có pytest; tạo `src/.venv` và cài dependencies từ `src/requirements.txt`.
- Lệnh lọc test student có thể lấy cả tham số shape khác do tên test chứa từ `single`; dùng biểu thức lọc loại `workflow`, `orchestrator`, `swarm` để chỉ chạy B.
- Swarm có sai khác chủ ý ở seed 55. B3 xử lý bằng kiểm chứng trên order có cấu trúc; benchmark trên case tự viết cũng cho thấy biến thiên theo seed của baseline.

## 6. Tổng hợp đóng góp

Shape A do Đào Huy Hoàng, B do Ngô Đức Thịnh, C do Lê Hồng Quân phụ trách; D baseline và B3 do Phan Trọng Hậu phụ trách. B/C cần bổ sung test do thành viên phụ trách thêm hoặc sửa theo checklist đóng góp cá nhân.

## 7. Hạn chế và hướng cải thiện

MockLLM không phải model sản xuất và cost là giá mô phỏng; benchmark không đo latency. Bộ case B3 tự viết chỉ có tám claim nên không đại diện cho phân bố production. Cần nhận hidden pack, chọn shape chính dựa trên benchmark, điền ADR/research card và bổ sung test cho đóng góp B/C.

## 8. Tài liệu tham khảo

- `README.md`, `docs/business_rules.md`, `docs/contracts.md`, `docs/architecture.md`, `docs/metrics.md`.
- `docs/bonus_topics.md`, topic B3: verifier/aggregator chống khuếch đại lỗi.
