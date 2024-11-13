from operator import itemgetter
import matplotlib.pyplot as plt
import numpy as np


# ฟังก์ชันสำหรับการทำงานแบบ Priority Scheduling
def priority_scheduling(input):
    processes = []
    for i in range(len(input)):
        processes.append((input[i][0], input[i][1], input[i][2], input[i][3]))

    # เรียงลำดับกระบวนการตามลำดับความสำคัญ  
    processes.sort(key=lambda x: x[3])
    current_time = 0  # เวลาปัจจุบัน
    waiting_times = []  # รายการเวลารอ (ผลลัพธ์)
    turnaround_times = []  # รายการเวลารวม (ผลลัพธ์)
    process_priorities = []  # รายการ Priority ของแต่ละ process

    # คำนวณ Waiting Time และ Turnaround Time
    for process in processes:
        pid, start_delay, burst_time, priority = process
        
        start_time = max(current_time, start_delay)  # เวลาเริ่มต้นต้องมากกว่าหรือเท่ากับเวลารอเริ่มต้น
        end_time = start_time + burst_time  # การสิ้นสุด process
        
        waiting_time = start_time - start_delay  # เวลาที่ process รอ
        turnaround_time = end_time - start_delay  # เวลาที่ process ใช้งานทั้งหมด
        
        # อัพเดทเวลา
        current_time = end_time

        # บันทึกค่า Waiting Time, Turnaround Time และ Priority
        waiting_times.append(waiting_time)
        turnaround_times.append(turnaround_time)
        process_priorities.append(priority)
    
    context = [(a, b, c) for (a, b, c, d) in processes]

    # คืนค่า Waiting Times, Turnaround Times และ Priority เพื่อใช้ใน Ui.py
    return waiting_times, turnaround_times, context

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