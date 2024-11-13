import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import importlib
import random
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import sys

class ProcessSchedulerApp:
    def __init__(self, master):
        self.master = master
        master.title("Process Scheduling Algorithms")
        
        # Set initial window size and position
        window_width = 600
        window_height = 800
        
        # Get screen dimensions
        screen_width = master.winfo_screenwidth()
        screen_height = master.winfo_screenheight()
        
        # Calculate position for center of screen
        center_x = int(screen_width/2 - window_width/2)
        center_y = int(screen_height/2 - window_height/2)
        
        # Set window size and position
        master.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        
        # Set minimum window size
        master.minsize(850, 800)
        
        # Create main scrollable frame
        self.main_frame = tk.Frame(master)
        self.main_frame.pack(fill=tk.BOTH, expand=1)

        # Create a canvas
        self.canvas = tk.Canvas(self.main_frame, bg="white")
        self.scrollbar = ttk.Scrollbar(self.main_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg="white")

        # Configure the canvas
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        # Create a window in the canvas to hold the scrollable frame
        self.window_id = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        # Configure canvas to expand horizontally
        self.canvas.bind('<Configure>', self.on_canvas_configure)

        # Configure mousewheel scrolling
        self.scrollable_frame.bind('<Enter>', self._bound_to_mousewheel)
        self.scrollable_frame.bind('<Leave>', self._unbound_to_mousewheel)

        # Pack the canvas and scrollbar
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Configure the canvas to use the scrollbar
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Add this line to bind the close event
        master.protocol("WM_DELETE_WINDOW", self.on_close) 

        # Label for algorithm selection
        self.label = tk.Label(self.scrollable_frame, text="Select Scheduling Algorithm:", bg="white")
        self.label.grid(row=0, column=0, columnspan=4, pady=(10, 5))

        self.algorithms = ["All", "FCFS", "SJF", "Priority", "RoundRobin", "MLFQ", "SRTF", "HRRN"]
        self.selected_algorithm = tk.StringVar(master)
        self.selected_algorithm.set(self.algorithms[0])
        
        # Change from OptionMenu to Combobox
        self.dropdown = ttk.Combobox(self.scrollable_frame, textvariable=self.selected_algorithm, values=self.algorithms, state="readonly")
        self.dropdown.grid(row=1, column=0, columnspan=4, pady=(5, 10))
        self.dropdown.bind("<<ComboboxSelected>>", self.update_priority_visibility)

        # Frame for process input
        self.process_frame = tk.Frame(self.scrollable_frame, bd=0, relief="flat", padx=10, pady=10, bg="white")
        self.process_frame.grid(row=2, column=0, columnspan=4, pady=10)

        tk.Label(self.process_frame, text="Process ID:", bg="white").grid(row=0, column=0)
        self.process_id_entry = tk.Entry(self.process_frame)
        self.process_id_entry.grid(row=0, column=1)

        tk.Label(self.process_frame, text="Start Time:", bg="white").grid(row=0, column=2)
        self.start_time_entry = tk.Entry(self.process_frame)
        self.start_time_entry.grid(row=0, column=3)

        tk.Label(self.process_frame, text="CPU Time:", bg="white").grid(row=1, column=0)
        self.cpu_time_entry = tk.Entry(self.process_frame)
        self.cpu_time_entry.grid(row=1, column=1)

        # Priority label and entry, initially hidden
        self.priority_label = tk.Label(self.process_frame, text="Priority:", bg="white")
        self.priority_entry = tk.Entry(self.process_frame)

        # Number of random processes to generate
        tk.Label(self.process_frame, text="Number of Random Processes:", bg="white").grid(row=2, column=0)
        self.num_processes_entry = tk.Entry(self.process_frame)
        self.num_processes_entry.grid(row=2, column=1)

        # Control buttons
        self.button_frame = tk.Frame(self.scrollable_frame, bg="white")
        self.button_frame.grid(row=3, column=0, columnspan=4, pady=5)
        
        self.add_button = ttk.Button(self.button_frame, text="Add Process", command=self.add_process)
        self.add_button.grid(row=0, column=0, padx=5, pady=2)

        self.random_button = ttk.Button(self.button_frame, text="Generate Random Processes", command=self.generate_random_process)
        self.random_button.grid(row=0, column=1, padx=5, pady=2)

        self.clear_button = ttk.Button(self.button_frame, text="Clear All Processes", command=self.clear_processes)
        self.clear_button.grid(row=0, column=2, padx=5, pady=2)

        self.submit_button = ttk.Button(self.scrollable_frame, text="Submit", command=self.submit)
        self.submit_button.grid(row=4, column=0, columnspan=4, pady=5)

        # Create a frame for the treeview and its scrollbar
        self.tree_frame = tk.Frame(self.scrollable_frame)
        self.tree_frame.grid(row=5, column=0, columnspan=4, pady=(10, 0))

        # Treeview for displaying processes
        self.tree = ttk.Treeview(self.tree_frame, columns=("ID", "Start Time", "CPU Time", "Priority"), show='headings', height=6)
        self.tree.heading("ID", text="Process ID")
        self.tree.heading("Start Time", text="Start Time")
        self.tree.heading("CPU Time", text="CPU Time")
        self.tree.heading("Priority", text="Priority")

        # Add scrollbar for the treeview
        self.tree_scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.tree_scrollbar.set)

        # Pack the treeview and its scrollbar
        self.tree.pack(side="left", fill="both", expand=True)
        self.tree_scrollbar.pack(side="right", fill="y")

        # Set column widths
        for col in ("ID", "Start Time", "CPU Time", "Priority"):
            self.tree.column(col, width=100)

        # Treeview for displaying averages
        self.avg_tree = ttk.Treeview(self.scrollable_frame, columns=("Algorithm", "Average Turnaround Time", "Average Waiting Time"), show='headings')
        self.avg_tree.heading("Algorithm", text="Algorithm")
        self.avg_tree.heading("Average Turnaround Time", text="Average Turnaround Time")
        self.avg_tree.heading("Average Waiting Time", text="Average Waiting Time")
        self.avg_tree.grid(row=6, column=0, columnspan=4, pady=(10, 0))

        # Set column widths for avg_tree
        self.avg_tree.column("Algorithm", width=100)
        self.avg_tree.column("Average Turnaround Time", width=200)
        self.avg_tree.column("Average Waiting Time", width=200)

        # Canvas for plot
        self.canvas_frame = tk.Frame(self.scrollable_frame, bg="white")
        self.canvas_frame.grid(row=7, column=0, columnspan=4, pady=10)
        
        # Set fixed figure size (in inches)
        self.fig, self.ax = plt.subplots(figsize=(5, 2))
        
        # Create canvas for plotting
        self.plot_canvas = FigureCanvasTkAgg(self.fig, master=self.canvas_frame)
        canvas_widget = self.plot_canvas.get_tk_widget()
        
        # Set canvas widget size (in pixels)
        canvas_widget.config(width=800, height=300)
        canvas_widget.grid(row=0, column=0)
        
        # Adjust figure layout
        self.fig.tight_layout()

        self.processes = []

        # Initial visibility of the priority label and entry
        self.update_priority_visibility()

    def _bound_to_mousewheel(self, event):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        
    def _unbound_to_mousewheel(self, event):
        self.canvas.unbind_all("<MouseWheel>")
        
    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def on_canvas_configure(self, event):
        # Update the width of the canvas window to fit the frame
        self.canvas.itemconfig(self.window_id, width=event.width)

    def update_priority_visibility(self, event=None):
        selected_algorithm = self.selected_algorithm.get()
        if selected_algorithm == "Priority" or selected_algorithm == "All":
            self.priority_label.grid(row=1, column=2)
            self.priority_entry.grid(row=1, column=3)
            self.tree.heading("Priority", text="Priority")
            self.tree.column("Priority", width=80)
        else:
            self.priority_label.grid_forget()
            self.priority_entry.grid_forget()
            self.tree.heading("Priority", text="")
            self.tree.column("Priority", width=0, stretch=tk.NO)
            
    def update_ui_for_single_algorithm(self):
        # Resize the avg_tree to show only one row
        self.avg_tree.configure(height=1)
        
        # Clear existing canvas
        for widget in self.canvas_frame.winfo_children():
            widget.destroy()
        
        # Create new canvas for single Gantt chart
        self.fig, self.ax = plt.subplots(figsize=(10, 3))
        self.plot_canvas = FigureCanvasTkAgg(self.fig, master=self.canvas_frame)
        canvas_widget = self.plot_canvas.get_tk_widget()
        canvas_widget.config(width=800, height=300)
        canvas_widget.grid(row=0, column=0)

    def add_process(self):
        process_id = self.process_id_entry.get().strip()
        start_time = self.start_time_entry.get().strip()
        cpu_time = self.cpu_time_entry.get().strip()
        priority = self.priority_entry.get().strip() if self.priority_entry.winfo_ismapped() else None

        if process_id and start_time and cpu_time:
            try:
                start_time = int(start_time)
                cpu_time = int(cpu_time)

                if self.selected_algorithm.get() in ["Priority", "All"]:
                    if not priority:
                        messagebox.showerror("Input Error", "Please fill the Priority field.")
                        return
                    priority = int(priority)

                    process_tuple = (process_id, start_time, cpu_time, priority)
                else:
                    process_tuple = (process_id, start_time, cpu_time)

                self.processes.append(process_tuple)
                self.tree.insert("", "end", values=(process_id, start_time, cpu_time, priority if priority else "N/A"))
                self.clear_input_fields()
            except ValueError as ve:
                messagebox.showerror("Input Error", f"Invalid input: {ve}. Please enter valid integers for Start Time, CPU Time, and Priority.")
        else:
            messagebox.showerror("Input Error", "Please fill all fields.")

    def generate_random_process(self):
        num_processes = self.num_processes_entry.get().strip()
        if not num_processes.isdigit() or int(num_processes) <= 0:
            messagebox.showerror("Input Error", "Please enter a valid positive integer for the number of processes.")
            return
        
        num_processes = int(num_processes)
        self.tree.delete(*self.tree.get_children())
        self.processes.clear()

        for i in range(num_processes):
            process_id = f'P-{i + 1}'
            start_time = random.randint(0, 10)
            cpu_time = random.randint(1, 10)
            priority = random.randint(1, 5)

            self.processes.append((process_id, start_time, cpu_time, priority))
            self.tree.insert("", "end", values=(process_id, start_time, cpu_time, priority))

        self.clear_input_fields()

    def clear_input_fields(self):
        self.process_id_entry.delete(0, tk.END)
        self.start_time_entry.delete(0, tk.END)
        self.cpu_time_entry.delete(0, tk.END)
        if self.priority_entry.winfo_ismapped():
            self.priority_entry.delete(0, tk.END)
        self.num_processes_entry.delete(0, tk.END)

    def clear_processes(self):
        self.processes.clear()
        self.clear_input_fields()
        self.tree.delete(*self.tree.get_children())
        self.avg_tree.delete(*self.avg_tree.get_children())  # Clear average times
        self.ax.clear()  # Clear the plot
        self.ax.set_title("")  # Clear the title
        self.plot_canvas.draw()  # Redraw the empty canvas
        
        # Clear all widgets in canvas_frame
        for widget in self.canvas_frame.winfo_children():
            widget.destroy()
        
        # Recreate the plot canvas
        self.fig, self.ax = plt.subplots(figsize=(5, 2))
        self.plot_canvas = FigureCanvasTkAgg(self.fig, master=self.canvas_frame)
        canvas_widget = self.plot_canvas.get_tk_widget()
        canvas_widget.config(width=800, height=300)
        canvas_widget.grid(row=0, column=0)
        self.fig.tight_layout()

    def submit(self):
        selected_algorithm = self.selected_algorithm.get()
        if not self.processes:
            messagebox.showwarning("Warning", "No processes added. Please add processes before submitting.")
            return

        if selected_algorithm == "All":
            self.run_all_algorithms()
        else:
            self.update_ui_for_single_algorithm()
            self.run_single_algorithm(selected_algorithm)

    def run_single_algorithm(self, algorithm):
        try:
            algorithm_module = importlib.import_module(algorithm.lower())
            
            if algorithm == "MLFQ":
                waiting_times, turnaround_times, context = algorithm_module.multilevel_queue_scheduling(self.processes)
            elif algorithm == "SJF":
                waiting_times, turnaround_times, context = algorithm_module.sjf(self.processes)
            elif algorithm == "SRTF":
                waiting_times, turnaround_times, context = algorithm_module.srtf(self.processes)
            elif algorithm == "Priority":
                waiting_times, turnaround_times, context = algorithm_module.priority_scheduling(self.processes)
            elif algorithm == "HRRN":
                waiting_times, turnaround_times, context = algorithm_module.hrrn_scheduling(self.processes)
            elif algorithm == "RoundRobin":
                waiting_times, turnaround_times, context = algorithm_module.round_robin_scheduler(self.processes)
            elif algorithm == "FCFS":
                waiting_times, turnaround_times, context = algorithm_module.fcfs_scheduler(self.processes)

            avg_waiting_time = sum(waiting_times) / len(waiting_times) if waiting_times else 0
            avg_turnaround_time = sum(turnaround_times) / len(turnaround_times) if turnaround_times else 0
            
            self.avg_tree.delete(*self.avg_tree.get_children())
            self.avg_tree.insert("", "end", values=(algorithm, f"{avg_turnaround_time:.2f}", f"{avg_waiting_time:.2f}"))
            
            self.update_gantt_chart(algorithm_module, context, algorithm)

        except ImportError:
            messagebox.showerror("Error", f"Algorithm {algorithm} not found.")

    def run_all_algorithms(self):
        self.avg_tree.configure(height=7)
        algorithms = ["FCFS", "SJF", "Priority", "RoundRobin", "MLFQ", "SRTF", "HRRN"]
        results = []

        for algorithm in algorithms:
            try:
                algorithm_module = importlib.import_module(algorithm.lower())
                
                if algorithm == "MLFQ":
                    waiting_times, turnaround_times, context = algorithm_module.multilevel_queue_scheduling(self.processes)
                elif algorithm == "SJF":
                    waiting_times, turnaround_times, context = algorithm_module.sjf(self.processes)
                elif algorithm == "SRTF":
                    waiting_times, turnaround_times, context = algorithm_module.srtf(self.processes)
                elif algorithm == "Priority":
                    waiting_times, turnaround_times, context = algorithm_module.priority_scheduling(self.processes)
                elif algorithm == "HRRN":
                    waiting_times, turnaround_times, context = algorithm_module.hrrn_scheduling(self.processes)
                elif algorithm == "RoundRobin":
                    waiting_times, turnaround_times, context = algorithm_module.round_robin_scheduler(self.processes)
                elif algorithm == "FCFS":
                    waiting_times, turnaround_times, context = algorithm_module.fcfs_scheduler(self.processes)

                avg_waiting_time = sum(waiting_times) / len(waiting_times) if waiting_times else 0
                avg_turnaround_time = sum(turnaround_times) / len(turnaround_times) if turnaround_times else 0
                
                results.append((algorithm, avg_turnaround_time, avg_waiting_time, algorithm_module, context))

            except ImportError:
                messagebox.showerror("Error", f"Algorithm {algorithm} not found.")

        self.avg_tree.delete(*self.avg_tree.get_children())
        for result in results:
            self.avg_tree.insert("", "end", values=(result[0], f"{result[1]:.2f}", f"{result[2]:.2f}"))

        self.update_all_gantt_charts(results)

    def update_gantt_chart(self, algorithm_module, context, algorithm_name):
        self.ax.clear()
        algorithm_module.plot_gantt_chart(context, self.ax)
        self.ax.set_title(f"Gantt Chart for {algorithm_name}")
        self.plot_canvas.draw()

    def update_all_gantt_charts(self, results):
        num_algorithms = len(results)
        fig, axes = plt.subplots(num_algorithms, 1, figsize=(10, 2 * num_algorithms), squeeze=False)
        
        for i, (algorithm, _, _, algorithm_module, context) in enumerate(results):
            ax = axes[i, 0]
            algorithm_module.plot_gantt_chart(context, ax)
            ax.set_title(f"Gantt Chart for {algorithm}")
        
        plt.tight_layout()
        
        # Clear existing canvas
        for widget in self.canvas_frame.winfo_children():
            widget.destroy()
        
        # Create new canvas with all Gantt charts
        new_canvas = FigureCanvasTkAgg(fig, master=self.canvas_frame)
        new_canvas_widget = new_canvas.get_tk_widget()
        new_canvas_widget.config(width=800, height=200 * num_algorithms)
        new_canvas_widget.grid(row=0, column=0)
        new_canvas.draw()
        
    def on_close(self):
        """Handle the window close event to kill the terminal"""
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.master.quit()
            sys.exit()

if __name__ == "__main__":
    root = tk.Tk()
    app = ProcessSchedulerApp(root)
    root.mainloop()