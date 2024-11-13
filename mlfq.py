import time
import queue
import matplotlib.pyplot as plt
import numpy as np

# ฟังก์ชันจำลองการทำงานของ process
def worker_process(burst_time):
    time.sleep(burst_time/1000)


# ฟังก์ชันสำหรับ Multilevel Queue Scheduling with Feedback
def multilevel_queue_scheduling(input):
    process_data = []
    for i in range(len(input)):
        process_data.append((input[i][0], input[i][1], input[i][2]))

    # คิวหลายระดับ (ระดับ 1, 2, 3 โดยระดับ 1 มี priority สูงสุด)
    level_queues = [queue.Queue() for _ in range(3)]
    time_quantums = [3, 6, 12]  # time quantum สำหรับแต่ละคิว

    # เรียงข้อมูล process ตาม arrival_time
    process_data.sort(key=lambda x: x[1])

    current_time = 0  # เริ่มต้นเวลา
    process_index = 0  # ตัวชี้ตำแหน่งของ process
    remaining_time = {name: burst_time for name, _, burst_time in process_data}  # สร้าง dictionary สำหรับเก็บเวลาที่เหลือของแต่ละ process
    finished_time = {}  # เก็บเวลาที่ process เสร็จสิ้น
    context = []
    
    
    # ทำงานจนกว่าคิวทั้งหมดจะว่างหรือ process ทั้งหมดเสร็จสิ้น
    while process_index < len(process_data) or any(not q.empty() for q in level_queues):
        # เพิ่ม process ใหม่ลงในคิวถ้าถึงเวลา
        while process_index < len(process_data) and process_data[process_index][1] <= current_time:
            level_queues[0].put(process_data[process_index])
            process_index += 1

        # เช็คว่ามีโปรเซสไหนในระดับคิวแรกให้ทำ
        for level, quantum in enumerate(time_quantums):
            if not level_queues[level].empty():
                process = level_queues[level].get()
                name, arrival_time, burst_time = process
                
                # รันโปรเซสตาม time quantum ที่กำหนด
                time_to_run = min(remaining_time[name], quantum)
                process_tuple = (name, current_time , time_to_run)
                context.append(process_tuple)
                # จำลองการทำงาน
                worker_process(time_to_run)

                # อัปเดตเวลาที่เหลือ
                remaining_time[name] -= time_to_run
                current_time += time_to_run  # อัปเดตเวลารวม

                # ถ้าโปรเซสทำงานเสร็จ
                if remaining_time[name] == 0:
                    finished_time[name] = current_time
                else:
                    # ถ้ายังไม่เสร็จ ย้ายโปรเซสไปยังคิวถัดไป ถ้าอยู่ในระดับคิว 1 หรือ 2
                    if level + 1 < len(level_queues):
                        level_queues[level + 1].put((name, 0, remaining_time[name]))
                    else:
                        # ถ้าอยู่ในคิวสุดท้ายแล้วยังไม่เสร็จ ให้ต่อคิวที่ระดับเดิม (level 3)
                        level_queues[level].put((name, 0, remaining_time[name]))

                break

        else:
            # ถ้าไม่มีโปรเซสไหนในคิวพร้อมทำงาน ให้เพิ่มเวลาไปข้างหน้า
            if process_index < len(process_data):
                next_process_time = process_data[process_index][1]
                current_time = max(current_time + 1, next_process_time)
            else:
                current_time += 1

    # เพิ่ม finished_time ลงใน process_data
    new_process_data = []  # เก็บผลลัพธ์ใหม่
    
    for process in process_data:
        name = process[0]  # ชื่อ process
        if name in finished_time:  # ตรวจสอบว่าชื่อ process อยู่ใน finished_times หรือไม่
            # แปลง tuple เป็น list เพื่อให้สามารถ append ได้
            process_list = list(process)
            process_list.append(finished_time[name])  # เพิ่ม finished_time เข้าไปใน list
            new_process_data.append(tuple(process_list))  # แปลงกลับเป็น tuple และเพิ่มเข้า new_process_data
        else:
            new_process_data.append(process)  # ถ้าไม่มี finished_time ก็เก็บ process เดิมไว้
    
    waiting_times = []
    turnaround_times = []
    
    for process in new_process_data:
        waiting_times.append(process[3] - process[1] - process[2])
        turnaround_times.append(process[3] - process[1])
        
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