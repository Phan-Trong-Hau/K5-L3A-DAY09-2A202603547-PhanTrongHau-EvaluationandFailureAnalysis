# Lab09 — Evaluation and Failure Analysis

Phan Trọng Hậu · 2A202603547.

Báo cáo chính: [report/2A202603547-PhanTrongHau.md](report/2A202603547-PhanTrongHau.md).

| Yêu cầu | File triển khai / bằng chứng |
| --- | --- |
| M0: taxonomy và trace | [Taxonomy](../../docs/failure_taxonomy.md), [trace case](../../docs/trace_case.md) |
| M1: eval set, nhãn tách và provenance | [evalset.py](evalset.py), [dữ liệu v1/v2](../data/eval/) |
| M2: calibration và audit 5 case | [stats.py](stats.py), [judge.py](judge.py), [judge audit](../../docs/judge_audit.md) |
| M3: code graders và FM-08 | [graders.py](graders.py), [spec v1](../config/metric_spec.yaml) |
| M4: paired bootstrap và gate | [gate.py](gate.py), [baseline v1](../reports/baseline_v1.json) |
| M5: adversarial và slice gate | [spec v2](../config/metric_spec_v2.yaml), [FM map](../config/fm_map.yaml) |
| M6: pass@k, pass^k và A/A | [stats.py](stats.py), [A/A v2](../reports/lab9/aa_v2.json) |
| M7: integrity và ratchet | [gate.py](gate.py), [trap log](../reports/lab9/traps.log) |
| Báo cáo yêu cầu | [PRD v1.1](../../docs/PRD_v1.1.md), [eval card](../../docs/eval_card.md) |
| Tái lập và kết quả | [report.py](report.py), [summary](../reports/lab9/summary.json), [406 test đạt](../reports/lab9/full_tests.log) |

Báo cáo chính và code nằm trong thư mục Lab09 này. Các template `docs/`, cấu hình `src/config/`, dữ liệu `src/data/eval/` và baseline `src/reports/` giữ đường dẫn do công cụ/CI Lab09 sử dụng. Các liên kết trên dẫn tới bản tài liệu tương ứng để tránh nhiều bản khác nhau.

Chạy từ **thư mục `src/`** sau khi activate venv:

```bash
python -m lab9.smoke
python -m lab9.evalset --check
python -m lab9.evalset --v2
python -m lab9.report
python -m pytest -q -m student -o addopts= -k lab9
```

Kết quả ghi trong báo cáo lấy từ lần chạy đã lưu: v2 chặn 3/3 hồi quy, cho qua fixed/honest_refactor, chặn 4/4 public integrity trap. Giới hạn và phần audit người thực hiện xác nhận được ghi rõ trong báo cáo chính.

Đối chiếu các khoản trừ điểm, trạng thái Bonus và Expert: [PenaltyExpertAudit.md](report/PenaltyExpertAudit.md).

## Bonus Inspect AI

[BonusInspectAI.md](report/BonusInspectAI.md): port 3 grader, khớp 3372/3372 phép chấm. Từ `src/`, cài `python -m pip install -r requirements.txt -r requirements-lab9-bonus.txt`, chạy `python -m lab9.bonus`. Inspect là dependency tùy chọn, core CI giữ nguyên.

## Slide HTML để học và đọc

[2A202603547-PhanTrongHau-Lab09-Slides.html](report/2A202603547-PhanTrongHau-Lab09-Slides.html): 43 slide offline, sơ đồ minh họa, từ điển 141 thuật ngữ, ví dụ pass@k/pass^k tương tác, chế độ đọc và In/PDF. Mở trực tiếp bằng trình duyệt.
