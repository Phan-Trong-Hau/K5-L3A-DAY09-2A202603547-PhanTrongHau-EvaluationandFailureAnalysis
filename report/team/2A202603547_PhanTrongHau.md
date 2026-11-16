# Báo cáo cá nhân — Phan Trọng Hậu

## 1. Thông tin thành viên

- Họ tên: Phan Trọng Hậu
- MSSV: 2A202603547
- Email: Không cung cấp
- GitHub: [Phan-Trong-Hau](https://github.com/Phan-Trong-Hau)

## 2. Phần việc phụ trách

- Shape D (`swarm`) làm baseline đối chứng và bonus B3: biến thể swarm có verifier dựa trên dữ liệu order có cấu trúc.
- Thêm bộ case đối kháng, kiểm thử, benchmark và báo cáo bonus.

## 3. Đóng góp cụ thể

- Tạo `src/bonus/swarm_verified.py`: kiểm chứng dữ kiện quote trước khi gọi host ghi refund; khi dữ kiện do swarm thay đổi không khớp order, tính lại quote từ order có cấu trúc.
- Tạo `src/bonus/workflow_baseline.py` làm baseline deterministic độc lập trong giai đoạn A còn stub. Benchmark B3 hiện đã chạy lại với Shape A chính thức.
- Tạo tám claim có nhãn viết tay trong `src/bonus/cases.jsonl` và world tương ứng trong `src/bonus/world.json`.
- Thêm kiểm thử cho các case đối kháng, workflow baseline, public T02 seed 55, trace verifier và resume sau crash trong `src/tests/test_bonus_swarm_verified.py`.
- Tạo `src/bonus/summarize_b3.py` và `src/reports/bonus_analysis.json` để đếm verifier override và trích trace minh họa.
- Commit chính: `87b2508` — Add verified swarm B3 bonus.

## 4. Bằng chứng

- Test: `python -m pytest -q tests/test_bonus_swarm_verified.py` — 22 passed; full default suite `python -m pytest -q` — 118 passed, 248 deselected; crash suite 20/20.
- Benchmark public: `src/reports/bonus_benchmark_public.json`, 70 trial mỗi shape; swarm pass rate 0.986, swarm_verified và workflow 1.000.
- Benchmark case đối kháng: `src/reports/bonus_benchmark_adversarial.json`, 40 trial mỗi shape; swarm pass rate 0.850, swarm_verified và workflow 1.000.
- Verifier can thiệp 1/70 trial public và 7/40 trial đối kháng (`src/reports/bonus_analysis.json`).
- Run ID ví dụ: `R-swarm_verified-C-002-s55`.
- B3 đã so sánh với Shape A chính thức; hidden benchmark còn chờ grader. Nhóm đã chọn workflow cho C2 và B3 làm bonus.

## 5. Công cụ AI đã dùng

- Codex hỗ trợ đọc yêu cầu, viết biến thể và test. Đã tự kiểm tra bằng 22 test, trace, ledger và benchmark tái lập được.

## 6. Tự đánh giá

B3 cải thiện kết quả của swarm trên T02 seed 55 và bộ tám case đối kháng trong benchmark hiện tại. Kết quả còn giới hạn ở MockLLM, dữ liệu public và case tự tạo; hidden vẫn cần grader xác nhận.
