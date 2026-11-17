# Eval card — Lab09

Phan Trọng Hậu · MSSV 2A202603547 · GitHub Phan-Trong-Hau · ngày 17/11/2026.

- Baseline v1: `E-swarm-20261117-266d`, SHA `266dd9056622`, 14 item × 5 seed.
- Baseline v2: `E-swarm-20261117-6b17`, SHA `6b17ce678794`, 28 item × 5 seed (14 public + 14 adversarial).
- Spec: 1.0/v1 và 2.0/v2. Seed chính: 11,22,33,44,55; A/A: 66,77,88,99,110. MockLLM, Python 3.12.3.
- Code/grader: đã commit/push trong `712959e`. JSON lưu commit nền tại thời điểm chạy và hash nội dung code/config/test để đối chiếu. [Dữ liệu tổng hợp](../src/reports/lab9/summary.json), [lệnh tái lập](../src/lab9/report.py).

## Baseline và PR mô phỏng

| Shape v2 | pass_rate | pass^5 | Δ pass_rate, CI95% | Gate |
|---|---|---|---|---|
| swarm | 0.9786 | 0.8929 | +0.0000 [+0.0000, +0.0000] | baseline |
| fixed | 1.0 | 1.0 | +0.0214 [+0.0000, +0.0429] | merge |
| honest_refactor | 1.0 | 1.0 | +0.0214 [+0.0000, +0.0429] | merge |
| seeded_regression | 0.6429 | 0.6429 | -0.3357 [-0.5000, -0.1714] | block |
| slice_regression | 0.9357 | 0.8929 | -0.0429 [-0.1214, +0.0286] | block |
| flaky_regression | 0.9143 | 0.5714 | -0.0643 [-0.1143, -0.0143] | block |

Cả 3 mutant v2 bị chặn; fixed và honest_refactor được qua. v1 bỏ lọt slice_regression, minh họa lý do thêm slice thay vì dựa duy nhất mean chung. “PR” trong bảng là variant chạy cục bộ, chưa phải PR GitHub.

[Spec v1](../src/config/metric_spec.yaml), [spec v2](../src/config/metric_spec_v2.yaml) quy định ngưỡng. An toàn đếm số vi phạm, max=0; không lấy trung bình để che lỗi. Refund floor v1=0.95, v2=0.90; pass_rate≥0.85; reply-ledger=1.0; v2 thêm pass^5≥0.85 và slices. Các CI lấy mẫu theo item, không coi 140 trial là 140 quan sát độc lập.

## A/A và độ tin cậy

Baseline v2 pass@1=0.9786, pass@3=1.0, pass@5=1.0; pass^1=0.9786, pass^3=0.9357, pass^5=0.8929. Một lần thử thành công không đồng nghĩa mọi lần đều thành công. Flaky giảm pass^5 xuống 0.5714 dù pass_rate vẫn 0.9143.

A/A hai bộ seed có cùng metric; pass^5=0.8929, Δ=0. Chọn floor 0.85, thấp hơn mức quan sát 0.0429. Đây là margin thực nghiệm trên hai bộ có cấu trúc tương tự, chưa phải ước lượng noise band production. [A/A v2](../src/reports/lab9/aa_v2.json).

## Calibration, trace và owner

Tone κ=0.757, P=0.857, R=0.8: đạt. Helpful κ=0.375, R=0.3: loại. [Audit 5 case](judge_audit.md). [Trace case](trace_case.md): event 3 ghi đè DB là bước sai đầu tiên; có regression chạy được.

Grader detection v1/v2 đều 100%, false alarm 0% trên fixed. [Bốn bẫy integrity](../src/reports/lab9/traps.log) đều bị chặn. Owner: Phan Trọng Hậu; phạm vi pilot và quy trình release ở [PRD](PRD_v1.1.md).

Giới hạn: chỉ public/mock, không hidden/production; judge chưa có held-out mới; legacy swarm không có reply event nên score reply=1.0 là không áp dụng. Tăng version khi đổi dữ liệu/nhãn, giữ baseline cùng SHA trước khi gate. Không suy luận điểm chính thức từ public suite.

## Giới hạn cỡ mẫu và nhiễu (M6)

Với 5 seed, lỗi có xác suất xuất hiện 1/3 mỗi lần **không được phát hiện ổn định**. Nếu các lần độc lập, xác suất cả 5 lần đều bỏ lỡ lỗi là (2/3)^5 ≈ 13.2%; khả năng kết luận giảm có ý nghĩa còn phụ thuộc số item và tương quan giữa chúng. Đây là minh họa xác suất, không phải kết quả đo của MockLLM. Không hạ ngưỡng chỉ để bắt một variant; cần tăng số seed, thêm item đại diện và đo lại A/A trước khi đổi contract.

A/A MockLLM Δ=0 vì chạy xác định và hai bộ seed có cấu trúc tương tự. LLM thật có biến thiên lấy mẫu và môi trường/tool nên dải nhiễu có thể >0; cần đo nhiều lần và chọn sàn ngoài dải nhiễu của agent không đổi. Floor pass_hat_5=0.85 hiện chỉ được biện minh trong phạm vi thử nghiệm công khai này.
