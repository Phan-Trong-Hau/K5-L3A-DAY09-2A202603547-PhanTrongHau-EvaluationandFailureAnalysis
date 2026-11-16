# Team

## Thông tin nhóm

- Tên nhóm:
- Lớp: L3A
- Repo nhóm: `K5-L3A-DAY08-TenNhom-FromWorkflowsToAgents` (xem [SUBMISSION.md](SUBMISSION.md))
- URL repo, nhánh nộp, commit chốt:

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 | Đào Huy Hoàng       | 2A202603451     | 26ai.hoangdh@vinuni.edu.vn | [hoang2k3ai](https://github.com/hoang2k3ai) | Shape A — workflow |
|   2 | Lê Hồng Quân       | 2A202603705     | 26ai.quanlh3@vinuni.edu.vn | [LeHongQuanMarble](https://github.com/LeHongQuanMarble) | Shape C — orchestrator + handoff; bonus B1 |
|   3 | Phan Trọng Hậu       | 2A202603547     |       | [Phan-Trong-Hau](https://github.com/Phan-Trong-Hau) | D baseline + bonus B3, đánh giá |
|   4 | Ngô Đức Thịnh       | 2A202603548     |       | [`NgooThinh05`](https://github.com/NgooThinh05) | Shape B — single |
Gợi ý chia vai:

- Nhóm 6 người: integration; workflow; single agent; orchestrator; ledger/policy/crash; eval/report.
- Nhóm 4 người: workflow + integration; single; orchestrator + handoff; ledger + evaluation.

## Bảng đóng góp

`python -m lab8.check_submission` đọc bảng này bằng máy: giữ nguyên tiêu đề `## Bảng đóng góp` và các cột. Mỗi người một dòng: commit có nội dung và ít nhất một test đã thêm hoặc sửa.

| Người | Vai | Commit | Test đã thêm hoặc sửa |
| --- | --- | --- | --- |
| Đào Huy Hoàng | Shape A — workflow (`src/lab8/shapes/workflow.py`) | `26c4fde` | `src/tests/test_workflow_extra.py`: `test_workflow_quotes_from_order_row_not_ticket`, `test_workflow_trace_has_no_ticket_or_secret` |
| Phan Trọng Hậu | D baseline + bonus B3, đánh giá | `87b2508` | `src/tests/test_bonus_swarm_verified.py` (22 passed) |
| Lê Hồng Quân | Shape C — orchestrator (`src/lab8/shapes/orchestrator.py`); bonus B1 | `fbe22ed`, `01e9ecf` | `src/tests/test_orchestrator_shape.py` (7 test); `src/tests/test_bonus_orchestrator_parallel.py` (song song, timing) |
| Ngô Đức Thịnh | Shape B — single | `a517bc7` | Chưa thêm test trong commit; 62 test student của `test_public_matrix.py` đã pass |

## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

Ví dụ: `report/team/20241234_NguyenVanAn.md`.

Sao chép mục dưới đây cho từng thành viên.

## MSSV_HoTen

### Phần việc phụ trách

-

### Đóng góp cụ thể

-

### Bằng chứng

-

## 2A202603451_DaoHuyHoang

### Phần việc phụ trách

- Shape A — `workflow` (`src/lab8/shapes/workflow.py`): chuỗi quyết định cố định, host ghi refund.

### Đóng góp cụ thể

- Cài đặt 8 bước quyết định theo docstring, truyền quote đầy đủ vào `durability.issue_refund`, truyền `crash_at` và không bắt `InjectedCrash`, một điểm thoát `_finish()` cho mọi nhánh, trace không ghi ticket/secret/PII.
- Kết quả: `pytest -q -m student -o addopts= -k workflow` → 62 passed; `pytest -q` → 56 passed.

### Bằng chứng

- Commit `26c4fde` (nhánh `main`): `feat(workflow): implement shape A decision ladder`.
- Test tự thêm: `src/tests/test_workflow_extra.py` (2 test).
- Báo cáo cá nhân: `report/team/2A202603451_DaoHuyHoang.md`.

## 2A202603705_LeHongQuan

### Phần việc phụ trách

- Shape C — `orchestrator` (`src/lab8/shapes/orchestrator.py`): handoff qua `make_handoff`, investigator chỉ đọc qua `run_readonly_investigators`, quote từ `compute_compensation`, truyền `crash_at` vào `issue_refund` và không bắt `InjectedCrash`.
- Bonus B1 — investigator song song (`src/bonus/orchestrator_parallel.py`, `src/bonus/timing_report.py`): kết quả đo thật, speedup 0.835, không ủng hộ giả thuyết.

### Đóng góp cụ thể

- Ma trận student cho orchestrator: 62 passed; crash suite 20/20; `check_submission` báo orchestrator OK.
- Quyết định chọn orchestrator làm shape nộp (ADR), research card R1 với ablation đo thật.

### Bằng chứng

- Commit `fbe22ed` (shape), `01e9ecf` (test và B1), `0ff146b` (dòng trong bảng này), `7b6c181` (ADR, research card, báo cáo cá nhân).
- Test tự thêm: `src/tests/test_orchestrator_shape.py` (7 test), `src/tests/test_bonus_orchestrator_parallel.py`.
- Báo cáo cá nhân: `report/team/2A202603705_LeHongQuan.md`; báo cáo bonus: `report/team/bonus_report_b1.md`.
