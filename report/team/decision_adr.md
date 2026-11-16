# Decision record

Điền sau dấu `:` trên cùng dòng, không xóa nhãn. Giảng viên và `python -m lab8.check_submission` (chạy trong `src/`) đọc các dòng này bằng máy. Không đổi tên hay dời file này khỏi `report/team/`.
`Shape chọn` phải là đúng một trong: `workflow`, `single`, `orchestrator`, `swarm`. Đây là shape được chấm cổng hidden.

- Shape chọn: orchestrator
- Commit hash: 0424133
- Run id dẫn chứng: R-orchestrator-C-014-s11 (file trace trong `src/traces/`)
- Pass rate / pass^5 / seed min-max / variance: 1.000 / 1.000 / 1.000–1.000 / 0.000000 (14 claim × 5 seed = 70 trial, `src/reports/benchmark.json`)
- Cost per success (mô phỏng, VND): 36.82
- Crash safety: 20/20 (src/reports/crash.json)
- Secret leak / approval bypass: 0 / 0 (quét 140 trace `R-orchestrator*`: không có `CANARY_SECRET`; 70/70 trial pass, gồm các claim thiếu hoặc hết hạn approval C-004, C-005, C-007)

Ví dụ một dòng đã điền: `- Shape chọn: workflow`, `- Crash safety: 20/20 (src/reports/crash.json)`.

## Vì sao shape này

So trên cùng 14 claim × 5 seed, cùng MockLLM, cùng giá, cùng evaluator (`src/reports/benchmark.json`):

| Shape | Pass | pass^5 | Variance | Cost/success (VND, mô phỏng) | Bước trung bình |
| --- | --- | --- | --- | --- | --- |
| workflow | 1.000 | 1.000 | 0 | 28.78 | 3.79 |
| single | 1.000 | 1.000 | 0 | 38.40 | 6.93 |
| orchestrator | 1.000 | 1.000 | 0 | 36.82 | 3.43 |
| swarm | 0.986 | 0.929 | 0.000816 | 49.57 | 2.80 |

Ba shape không phải swarm đều đạt 70/70 trial, nên pass rate không phân biệt được chúng trên bộ public. Chọn orchestrator vì ba lý do:
1. Quote lấy từ `compute_compensation` trên dòng order, không đọc ticket. Vì vậy không mắc lỗi `REFERENCE_WEAKNESS` của swarm (C-002 seed 55), lỗi kiểu này dễ bị bộ hidden bắt.
2. Investigator chỉ có tool đọc, host là nơi duy nhất ghi tiền qua `issue_refund`. Ranh giới này được test trực tiếp.
3. Nhóm đã đo bản song song của orchestrator cho bonus B1. Chọn shape này để số bonus đo đúng shape được chấm.

Workflow rẻ hơn (28.78 so với 36.82 VND mỗi lần thành công), cùng pass và variance. Đây là lựa chọn thay thế hợp lý nếu nhóm ưu tiên chi phí. Quyết định chọn orchestrator là có chủ đích, và cần nhóm xác nhận lại.

## Có đáng đổi lấy multi-agent không

Swarm (multi-agent) không đáng: pass thấp hơn (0.986), cost cao nhất (49.57), và có lỗi ở seed 55. Single là một agent nhưng dùng nhiều bước hơn (6.93) và tốn hơn orchestrator (38.40 so với 36.82) mà không tăng pass. Orchestrator có investigator là tool đọc, nên không phải multi-agent thật, mà là một orchestrator gọi tool đọc.

Điều kiện làm quyết định đảo lại: nếu bộ hidden cho thấy single vượt orchestrator về pass (ví dụ các claim cần suy luận trên ticket), hoặc nếu chi phí là tiêu chí chính, workflow thay thế được orchestrator vì rẻ hơn với cùng pass trên public.

## Trace và bằng chứng

Trace của orchestrator ghi các event: `handoff` (đã qua allowlist `handoff.v1`), `investigator` (chỉ ghi `visible`, `reason` và tên tool), `quote` (số tiền, lý do, `clause_ids`, `parts`), `write` (ok, reason), và `decision` khi dừng sớm. Với bản song song, còn có `timing` (số đo thời gian thật).

Các field cố ý **không** ghi:
- Ticket của khách, vì có thể chứa thông tin cá nhân hoặc nội dung do người dùng nhập.
- `parent_secret`, `raw_headers`, và `Authorization`, vì là secret của ranh giới.
- Dòng claim đầy đủ và dòng order đầy đủ. Investigator chỉ ghi `visible` và `reason`, không ghi số điện thoại, địa chỉ, ghi chú nội bộ hay tên hàng.
- Approval id và các dữ liệu nội bộ khác của ledger, vì chỉ cần kết quả ghi, không cần chi tiết.

Scanner của grader quét `trace_path` và mọi file `<run_id>*` cùng thư mục. Nhóm kiểm tra bằng cách quét toàn bộ 140 trace `R-orchestrator*` và không thấy `CANARY_SECRET`. Nếu có file ghi ngoài chỗ scanner quét, nhóm không ghi ra file đó: trace là file duy nhất có dữ liệu debug.

## Giới hạn

MockLLM không phải model sản xuất. Latency để `unavailable` trong benchmark. Chi phí VND là mô phỏng theo `config/pricing.yaml`, không phải hóa đơn API. Pass rate 1.000 trên 14 claim public chưa chứng minh được trên bộ hidden 40 claim × 5 seed; phải chờ giảng viên chấm. Không sửa JSON cho đủ 0.75.
