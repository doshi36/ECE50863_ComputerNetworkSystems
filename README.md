This repository contains three projects:

A. Software-Defined Networking (SDN) Infrastructure

This project focuses on architecting and deploying a robust Software-Defined Networking (SDN) infrastructure to enhance network resilience and optimize data flow. The solution integrates multiple switches and a centralized controller, using C++ and Python for seamless interaction and control.

Key Features:
1. Dynamic Network Topology Management
Designed and implemented real-time topology management to adapt to network changes dynamically.
2. Node and Link Failure Detection & Recovery
Developed mechanisms for detecting and recovering from node and link failures, leveraging periodic messaging protocols for real-time updates.
3. Centralized Controller Integration
Orchestrated communication between multiple switches and a centralized controller for streamlined network operations.

Impact:
1. Enhanced network resilience through automated failure detection and recovery mechanisms.
2. Optimized data flow, reducing latency and ensuring consistent network performance.
   
Tools & Technologies:
1. Languages: C++, Python
2. Networking Concepts: SDN principles, centralized control, messaging protocols
3. Metrics for Success: Efficient fault recovery and improved data flow management

B. Adaptive Bitrate Streaming Optimization

This project focuses on developing an advanced Adaptive Bitrate Streaming (ABR) system to enhance the quality of experience (QoE) for video streaming users. By combining the best features of BBA-2 (Buffer-Based Algorithm) and Robust-MPC (Model Predictive Control), the solution delivers seamless video playback with minimal rebuffering and smoother quality transitions.

Key Features:
1. Optimized Adaptive Bitrate Algorithm
Designed and integrated a custom ABR algorithm that combines the strengths of BBA-2 and Robust-MPC for improved QoE.
2. Dynamic Lookahead Window
Implemented a dynamic lookahead mechanism to predict video throughput accurately, minimizing rebuffering events during playback.
3. Quality Variation Fine System (QVFS)
Developed a Quality Variation Fine System that applies penalties for frequent quality changes, reducing unnecessary switches in streaming throughput and ensuring a more stable viewing experience.

Impact:
1. Improved user experience by minimizing video rebuffering and reducing quality variations.
2. Enhanced streaming efficiency with accurate throughput predictions and balanced buffer management.
3. Delivered smoother and consistent playback, optimizing network utilization.

Tools & Technologies:
1. Languages: Python, C++
2. Techniques: Network programming, adaptive bitrate streaming algorithms
3. Metrics for Success: Reduced rebuffering events, minimized quality switches, and improved QoE scores.

C. Project: TCP Protocol Ablation Study and Reliable Data Transmission Optimization

This project focuses on designing and implementing a reliable data transmission protocol tailored to achieve high goodput and low overhead under diverse network conditions. By integrating advanced flow control mechanisms, including stop-and-go and sliding window techniques, and introducing cumulative acknowledgment (ACK) functionality, the project explores the trade-offs between speed, reliability, and network congestion management.

Key Features:
1. TCP Protocol Implementation
Developed core TCP functionality with stop-and-go and sliding window mechanisms, enhancing network efficiency and data flow.
2. Cumulative Acknowledgment (ACK) Optimization
Implemented cumulative ACK to reduce individual acknowledgments, boosting throughput and minimizing overhead.
3. Performance Analysis of Flow Control Methods
Conducted a comparative study of implemented flow control mechanisms, evaluating their impact on speed, reliability, and network congestion management under varied conditions.

Objectives:
1. Design a custom protocol to maximize goodput while minimizing network resource consumption.
2. Benchmark performance against a baseline scheme for comparative analysis.
3. Document design trade-offs and performance across different network scenarios, providing clear insights into protocol efficiency.

Key Deliverables:
1. Protocol Design and Implementation:
Developed an optimized data transmission protocol that balances performance and reliability.
2. Baseline Implementation:
Created a baseline scheme to serve as a benchmark for comparison.

Performance Evaluation Report:
1. Documented findings and evaluated performance metrics (e.g., goodput, overhead, latency) under diverse network conditions.
2. Analyzed design trade-offs and the impact of optimizations on protocol behavior.

Tools & Technologies:
1. Languages: Python, C++
2. Concepts: TCP/IP Suite, flow control mechanisms, network programming
3. Evaluation Metrics: Goodput, latency, overhead reduction, and congestion management performance.
