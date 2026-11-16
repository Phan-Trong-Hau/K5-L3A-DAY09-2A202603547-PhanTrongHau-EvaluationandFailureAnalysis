# Báo cáo cá nhân — 2A202603451_DaoHuyHoang

## 1. Thông tin thành viên

- Họ tên: Dao Huy Hoang
- MSSV: 2A202603451
- Email: 26ai.hoangdh@vinuni.edu.vn
- GitHub: https://github.com/hoang2k3ai

## 2. Phần việc phụ trách

**Shape A — `workflow`** (kiến trúc ít tự chủ nhất trong bốn shape): cài đặt hoàn chỉnh
quy trình xử lý claim bằng các bước Python cố định trong `src/lab8/shapes/workflow.py`,
giữ nguyên chữ ký `run_claim(claim_id, *, seed, store_path, crash_at=None) -> RunResult`.

## 3. Đóng góp cụ thể

### Commit chính

- `26c4fde` — `feat(workflow): implement shape A decision ladder`

### Quyết định kỹ thuật tôi đưa ra

1. **Chuỗi quyết định cố định 8 bước** theo đúng docstring đề bài: đọc claim qua
   `get_claim_view` → thiếu `order_id` trả `needs_info` → `lookup_order` không thấy /
   khác principal trả `escalated` → quote từ `compute_compensation` (bỏ qua số ngày trễ
   viết trong ticket) → quote 0 trả `denied` (không gọi `issue_refund`) → quote > 0
   chuyển cho host.
2. **Truyền quote đầy đủ** vào `durability.issue_refund`, không tự trừ phần các claim
   trước đã nhận trên cùng đơn (T13, T14) — host là người trừ, tự trừ sẽ bị trừ hai lần.
3. **Không tự từ chối khi approval hỏng:** để host từ chối để có audit `policy_denied`
   (T07, T13); shape tự chối thì không có audit nên fail.
4. **TODO CP3:** truyền `crash_at` vào `issue_refund` và **không** bắt `InjectedCrash`
   để crash thật sự xảy ra (T12); trace được ghi trước khi ném lại exception.
5. **Một điểm thoát duy nhất `_finish()`:** mọi nhánh return (kể cả `needs_info`,
   `escalated`, `failed`) đều qua `lab8.shapes.common.finish()` để `refund_effects`,
   `committed_audit_count` và trace luôn nhất quán với ledger.
6. **Ranh giới bảo mật trong trace:** không ghi ticket, claim row thô (chứa
   `parent_secret`), order row thô (SĐT, địa chỉ, ghi chú nội bộ); chỉ ghi các field
   đã qua allowlist, copy payload bằng `safe_dump`.
7. **Ranh giới code / model:** tiền do `compute_compensation` (code) tính, refund do
   `issue_refund` (host) ghi; MockLLM chỉ được gọi `purpose="draft"` để soạn chữ trả
   lời khách, không quyết số tiền.

### Test đã thêm hoặc sửa

- File mới: `src/tests/test_workflow_extra.py` (commit theo), 2 test:
  - `test_workflow_quotes_from_order_row_not_ticket` — C-002 ticket khai trễ 5 ngày
    nhưng order row ghi 2 ngày → shape phải quote theo **order row** (denied, 0 VND),
    không giống điểm yếu có chủ ý của swarm trả 20000 VND.
  - `test_workflow_trace_has_no_ticket_or_secret` — trace phải đúng contract v1
    (run_id khớp, có `events`) và **không** chứa `CANARY_SECRET_PARENT_*`, header
    `Bearer`, hay chữ trong ticket.

### Kết quả kiểm chứng

- `python -m pytest -q -m student -o addopts= -k workflow` → **62 passed** (T01–T14 × 5 seed: 11, 22, 33, 44, 55)
- `python -m pytest -q tests/test_workflow_extra.py` → **2 passed** (2 test tự thêm)
- `python -m pytest -q` (cổng host) → **56 passed** (54 phần chung + 2 test tự thêm)

## 4. Bằng chứng

- File: `src/lab8/shapes/workflow.py` (shape A) và `src/tests/test_workflow_extra.py` (test riêng)
- Link commit: https://github.com/hoang2k3ai/K5-L3A-DAY08-HHTQ-FromWorkflowsToAgents/commit/26c4fde
  *(commit `26c4fde` trên nhánh `main`; link hoạt động đầy đủ sau khi `git push`)*
- Lệnh chạy và output ghi ở mục 3 trên.
- Run id của shape: `R-workflow-<claim_id>-s<seed>` (ví dụ `R-workflow-C-001-s11`).

## 5. Công cụ AI đã dùng

- **Công cụ:** OpenCode (agentic coding assistant, model GLM) trong buổi lab.
- **Dùng vào việc gì:**
  - Đọc và tóm tắt đề bài, contract (`docs/contracts.md`, `docs/business_rules.md`),
    bảng 14 case T01–T14 và API có sẵn (`tools.py`, `durability.py`, `common.py`,
    `swarm_reference.py`).
  - Đánh giá độ lớn task Shape A và chia thành 6 subtask (T-A1…T-A6) có điểm tự kiểm
    riêng theo bộ test.
  - Gợi ý code hoàn chỉnh cho `workflow.py` theo docstring của đề bài.
- **Tự kiểm tra kết quả thế nào:**
  - Chạy lại bộ test của đề: `pytest -q -m student -o addopts= -k workflow` → 62 passed;
    `pytest -q` → cổng host vẫn xanh.
  - Đọc lại từng nhánh code, đối chiếu với docstring 8 bước đầu file và bảng case
    T01–T14 trong `docs/contracts.md`; tự giải thích được vì sao truyền quote đầy đủ,
    vì sao để host từ chối thay vì shape tự chối, và trace cố ý không ghi field nào
    (ticket, `parent_secret`, SĐT, địa chỉ, ghi chú nội bộ).

## 6. Tự đánh giá

- Điểm làm tốt: [...]
- Điểm cần cải thiện: [...]
- Thời lượng thực tế: [...]
