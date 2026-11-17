# Kiểm tra khoản trừ điểm, Bonus và Expert

Đối chiếu RUBRIC Lab09 ngày 17/11/2026. Mốc đóng băng Lab08: commit overlay `5d887c5`; mã được kiểm: `a09bdcb`.

| Khoản | Kết quả kiểm tra |
|---|---|
| Sửa lab8/ (−10) | Không có diff trong src/lab8 từ mốc overlay đến mã đã merge. Các thay đổi làm bài Lab08 trước overlay không bị xem là sửa trong Lab09. |
| Sửa tay reports/ (−20) | Không thấy dấu hiệu làm đẹp số liệu: chạy lại swarm và 5 variant trên cả v1/v2, toàn bộ rows/metrics/evaluator_failures khớp report đã lưu. Hai report đúng tên cũng khớp report variant v1 tương ứng. Report runtime được sinh bằng CLI/report.py; trap cố tình sai được sinh bằng traps.py theo đề. Kiểm tra này xác nhận tính tái lập của kết quả, không phải chứng minh mọi thao tác lịch sử. |
| Nới ngưỡng cùng version (−10) | Đối chiếu các chuyển tiếp spec đã commit trên lịch sử main từ overlay: không có ratchet violation. Refund floor v1=0.95 và v2=0.90 là hai eval-set version khác nhau, đúng với contract starter v2; không phải hạ sàn trên cùng version. |
| Nhãn inline (−5) | Không có label/labels/expected/expected_output trong các item v1/v2. Nhãn để ở labels_v1.json và labels_v2.json. |
| Sửa variant/trap/bộ chấm để qua (−15) | Không có diff của variants.py, variant_agent.py, traps.py, ci_check.py, adversarial_v2.json hoặc các file test Lab09 công khai có sẵn. Chỉ hoàn thiện grader/gate theo bài tập và thêm test regression riêng. |

Kết luận: **không phát hiện căn cứ áp dụng 5 khoản trừ điểm trong phạm vi kiểm tra này**. Quyết định chấm điểm thuộc giảng viên.

## Bonus +5

**Chưa thực hiện.** Chưa có port 3 grader sang Inspect AI/DeepEval hoặc bằng chứng so khớp kết quả giữa hai harness. pydantic-evals là harness bắt buộc của bài, không tính là bonus. Không tự cộng 5 điểm.

## Expert M7

Đã triển khai integrity và ratchet; 4 trap công khai bị chặn, mutation 3/3 và không báo nhầm. Baseline so với chính nó merge; A/A Δ=0; pass_hat_5 floor=0.85 (≥0.8), blocking. Flaky_regression bị chặn (pass_hat_5=0.5714). Các bằng chứng public và CI có trong PR #1 đã merge.

Kiểm tra bổ sung lần này chạy trong bộ nhớ, không sửa report/variant/trap đã nộp: duplicate row, evaluator_failures trên report xanh, None grader và đổi slice đều bị integrity chặn. Biến thể chẩn đoán quiet_override không ghi model_override vẫn bị gate chặn bởi outcome/slice. Đây là chẩn đoán tự bổ sung, **không phải** bộ chấm ẩn của giảng viên; không bảo đảm 15/15 Expert.

```text
config/metric_spec.yaml: no loosened thresholds in published same-version transitions
config/metric_spec_v2.yaml: no loosened thresholds in published same-version transitions
reproduce v1/swarm: rows/metrics/evaluator_failures MATCH
reproduce v1/fixed: rows/metrics/evaluator_failures MATCH
reproduce v1/seeded_regression: rows/metrics/evaluator_failures MATCH
reproduce v1/honest_refactor: rows/metrics/evaluator_failures MATCH
reproduce v1/slice_regression: rows/metrics/evaluator_failures MATCH
reproduce v1/flaky_regression: rows/metrics/evaluator_failures MATCH
v1: no inline labels in 14 items
reproduce v2/swarm: rows/metrics/evaluator_failures MATCH
reproduce v2/fixed: rows/metrics/evaluator_failures MATCH
reproduce v2/seeded_regression: rows/metrics/evaluator_failures MATCH
reproduce v2/honest_refactor: rows/metrics/evaluator_failures MATCH
reproduce v2/slice_regression: rows/metrics/evaluator_failures MATCH
reproduce v2/flaky_regression: rows/metrics/evaluator_failures MATCH
v2: no inline labels in 28 items
Expert baseline self-comparison: MERGE
Expert supplemental diagnostic duplicate_row: BLOCK integrity
Expert supplemental diagnostic evaluator_failure_on_green: BLOCK integrity
Expert supplemental diagnostic none_grader: BLOCK integrity
Expert supplemental diagnostic relabeled_slice: BLOCK integrity
Expert supplemental quiet_override: BLOCK refund_amount_correct, slice:denial/pass_rate, slice:adversarial/pass_rate; no override events detected
```
