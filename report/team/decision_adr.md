# Decision record

Điền sau dấu `:` trên cùng dòng, không xóa nhãn. Grader và `python -m lab8.check_submission` đọc các dòng này bằng máy. Shape được chọn để chấm hidden là `workflow`.

- Shape chọn: workflow
- Commit hash: `CHOT_HASH` (commit bằng chứng benchmark/crash — ghi chính thức ở bước nộp cuối)
- Run id dẫn chứng: `R-workflow-C-001-s11`
- Pass rate / pass^5 / seed min-max / variance: public 14 claim × 5 seed = 1.000 / 1.000 / 1.000–1.000 / 0.000000; hidden chưa có grade
- Cost per success (mô phỏng, VND): 28.78 (public; so với 38.40 single, 36.82 orchestrator, 49.57 swarm)
- Crash safety: 20/20 (`src/reports/crash.json`)
- Secret leak / approval bypass: 0 / 0 phát hiện trên public suite; approval, trần theo đơn và idempotency do host (`durability.issue_refund`) kiểm, nhánh từ chối của host ghi audit `policy_denied`; hidden chưa có số liệu

## Vì sao shape này

So cùng corpus (14 claim public) và cùng seed (11, 22, 33, 44, 55), bốn kiến trúc đều đạt pass rate 1.000 trừ swarm (0.986, pass^5 0.929 vì điểm yếu ở seed 55 tin số ngày trong ticket thay vì order row). Khi chất lượng ngang nhau, tiêu chí quyết định là mức tự chủ thấp nhất mà vẫn làm được việc, đúng tinh thần đề bài. Workflow là kiến trúc ít tự chủ nhất: toàn bộ chuỗi quyết định là code cố định, MockLLM chỉ soạn chữ trả lời khách, không bao giờ chọn số tiền hay ghi ledger; host kiểm approval và ghi refund. Nó cũng rẻ nhất: cost/success 28.78 VND mô phỏng so với 36.82 (orchestrator), 38.40 (single) và 49.57 (swarm). Số liệu nguồn: `src/reports/benchmark.json` (4 shape × 14 claim × 5 seed). Đây là kết luận theo public benchmark; hidden grader mới xác nhận workflow có đạt cổng hidden không.

## Có đáng đổi lấy multi-agent không

Không đáng với corpus này. Single và orchestrator đạt cùng pass rate nhưng tốn thêm 28–33% chi phí mỗi lần thành công (38.40 và 36.82 so với 28.78) và nhiều bước hơn (6.93 và 3.43 so với 3.79). Swarm là kiến trúc duy nhất có variance khác 0 (0.000816) vì hành vi lệch thuộc seed, tức là thêm agent tự chủ chỉ thêm rủi ro dao động chứ không thêm chất lượng trên các claim tuần tự kiểu hoàn phí ship. Chỉ cân nhắc đổi nếu hidden cho thấy workflow dưới ngưỡng 0.75, hoặc nghiệp vụ sau này bắt buộc điều tra đa bước thật sự (nhiều nguồn dữ liệu phải tổng hợp, ticket mơ hồ cần hỏi lại người dùng) — khi đó orchestrator là ứng viên nâng cấp đầu tiên vì handoff cho investigator đọc rộng mà vẫn giữ cổng ghi duy nhất ở host. Nếu muốn nhận bonus B3, shape được chọn còn phải đạt hidden pass rate ít nhất 0.80.

## Trace và bằng chứng

Workflow trace ghi các event `claim_view` (claim đã qua `get_claim_view`, không có ticket), `order_view` (reason/order_id, không có order row thô), `quote` (số tiền, reason, clause_ids, parts), `decision` và `crash` khi có crash. Trace cố ý bỏ: ticket của khách (dữ liệu người dùng), `parent_secret` và `raw_headers` (CANARY_SECRET_*), SĐT/địa chỉ/ghi chú nội bộ/tên hàng. Scanner quét `trace_path` và mọi file `<run_id>*` cùng thư mục; nhóm không ghi gì ra stdout hay file ngoài vùng này. Bằng chứng public: `src/reports/benchmark.json`, `src/reports/crash.json`, 248 test student pass và 124 test cổng thường pass; các test tự viết (`test_workflow_extra.py`, `test_single_extra.py`, `test_orchestrator_extra.py`) kiểm trực tiếp trace không chứa CANARY_SECRET, header Bearer hay chữ trong ticket. Hidden secret-leak và approval-bypass counts đang chờ grader.

## Giới hạn

MockLLM không phải model sản xuất; chi phí là VND mô phỏng và latency là `unavailable`. Bộ benchmark public nhỏ hơn hidden 40 claim × 5 seed. Không có hidden pack trong workspace, nên chưa thể khẳng định C2 hoặc các must-pass hidden đã đạt.
