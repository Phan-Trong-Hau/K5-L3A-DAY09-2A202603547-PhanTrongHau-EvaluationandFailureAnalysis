# Bonus report: B1

- Topic + nguồn: B1 — Investigator song song và critical path. Google Research 2026, *Towards a Science of Scaling Agent Systems*, slide 15 (Parallelization), 24 (Graph scheduling), 33 (Latency model), 41.
- CLAIM của nguồn: multi-agent chỉ có lợi khi task chia song song được; với task tuần tự, các biến thể multi-agent giảm 39–70%.
- BOUNDARY: nghiên cứu nguồn đo agent gọi model và tool có độ trễ lớn. LogiX ở đây chỉ có tool đọc SQLite cục bộ (mili-giây hoặc nhỏ hơn). Kết quả không suy ra được cho tool có độ trễ mạng.
- HYPOTHESIS trên LogiX: hai bước đọc độc lập (`lookup_order`, `lookup_policy`) chạy song song sẽ giảm thời gian chạy một claim, và pass rate, ledger không đổi.
- Biến cố định / biến thay đổi: cố định claim, seed, corpus, store (bản sao từ cùng một template), MockLLM, evaluator, policy. Biến thay đổi: đọc tuần tự hay song song.
- Lệnh tái lập (chạy trong `src/`):
  ```bash
  python -m bonus.timing_report --seeds 11,22,33,44,55 --reps 5 --out reports/bonus_timing.json
  python -m lab8.benchmark --shapes orchestrator,orchestrator_parallel --extra-shape orchestrator_parallel=bonus.orchestrator_parallel:run_claim --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/bonus_benchmark.json
  python -m pytest -q tests/test_bonus_orchestrator_parallel.py
  ```
- File report: `src/reports/bonus_timing.json` (thời gian thật, 70 trial × 5 lần lặp mỗi shape) và `src/reports/bonus_benchmark.json` (pass, pass^5, variance do lab tính). Run id có dạng `R-orchestrator_parallel-<claim>-s<seed>` trong `src/traces/`; event `timing` trong mỗi trace chứa số đo của run đó.

## Đo gì và đo thế nào

- Thời gian là wall-clock đo bằng `time.perf_counter()` quanh đúng lời gọi `run_claim`, gồm kết nối SQLite, bước đọc, ghi và ghi trace. Không tính thời gian copy store.
- Mỗi claim × seed: một lần chạy thử không tính giờ, rồi 5 lần đo cho mỗi shape. Thứ tự chạy (tuần tự trước hay song song trước) đổi luân phiên theo lần lặp.
- Số trong báo cáo lấy từ median của 5 lần đo mỗi trial, rồi tổng theo 70 trial.
- Môi trường: Python 3.12.3, Linux x86_64, 8 CPU, SQLite 3.45.1, `max_workers` = 2.

## Kết quả

| Chỉ số | Tuần tự (orchestrator) | Song song (orchestrator_parallel) |
|---|---:|---:|
| Tổng thời gian median (ms, 70 trial) | 248.6 | 297.7 |
| Speedup tổng (tuần tự / song song) | — | **0.835** |
| Speedup median theo từng trial | — | 0.827 |
| Số trial song song nhanh hơn | — | 4 / 70 |
| Pha đọc song song, median (ms) | — | 0.564 |
| Kết quả và ledger giống nhau | — | 70 / 70 |
| Pass rate | 1.000 | 1.000 |

Từ `bonus_benchmark.json` (do lab tính): pass^5 = 1.000 và variance = 0 cho cả hai shape. Cost/success 36.82 và số `steps` là mô phỏng theo `config/pricing.yaml` và MockLLM của lab, không phải số đo thời gian. Số `steps` của bản song song cao hơn (4.43 so với 3.43) vì trace có thêm event `timing` và `write`.

Thời gian của từng trial dao động từ khoảng 0.28 ms đến 6–7 ms. Pha đọc song song chỉ kéo dài khoảng 0.56 ms, nên chi phí tạo thread và mở connection riêng cho mỗi worker lớn hơn phần việc thực sự.

## Kết luận

**Không ủng hộ hypothesis trên workload này.** Với tool đọc SQLite cục bộ, song song hóa hai bước đọc làm chậm claim, không tăng tốc: speedup 0.835. Pass rate và ledger không đổi, nên song song không làm sai kết quả, chỉ làm chậm.

Kết luận này chỉ áp dụng cho boundary đã đo. Kết luận sẽ đảo nếu tool đọc có độ trễ lớn hơn nhiều so với chi phí tạo thread (ví dụ tra cứu qua mạng). Điều đó chưa được đo ở đây, và báo cáo không suy ra từ số đo này.

## Giới hạn

- Chỉ 14 claim public, 5 seed, 5 lần đo mỗi shape. Bộ hidden chưa được kiểm.
- Một máy, một hệ điều hành. Thời gian có thể khác trên máy khác.
- Tool không có độ trễ mạng; không có tool chậm nhân tạo nào được thêm vào để đo.
- Chi phí VND, số `steps` và pass^5 là mô phỏng theo thiết kế của lab (MockLLM, `pricing.yaml`), không phải số đo thời gian thật.
