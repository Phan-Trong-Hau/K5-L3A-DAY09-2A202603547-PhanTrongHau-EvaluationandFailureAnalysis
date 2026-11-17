# Trace case — tìm quyết định sai đầu tiên

Phan Trọng Hậu · MSSV 2A202603547 · GitHub Phan-Trong-Hau · ngày 17/11/2026.

Trial: `seeded_regression C-002@11`, run `E-seeded_regression-20261117-266d`. [Report](../src/reports/lab9/seeded_regression_v1.json), [trace lỗi](../src/reports/lab9/trace_case_broken.log), [đối chứng](../src/reports/lab9/trace_case_fixed.log).

| Trường | Bằng chứng |
|---|---|
| Triệu chứng | Status resolved thay vì denied; ledger 20000 thay vì 0; 1 refund thay vì 0. |
| Bước sai đầu tiên | Event **3**, `model_override`, payload `{"delay_days":5}`. |
| Trước bước đó | Event 1 handoff giới hạn công cụ và principal; event 2 investigator trả DB O-202 với delay_days=2. Hai bước này cung cấp phạm vi và dữ kiện đúng. |
| Chuỗi hậu quả | Ticket ghi trễ 5 ngày → ghi đè DB 2 → event 4 quote 20000 → event 6 reply xác nhận 20000; ledger ghi tiền ngoài quyền lợi. |
| Failure mode | FM-03; `db_fact_kept=False`, `proposal_amount_correct=False`, `refund_amount_correct=False`, `pass_rate=False`. |
| Đối chứng | Cùng C-002@11 trên fixed không có model_override; quote=0, denied, ledger=0, graders trên đều True. |
| Regression chạy được | `tests/test_lab9_regressions.py::test_lab9_trace_ticket_override_regression`; assert lỗi trên seeded_regression và đạt trên fixed. E-002 cũng nằm trong eval set. |
| Chưa chứng minh | Trace xác định lần ghi đè đầu tiên quan sát được, không cho thấy suy luận nội bộ model; MockLLM không đại diện production. |

```bash
cd src
python -m lab9.trace_case --shape seeded_regression --claim C-002 --seed 11
python -m lab9.trace_case --shape fixed --claim C-002 --seed 11
python -m pytest -q -m student -o addopts= -k lab9_trace_ticket_override
```

Một regression bổ sung kiểm FM-08: `test_lab9_misreport_correct_ledger_is_still_a_failure`. C-008@11 có ledger đúng 20000, Lab8 pass, nhưng reply sai 35000; grader mới phải fail. `test_lab9_honest_paraphrase_has_no_reply_false_alarm` kiểm cách diễn đạt khác vẫn đạt. [Trace FM-08](../src/reports/lab9/trace_FM-08.json).
