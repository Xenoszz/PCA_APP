import matplotlib.pyplot as plt
import numpy as np

def round_robin_scheduler(input):
    processes = []
    for i in range(len(input)):
        processes.append((input[i][0], input[i][1], input[i][2]))

    time_quantum = 3
    n = len(processes)
    remaining_time = [p[2] for p in processes]
    completion_time = [0] * n
    waiting_time = [0] * n
    turnaround_time = [0] * n
    gantt_chart = []
    time = min(p[1] for p in processes)  # เริ่มที่เวลามาถึงของโพรเซสแรก
    ready_queue = []
    # ดำเนินการจนกว่าจะประมวลผลทุกโพรเซสเสร็จ
    while True:
        # เพิ่มโพรเซสที่มาถึงแล้วเข้า ready queue
        for i, process in enumerate(processes):
            if process[1] <= time and remaining_time[i] > 0 and i not in ready_queue:
                ready_queue.append(i)
        if not ready_queue:  # ถ้า ready queue ว่าง
            if all(rt == 0 for rt in remaining_time):  # ถ้าทุกโพรเซสเสร็จแล้ว
                break
            # ข้ามไปยังเวลาที่โพรเซสถัดไปมาถึง
            next_arrival = min((p[1] for i, p in enumerate(processes) if remaining_time[i] > 0), default=time)
            time = max(time, next_arrival)
            continue

        # ประมวลผลโพรเซสปัจจุบัน
        current_process = ready_queue.pop(0)
        execute_time = min(time_quantum, remaining_time[current_process])
        # บันทึกลงใน Gantt chart
        gantt_chart.append((processes[current_process][0], time, time + execute_time))
        # อัปเดตเวลาที่เหลือและเวลาปัจจุบัน
        remaining_time[current_process] -= execute_time
        time += execute_time

        # ถ้าโพรเซสยังไม่เสร็จ ให้ใส่กลับเข้า ready queue
        if remaining_time[current_process] > 0:
            ready_queue.append(current_process)
        else:  # ถ้าโพรเซสเสร็จแล้ว คำนวณเวลาต่างๆ
            completion_time[current_process] = time
            turnaround_time[current_process] = completion_time[current_process] - processes[current_process][1]
            waiting_time[current_process] = turnaround_time[current_process] - processes[current_process][2]

    context = []
    for i in range(len(gantt_chart)):
        if i == len(gantt_chart) - 1:
            context.append((gantt_chart[i][0], gantt_chart[i][1], gantt_chart[i][1] - gantt_chart[i][2]))
            break
        context.append((gantt_chart[i][0], gantt_chart[i][1], gantt_chart[i + 1][1] - gantt_chart[i][1]))
    
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