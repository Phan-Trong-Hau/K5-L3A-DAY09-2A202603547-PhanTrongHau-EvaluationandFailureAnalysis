# Team

## Thông tin nhóm

- Tên nhóm: HHTQ
- Lớp: L3A
- Repo nhóm: `K5-L3A-DAY08-HHTQ-FromWorkflowsToAgents` (xem [SUBMISSION.md](SUBMISSION.md))
- URL repo, nhánh nộp, commit chốt: https://github.com/hoang2k3ai/K5-L3A-DAY08-HHTQ-FromWorkflowsToAgents, nhánh `main`, commit bằng chứng: `77619d7` (được ghi trong `report/team/decision_adr.md`)

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 | Đào Huy Hoàng       | 2A202603451     | 26ai.hoangdh@vinuni.edu.vn | [hoang2k3ai](https://github.com/hoang2k3ai) | Shape A — workflow |
|   2 | Lê Hồng Quân       | 2A202603705     | 26ai.quanlh3@vinuni.edu.vn | [LeHongQuanMarble](https://github.com/LeHongQuanMarble) | Shape C — orchestrator + handoff; ablation nghiên cứu R1 |
|   3 | Phan Trọng Hậu       | 2A202603547     |       | [Phan-Trong-Hau](https://github.com/Phan-Trong-Hau) | D baseline + bonus B3, đánh giá |
|   4 | Ngô Đức Thịnh       | 2A202603548     | 26ai.thinhnd2@vinuni.edu.vn | [`NgooThinh05`](https://github.com/NgooThinh05) | Shape B — single |

Gợi ý chia vai:

- Nhóm 6 người: integration; workflow; single agent; orchestrator; ledger/policy/crash; eval/report.
- Nhóm 4 người: workflow + integration; single; orchestrator + handoff; ledger + evaluation.

## Bảng đóng góp

`python -m lab8.check_submission` đọc bảng này bằng máy: giữ nguyên tiêu đề `## Bảng đóng góp` và các cột. Mỗi người một dòng: commit có nội dung và ít nhất một test đã thêm hoặc sửa.

| Người | Vai | Commit | Test đã thêm hoặc sửa |
| --- | --- | --- | --- |
| Đào Huy Hoàng | Shape A — workflow (`src/lab8/shapes/workflow.py`) | `26c4fde`, `eab8322` | `src/tests/test_workflow_extra.py`: `test_workflow_quotes_from_order_row_not_ticket`, `test_workflow_trace_has_no_ticket_or_secret` |
| Ngô Đức Thịnh | Shape B — single (`src/lab8/shapes/single.py`) | `a517bc7`, `ab6624c` | `src/tests/test_single_shape.py` (5 test: ticket delay seed 55, trace secret/PII, per-order cap T13/T14, crash propagation, unknown claim); `src/tests/test_single_extra.py` (3 test); 62 test student `single` |
| Lê Hồng Quân | Shape C — orchestrator (`src/lab8/shapes/orchestrator.py`); ablation R1 | `fbe22ed`, `01e9ecf` | `src/tests/test_orchestrator_shape.py` (7 test); `src/tests/test_bonus_orchestrator_parallel.py` (song song, timing); `src/tests/test_orchestrator_extra.py` |
| Phan Trọng Hậu | D baseline + bonus B3, đánh giá | `87b2508` | `src/tests/test_bonus_swarm_verified.py`: `test_verifier_checks_every_business_fact_used_for_quote`, `test_adversarial_cases_follow_structured_order`, `test_workflow_baseline_matches_labels_on_adversarial_cases`, `test_verifier_fixes_reference_swarm_seed_55_public_t02`, `test_verifier_emits_override_trace_for_seed_55`, `test_verified_variant_resumes_after_effect_crash_once` (22 cases passed) |

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
- Nghiên cứu R1 (research card) — investigator song song (`src/bonus/orchestrator_parallel.py`, `src/bonus/timing_report.py`): kết quả đo thật, speedup 0.835, không ủng hộ giả thuyết. Đây không phải topic bonus; topic bonus của nhóm là B3.

### Đóng góp cụ thể

- Ma trận student cho orchestrator: 62 passed; crash suite 20/20; `check_submission` báo orchestrator OK.
- Đề xuất orchestrator làm shape nộp trong ADR trước khi nhóm chọn workflow (xem lịch sử git); research card R1 với ablation đo thật.

### Bằng chứng

- Commit `fbe22ed` (shape), `01e9ecf` (test và ablation R1), `0ff146b` (dòng trong bảng này), `7b6c181` (ADR, research card, báo cáo cá nhân).
- Test tự thêm: `src/tests/test_orchestrator_shape.py` (7 test), `src/tests/test_bonus_orchestrator_parallel.py`.
- Báo cáo cá nhân: `report/team/2A202603705_LeHongQuan.md`.

## 2A202603547_PhanTrongHau

### Phần việc phụ trách

- Shape D (`swarm`) làm baseline đối chứng và bonus B3: biến thể swarm có verifier dựa trên dữ liệu order có cấu trúc.
- Bộ case đối kháng, kiểm thử, benchmark và báo cáo bonus.

### Đóng góp cụ thể

- `src/bonus/swarm_verified.py`: kiểm chứng dữ kiện quote trước khi gọi host ghi refund; tính lại quote từ order khi dữ kiện không khớp.
- `src/bonus/workflow_baseline.py`: baseline deterministic độc lập để so sánh B3, không thay file Shape A.
- Tám claim đối kháng có nhãn viết tay (`src/bonus/cases.jsonl`, `src/bonus/world.json`), `src/bonus/summarize_b3.py`, `src/reports/bonus_analysis.json`.

### Bằng chứng

- Commit `87b2508`: `Add verified swarm B3 bonus`.
- Test: `src/tests/test_bonus_swarm_verified.py` — 22 passed.
- Benchmark: `src/reports/bonus_benchmark_public.json`, `src/reports/bonus_benchmark_adversarial.json`.
- Báo cáo cá nhân: `report/team/2A202603547_PhanTrongHau.md`.

## 2A202603548_NgoDucThinh

### Phần việc phụ trách

- Shape B — `single` (`src/lab8/shapes/single.py`): một vòng ReAct tối đa 8 bước, chỉ dùng tool đọc; host là nơi duy nhất ghi refund.

### Đóng góp cụ thể

- Quote lấy từ `lookup_order` và `compute_compensation`, không dùng số ngày trễ hay điều khoản trong ticket; truyền quote đầy đủ vào `issue_refund`; truyền `crash_at` và không nuốt `InjectedCrash`.
- Kết quả: `pytest -q -m student -o addopts= -k "single]"` → 62 passed; `pytest -q` → 54 passed.

### Bằng chứng

- Commit `a517bc7` (`Shape B single`).
- Test tự thêm: `src/tests/test_single_shape.py` (5 test).
- Run id: `R-single-C-001-s11`, `R-single-C-002-s55`, `R-single-C-012-s11`.
- Báo cáo cá nhân: `report/team/2A202603548_NgoDucThinh.md`.
