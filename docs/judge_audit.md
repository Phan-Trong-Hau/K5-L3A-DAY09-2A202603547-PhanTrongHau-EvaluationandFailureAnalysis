# Judge audit — Lab09

Phan Trọng Hậu · MSSV 2A202603547 · GitHub Phan-Trong-Hau · ngày 17/11/2026.

| Tiêu chí | n | κ | Precision | Recall | Đạt floors? | Quyết định |
|---|---|---|---|---|---|---|
| tone_ok | 100 | 0.757 | 0.857 | 0.8 | Có | Dùng cho tone replay |
| helpful | 100 | 0.375 | 1.0 | 0.3 | Không | Loại khỏi gate |

FAIL là lớp dương. Floors: κ≥0.6, precision≥0.8, recall≥0.7. Chạy `python -m lab9.judge --csv data/eval/judge_tone_public.csv --audit 5` và đổi sang `judge_helpful_public.csv` cho helpful.

| Tiêu chí | TP | FP | FN | TN | Fail quan sát | Rogan–Gladen |
|---|---|---|---|---|---|---|
| tone_ok | 24 | 4 | 6 | 66 | 0.28 | 0.3 |
| helpful | 9 | 0 | 21 | 70 | 0.09 | 0.3 |

## Năm case audit có người xác nhận

Đối chiếu toàn bộ reply trong CSV, không chỉ xét tiền. Người thực hiện xác nhận đồng ý cả 5 nhận xét trong trao đổi ngày 17/11/2026. Cột Người là nhãn human có sẵn; nhận xét là phần rà soát được xác nhận, không phải thu thập một tập nhãn độc lập mới.

| Case | Người nói | Judge nói | Ai đúng? | Lý do |
|---|---|---|---|---|
| H-008 | FAIL | PASS | Người | “em…anh…nha…check” quá suồng sã cho giọng CSKH yêu cầu. |
| H-017 | FAIL | PASS | Người | “bạn ơi…rồi nha” không nhất quán cách xưng hô chuyên nghiệp. |
| H-029 | FAIL | PASS | Người | “không cần nhắn thêm” mang tính gạt bỏ khách hàng. |
| H-042 | PASS | FAIL | Người | Thông báo khoản hoàn và thời gian rõ, có “Dạ/ạ”. |
| H-051 | PASS | FAIL | Người | “refund” là từ vay mượn, chưa đủ để kết luận giọng điệu bất lịch sự. |

Helpful bỏ sót 21/30 lỗi (recall 0.3), κ=0.375; precision 1.0 không bù được các lỗi bị bỏ sót. Tone đạt floors nhưng vẫn có 6 false negative và 4 false positive; chỉ đủ điều kiện dùng cho tiêu chí giọng điệu trong phạm vi replay. Gate tiền/approval hiện chỉ dùng code; chưa tích hợp tone vào chặn release. Rogan–Gladen cho tỷ lệ 0.3 trên cả hai CSV, không làm helpful trở thành classifier đạt chuẩn.

Giới hạn: CSV đã công khai, có nhãn human, không phải held-out mới; một câu có tone tốt vẫn có thể sai tiền. [Kết quả máy](../src/reports/lab9/summary.json), [tone log](../src/reports/lab9/judge_tone.log), [helpful log](../src/reports/lab9/judge_helpful.log). Helpful CLI exit 1 là kết quả loại đúng theo floors.

## Hành động sửa rubric sau audit

| Case | Quy tắc cần bổ sung cho rubric tone |
|---|---|
| H-008 | Yêu cầu cách xưng hô CSKH nhất quán, tôn trọng; đánh dấu FAIL khi cả câu dùng giọng suồng sã như “em…anh…rồi nha…check giúp em”. Không quyết định chỉ bằng sự có mặt của từ “hoàn”. |
| H-017 | Chấm toàn câu, không cho PASS chỉ vì có “Dạ”; cụm “bạn ơi…rồi nha” trong ngữ cảnh này không đạt giọng CSKH đã chọn. |
| H-029 | Thêm tiêu chí không gạt bỏ khách: yêu cầu khách “không cần nhắn thêm” mà không hướng dẫn hỗ trợ tiếp theo là FAIL tone. |
| H-042 | Thêm ví dụ PASS: thông báo rõ khoản hoàn, thời gian dự kiến, giọng lịch sự “Dạ/ạ”; không bắt buộc câu dài hoặc đủ mọi từ mẫu. |
| H-051 | Không tự động FAIL vì từ vay mượn “refund” khi toàn câu vẫn rõ và lịch sự; chỉ đánh lỗi nếu gây khó hiểu hoặc giọng điệu không tôn trọng. |

Rubric helpful cần tách “lịch sự” khỏi “giúp khách giải quyết yêu cầu”: phải trả lời đúng vấn đề, có thông tin/hành động tiếp theo phù hợp; lời xin lỗi dài không tự động đạt helpful. Đây là đề xuất sửa rubric từ audit, **chưa** có tập nhãn mới hoặc judge mới được hiệu chuẩn. CSV replay và các số κ/P/R ở trên giữ nguyên; helpful tiếp tục bị loại. Trước khi dùng rubric mới làm gate, cần đánh giá lại trên dữ liệu held-out có nhãn người.
