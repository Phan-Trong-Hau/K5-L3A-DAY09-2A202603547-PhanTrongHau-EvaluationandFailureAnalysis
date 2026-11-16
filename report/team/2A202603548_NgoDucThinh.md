# Báo cáo cá nhân — 2A202603548_NgoDucThinh

## 1. Thông tin thành viên

- Họ tên: Ngô Đức Thịnh
- MSSV: `2A202603548`
- Email: 
- GitHub: [`NgooThinh05`](https://github.com/NgooThinh05)
- Vai trò trong nhóm: Phụ trách **Shape B — Single ReAct Agent** (`src/lab8/shapes/single.py`) và kiểm thử Shape B.

## 2. Phần việc phụ trách

- Thiết kế và hiện thực hóa kiến trúc **Shape B (`single`)** trong `src/lab8/shapes/single.py` theo chữ ký chuẩn `run_claim(claim_id, *, seed, store_path, crash_at=None) -> RunResult`.
- Đảm bảo Shape B tuân thủ đầy đủ [docs/business_rules.md](../../docs/business_rules.md), [docs/contracts.md](../../docs/contracts.md) (Output contract & Trace contract v1), cùng 3 điều kiện *must-pass* (không bypass approval, không lộ `CANARY_SECRET_*` / PII trong trace, an toàn khi retry/crash).
- Chạy kiểm thử cổng host (`python -m pytest -q`) và bộ 62 test ma trận student (`T01`–`T14` trên 5 seed `11, 22, 33, 44, 55`) cho Shape B.

## 3. Đóng góp cụ thể

- **Commit chính:** `a517bc7` (`Shape B single`) — cài đặt hoàn chỉnh `src/lab8/shapes/single.py`.
- **Kiểm thử:** Thêm mới bộ unit test riêng [`src/tests/test_single_shape.py`](../../src/tests/test_single_shape.py) (5 test) và chạy xác nhận pass toàn bộ 62 test của `single` trong `src/tests/test_public_matrix.py` (`test_public_single_run_cases`, `test_t11_retry_keeps_one_refund[single]`, `test_t12_crash_before_checkpoint_does_not_double_pay[single]`) cùng cổng host.
- **Các quyết định kỹ thuật chính:**
  1. **Giới hạn quyền của ReAct loop (`worker=True`, `max_steps=8`):** Dùng `lab8.runtime.run_react` với `worker=True` để ép mọi tool gọi trong vòng lặp `decide` chỉ nằm trong `READONLY_TOOLS` (`lookup_order`, `lookup_refund_history`, `compute_compensation`), tuyệt đối không cho model gọi `issue_refund`.
  2. **Ranh giới Code vs. Model (chống prompt injection & sai lệch dữ liệu ticket):** Chỉ dùng `MockLLM` (`complete`) để ghi nhận bước suy luận/soạn phản hồi và tính đúng `Budget`; mọi dữ kiện tính tiền (`delay_days`, `shipping_fee_vnd`, `paid_vnd`, `damage_verified`) đều lấy từ dòng `order` trong DB qua `lookup_order` và tính bằng `compute_compensation`, bỏ qua số ngày trễ hoặc điều khoản cũ (`SHIP-LATE-OLD`) do khách viết trong ticket.
  3. **Xử lý trần hoàn tiền theo đơn (Per-order cap — T13, T14):** Gọi `lookup_refund_history` để quan sát lịch sử hoàn tiền của đơn nhưng luôn truyền **quote đầy đủ** (`proposal_amount`) vào `durability.issue_refund` để host tự trừ phần đã hoàn của các claim trước trong cùng transaction, tránh lỗi trừ hai lần ở T14 và đảm bảo host ghi đúng audit `policy_denied` ở T13.
  4. **Độ bền (Durability, Idempotency & Crash propagation — T11, T12):** Truyền `crash_at` trực tiếp vào `durability.issue_refund`; khi gặp `InjectedCrash`, ghi sự kiện `crash` và flush file trace trước khi re-raise exception (không nuốt `InjectedCrash`).
  5. **Bảo mật Trace (Trace contract v1):** Đọc claim qua `get_claim_view` (loại bỏ `parent_secret` và `raw_headers`), chỉ ghi dữ liệu đã qua allowlist (`safe_dump`) vào `lab8.trace.Trace`, và trả kết quả qua `lab8.shapes.common.finish()` trên mọi nhánh thoát (`unknown_claim`, `needs_info`, `escalated`, `denied`, `failed`, `resolved`).

## 4. Bằng chứng

- **Commit:** `a517bc7` trên repo nhóm [`K5-L3A-DAY08-HHTQ-FromWorkflowsToAgents`](https://github.com/hoang2k3ai/K5-L3A-DAY08-HHTQ-FromWorkflowsToAgents).
- **File code & test:** [`src/lab8/shapes/single.py`](../../src/lab8/shapes/single.py), [`src/tests/test_single_shape.py`](../../src/tests/test_single_shape.py) (5 test: `test_single_ignores_ticket_delay_even_on_seed_55`, `test_single_trace_omits_secrets_pii_and_ticket_text`, `test_single_passes_full_quote_for_per_order_cap`, `test_single_propagates_crash_and_resumes_once`, `test_single_unknown_claim_fails_cleanly_with_trace`).
- **Kết quả chạy test thực tế (chạy trong `src/`):**
  - `python -m pytest -q tests/test_single_shape.py` → `5 passed`.
  - `python -m pytest -q` → passed (toàn bộ cổng host + test nhóm).
  - `python -m pytest -q -m student -o addopts= -k "single]"` → `62 passed, 240 deselected`.
- **Run ID tiêu biểu:** `R-single-C-001-s11`, `R-single-C-002-s55` (pass đúng `denied`, không mắc lỗi tin ticket như `swarm`), `R-single-C-011-s11`, `R-single-C-012-s11`, `R-single-C-013-s11`, `R-single-C-014-s11`.

## 5. Công cụ AI đã dùng

- **Công cụ:** Antigravity (Gemini).
- **Mục đích sử dụng:** Hỗ trợ đọc nhanh cấu trúc repo, đối chiếu yêu cầu trong `docs/business_rules.md` và `docs/contracts.md`, gợi ý khung cài đặt hàm `_run` / `decide` cho `src/lab8/shapes/single.py` và rà soát các điều kiện must-pass.
- **Cách tự kiểm tra kết quả (theo [RULES.md](../../RULES.md)):**
  - Tự đọc và kiểm tra lại từng nhánh logic trong `src/lab8/shapes/single.py` (đặc biệt là cách truyền `proposal` đầy đủ vào `issue_refund` và xử lý `InjectedCrash`).
  - Chạy trực tiếp bộ test `python -m pytest -q` và `python -m pytest -q -m student -o addopts= -k "single]"` trên terminal để xác nhận 62/62 test của Shape B đều xanh.
  - Kiểm tra nội dung file trace sinh ra trong `src/traces/R-single-*.json` (và qua `trial_pass` / `check_trace`) để đảm bảo đúng `Trace contract v1` và không rò rỉ `CANARY_SECRET_*` hay thông tin cá nhân (SĐT, địa chỉ, ghi chú nội bộ, tên hàng).

## 6. Tự đánh giá

- Hoàn thành 100% nhiệm vụ phụ trách đúng hạn (CP2–CP4 cho Shape B `single`, đạt 62/62 test student và giữ xanh 54/54 test cổng host).
- Hiểu rõ sự khác biệt giữa Shape A (`workflow`), Shape B (`single` ReAct), Shape C (`orchestrator`) và Shape D (`swarm`), cũng như lý do mọi quyết định về tiền, approval, per-order cap và idempotency phải đặt ở tầng code/host thay vì phó mặc cho LLM.
