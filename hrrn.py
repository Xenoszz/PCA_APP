import matplotlib.pyplot as plt
import numpy as np

def hrrn_scheduling(input):
    input = [input[:-1] for input in input]
    processes = []
    for i in range(len(input)):
        processes.append((input[i][0], input[i][1], input[i][2]))

    # Initialize waiting and turnaround times
    waiting_times = []
    turnaround_times = []
    execution_order = []  # To keep track of the order of executed processes
    current_time = processes[0][1]  # Use start time (arrival time)
    

    while True:
        # Select available processes
        available_processes = [p for p in processes if p[1] <= current_time and (len(p) < 4 or p[3] is None)]

        if not available_processes:
            # No available processes, increment current time and check for a timeout
            if current_time - processes[0][1] > 100:  # Timeout condition to avoid infinite loop
                break
            current_time += 1
            continue

        # Calculate Highest Response Ratio
        hrrn_values = []
        for p in available_processes:
            response_ratio = (p[2] + (current_time - p[1])) / p[2]  # p[2] is CPU time
            hrrn_values.append((response_ratio, p))

        # Select the process with the highest response ratio
        next_process = max(hrrn_values, key=lambda x: x[0])[1]

        # Update time and calculate waiting time and turnaround time
        current_time += next_process[2]  # next_process[2] is CPU time
        waiting_time = current_time - next_process[1] - next_process[2]  # waiting time
        turnaround_time = current_time - next_process[1]  # turnaround time
        
        waiting_times.append(waiting_time)
        turnaround_times.append(turnaround_time)
        # Mark the process as completed (update waiting and turnaround times)
        processes[processes.index(next_process)] = (*next_process[:3], waiting_time, turnaround_time)  # Update the process tuple with waiting and turnaround times

        # Add the executed process to the execution order
        execution_order.append(next_process)

        if all(len(p) == 4 for p in processes):  # Check if all processes are completed
            break

    return waiting_times, turnaround_times, execution_order

def plot_gantt_chart(processes, ax):
    
    processes.sort(key=lambda x: x[1])
    
    current_time = processes[0][1]
    colors = plt.cm.tab20.colors  # ชุดสีทั้งหมดที่จะใช้
    color_mapping = {}  # พจนานุกรมสำหรับเก็บสีที่สัมพันธ์กับ process_id

    for i, process in enumerate(processes):
        process_id, start_time, cpu_time = process[:3]

        # เช็คว่า process_id นี้เคยใช้สีไปแล้วหรือยัง ถ้ายังให้เพิ่มสีใหม่เข้าไป
        if process_id not in color_mapping:
            color_mapping[process_id] = colors[len(color_mapping) % len(colors)]

        # วาดแถบ Gantt Chart โดยให้ process เดียวกันใช้สีเดียวกัน
        ax.barh(0, cpu_time, left=current_time, color=color_mapping[process_id], edgecolor='black', align='center')

        # แทรกข้อความ process_id ลงในแถบ Gantt Chart
        ax.text(current_time + cpu_time / 2, 0, process_id, ha='center', va='center', color='white', fontsize=10)

        # อัปเดตเวลาปัจจุบัน
        current_time += cpu_time

    count = current_time // 15
    
    # ตั้งค่าภาพ Gantt Chart
    ax.set_yticks([0])
    ax.set_yticklabels(["Processes"])
    ax.set_xlabel("Time")
    ax.get_yaxis().set_visible(False)  # ซ่อนแกน Y
    ax.set_xticks(np.arange(int(processes[0][1]), int(current_time) + 1, count))