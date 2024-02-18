# Project 2: Designing and Optimizing a Reliable Data Transmission Protocol

In this project, your goal is to design and implement a reliable transfer protocol that can achieve high goodput, and low overhead under diverse network conditions. You will compare your protocol with a baseline scheme for comparison, which you will also implement.  While we provide hints, the specific optimizations that you will implement in your protocol is up to you. While correctness of all implementations is a minimal requirement, the project will be primarily evaluated on (i) the kinds of optimizations you implement; (ii) the performance that you achieve; and (iii) a documentation of the performance of the schemes under different network conditions, along with a clear understanding of the design trade-offs. You will document the above information in a report, which is a mandatory requirement for the project.

## Running your code
------------
We will be testing your code using the configuration files similar to the ones provided under TestConfig in the starter code. The network emulator will be launched before the endpoints.

### Important
Do not modify the Emulator, Monitor.

## What you need to submit on Gradescope
------------

For code submission (both interim code submission), you will need to submit 4 files:

 * receiver.py (The receiver of your optimized protocol)
 * receiver_stop_and_go.py (The receiver of your stop and go implementation)
 * sender.py (The sender of your optimized protocol)
 * sender_stop_and_go.py (The sender of your stop and go implementation)

Note that the name of the file must be matching exactly as the one listed above to prevent auto grader failure. Please do not submit zip file or directory.

You'll also need to submit report based on the provided template, and following all the guidelines.

## Grading
A minimal expectation for all protocol implementations is correctness. A major criterion for grading is your performance results, whether the overall trends make sense, and the effort and creativity you have shown in adding optimizations. The clarity of report (documenting the effort, appropriately presenting graphs and containing the right level of detail in the writing) will also be a factor.
