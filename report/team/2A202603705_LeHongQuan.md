# Báo cáo cá nhân — 2A202603705_LeHongQuan

## 1. Thông tin thành viên

- Họ tên: Lê Hồng Quân
- MSSV: 2A202603705
- Email: 26ai.quanlh3@vinuni.edu.vn
- GitHub: LeHongQuanMarble

## 2. Phần việc phụ trách

- **Shape 03 — orchestrator** (`src/lab8/shapes/orchestrator.py`): CP2 và CP3. Dựng handoff bằng `make_handoff`, chạy investigator chỉ đọc, quote từ `compute_compensation`, trả `needs_info` / `escalated` / `denied` / `resolved`. Truyền `crash_at` vào `durability.issue_refund`, không bắt `InjectedCrash`, luôn đưa toàn bộ quote và không tự trừ phần đã hoàn.
- **Investigator chỉ đọc:** dùng `lab8.runtime.run_readonly_investigators` có sẵn, với `lookup_order`, `lookup_policy`, `compute_compensation`. Không viết class investigator mới.
- **Ablation nghiên cứu R1 — investigator song song** (`src/bonus/orchestrator_parallel.py`, `src/bonus/timing_report.py`, ablation trong `report/team/research_card.md`): hai bước đọc độc lập chạy trên `ThreadPoolExecutor`. Mỗi worker mở kết nối SQLite riêng, chỉ thread chính ghi tiền. Đây không phải topic bonus; nhóm chọn B3.

## 3. Đóng góp cụ thể

- **Commit:**
  - `fbe22ed` — "shape 03: orchestator by LeHongQuan_03705": `src/lab8/shapes/orchestrator.py`, `src/reports/benchmark.json`, `src/reports/crash.json`. Lần push đầu bị từ chối (non-fast-forward) vì đồng đội đã push `a517bc7` ("Shape B single"). Tôi rebase lên trên commit đó rồi push lại, không ghi đè.
  - `01e9ecf` — "update orchestractor by LeHongQuan": test orchestrator, code ablation R1 và số đo. Lúc rebase có xung đột với B3 của Phan Trọng Hậu ở `src/bonus/__init__.py` và `report/team/bonus_report.md`. Tôi giữ bản của Hậu ở đường dẫn chuẩn.
  - `0ff146b` — thêm dòng của tôi vào bảng đóng góp trong `TEAM.md`.
- **Test đã thêm:**
  - `src/tests/test_orchestrator_shape.py`, 7 test: investigator chỉ có tool đọc; handoff trong trace chỉ có field allowlist và không có `CANARY_SECRET`; trace vẫn được ghi ở nhánh `needs_info`; nhánh `escalated` không lộ PII; `denied` do approval thì không refund; quote là toàn bộ entitlement; crash lan ra ngoài và lần resume chỉ có một refund.
  - `src/tests/test_bonus_orchestrator_parallel.py`: kết quả song song giống orchestrator tuần tự trên 14 claim × 2 seed; kết quả không đổi khi thứ tự thread thay đổi; event `timing` là số đo thật, và worker không dài hơn pha đọc; trace không có secret; crash và resume.
- **Quyết định kỹ thuật:**
  - Quote lấy từ investigator, không đọc ticket, nên không mắc lỗi `REFERENCE_WEAKNESS` của swarm ở seed % 5 == 0.
  - Không bắt `InjectedCrash`, đúng yêu cầu CP3. Vì vậy trace không có event `crash` khi crash.
  - Bản song song đo thời gian bằng `time.perf_counter` trên lần chạy thật. Trước đó tôi dùng latency mô phỏng, sau khi có yêu cầu thì bỏ hẳn.

## 4. Bằng chứng

- Commit `fbe22ed`, `01e9ecf`, `0ff146b` trên `origin/main`.
- Test: `test_orchestrator_shape.py::test_crash_propagates_and_resume_keeps_one_refund`, `test_bonus_orchestrator_parallel.py::test_parallel_matches_sequential_orchestrator`.
- Lệnh và kết quả (chạy trong `src/`):
  - `python -m lab8.crash_test --count 20 --out reports/crash.json` → `crash_safety 20/20`.
  - `python -m pytest -q -m student -o addopts= -k orchestrator` → 62 passed.
  - `python -m pytest -q -m student -o addopts=` (cả bốn shape) → 248 passed.
  - `python -m pytest -q` → 118 passed. `python -m pytest -q tests/test_bonus_*.py` → 55 passed.
  - `python -m lab8.check_submission` → shape orchestrator OK, 12/12 claim public pass ở seed 11.
  - `python -m bonus.timing_report --seeds 11,22,33,44,55 --reps 5 --out reports/bonus_timing.json` → speedup song song/tuần tự **0.835** (tổng median 248.6 ms so với 297.7 ms). Song song nhanh hơn ở 4/70 trial. Kết quả giống nhau 70/70.
- File số liệu: `src/reports/bonus_timing.json`, `src/reports/crash.json`, `src/reports/benchmark.json`.
- Run id mẫu: `R-orchestrator-C-012-s11`, `R-orchestrator_parallel-C-001-s11`.
- Trace: 140 file `R-orchestrator*` trong `src/traces/` không có chuỗi `CANARY_SECRET`.

## 5. Công cụ AI đã dùng

- **Claude Code** (trợ lý lập trình trong terminal): đọc code lab, viết `orchestrator.py` và test, viết script đo thời gian, soạn báo cáo bonus, xử lý rebase và push.
- **Cách tự kiểm tra:** mọi con số trong báo cáo đều chạy lại được bằng lệnh ở mục 4. Tôi kiểm tra từng kết quả bằng lệnh hoặc đọc file JSON do script sinh ra, không sửa tay file trong `src/reports/`. Phần cost (VND) và `steps` trong benchmark là mô phỏng theo thiết kế của lab, tôi không coi đó là số đo thời gian.

## 6. Tự đánh giá

**Làm tốt:**
- Shape orchestrator qua 62 test student, crash 20/20, không có canary trong trace, và không sửa file thước đo.
- Xử lý lỗi push và xung đột bằng rebase, không ghi đè commit của đồng đội.
- Báo cáo bonus ghi đúng kết quả đo được, kể cả kết quả không ủng hộ giả thuyết (song song chậm hơn).

**Còn yếu:**
- Ablation R1 ban đầu dùng latency mô phỏng khi chưa được yêu cầu đo thật. Đến khi bạn yêu cầu tôi mới đổi. Lẽ ra nên đo thật ngay từ đầu.
- Commit orchestrator đầu tiên (`fbe22ed`) không kèm test. Test được thêm ở `01e9ecf`, nên commit hiện tại có test, nhưng commit đầu thì không.
- Chưa kiểm được pass rate trên bộ hidden 40 claim × 5 seed. Mới kiểm trên 14 claim public, nơi orchestrator đạt 1.000.
- Benchmark chính (`src/reports/benchmark.json`) trong commit cũ còn số của thời workflow là stub. Tôi đã chạy lại và file mới chưa commit.

**Việc tiếp theo:**
- Commit `src/reports/benchmark.json` mới.
- Nhóm chọn shape nộp, rồi điền `decision_adr.md` (commit hash, run id, số liệu từ `benchmark.json` và `crash.json`).
- Điền `research_card.md` cùng nhóm.
- Nhắc Ngô Đức Thịnh thêm dòng của anh ấy vào bảng đóng góp `TEAM.md`.
