# Báo cáo Lab09 — Evaluation and Failure Analysis

Phan Trọng Hậu · MSSV 2A202603547 · GitHub Phan-Trong-Hau · ngày 17/11/2026.

Repository: `K5-L3A-DAY09-2A202603547-PhanTrongHau-EvaluationandFailureAnalysis`.

## Mục tiêu và cách thực hiện

Xây dựng đánh giá có thể tái lập để phân biệt sửa lỗi, đổi cách diễn đạt hợp lệ và hồi quy; tìm bước sai đầu tiên từ trace, kiểm chất lượng judge trước khi dùng. Giữ nguyên implementation Lab8, bổ sung lớp Lab9. Không cần API key vì model/judge dùng mock và CSV replay.

## Hoàn thành theo milestone

| Mốc | Kết quả | Bằng chứng |
|---|---|---|
| M0 | Taxonomy 9 FM, có trace/đối chứng; FM09 ghi rõ tấn công bị chặn | [Taxonomy](../../../docs/failure_taxonomy.md) |
| M1 | v1 14 item, v2 28 item; nhãn tách, provenance và coverage hợp lệ | [v1](../../data/eval/eval_set_v1.jsonl), [v2](../../data/eval/eval_set_v2.jsonl) |
| M2 | Confusion, P/R, κ, Rogan–Gladen; 5 audit được người thực hiện xác nhận | [Judge audit](../../../docs/judge_audit.md) |
| M3 | Approval/ledger graders, FM08 reply-ledger, proposal diagnostic; detection 100%, FA 0% | [Grader](../../lab9/graders.py), [summary](../../reports/lab9/summary.json) |
| M4 | Paired percentile bootstrap theo item, fixed qua và seeded bị chặn | [Gate v1](../../reports/lab9/gate_seeded_regression_v1.log) |
| M5 | Map adversarial và 3 slice; fixed/honest qua, slice mutant bị chặn | [Spec v2](../../config/metric_spec_v2.yaml) |
| M6 | pass@k, pass^k; A/A và floor pass_hat_5=0.85 | [A/A](../../reports/lab9/aa_v2.json) |
| M7 | Integrity grid/NaN/grader/ratchet/slice, chặn 4 public trap | [Trap log](../../reports/lab9/traps.log) |

## Kết quả đo

Baseline v1 `E-swarm-20261117-266d`, SHA `266dd9056622`, pass_rate=0.9857, pass_5=0.9286; v2 `E-swarm-20261117-6b17`, SHA `6b17ce678794`.

| Biến thể v2 | pass_rate | pass^5 | Δ pass_rate, CI95% | Gate |
|---|---|---|---|---|
| swarm | 0.9786 | 0.8929 | +0.0000 [+0.0000, +0.0000] | baseline |
| fixed | 1.0 | 1.0 | +0.0214 [+0.0000, +0.0429] | merge |
| honest_refactor | 1.0 | 1.0 | +0.0214 [+0.0000, +0.0429] | merge |
| seeded_regression | 0.6429 | 0.6429 | -0.3357 [-0.5000, -0.1714] | block |
| slice_regression | 0.9357 | 0.8929 | -0.0429 [-0.1214, +0.0286] | block |
| flaky_regression | 0.9143 | 0.5714 | -0.0643 [-0.1143, -0.0143] | block |

A/A pass^5=0.8929 trên cả hai bộ seed; floor=0.85 có margin 0.0429. Slice regression có mean trên floor chung nhưng money_movement dưới floor; v1 bỏ lọt và v2 chặn. Flaky pass@5=1.0 nhưng pass^5=0.5714: có ít nhất một lần thành công khác với chạy ổn định mọi lần. Mutation score v2 3/3, false alarm 0/2. Detection các trial lỗi của seeded=100%; false alarm trên fixed=0% cho cả v1/v2.

## Kiểm chứng cuối cùng

- Toàn bộ repo: **406 passed** (`pytest -q -o addopts=`).
- Nhóm test student Lab09: **26 passed**; 3 test CLI evalset còn lại được kiểm trong bộ đầy đủ.
- `lab9.smoke`, kiểm eval set v1/v2, `ci_check` và gate fresh swarm: đạt.
- Bốn public integrity trap bị chặn; v2 mutation 3/3, false alarm 0/2.
- Dấu vân tay SHA-256 code/config/test/requirements: `997d6703659e792b70f3ddfd2fe725aa40f19c5c955bc8b1bd479a38b3b9b211`; danh sách hash từng file ở `summary.json`.

## Phân tích và quyết định

C-002@11: DB trễ 2 ngày, event 3 đổi thành 5 theo ticket, sinh khoản hoàn 20000 thay vì 0. Regression test chạy cả mutant và fixed. C-008@11: mutant misreport có ledger đúng 20000 và Lab8 pass, nhưng reply nói 35000; metric FM08 mới phát hiện được. Tiền/approval chấm code, tone chỉ đủ điều kiện theo calibration, helpful bị loại vì recall 0.3 và κ 0.375. [Chi tiết trace](../../../docs/trace_case.md).

## Tài liệu bàn giao

- [PRD v1.1](../../../docs/PRD_v1.1.md): ngưỡng, trách nhiệm, release gate, rủi ro và phiên bản.
- [Eval card](../../../docs/eval_card.md): baseline/variant, CI, A/A và giới hạn.
- [Evidence JSON](../../reports/lab9/summary.json): dữ liệu máy sinh; [log tái lập](../../reports/lab9/reproduce.log).
- [Kết quả kiểm tra](../../reports/lab9/tests.log), [smoke](../../reports/lab9/smoke.log).

## Tái lập

```bash
cd src
# Dùng Python trong venv đã cài requirements.txt và requirements-lab9.txt
python -m lab9.evalset --build --check
python -m lab9.evalset --v2 --build
python -m lab9.report
python -m pytest -q -m student -o addopts= -k lab9
```

`lab9.report` sinh baseline, các variant, A/A, calibration và trace; chạy trap và kiểm kỳ vọng gate. JSON không chỉnh tay. Các trap cố tình chứa dữ liệu không hợp lệ để kiểm gate, không dùng làm baseline. Judge helpful exit 1 và gate mutant exit 1 là kết quả mong đợi.

## Giới hạn và trách nhiệm

Phan Trọng Hậu phụ trách bài lab và xử lý gate đỏ; chưa có waiver/release được phê duyệt. Dữ liệu public nhỏ và MockLLM, không đo người dùng thật hoặc hidden. A/A cùng cấu trúc modulo không đại diện mọi nguồn nhiễu. Reply parser giới hạn VND dạng số, legacy không có reply event thì không áp dụng. FM09 mới quan sát phòng vệ thành công. Năm nhận xét tone được người thực hiện xác nhận trên dữ liệu có sẵn; chưa thay thế held-out mới. Code/grader và bằng chứng đã được commit/push tại `712959e`. Trường commit trong JSON ghi lại nền mã nguồn tại thời điểm chạy; dấu vân tay SHA-256 ở trên định danh nội dung code/config/test đã đánh giá. Báo cáo chính được đặt trong `src/lab9/report/`.

## Bổ sung checklist nộp chính thức

Sau khi đối chiếu 4 tài liệu trong lab9-starter, đã bổ sung section eval trong harness_map 1.2, report eval_fixed/eval_seeded_regression đúng tên, hành động sửa rubric tone, layer kiến trúc và giới hạn 5 seed. Xem [bảng rà soát](SubmissionAudit.md). Bằng chứng gate, mutation, A/A và trap được đưa vào PR starter/d09 → main; kết quả CI theo checks GitHub của PR.

## Đối chiếu trừ điểm / Bonus / Expert

[Biên bản kiểm tra](PenaltyExpertAudit.md): không phát hiện vi phạm 5 khoản trừ điểm; báo cáo runtime tái lập khớp. Bonus Inspect AI/DeepEval chưa thực hiện, chưa tính +5. Expert đã qua public suite và các chẩn đoán bổ sung; bộ chấm ẩn và điểm cuối do giảng viên xác nhận.
