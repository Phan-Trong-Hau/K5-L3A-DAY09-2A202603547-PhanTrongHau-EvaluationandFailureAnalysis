# Rà soát yêu cầu nộp Lab09

Đối chiếu ngày 17/11/2026, commit `4ba95b5`. Tài liệu chuẩn đọc trực tiếp từ `/home/ryanphan/Workspaces/ai_action/labs/lab9-starter/`: README.md, SUBMISSION.md, RUBRIC.md, CHECKPOINTS.md. Đây là kết quả rà soát; không thay thế bộ chấm ẩn.

**Kết quả rà soát ban đầu:** kiểm tra kỹ thuật công khai đạt; checklist bàn giao/nộp bài còn thiếu.

## Đợt bổ sung sau rà soát

Các điểm local trong bảng bên dưới đã được xử lý trên nhánh `starter/d09`: harness_map version 1.2 có section eval; hai report đúng đường dẫn sinh lại bằng `lab9.eval`; audit có hành động sửa rubric; taxonomy dùng layer kiến trúc; eval card có giới hạn bug 1/3 với 5 seed và nhiễu LLM thật. Bảng giữ lại phát hiện ban đầu để đối chiếu.

Bài triển khai đã được push lên main trước đợt rà soát; PR lần này đưa các phần còn thiếu vào main, không viết lại lịch sử hoặc giả định code trước đó chưa ở main. Bằng chứng gate, mutation, A/A và bốn trap CLI được đính trong mô tả PR. Trạng thái CI được xác nhận bằng checks của PR; không dùng test local để thay thế kết quả GitHub.


## Các điểm cần bổ sung

| Mức | Phát hiện | Yêu cầu chuẩn và cách hoàn tất |
| --- | --- | --- |
| Bắt buộc | `src/harness_map.yaml` còn version 1.1 và chỉ có `sections.orchestration`, chưa có `sections.eval`. | SUBMISSION Core và RUBRIC M4 yêu cầu section eval. Ghép mẫu `src/harness_map.eval.yaml` dưới sections, tăng version 1.2; giữ section Lab8. |
| Bắt buộc | Chưa có `src/reports/eval_fixed.json`, `src/reports/eval_seeded_regression.json`. Dữ liệu tương đương đang ở `src/reports/lab9/fixed_v1.json`, `seeded_regression_v1.json`. | SUBMISSION yêu cầu đúng hai đường dẫn trên. Chạy `lab9.eval --shape fixed` và `--shape seeded_regression` để sinh đúng tên; không sửa JSON tay. |
| Bắt buộc | Audit có 5 bất đồng, kết luận ai đúng và giải thích, nhưng chưa ghi hành động sửa rubric. | RUBRIC M2 và CHECKPOINTS M2 yêu cầu “sửa rubric ra sao”. Bổ sung tiêu chí/rule rõ cho từng case hoặc nhóm lỗi; phân biệt đề xuất rubric mới với kết quả replay cũ. |
| Cần chỉnh | Cột Layer trong taxonomy dùng trajectory/step/outcome/reply, là mức đánh giá. | CHECKPOINTS M1 yêu cầu layer kiến trúc: model/prompt, tool/schema, retrieval, orchestration/state, guardrail/approval. Đổi hoặc thêm cột layer kiến trúc; có thể giữ mức đánh giá ở cột riêng. |
| Bắt buộc | Eval card có A/A, floor và giới hạn chung, nhưng thiếu câu giới hạn cụ thể về bug 1/3 seed với 5 seed. | SUBMISSION Advanced yêu cầu nêu rõ 5 seed không phát hiện ổn định lỗi kiểu này; giải thích A/A MockLLM Δ=0 không có nghĩa model thật không có nhiễu, không chỉnh floor chỉ để bắt mutant. |
| Bắt buộc trên GitHub | Repo hiện không có PR; `gh pr list --state all` trả `[]`. `gh run list --workflow eval-gate.yml` cũng trả `[]`. | SUBMISSION yêu cầu PR `starter/d09` → `main`, job eval-gate/eval-gate-v2 xanh và mô tả PR có seeded exit 1, mutation, A/A, bốn trap exit 1. Push thẳng main không kích hoạt workflow này. Các kết quả local chưa đáp ứng bằng chứng CI GitHub. Vì code đã vào main, cần xử lý PR bổ sung một cách minh bạch, không giả lập lịch sử nộp. |

## Phần đã kiểm tra lại và đạt

- Full suite: **406 passed** (15.87s).
- `lab9.smoke`: M0 PASS.
- Eval set v1 SHA `266dd9056622`, v2 SHA `6b17ce678794`: đều 0 problem.
- Taxonomy có hơn 5 failure mode quan sát được, liên kết trace/đối chứng; FM09 được ghi rõ là tấn công bị chặn.
- Nhãn v1/v2 tách riêng, baseline v1/v2 đã commit.
- Calibration và số liệu audit phù hợp: tone κ=0.757/P=0.857/R=0.8; helpful κ=0.375/R=0.3 bị loại.
- Detection **100%**, false alarm **0%** qua `lab9.mutation --detect` chạy lại.
- Gate Core: fixed exit 0; seeded exit 1, danh sách chặn có pass_rate. Δ pass_rate −0.271, CI [−0.500, −0.057] khớp CHECKPOINTS.
- Mutation v2: **3/3**, 0 false alarm; slice_regression bị chặn bởi slice:money_movement/pass_rate; flaky bị chặn bởi pass_hat_5.
- A/A chạy lại: tất cả metric Δ=0; pass_hat_5 floor=0.85, blocking, đáp ứng tối thiểu 0.8 trong rubric.
- Bốn trap đều chạy qua CLI gate riêng: exit 1, lý do integrity; trap loosened_spec truyền base-spec đúng yêu cầu.
- So với commit overlay `5d887c5`, không sửa `src/lab8/`, variants, variant_agent, traps hoặc adversarial pack.
- Năm template báo cáo chính vẫn nằm đúng `docs/` theo SUBMISSION. Báo cáo tổng hợp bổ sung nằm trong `src/lab9/report/` không làm thay đổi các đường dẫn bắt buộc.

## Chưa thể xác nhận

- Năm anchor so với key riêng của giảng viên: không có key công khai; không kết luận khớp 5/5.
- Variant/trap/vector ẩn: public suite không chứng minh đạt đủ điểm Advanced/Expert hoặc tổng 100 điểm.
- Không có CI run trên GitHub để xác nhận trạng thái xanh.
- Bonus đã bổ sung sau rà soát: [port 3 grader sang Inspect AI](BonusInspectAI.md), khớp 3372/3372 phép chấm; điểm cộng do giảng viên xác nhận.

Đợt bổ sung không sửa implementation Lab8, threshold, nhãn, variant hoặc trap. Hai report đúng tên sinh bằng CLI, không chỉnh JSON tay. Key anchor và bộ chấm ẩn vẫn thuộc phạm vi đánh giá của giảng viên.
