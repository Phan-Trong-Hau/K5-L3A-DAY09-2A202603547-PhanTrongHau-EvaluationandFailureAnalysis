# Decision record

Điền sau dấu `:` trên cùng dòng, không xóa nhãn. Grader và `python -m lab8.check_submission` đọc các dòng này bằng máy. Shape được chọn để chấm hidden là `workflow`.

- Shape chọn: workflow
- Commit hash: `ffb85f9` (commit benchmark public)
- Run id dẫn chứng: `R-workflow-C-001-s11`
- Pass rate / pass^5 / seed min-max / variance: public 14 claim × 5 seed = 1.000 / 1.000 / 1.000–1.000 / 0.000000; hidden chưa có grade
- Cost per success (mô phỏng, VND): 28.78 (public)
- Crash safety: 20/20 (`src/reports/crash.json`)
- Secret leak / approval bypass: 0 / 0 phát hiện trên public suite; hidden chưa có số liệu

## Vì sao shape này

Chọn workflow vì benchmark public cho thấy pass rate 1.000 và pass^5 1.000, bằng single và orchestrator, nhưng cost/success thấp hơn: 28.78 VND so với 38.40 và 36.82. Workflow cũng là kiến trúc ít tự chủ nhất: các bước và quote do code quyết định, host kiểm approval và ghi ledger. Đây là kết luận tạm theo public 14 claim × 5 seed; hidden grader mới xác nhận workflow có đạt cổng C2 hay không.

## Có đáng đổi lấy multi-agent không

Trên public benchmark hiện tại, chưa có lợi ích về pass rate để bù chi phí cao hơn của single/orchestrator; swarm có pass rate và pass^5 thấp hơn. Chỉ cân nhắc đổi nếu hidden cho thấy workflow dưới ngưỡng 0.75 hoặc một shape khác cải thiện đáng kể pass rate mà vẫn qua đủ must-pass. Nếu muốn nhận bonus B3, shape được chọn còn phải đạt hidden pass rate ít nhất 0.80.

## Trace và bằng chứng

Workflow trace ghi các event `claim_view`, `order_view`, `quote`, `decision` và `crash` khi có crash. Trace bỏ ticket, raw claim/order row, parent secret, header, SĐT, địa chỉ, tên hàng và ghi chú nội bộ. Bằng chứng public gồm `src/reports/benchmark.json`, `src/reports/crash.json`, 248 test student pass và 118 test trong cổng thường pass. Hidden secret-leak và approval-bypass counts đang chờ grader.

## Giới hạn

MockLLM không phải model sản xuất; chi phí là VND mô phỏng và latency là `unavailable`. Bộ benchmark public nhỏ hơn hidden 40 claim × 5 seed. Không có hidden pack trong workspace, nên chưa thể khẳng định C2 hoặc các must-pass hidden đã đạt.
