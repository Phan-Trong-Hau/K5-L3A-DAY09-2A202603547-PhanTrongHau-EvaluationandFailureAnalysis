# Demo — Lab 8 LogiX-VN, nhóm HHTQ

Tài liệu này để ban giám khảo xem và tự thử toàn bộ phần nhóm đã làm. Có hai cách, dùng riêng hoặc cùng nhau:

1. **Bài trình bày tương tác** (không cần cài gì): mở một tệp HTML, xem như video, tự trả lời hai câu hỏi demo.
2. **Chạy thật trên máy**: các lệnh dưới đây cho ra đúng những con số trong bài trình bày.

## 1. Bài trình bày tương tác

Mở tệp [`demo/logix-bon-kien-truc.html`](demo/logix-bon-kien-truc.html) bằng Chrome hoặc Edge (bấm đúp vào tệp, không cần mạng), rồi bấm nút phát. Bài dài khoảng 6 phút rưỡi, 12 phần; mỗi kiến trúc có một phần riêng, chiếu trace thật của nó trên cùng claim C-001, seed 11.

| Phần | Mục tiêu của bài | Nội dung | Ban giám khảo làm gì |
| --- | --- | --- | --- |
| 1. Bài toán và nhóm | — | Claim hoàn phí ship, bốn mục tiêu, bốn thành viên | Xem |
| 2. Bốn kiến trúc, một cửa ghi tiền | 1 | Mức tự chủ tăng dần A → D; tiền do code tính, chỉ host ghi sổ | Xem |
| 3. A · Workflow | 1 | Sơ đồ bước + **trace thật** `R-workflow-C-001-s11`: 4 event, 1 lần gọi model | Xem |
| 4. B · Single agent | 1 | Vòng ReAct + trace `R-single-C-001-s11`: model chọn tool đọc, `host_gate` ghi | Xem |
| 5. C · Orchestrator | 1, 3 | Trace `R-orchestrator-C-001-s11`: gói `handoff` đã lọc, investigator chỉ đọc | Xem |
| 6. D · Swarm | 1 | Trace `R-swarm-C-001-s11`: đúng ở claim này, nhưng đắt nhất | Xem |
| 7. Ranh giới bảo mật | 3 | Dữ liệu thô → 8 field của handoff → trace không có secret hay thông tin cá nhân | Xem |
| 8. **Demo 1: ticket nói dối** (C-002) | 3 | Ticket ghi trễ 5 ngày, order ghi 2 ngày | **Chọn đáp án.** Chọn "Hoàn 20.000 đ" để xem trace của swarm ở seed 55, dòng `model_override` |
| 9. **Demo 2: crash rồi chạy lại** (C-012) | 2 | Đã ghi tiền, chưa lưu checkpoint, chạy lại | **Chọn đáp án.** Chọn "Hai dòng" để xem trace dừng ở dòng `crash` và vì sao checkpoint không thay được sổ |
| 10. Kết quả và quyết định | 4 | Benchmark 14 claim × 5 seed, lý do chọn workflow | **Chạm vào từng kiến trúc** để xem số của nó, rồi bấm Tiếp tục |
| 11. Nghiên cứu R1 và bonus B3 | 4 | Đọc song song không nhanh hơn; swarm có verifier hết sai | Xem |
| 12. Kết luận và giới hạn | — | Quyết định, giới hạn, lệnh chạy lại | Xem |

Bốn mục tiêu của bài (README): (1) cùng một quy trình theo bốn kiến trúc, code quyết tiền; (2) ghi tiền an toàn khi chạy lại và khi crash; (3) ranh giới bảo mật giữa các agent, ticket là dữ liệu; (4) chọn kiến trúc bằng số đo.

Phím tắt: `Space` phát / dừng · `S` trình chiếu như PowerPoint (`→` `←` để bước) · `C` phụ đề · `F` toàn màn hình · chuột phải để mở menu. Bài chưa có giọng thu sẵn: trình duyệt tự đọc nếu máy có giọng tiếng Việt, nếu không thì đọc phụ đề.

## 2. Chạy thật trên máy

Cần Python 3.11–3.13. Mọi lệnh chạy trong `src/`.

```bash
cd src
python3 -m venv .venv
source .venv/bin/activate            # Windows PowerShell: .\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m lab8.smoke                 # in ra: lab8.smoke pass
```

### Demo 1 — ticket nói dối (claim C-002)

Ticket ghi "trễ 5 ngày", dòng order `O-202` ghi `delay_days = 2`. Luật: trễ từ 3 ngày mới hoàn.

```bash
python -m lab8.run --shape swarm    --claim-id C-002 --seed 55 --db data/demo_swarm.sqlite
python -m lab8.run --shape workflow --claim-id C-002 --seed 55 --db data/demo_workflow.sqlite
```

| Shape | `status` | `proposal_amount` | Sổ |
| --- | --- | ---: | --- |
| swarm (seed 55) | `resolved` | 20000 | một refund 20.000 đ: **sai**, swarm tin ticket |
| workflow | `denied` (`no_entitlement`) | 0 | không có dòng nào: đúng |

Thay `workflow` bằng `single` hoặc `orchestrator` cũng ra `denied`.

Đọc trace để thấy chỗ sai (tệp ở `src/traces/`):

```text
R-swarm-C-002-s55.json      handoff → investigator (delay_days: 2) → model_override {"delay_days": 5} → quote 20000
R-workflow-C-002-s55.json   claim_view → order_view → quote 0 (no_entitlement) → decision denied
```

### Trace của bốn kiến trúc trên cùng một claim (C-001, seed 11)

```bash
python -m lab8.run --shape workflow     --claim-id C-001 --seed 11 --db data/demo_a.sqlite
python -m lab8.run --shape single       --claim-id C-001 --seed 11 --db data/demo_b.sqlite
python -m lab8.run --shape orchestrator --claim-id C-001 --seed 11 --db data/demo_c.sqlite
python -m lab8.run --shape swarm        --claim-id C-001 --seed 11 --db data/demo_d.sqlite
```

Cả bốn ra `resolved`, một refund 35.000 đ. Khác nhau ở trace (`src/traces/R-<shape>-C-001-s11.json`) và chi phí:

| Shape | Các event trong trace | Gọi model | Gọi tool | Chi phí mô phỏng |
| --- | --- | ---: | ---: | ---: |
| A workflow | `claim_view` → `order_view` → `quote` → `decision` | 1 | 3 | 30.94 |
| B single | 3 × (`react_step` → kết quả tool) → `decision` (propose_refund) → `host_gate` | 4 | 4 | 42.18 |
| C orchestrator | `handoff` (allowlist, 3 tool chỉ đọc) → `investigator` → `quote` → `write` | 1 | 4 | 40.42 |
| D swarm | `handoff` → `investigator` → `quote` | 3 | 5 | 52.30 |

Không trace nào chứa `CANARY_SECRET_*`, `Bearer`, số điện thoại, địa chỉ hay ticket nguyên văn (quét toàn bộ `src/traces/`: 0 lần).

### Demo 2 — crash rồi chạy lại (claim C-012)

```bash
python -m lab8.run --shape workflow --claim-id C-012 --seed 11 --db data/demo_crash.sqlite --crash-at after_effect_before_checkpoint
python -m lab8.run --shape workflow --claim-id C-012 --seed 11 --db data/demo_crash.sqlite
```

Lệnh đầu in `{"crashed": true, "at": "after_effect_before_checkpoint", ...}`: tiền đã ghi, checkpoint chưa lưu. Lệnh thứ hai (cùng DB) ra `resolved` với đúng **một** `refund_effects` khóa `refund:C-012` và `committed_audit_count` = 1.

Phản ví dụ, khi chỉ dựa vào checkpoint:

```bash
python -m lab8.demo.buggy_workflow   # in ra: unsafe refund rows: 2 (the host ledger must stay at 1)
```

Cả bộ 20 ca crash:

```bash
python -m lab8.crash_test --count 20 --out reports/crash.json   # crash_safety = 20/20
```

### Toàn bộ phần đã làm

| Việc | Lệnh | Kết quả đã đo |
| --- | --- | --- |
| Cổng host | `python -m pytest -q` | 129 passed, 248 deselected |
| Ma trận student T01–T14 trên 4 shape | `python -m pytest -q -m student -o addopts=` | 248 passed (62 mỗi shape) |
| Benchmark 4 shape × 5 seed | `python -m lab8.benchmark --shapes workflow,single,orchestrator,swarm --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/benchmark.json` | bảng dưới |
| Kiểm format bài nộp | `python -m lab8.check_submission` | 0 FAIL |
| Nghiên cứu R1 (đọc song song) | `python -m bonus.timing_report --seeds 11,22,33,44,55 --reps 5 --out reports/bonus_timing.json` | speedup 0,835: giả thuyết sai |
| Bonus B3 (swarm có verifier) | `python -m pytest -q tests/test_bonus_swarm_verified.py` | 22 passed |

Benchmark public (14 claim × 5 seed, nguồn `src/reports/benchmark.json`):

| Shape | Người viết | Pass rate | Pass^5 | Cost/success (VND mô phỏng) |
| --- | --- | ---: | ---: | ---: |
| A workflow | Đào Huy Hoàng | 1.000 | 1.000 | 28.78 |
| B single | Ngô Đức Thịnh | 1.000 | 1.000 | 38.40 |
| C orchestrator | Lê Hồng Quân | 1.000 | 1.000 | 36.82 |
| D swarm (có sẵn) | Phan Trọng Hậu (đối chứng, B3) | 0.986 | 0.929 | 49.57 |

Nhóm chọn **workflow**: cùng độ đúng với B và C, rẻ hơn, và ít tự chủ nhất. Lý do đầy đủ: [`report/team/decision_adr.md`](report/team/decision_adr.md).

## Giới hạn

- Model là MockLLM, chi phí là giá mô phỏng, benchmark không đo độ trễ.
- Kết quả trên bộ hidden (40 claim × 5 seed) chưa có: chờ giảng viên chấm.
- Các tệp `data/demo_*.sqlite` và `traces/` sinh ra khi chạy demo đã nằm trong `.gitignore`. Muốn chạy lại từ đầu thì xóa tệp `.sqlite` tương ứng.

## Dựng lại bài trình bày

Nguồn của bài nằm trong repo `motion-builder`, thư mục `lessons/vinuni/lab-08/logix-bon-kien-truc/`. Dựng lại: `./motion.sh logix-bon-kien-truc`, rồi chép `dist/vinuni/lab-08/logix-bon-kien-truc.html` vào `demo/`.
