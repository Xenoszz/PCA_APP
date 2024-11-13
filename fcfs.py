import matplotlib.pyplot as plt
import numpy as np

def fcfs_scheduler(input):
    processes = []
    for i in range(len(input)):
        processes.append((input[i][0], input[i][1], input[i][2]))

    processes.sort(key=lambda x: x[1])
    waiting_times = []
    wt = waiting_times
    turnaround_time = []
    tat = turnaround_time
    n = len(processes)  # จำนวน process ทั้งหมด
    wt, tat, ct = [0] * n, [0] * n, [0] * n  # การจัดเตรียม list สำหรับ waiting time, turnaround time, และ completion time
    gantt_chart = []  # เก็บข้อมูล Gantt Chart
    current_time = float(processes[0][1])  # เริ่มที่เวลามาถึงของโพรเซสแรก

    # Process ตัวแรก
    ct[0] = current_time + processes[0][2]  # เวลาสิ้นสุดของ process แรก
    tat[0] = ct[0] - processes[0][1]  # turnaround time ของ process แรก
    wt[0] = tat[0] - processes[0][2]  # waiting time ของ process แรก
    gantt_chart.append((processes[0][0], current_time, ct[0]))  # บันทึกข้อมูลสำหรับ Gantt Chart
    current_time = ct[0]  # ปรับเวลาเป็นเวลาที่ process แรกเสร็จสิ้น

    # Process process ที่เหลือ
    for i in range(1, n):
        current_time = max(current_time, float(processes[i][1]))  # ปรับเวลาปัจจุบันถ้า process ที่มาถึงช้ากว่า
        ct[i] = current_time + processes[i][2]  # เวลาสิ้นสุดของ process
        tat[i] = ct[i] - processes[i][1]  # turnaround time
        wt[i] = tat[i] - processes[i][2]  # waiting time
        gantt_chart.append((processes[i][0], current_time, ct[i]))  # บันทึก Gantt Chart
        current_time = ct[i]  # ปรับเวลาเป็นเวลาที่ process เสร็จสิ้น
        
    context  = []   
    for i in range(len(gantt_chart)):
        if i == len(gantt_chart) - 1:
            context.append((gantt_chart[i][0], gantt_chart[i][1], gantt_chart[i][2] - gantt_chart[i][1]))
            break
        context.append((gantt_chart[i][0], gantt_chart[i][1], gantt_chart[i + 1][1] - gantt_chart[i][1]))

    return wt, tat, context

def plot_gantt_chart(processes, ax):
    # Sort processes based on their start time (second element of the tuple)

    current_time = processes[0][1]
    colors = plt.cm.tab20.colors  # Set of colors to use for Gantt chart
    color_mapping = {}  # Dictionary to store colors associated with process_id

    for process in processes:
        process_id, start_time, cpu_time = process[:3]  # Unpacking only the first three elements

        # Check if this process_id has been assigned a color; if not, assign a new color
        if process_id not in color_mapping:
            color_mapping[process_id] = colors[len(color_mapping) % len(colors)]

        # Draw the Gantt chart bar, using the color associated with this process_id
        ax.barh(0, cpu_time, left=current_time, color=color_mapping[process_id], edgecolor='black', align='center')

        # Insert process_id text into the Gantt chart bar
        ax.text(current_time + cpu_time / 2, 0, process_id, ha='center', va='center', color='white', fontsize=10)

        # Update the current time
        current_time += cpu_time

    count = current_time // 15
    # Set up Gantt chart aesthetics
    ax.set_yticks([0])
    ax.set_yticklabels(["Processes"])
    ax.set_xlabel("Time")
    ax.get_yaxis().set_visible(False)  # Hide the Y-axis
    ax.set_xticks(np.arange(int(processes[0][1]), int(current_time) + 1, count))  # Adjust X-ticks