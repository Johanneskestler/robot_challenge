import URBasic
import math
import time
import threading
from robot_movements import RobotMovements
from gesture_control import GestureRecognizer
from robotiq_gripper import RobotiqGripper

class RobotGestureController:
    def __init__(self):
        
        """Base Initialization"""
        self.robot_ip = '172.17.0.2'
        self.robot_port = 63352

        """Initialize robot and gesture tracking"""
        # Gripper settings
        #self.gripper = RobotiqGripper()
        #self.gripper.connect(hostname=self.robot_ip, port=self.robot_port)
        #self.gripper.activate()
        #self.gripper.open()
        

        # Robot settings
        self.robot = RobotMovements(
            robot_ip=self.robot_ip,
            # gripper=self.gripper,
            acceleration=0.7,
            velocity=0.7
        )
        self.current_position = "start"
        self.timer_running = False
        self.current_tool = None

    def handle_gesture(self, gesture):
        """Handle detected gestures"""
        try:
            if gesture.startswith("Area specification"):
                print("Performing area specification movement...")
                if ":" in gesture:
                    coordinates = gesture.split(":")[1].strip()
                    x1, y1, x2, y2 = map(int, coordinates.replace('(', '').replace(')', '').replace(',', '').split())
                    if not self.timer_running:
                        self.timer_running = True
                        threading.Timer(5.0, self.start_trajectory, args=(x1, y1, x2, y2)).start()
                        print("Timer started")
                
            elif gesture == "Tool Selection: Level 1":
                print("Performing get tool movement...")
                """Drop current tool and get new tool"""
                if self.current_tool is not None:
                    drop_thread = threading.Thread(target=self.robot.drop_tool, args=(self.current_tool,))
                    drop_thread.start()
                    drop_thread.join()  # Wait for drop to complete
                    self.current_position = "drop_tool"
                    self.current_tool = None
                
                tool_choice = 1  # Beispiel: Werkzeug 1 auswählen
                get_thread = threading.Thread(target=self.robot.get_tool, args=(tool_choice, 0.1))
                get_thread.start()
                get_thread.join()  # Wait for get tool to complete
                self.current_position = "get_tool"
                self.current_tool = tool_choice
                
                # Move to wait position in a new thread after tool operations complete
                wait_thread = threading.Thread(target=self.robot.move_to_wait_for_input_pose)
                wait_thread.start()

            elif gesture == "Tool Selection: Level 2":
                print("Performing get tool movement...")
                """Drop current tool and get new tool"""
                if self.current_tool is not None:
                    drop_thread = threading.Thread(target=self.robot.drop_tool, args=(self.current_tool,))
                    drop_thread.start()
                    drop_thread.join()  # Wait for drop to complete
                    self.current_position = "drop_tool"
                    self.current_tool = None
                
                tool_choice = 2  # Beispiel: Werkzeug 2 auswählen
                get_thread = threading.Thread(target=self.robot.get_tool, args=(tool_choice, 0.1))
                get_thread.start()
                get_thread.join()  # Wait for get tool to complete
                self.current_position = "get_tool"
                self.current_tool = tool_choice
                
                # Move to wait position in a new thread after tool operations complete
                wait_thread = threading.Thread(target=self.robot.move_to_wait_for_input_pose)
                wait_thread.start()

            elif gesture == "Tool Selection: Level 3":
                print("Performing get tool movement...")
                """Drop current tool and get new tool"""
                if self.current_tool is not None:
                    drop_thread = threading.Thread(target=self.robot.drop_tool, args=(self.current_tool,))
                    drop_thread.start()
                    drop_thread.join()  # Wait for drop to complete
                    self.current_position = "drop_tool"
                    self.current_tool = None
                
                tool_choice = 3  # Beispiel: Werkzeug 3 auswählen
                get_thread = threading.Thread(target=self.robot.get_tool, args=(tool_choice, 0.1))
                get_thread.start()
                get_thread.join()  # Wait for get tool to complete
                self.current_position = "get_tool"
                self.current_tool = tool_choice
                
                # Move to wait position in a new thread after tool operations complete
                wait_thread = threading.Thread(target=self.robot.move_to_wait_for_input_pose)
                wait_thread.start()
                
            # elif gesture == "Error gesture":
            #     print("Performing redo movement...")
            #     threading.Thread(target=self.robot.perform_redo_movement).start()
            #     self.current_position = "redo_movement"
                
        except Exception as e:
            print(f"Error during robot movement: {str(e)}")

    def start_trajectory(self, x1, y1, x2, y2):
        """Start trajectory generation after 5 seconds"""
        top_left = (min(x1, x2), min(y1, y2))
        top_right = (max(x1, x2), min(y1, y2))
        bottom_left = (min(x1, x2), max(y1, y2))
        bottom_right = (max(x1, x2), max(y1, y2))
        print(f"Pixel Coordinates after 5 seconds: top_left: ({top_left}), top_right: ({top_right}), bottom_left: ({bottom_left}), bottom_right: ({bottom_right})")
        print(f"Selected Coordinates for Start point: bottom_left: ({bottom_left[0]}, {bottom_left[1]})")
        print(f"Selected Coordinates for End point: top_right: ({top_right[0]}, {top_right[1]})")
        print("-------------------")
        world_x1, world_y1 = self.robot.pixel_to_world(bottom_left[0], bottom_left[1])
        world_x2, world_y2 = self.robot.pixel_to_world(top_right[0], top_right[1])
        print(f"World coordinates Start Point: ({world_x1}, {world_y1})")
        print(f"World coordinates End Point: ({world_x2}, {world_y2})")
        threading.Thread(target=self.robot.perform_trajectory, args=(world_x1, world_y1, world_x2, world_y2)).start()
        self.timer_running = False

    def run(self):
        """Main run loop"""
        try:
            print("\nStarting gesture-controlled robot system")
            print("Press ESC to quit\n")
            
            recognizer = GestureRecognizer(self.handle_gesture)
            recognizer.main()
                
        except KeyboardInterrupt:
            print("\nClosing robot connection...")
        except Exception as e:
            print(f"\nError occurred: {str(e)}")
        finally:
            self.robot.robot.close()
            print("Robot connection closed")

def main():
    controller = RobotGestureController()
    controller.run()

if __name__ == "__main__":
    main()