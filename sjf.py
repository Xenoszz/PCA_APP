import matplotlib.pyplot as plt
import numpy as np

def sjf(input):
    processes = []
    for i in range(len(input)):
        processes.append((input[i][0], input[i][1], input[i][2]))

    n = len(processes)
    processes.sort(key=lambda x: (x[1], x[2]))  
    completed = [False] * n
    current_time = 0
    waiting_time = [0] * n
    turnaround_time = [0] * n
    completed_processes = 0
    gantt_chart = [] 

    while completed_processes < n:
        available = []
        for i in range(n):
            if not completed[i] and processes[i][1] <= current_time:
                available.append((processes[i][2], i)) 

        if available:
            available.sort() 
            idx = available[0][1]  
            process = processes[idx]
            start_time = current_time  
            gantt_chart.append((f"{process[0]}", start_time, process[2]))  
            current_time += process[2]  
            completed[idx] = True
            completed_processes += 1
            
            turnaround_time[idx] = current_time - process[1]
            waiting_time[idx] = turnaround_time[idx] - process[2]
        else:
            current_time += 1
            
    return waiting_time, turnaround_time, gantt_chart

def plot_gantt_chart(processes, ax):
    
    current_time = processes[0][1]
    colors = plt.cm.tab20.colors  # ชุดสีทั้งหมดที่จะใช้
    color_mapping = {}  # พจนานุกรมสำหรับเก็บสีที่สัมพันธ์กับ process_id

    for i, process in enumerate(processes):
        process_id, start_time, cpu_time = process

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