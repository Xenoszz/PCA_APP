import matplotlib.pyplot as plt
import numpy as np

def srtf(input):
    processes = []
    for i in range(len(input)):
        processes.append((input[i][0], input[i][1], input[i][2]))

    n = len(processes)
    remaining_time = [process[2] for process in processes]      
    current_time = 0
    completed = 0
    waiting_time = [0] * n
    turnaround_time = [0] * n
    gantt_chart = []  

    while completed < n:
        available = [i for i in range(n) if processes[i][1] <= current_time and remaining_time[i] > 0]

        if available:
            process_in_queue = min(available, key=lambda i: remaining_time[i])

            if not gantt_chart or gantt_chart[-1][2] != processes[process_in_queue][0]:
                gantt_chart.append((current_time, None, processes[process_in_queue][0]))

            remaining_time[process_in_queue] -= 1
            current_time += 1

            if remaining_time[process_in_queue] == 0:
                completed += 1
                finish_time = current_time
                turnaround_time[process_in_queue] = finish_time - processes[process_in_queue][1]
                waiting_time[process_in_queue] = turnaround_time[process_in_queue] - processes[process_in_queue][2]

                gantt_chart[-1] = (gantt_chart[-1][0], finish_time, gantt_chart[-1][2])
        else:
            current_time += 1
    context = []

    for i in range(len(gantt_chart)):
        if i == len(gantt_chart) - 1:
            context.append((gantt_chart[i][2], gantt_chart[i][0], gantt_chart[i][1] - gantt_chart[i][0]))
            break
        context.append((gantt_chart[i][2], gantt_chart[i][0], gantt_chart[i + 1][0] - gantt_chart[i][0]))

    return waiting_time, turnaround_time, context

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