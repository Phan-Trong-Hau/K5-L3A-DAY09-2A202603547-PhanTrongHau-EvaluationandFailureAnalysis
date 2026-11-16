# Bonus report: B3

- Topic + nguồn: B3 — verifier/aggregator chống khuếch đại lỗi; Google Research 2026, *Towards a Science of Scaling Agent Systems*, slide 17, 22, 42.
- CLAIM của nguồn: bước verifier có thể phát hiện và sửa lỗi trước khi chúng đi vào hành động của hệ thống multi-agent.
- BOUNDARY (model / dataset / setup): MockLLM tất định, benchmark public 14 claim × 5 seed và 8 case đối kháng tự viết × 5 seed; chi phí mô phỏng, không đo độ trễ.
- HYPOTHESIS trên LogiX: đối chiếu dữ kiện dùng để quote với order có cấu trúc sẽ loại lỗi do ticket làm lệch delay, mà không làm tăng chi phí mô phỏng trung bình trên các case đã chạy.
- Biến cố định / biến thay đổi: cùng world, claim, seed và host; thay `swarm` bằng `swarm_verified` có bước verifier.
- Lệnh tái lập (copy-paste được), từ `src/`:

  ```bash
  python -m lab8.benchmark --shapes swarm,swarm_verified,workflow_baseline --extra-shape swarm_verified=bonus.swarm_verified:run_claim --extra-shape workflow_baseline=bonus.workflow_baseline:run_claim --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/bonus_benchmark_public.json
  python -m lab8.benchmark --shapes swarm,swarm_verified,workflow_baseline --extra-shape swarm_verified=bonus.swarm_verified:run_claim --extra-shape workflow_baseline=bonus.workflow_baseline:run_claim --cases bonus/cases.jsonl --world bonus/world.json --seeds 11,22,33,44,55 --out reports/bonus_benchmark_adversarial.json
  python -m bonus.summarize_b3 --out reports/bonus_analysis.json
  python -m pytest -q tests/test_bonus_swarm_verified.py
  ```

- File report + run id: `src/reports/bonus_benchmark_public.json` (`R-swarm_verified-C-002-s55`); `src/reports/bonus_benchmark_adversarial.json` (`R-swarm_verified-B3-001-s11`); verifier counts and trace excerpts: `src/reports/bonus_analysis.json`.

## Kết quả

| Bộ dữ liệu | Biến thể | Pass rate | Pass^5 | Variance theo seed | Cost/success (VND mô phỏng) |
| --- | --- | ---: | ---: | ---: | ---: |
| Public, 14 claim | swarm | 0.986 | 0.929 | 0.000816 | 49.57 |
| Public, 14 claim | swarm_verified | 1.000 | 1.000 | 0.000000 | 48.86 |
| Public, 14 claim | workflow baseline | 1.000 | 1.000 | 0.000000 | 27.86 |
| Tự viết, 8 claim | swarm | 0.850 | 0.250 | 0.090000 | 63.39 |
| Tự viết, 8 claim | swarm_verified | 1.000 | 1.000 | 0.000000 | 53.88 |
| Tự viết, 8 claim | workflow baseline | 1.000 | 1.000 | 0.000000 | 30.00 |

The bonus-local workflow baseline implements Shape A's documented deterministic sequence and does not replace the team's `lab8.shapes.workflow` implementation. Test B3: `python -m pytest -q tests/test_bonus_swarm_verified.py` — 22 passed. Trong public T02 seed 55, swarm trả 20.000 VND dựa trên ticket và fail; verifier giữ số liệu order (2 ngày), quote 0 và deny. `bonus_analysis.json` ghi **1/70** verifier override trên public và **7/40** trên case tự viết.

Trace minh họa (`R-swarm_verified-C-002-s55`, rút gọn):

```json
{"kind":"model_override","payload":{"delay_days":5}}
{"kind":"verifier_override","payload":{"fields":["delay_days"],"amount_vnd":0}}
{"kind":"quote","payload":{"amount_vnd":0,"reason":"no_entitlement","clause_ids":[],"parts":{}}}
```

## Kết luận

Kết quả cho thấy verifier đưa pass rate của swarm_verified ngang workflow baseline trên hai bộ hiện tại: 1.000 so với 1.000. Trên public, swarm_verified tốn 48.86 VND mô phỏng mỗi lần thành công so với 27.86 của workflow; trên case tự viết là 53.88 so với 30.00. Verifier sửa được lỗi seed 55, nhưng số bước và chi phí vẫn cao hơn workflow. Vì verifier lấy dữ kiện quote từ order có cấu trúc, quyết định tiền cốt lõi gần như đã trở thành workflow; swarm chỉ còn giá trị tiềm năng ở việc hiểu yêu cầu ngôn ngữ tự nhiên hoặc tạo phản hồi, điều benchmark này chưa chứng minh.

So sánh workflow ở đây dùng module bonus-local bám theo trình tự deterministic trong hợp đồng Shape A, vì file Shape A của nhóm hiện chưa triển khai. Cần chạy lại ba biến thể với `workflow` chính thức sau khi A hoàn thành.

## Giới hạn và việc còn lại

MockLLM không đại diện cho model thật. Bộ case tự viết nhỏ và tập trung vào mâu thuẫn giữa ticket với order; benchmark không đo latency. Workflow baseline mô phỏng hợp đồng A, chưa phải file A do thành viên nhóm hoàn thiện. Cần thay baseline bằng Shape A chính thức khi tích hợp. Bonus chỉ đủ điều kiện chấm khi shape chính qua các must-pass, hidden pass rate đạt ít nhất 0.80 và toàn bộ cổng test xanh.
