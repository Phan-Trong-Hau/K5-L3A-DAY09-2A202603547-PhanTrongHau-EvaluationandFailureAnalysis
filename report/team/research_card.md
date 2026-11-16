# Research card

File này nằm cố định ở `report/team/research_card.md`; `python -m lab8.check_submission` đọc cột "Nhóm điền" bằng máy.

Phần này nối tiếp phần mini research ở buổi lý thuyết (slide 62–63). Chọn **một** câu R1–R4, điền 6 dòng, rồi biến nó thành **một ablation** chạy được trong lab: giữ nguyên model (MockLLM), tool, seed, corpus và giá, chỉ thay đổi một biến.

| Câu | Nguồn (thư viện tham khảo, slide 68–69) | Câu hỏi gợi ý cho lab |
| --- | --- | --- |
| R1 · Scaling | Google Research 2026, *Towards a Science of Scaling Agent Systems* | Task claims chủ yếu tuần tự hay song song được? Dự đoán thêm investigator sẽ làm pass rate và cost/success thay đổi thế nào. |
| R2 · Failure taxonomy | MAST, NeurIPS 2025, *Why Do Multi-Agent LLM Systems Fail?* | Các trial fail của swarm (seed 55) thuộc nhóm nào: lỗi giao việc, lệch mục tiêu, hay lỗi kiểm chứng? |
| R3 · Architecture choices | AgentArch, AACL 2026 | Nếu đổi topology mà giữ nguyên mọi thứ khác, biến nào phải cố định để kết luận còn đúng? |
| R4 · Evaluation confounders | EMNLP 2026, *Rethinking Evaluation of MAS Efficiency* | Làm sao chứng minh chênh lệch giữa A/B/C/D là do topology, không phải do prompt, tool hay seed? |

## Phiếu của nhóm

Điền vào cột cuối. Không xóa hai cột đầu.

| Field | Hướng dẫn | Nhóm điền |
| --- | --- | --- |
| CÂU | R1 / R2 / R3 / R4 | R1 |
| SOURCE | Paper/blog, năm, URL, loại bằng chứng (benchmark, production report, blog kinh nghiệm) | Google Research, 2026, *Towards a Science of Scaling Agent Systems*. Loại bằng chứng: benchmark đa agent trên nhiều tác vụ (paper, không phải báo cáo production). Slide 15, 24, 33 của bài lý thuyết. |
| CLAIM | Một kết luận gốc của nguồn. Không viết rộng hơn phạm vi paper | Multi-agent chỉ có lợi khi tác vụ chia được thành các phần song song. Với tác vụ tuần tự, các biến thể multi-agent được đo giảm hiệu năng khoảng 39–70%. |
| BOUNDARY | Model / dataset / setup giới hạn kết luận đó | Agent gọi model ngôn ngữ thật, tác vụ có độ trễ model và tool lớn. LogiX: MockLLM tất định, tool đọc SQLite cục bộ (dưới 1 ms mỗi lần), 14 claim public × 5 seed. Kết luận của nguồn không áp dụng thẳng cho setup này. |
| HYPOTHESIS | Nếu đổi shape A→B (hoặc bật/tắt một thành phần), metric X sẽ đổi theo hướng nào, khoảng bao nhiêu | Chạy hai bước đọc độc lập (`lookup_order`, `lookup_policy`) song song thay vì tuần tự sẽ giảm thời gian chạy trung bình của một claim, khoảng 1.1–1.3×. Pass rate và ledger không đổi. |
| METHOD | Biến giữ cố định: model, tools, seed, corpus, giá, evaluator. Biến duy nhất được thay đổi: … | Cố định: MockLLM, tool, seed 11/22/33/44/55, 14 claim public, giá, evaluator `trial_pass`, store là bản copy của cùng một template. Biến duy nhất thay đổi: đọc hai bước độc lập tuần tự (orchestrator) hay song song (`orchestrator_parallel`, `ThreadPoolExecutor`, 2 worker). Mỗi trial đo 5 lần, thứ tự chạy luân phiên. |
| FAILURE / METRIC | Một lỗi dự kiến và cách đo nó: pass rate, pass^5, variance, cost/success, leak, bypass | Lỗi dự kiến: chi phí tạo thread và kết nối SQLite lớn hơn phần việc thật, khiến bản song song chậm hơn. Đo bằng thời gian wall-clock median của `run_claim` (`time.perf_counter`) và số trial song song nhanh hơn, cộng với kiểm tra kết quả và ledger giống nhau. |

## Kết quả ablation

- Lệnh đã chạy (copy nguyên văn):
  ```bash
  python -m bonus.timing_report --seeds 11,22,33,44,55 --reps 5 --out reports/bonus_timing.json
  ```
- Run id / file report: `src/reports/bonus_timing.json`. Run id mẫu `R-orchestrator_parallel-C-001-s11` (trace trong `src/traces/`).
- Kết quả so với hypothesis: **sai**. Tổng median 248.6 ms (tuần tự) so với 297.7 ms (song song). Speedup tổng 0.835, song song nhanh hơn ở 4/70 trial. Pass rate 1.000 cho cả hai, kết quả giống nhau 70/70. Pha đọc song song chỉ khoảng 0.56 ms, nhỏ hơn chi phí thread, nên hypothesis không được ủng hộ trong setup này.
- Giới hạn: MockLLM không phải model sản xuất, latency model là thời gian đo thật trên một máy (8 CPU, Linux, SQLite 3.45.1), chỉ 14 claim public. Không có tool có độ trễ mạng, nên kết luận không suy ra được cho tool chậm.
