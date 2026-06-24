# Lab Guide: Multi-Agent Research System

## Scenario

Bạn cần xây dựng một research assistant có thể nhận câu hỏi dài, tìm thông tin, phân tích và viết câu trả lời cuối cùng. Lab yêu cầu so sánh hai cách làm:

1. **Single-agent baseline**: một agent làm toàn bộ.
2. **Multi-agent workflow**: Supervisor điều phối Researcher, Analyst, Writer.

## Quy tắc quan trọng

- Không thêm agent nếu không có lý do rõ ràng.
- Mỗi agent phải có responsibility riêng.
- Shared state phải đủ rõ để debug.
- Phải có trace hoặc log cho từng bước.
- Phải benchmark, không chỉ nhìn output bằng cảm tính.

## Milestone 1: Baseline

File gợi ý:

- `src/multi_agent_research_lab/cli.py`
- `src/multi_agent_research_lab/services/llm_client.py`

TODO(student): thay baseline placeholder bằng một call LLM thật.

## Milestone 2: Supervisor

File gợi ý:

- `src/multi_agent_research_lab/agents/supervisor.py`
- `src/multi_agent_research_lab/graph/workflow.py`

TODO(student): implement routing policy.

Gợi ý câu hỏi thiết kế:

- Khi nào gọi Researcher?
- Khi nào gọi Analyst?
- Khi nào gọi Writer?
- Khi nào stop?
- Nếu agent fail thì retry hay fallback?

## Milestone 3: Worker agents

File gợi ý:

- `agents/researcher.py`
- `agents/analyst.py`
- `agents/writer.py`

TODO(student): implement từng worker.

## Milestone 4: Trace và benchmark

File gợi ý:

- `observability/tracing.py`
- `evaluation/benchmark.py`
- `evaluation/report.py`

Benchmark tối thiểu:

| Metric | Cách đo gợi ý |
|---|---|
| Latency | wall-clock time |
| Cost | token usage hoặc provider usage |
| Quality | rubric 0-10 do peer review |
| Citation coverage | số claims có source / tổng claims chính |
| Failure rate | số query fail / tổng query |

## Exit ticket

Mỗi nhóm trả lời 2 câu:

1. **Case nào nên dùng multi-agent? Vì sao?**
   - **Trả lời**: Nên dùng cho các tác vụ phức tạp, cần thu thập thông tin từ nhiều nguồn, phân tích dữ liệu chuyên sâu qua nhiều góc nhìn và kiểm duyệt chéo nội dung (ví dụ: làm báo cáo nghiên cứu học thuật, viết phân tích thị trường, phân tích rủi ro tài chính).
   - **Vì sao**: Nhờ cơ chế tách biệt vai trò (Separation of Concerns), từng Agent có thể tập trung vào một nhiệm vụ nhỏ (Researcher gom nguồn, Analyst đánh giá rủi ro, Writer viết báo cáo, Critic phản biện lỗi sai). Điều này giúp tối ưu hóa Prompts cho từng tác nhân, giảm thiểu tối đa hiện tượng ảo giác (hallucination) của LLM khi phải xử lý quá nhiều bối cảnh cùng lúc, và cho phép thiết lập vòng phản hồi kiểm soát chất lượng (Refinement loops).

2. **Case nào không nên dùng multi-agent? Vì sao?**
   - **Trả lời**: Không nên dùng cho các tác vụ đơn giản, mang tính chất một chiều (single-turn) và yêu cầu phản hồi tức thì với độ trễ thấp (ví dụ: chatbot giải đáp nhanh, sửa lỗi chính tả/ngữ pháp cơ bản, tóm tắt bài viết ngắn).
   - **Vì sao**: Hệ thống đa tác nhân tốn chi phí điều phối (orchestration overhead) lớn và phải thực hiện nhiều cuộc gọi API LLM liên tiếp. Điều này làm tăng độ trễ thời gian thực thi (Latency tăng từ ~12s lên ~47s như kết quả benchmark thực tế) và làm tăng chi phí sử dụng token lên gấp nhiều lần. Đối với các tác vụ đơn giản, một tác nhân đơn lẻ (Single-Agent Baseline) có thể xử lý cực kỳ nhanh chóng và tiết kiệm chi phí tối đa.


