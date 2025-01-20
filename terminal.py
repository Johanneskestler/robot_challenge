import cv2
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import numpy as np
from robot_movements import RobotMovements
import threading
import time
from queue import Queue


class UserInterface:
    def __init__(self, robot):
        self.robot = robot
        self.traj_start_x = 0
        self.traj_start_y = 0
        self.traj_end_x = 0
        self.traj_end_y = 0
        self.current_tool = None

        self.window = tk.Tk()
        self.window.title("Camera Feed")
        self.window.geometry("1600x1200")
        
        # Main container
        self.main_container = tk.Frame(self.window)
        self.main_container.pack(pady=10)
        
        # Video feed on left
        # Initialize camera and thread
        self.cap = cv2.VideoCapture(0)
        self.frame_queue = Queue(maxsize=2)
        self.stopped = False
        
        # Start camera thread
        self.camera_thread = threading.Thread(target=self.camera_stream, daemon=True)
        self.camera_thread.start()

        self.video_frame = tk.Label(self.main_container)
        self.video_frame.pack(side=tk.LEFT, pady=20, padx=20)
        
        # Right side container
        self.right_container = tk.Frame(self.main_container)
        self.right_container.pack(side=tk.LEFT)
        
        # Image at top of right container
        self.image_frame = tk.Frame(self.right_container)
        tk.Label(self.image_frame, text="1. Select Work Area", font=('Arial', 30, 'bold')).pack()
        self.image_frame.pack(pady=10)
        image = Image.open("terminal_workpiece.jpg")
        scale_factor = 0.2
        resized_image = image.resize((int(scale_factor * 2692), int(scale_factor * 1344)), Image.Resampling.LANCZOS)
        self.photo = ImageTk.PhotoImage(resized_image)
        self.image_label = tk.Label(self.image_frame, image=self.photo)
        self.image_label.pack()
        
        # Selection points container below image
        self.selection_container = tk.Frame(self.right_container)
        self.selection_container.pack(pady=10)
        
        # Start point frame
        self.work_frame_start = tk.Frame(self.selection_container)
        self.work_frame_start.pack(side=tk.LEFT, padx=10)
        tk.Label(self.work_frame_start, text="Select Start Point", font=('Arial', 20, 'bold')).pack()
        
        self.selected_row_start = tk.StringVar()
        self.row_dropdown_start = ttk.Combobox(self.work_frame_start, textvariable=self.selected_row_start)
        self.row_dropdown_start['values'] = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
        self.row_dropdown_start['state'] = 'readonly'
        self.row_dropdown_start.set('Select Row')
        self.row_dropdown_start.pack(pady=5)
        
        self.selected_col_start = tk.StringVar()
        self.col_dropdown_start = ttk.Combobox(self.work_frame_start, textvariable=self.selected_col_start)
        self.col_dropdown_start['values'] = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
        self.col_dropdown_start['state'] = 'readonly'
        self.col_dropdown_start.set('Select Column')
        self.col_dropdown_start.pack(pady=5)
        
        # End point frame
        self.work_frame_end = tk.Frame(self.selection_container)
        self.work_frame_end.pack(side=tk.LEFT, padx=10)
        tk.Label(self.work_frame_end, text="Select End Point", font=('Arial', 20, 'bold')).pack()
        
        self.selected_row_end = tk.StringVar()
        self.row_dropdown_end = ttk.Combobox(self.work_frame_end, textvariable=self.selected_row_end)
        self.row_dropdown_end['values'] = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
        self.row_dropdown_end['state'] = 'readonly'
        self.row_dropdown_end.set('Select Row')
        self.row_dropdown_end.pack(pady=5)
        
        self.selected_col_end = tk.StringVar()
        self.col_dropdown_end = ttk.Combobox(self.work_frame_end, textvariable=self.selected_col_end)
        self.col_dropdown_end['values'] = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
        self.col_dropdown_end['state'] = 'readonly'
        self.col_dropdown_end.set('Select Column')
        self.col_dropdown_end.pack(pady=5)
        
        # Confirm button at bottom
        self.confirm_work_area_button = tk.Button(self.right_container, text="Confirm Work Area", command=self.confirm)
        self.confirm_work_area_button.pack(pady=10)
        
        # Tool selection container
        self.tool_container = tk.Frame(self.window)
        self.tool_container.pack(pady=20)

        
        # Tool selection frame
        self.tool_frame = tk.Frame(self.tool_container)
        self.tool_frame.pack()
        tk.Label(self.tool_frame, text="2. Select Tool", font=('Arial', 30, 'bold')).pack(pady=10)
        
        # Tool dropdown
        self.selected_tool = tk.StringVar()
        self.tool_dropdown = ttk.Combobox(self.tool_frame, textvariable=self.selected_tool)
        self.tool_dropdown['values'] = ['Tool 1', 'Tool 2', 'Tool 3']
        self.tool_dropdown['state'] = 'readonly'
        self.tool_dropdown.set('Select Tool')
        self.tool_dropdown.pack(pady=10)
        
        # Process control container
        self.process_container = tk.Frame(self.window)
        self.process_container.pack(pady=20)
        
        # Process control frame
        self.process_frame = tk.Frame(self.process_container)
        self.process_frame.pack()
        tk.Label(self.process_frame, text="3. Process Control", font=('Arial', 30, 'bold')).pack(pady=10)
        
        # Button frame
        self.button_frame = tk.Frame(self.process_frame)
        self.button_frame.pack(pady=10)
        
        # Start button (Green with black text)
        self.start_button = tk.Button(self.button_frame, text="Start Process", 
                                    command=self.start_process,
                                    bg='lime green', fg='black',
                                    font=('Arial', 14, 'bold'),
                                    width=15, height=2,
                                    relief='raised',
                                    highlightbackground='green',
                                    activebackground='green')
        self.start_button.pack(side=tk.LEFT, padx=10)

        # Stop button (Red with black text)
        
        # Initialize other variables
        self.movement_active = False
        self.corner_color = (0, 255, 0)
        self.rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
        self.cols = [str(i) for i in range(1, 11)]
        self.update_frame()
        
    def start_process(self):
        self.start_button.config(state='disabled', bg='grey')
        print("Process started")
        current_tool = self.selected_tool.get()
        
        if current_tool == "Tool 1":
            print("Performing get tool movement...")
            if self.current_tool is not None:
                drop_thread = threading.Thread(target=self.robot.drop_tool, args=(self.current_tool,))
                drop_thread.start()
                drop_thread.join()
                self.current_position = "drop_tool"
                self.current_tool = None
                
            tool_choice = 1
            get_thread = threading.Thread(target=self.robot.get_tool, args=(tool_choice, 0.1))
            get_thread.start() 
            get_thread.join()
            self.current_position = "get_tool"
            self.current_tool = tool_choice

        elif current_tool == "Tool 2":
            print("Performing get tool movement...")
            if self.current_tool is not None:
                drop_thread = threading.Thread(target=self.robot.drop_tool, args=(self.current_tool,))
                drop_thread.start()
                drop_thread.join()
                self.current_position = "drop_tool"
                self.current_tool = None

            tool_choice = 2
            get_thread = threading.Thread(target=self.robot.get_tool, args=(tool_choice, 0.1))
            get_thread.start()
            get_thread.join()
            self.current_position = "get_tool"
            self.current_tool = tool_choice

        elif current_tool == "Tool 3":
            print("Performing get tool movement...")
            if self.current_tool is not None:
                drop_thread = threading.Thread(target=self.robot.drop_tool, args=(self.current_tool,))
                drop_thread.start()
                drop_thread.join()
                self.current_position = "drop_tool"
                self.current_tool = None
                
            tool_choice = 3
            get_thread = threading.Thread(target=self.robot.get_tool, args=(tool_choice, 0.1))
            get_thread.start()
            get_thread.join()
            self.current_position = "get_tool"
            self.current_tool = tool_choice

        traj_thread = threading.Thread(target=self.run_trajectory)
        traj_thread.start()

    def run_trajectory(self):
        self.robot.perform_trajectory(self.traj_start_x, self.traj_start_y,
                                    self.traj_end_x, self.traj_end_y)
        self.window.after(0, self.enable_start_button)

    def enable_start_button(self):
                # Reset all dropdowns
        self.row_dropdown_start.set('Select Row')
        self.col_dropdown_start.set('Select Column')
        self.row_dropdown_end.set('Select Row')
        self.col_dropdown_end.set('Select Column')
        self.tool_dropdown.set('Select Tool')
        
        # Clear selected area if it exists
        if hasattr(self, 'selected_area'):
            delattr(self, 'selected_area')
        self.start_button.config(state='normal', bg='lime green') 

        
    def confirm(self):
        
        start_row = self.selected_row_start.get()
        start_col = self.selected_col_start.get()
        end_row = self.selected_row_end.get()
        end_col = self.selected_col_end.get()
        
        if 'Select' in [start_row, start_col, end_row, end_col]:
            print("Please select both start and end points")
            return
        
        pose_name_start = f"{start_row}{start_col}"
        pose_start = getattr(self.robot, pose_name_start)

        pose_name_end = f"{end_row}{end_col}"
        pose_end = getattr(self.robot, pose_name_end)

    
        """Trajectory points"""
        self.traj_start_x = float(pose_start[0])
        self.traj_start_y = float(pose_start[1])
        self.traj_end_x = float(pose_end[0])
        self.traj_end_y = float(pose_end[1])
        print(f"Selected area from {start_row}{start_col} to {end_row}{end_col}")



        """For Visualization"""
        start_row_idx = self.rows.index(start_row)
        start_col_idx = int(start_col) - 1
        end_row_idx = self.rows.index(end_row) - 1
        end_col_idx = int(end_col) - 2
        
        self.selected_area = {
            'start_row': min(start_row_idx, end_row_idx),
            'end_row': max(start_row_idx, end_row_idx),
            'start_col': min(start_col_idx, end_col_idx),
            'end_col': max(start_col_idx, end_col_idx)
        }
        
        
    def toggle_movement(self):
        self.movement_active = not self.movement_active
        print("Hello World")
        
    def draw_grid(self, frame):
        height, width = frame.shape[:2]
        cell_height = height // 10
        cell_width = width // 10
        
        # Draw the blue rectangle if area is selected
        if hasattr(self, 'selected_area'):
            area = self.selected_area
            start_x = area['start_col'] * cell_width
            # Invert Y coordinates for rectangle
            start_y = height - (area['end_row'] + 1) * cell_height
            end_x = (area['end_col'] + 1) * cell_width
            end_y = height - area['start_row'] * cell_height
            
            overlay = frame.copy()
            cv2.rectangle(overlay, (start_x, start_y), (end_x, end_y), 
                         (255, 0, 0), -1)
            alpha = 0.3
            frame = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)
        
        # Draw grid lines
        for i in range(1, 10):
            x = i * cell_width
            cv2.line(frame, (x, 0), (x, height), (255, 255, 255), 1)
            
        for i in range(1, 10):
            y = i * cell_height
            cv2.line(frame, (0, y), (width, y), (255, 255, 255), 1)
        
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.4
        
        # Draw corner points and labels
        for i in range(11):
            for j in range(11):
                x = j * cell_width
                y = height - i * cell_height  # Invert Y coordinate
                cv2.circle(frame, (x, y), 3, self.corner_color, -1)
                
                if i < 10 and j < 10:
                    label = f"{self.rows[i]}{self.cols[j]}"
                    cv2.putText(frame, label, (x + 5, y - 5), 
                              font, font_scale, (0, 0, 0), 1)
        
        return frame
    
    def camera_stream(self):
        while not self.stopped:
            if not self.frame_queue.full():
                ret, frame = self.cap.read()
                if ret:
                    self.frame_queue.put(frame)
                time.sleep(0.01)
    
    def update_frame(self):
        if not self.frame_queue.empty():
            frame = self.frame_queue.get()
            height, width = frame.shape[:2]
            frame = cv2.resize(frame, (width//1, height//1))
            frame = self.draw_grid(frame)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            imgtk = ImageTk.PhotoImage(image=img)
            self.video_frame.imgtk = imgtk
            self.video_frame.configure(image=imgtk)
        self.window.after(10, self.update_frame)
                
    def run(self):
        self.window.mainloop()
        
    def cleanup(self):
        self.stopped = True
        if self.cap.isOpened():
            self.cap.release()

if __name__ == "__main__":
    app = UserInterface()
    try:
        app.run()
    finally:
        app.cleanup()