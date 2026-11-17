# Bonus Lab09 — Port 3 grader sang Inspect AI

Phan Trọng Hậu · 2A202603547 · 17/11/2026.

## Điều kiện bonus và kết quả

RUBRIC yêu cầu port 3 grader sang Inspect AI hoặc DeepEval và so khớp kết quả, bonus +5 (tổng điểm tối đa 100). Đã port **ApprovalBypass, RefundAmountCorrect và SecretLeak** sang Inspect AI 0.3.290, so với pydantic-evals 2.68.0.

**Khớp 3372/3372 phép chấm, 0 sai khác**, trên 1124 snapshot: 1120 trial thực thi MockLLM và 4 ca biên tổng hợp. Mỗi grader đều có đủ kết quả 0 và 1. Đây là bằng chứng đáp ứng phần triển khai bonus; giảng viên quyết định điểm cộng, không tự cộng điểm chính thức.

| Grader | Số kết quả 1 | Số kết quả 0 | Khớp từng snapshot | Agreement |
|---|---|---|---|---|
| `approval_bypass` | 57 | 1067 | 1124/1124 | 100% |
| `refund_amount_correct` | 1021 | 103 | 1124/1124 | 100% |
| `secret_leak` | 141 | 983 | 1124/1124 | 100% |

## Thiết kế so sánh

- [Bản port Inspect](../inspect_graders.py) triển khai logic độc lập, không gọi hay chuyển tiếp sang evaluator pydantic-evals.
- [Runner](../bonus.py) thực sự chạy `pydantic_evals.Dataset` và `inspect_ai.eval(Task(...))`, không chỉ đối chiếu hai hàm tự viết ngoài framework.
- Cùng projection của snapshot (`snapshot`, `unexpected_rows`, `blob`) được chấm bởi cả hai harness. Đây là đầy đủ các trường 3 grader sử dụng. Trial tạo từ cùng world/label v2, 28 item × 5 seed × 8 shape = 1120.
- 8 shape gồm swarm, fixed, seeded_regression, honest_refactor, slice_regression, flaky_regression và 2 probe leaky_trace/sibling_refund đăng ký tạm trong bộ nhớ. Không sửa public variants, traps, Lab8, spec hoặc baseline.
- 4 ca biên tổng hợp có nhãn phân biệt `synthetic_boundary`, kiểm approval bị cấm nhưng tiền đã ghi, dòng ledger ngoài quyền, zero refund/forbid rỗng và leak không có chuyển tiền. Chúng không thêm vào eval set chính thức.
- Nhãn bonus lưu riêng trong [targets.json](../../reports/lab9/bonus/targets.json); [corpus.jsonl](../../reports/lab9/bonus/corpus.jsonl) không chứa label/expected_scores. Label được đưa vào expected_output/Target khi chấm, không đưa cho solver.
- Inspect dùng solver replay snapshot, không gọi generate/model. Native log ghi **0 model calls**, không cần API key.

## Quy ước chiều metric

`approval_bypass` và `secret_leak`: **1 là có vi phạm**, 0 là an toàn. `refund_amount_correct`: **1 là đúng**, 0 là sai. Inspect dùng numeric Score và `mean()` để giữ nguyên chiều; mean safety là tỷ lệ vi phạm, không phải accuracy. Khi so sánh, kiểm từng snapshot, không chỉ khớp trung bình.

Theo [tài liệu Inspect Custom Scorers](https://inspect.aisi.org.uk/custom-scorers.html), custom scorer nhận TaskState/Target và trả Score. Bản port đọc completion chứa snapshot và target chứa nhãn, trả Score 0/1 và explanation. Aggregate metric theo [Inspect metrics](https://inspect.aisi.org.uk/metrics.html).

## Bằng chứng và kiểm thử

- [Summary máy sinh](../../reports/lab9/bonus/summary.json): số mẫu, agreement, sai khác, coverage, phiên bản, commit nền và SHA-256 của code/corpus/targets.
- [So sánh từng snapshot](../../reports/lab9/bonus/comparison.json).
- [Native Inspect log](../../reports/lab9/bonus/inspect/2026-11-17T10-54-28-00-00_lab9-bonus-inspect_dtaFwxYikxGP8EJihyvbCk.eval). Có thể mở bằng `inspect view reports/lab9/bonus/inspect` sau khi activate môi trường bonus.
- [Test bonus](../../tests/test_lab9_bonus.py): chạy 2 harness trên ca có đáp án biết trước; từ chối ID trùng; cố tình đảo grader tham chiếu để xác nhận bộ so sánh phát hiện 3 sai khác.
- Full suite trong môi trường bonus: **409 passed**. Môi trường core không cài Inspect: **406 passed, 3 skipped**. Test optional được skip rõ ràng khi thiếu Inspect, không làm workflow Lab8 cần thêm dependency.

## Tái lập từ repo

```bash
cd src
python -m venv .venv
# Activate venv theo hệ điều hành
python -m pip install -r requirements.txt -r requirements-lab9-bonus.txt
python -m lab9.bonus
python -m pytest -q -o addopts= -k lab9_bonus
```

Lần chạy bằng Python 3.12.3; Inspect được pin trong requirements-lab9-bonus.txt. Runner trả exit 1 khi có mismatch, và báo lỗi nếu thiếu sample, grader crash, ID trùng hoặc không đủ coverage hai chiều. Mọi JSON/log sinh bằng script; không sửa report bằng tay.

## Giới hạn

Parity xác nhận bản port tương đương grader gốc trên corpus đã đo, không chứng minh cả hai đúng với mọi input. Có thể cùng kế thừa thiếu sót về contract; ca biên biết trước giảm rủi ro đó. Dữ liệu public/mock và probe không thay thế bộ chấm ẩn hoặc dữ liệu người dùng thật. Đây là port code grader, không dùng LLM để quyết định tiền/approval.
