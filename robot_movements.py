import math
import time
import URBasic
import matplotlib.pyplot as plt

class RobotMovements:
    def __init__(self, robot_ip='192.168.56.101', gripper=None, acceleration=0.5, velocity=0.5):
        """Initialize gripper"""
        #self.gripper = gripper
        """Initialize robot movements controller"""
        self.acceleration = acceleration
        self.velocity = velocity
        self.last_position = None
        self.current_position = None

        self.pick_up_height = 0.163
        self.component_height = 0.1825

        """INITIALIZE BASIC ROBOT POSES"""
        self.ROBOT_WAKEUP_POSE = (
        math.radians(-180), # Base
        math.radians(3), # Shoulder
        math.radians(-142), # Elbow
        math.radians(-42), # Wrist 1
        math.radians(90), # Wrist 2
        math.radians(0) # Wrist 3
        )

        self.ROBOT_STANDBY_POSE = (
        math.radians(-180), # Base
        math.radians(3), # Shoulder
        math.radians(-142), # Elbow
        math.radians(-42), # Wrist 1
        math.radians(90), # Wrist 2
        math.radians(0) # Wrist 3
        )

        self.ROBOT_WAIT_FOR_INPUT_POSE = (
        math.radians(-180), # Base
        math.radians(-30), # Shoulder
        math.radians(-90), # Elbow
        math.radians(-60), # Wrist 1
        math.radians(90), # Wrist 2
        math.radians(0) # Wrist 3
        )
        
        # Initialize robot
        print("Initializing robot...")
        self.robotModel = URBasic.robotModel.RobotModel()
        # Set the IP address in the robot model
        self.robotModel.ipAddress = robot_ip
        
        self.robot = URBasic.urScriptExt.UrScriptExt(
            host=robot_ip,
            robotModel=self.robotModel
        )
        
        
        self.robot.reset_error()
        print("Robot initialized")
        
        # Initialize robot position
        self.move_to_wake_up_pose()
        self.move_to_wait_for_input_pose()

        self.create_pose_pattern_for_user_interface()

    def create_pose_pattern_for_user_interface(self):
        work_height = 0.2
        x_shift = 0.07  # shift in m
        y_shift = 0.105  # Made positive since we'll subtract it
        A1_x = -0.47
        A1_y = 0.105
        columns = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
        
        for row in range(1, 11):
            for col_idx, col in enumerate(columns):
                # X changes with column (letters)
                x = A1_x + col_idx * x_shift
                # Y decreases by 0.105 with each row (numbers)
                y = A1_y - (row - 1) * y_shift
                pose_name = f"{col}{row}"
                setattr(self, pose_name, (x, y, work_height, 2.25, 2.25, 0))
                print(f"Pose {pose_name}: {getattr(self, pose_name)}")


    def move_to_jpose(self, pose):
        """Move robot joints"""
        try:
            self.robot.movej(q=pose, a=self.acceleration, v=self.velocity, wait=True)
            self.last_position = pose
            return True
        except Exception as e:
            print(f"Error moving to pose: {str(e)}")
            return False

    def move_to_tpose(self, pose):
        """Move robot TCP in Taskspace"""
        try:
            self.robot.movel(pose=pose, a=self.acceleration, v=self.velocity, wait=True)
            self.robot.stopl(a=self.acceleration)  # Smooth deceleration
            self.last_position = pose
            return True
        except Exception as e:
            print(f"Error moving to pose: {str(e)}")
            return False
        
    def move_to_wake_up_pose(self):
        self.move_to_jpose(self.ROBOT_WAKEUP_POSE)
        self.robot.init_realtime_control()

    def move_to_standby_pose(self):
        self.move_to_jpose(self.ROBOT_STANDBY_POSE)
        self.robot.init_realtime_control()

    def move_to_wait_for_input_pose(self):
        self.move_to_jpose(self.ROBOT_WAIT_FOR_INPUT_POSE)
        self.robot.init_realtime_control()

    def perform_nod_movement(self):
        self.NOD_WAVEPOINT = (
        math.radians(0), # Base
        math.radians(-50), # Shoulder
        math.radians(-120), # Elbow
        math.radians(-10), # Wrist 1
        math.radians(90), # Wrist 2
        math.radians(0) # Wrist 3
        )
        """Perform nodding movement sequence"""
        self.move_to_jpose(self.ROBOT_WAIT_FOR_INPUT_POSE)
        self.move_to_jpose(self.NOD_WAVEPOINT)
        self.move_to_jpose(self.ROBOT_WAIT_FOR_INPUT_POSE)  
        
    def perform_redo_movement(self):    
        self.REDO_WAVEPOINT_TOP = (
        math.radians(0), # Base
        math.radians(-40), # Shoulder
        math.radians(-105), # Elbow
        math.radians(-35), # Wrist 1
        math.radians(90), # Wrist 2
        math.radians(0) # Wrist 3
        )
        self.REDO_WAVEPOINT_LEFT = (
        math.radians(15), # Base
        math.radians(-40), # Shoulder
        math.radians(-110), # Elbow
        math.radians(-32), # Wrist 1
        math.radians(90), # Wrist 2
        math.radians(0) # Wrist 3
        )
        """Perform redo movement sequence"""
        self.move_to_jpose(self.ROBOT_STANDBY_POSE)
        self.move_to_jpose(self.REDO_WAVEPOINT_TOP)
        self.move_to_jpose(self.REDO_WAVEPOINT_LEFT)
        self.move_to_jpose(self.ROBOT_STANDBY_POSE)
 

    def perform_decline_movement(self):
        self.DECLINE_WAVEPOINT_START = (
        math.radians(3), # Base
        math.radians(-37), # Shoulder
        math.radians(-114), # Elbow
        math.radians(-30), # Wrist 1
        math.radians(90), # Wrist 2
        math.radians(0) # Wrist 3
        )
        self.DECLINE_WAVEPOINT_END = (
        math.radians(-3), # Base
        math.radians(-37), # Shoulder
        math.radians(-114), # Elbow
        math.radians(-30), # Wrist 1
        math.radians(90), # Wrist 2
        math.radians(0) # Wrist 3
        )
        """Perform decline movement sequence"""
        self.move_to_jpose(self.ROBOT_STANDBY_POSE)
        self.move_to_jpose(self.DECLINE_WAVEPOINT_START)
        self.move_to_jpose(self.DECLINE_WAVEPOINT_END)
        self.move_to_jpose(self.ROBOT_STANDBY_POSE)
        self.move_to_jpose(self.ROBOT_WAIT_FOR_INPUT_POSE)

    def get_tool(self, tool_number=1, tool_pick_up_height=0.1):


        self.PICKUP_TOOL_1_HOVER = (0.0247, 0.34, 0.25, 3.154, 0.094, 0.012)
        self.PICKUP_TOOL_1 = (0.0247, 0.34, self.pick_up_height, 3.154, 0.094, 0.012)
        
        self.PICKUP_TOOL_2_HOVER = (0.133, 0.34, 0.25, 3.151, 0.088, -0.032)
        self.PICKUP_TOOL_2 = (0.133, 0.34, self.pick_up_height, 3.151, 0.088, -0.032)
        
        self.PICKUP_TOOL_3_HOVER = (0.233, 0.34, 0.25, 3.144, 0.007, -0.023)
        self.PICKUP_TOOL_3 = (0.233, 0.34, self.pick_up_height, 3.144, 0.007, -0.023)
        
        
        self.PICKUP_WAVEPOINT = (
            math.radians(-270), # Base
            math.radians(-90), # Shoulder
            math.radians(-100), # Elbow
            math.radians(-75), # Wrist 1
            math.radians(90), # Wrist 2
            math.radians(0) # Wrist 3
        )


        self.move_to_jpose(self.PICKUP_WAVEPOINT)
        

        if tool_number == 1:
            self.move_to_tpose(self.PICKUP_TOOL_1_HOVER)
            self.move_to_tpose(self.PICKUP_TOOL_1)
            """close gripper"""
            #self.gripper.close()
            self.move_to_tpose(self.PICKUP_TOOL_1_HOVER)
        elif tool_number == 2:
            self.move_to_tpose(self.PICKUP_TOOL_2_HOVER)
            self.move_to_tpose(self.PICKUP_TOOL_2)
            """close gripper"""
            #self.gripper.close()
            self.move_to_tpose(self.PICKUP_TOOL_2_HOVER)
        elif tool_number == 3:
            self.move_to_tpose(self.PICKUP_TOOL_3_HOVER)
            self.move_to_tpose(self.PICKUP_TOOL_3)
            """close gripper"""
            #self.gripper.close()
            self.move_to_tpose(self.PICKUP_TOOL_3_HOVER)
        

    def drop_tool(self, tool_number=1, tool_pick_up_height=0.1):
        
        self.PICKUP_TOOL_1_HOVER = (0.0247, 0.34, 0.25, 3.154, 0.094, 0.012)
        self.PICKUP_TOOL_1 = (0.0247, 0.34, self.pick_up_height, 3.154, 0.094, 0.012)
        
        self.PICKUP_TOOL_2_HOVER = (0.133, 0.34, 0.25, 3.151, 0.088, -0.032)
        self.PICKUP_TOOL_2 = (0.133, 0.34, self.pick_up_height, 3.151, 0.088, -0.032)
        
        self.PICKUP_TOOL_3_HOVER = (0.233, 0.34, 0.25, 3.144, 0.007, -0.023)
        self.PICKUP_TOOL_3 = (0.233, 0.34, self.pick_up_height, 3.144, 0.007, -0.023)
        

        self.PICKUP_WAVEPOINT = (
            math.radians(-270), # Base
            math.radians(-90), # Shoulder
            math.radians(-100), # Elbow
            math.radians(-75), # Wrist 1
            math.radians(90), # Wrist 2
            math.radians(0) # Wrist 3
        )


        self.move_to_jpose(self.PICKUP_WAVEPOINT)
        

        if tool_number == 1:
            self.move_to_tpose(self.PICKUP_TOOL_1_HOVER)
            self.move_to_tpose(self.PICKUP_TOOL_1)
            """close gripper"""
            #self.gripper.open()
            self.move_to_tpose(self.PICKUP_TOOL_1_HOVER)
        elif tool_number == 2:
            self.move_to_tpose(self.PICKUP_TOOL_2_HOVER)
            self.move_to_tpose(self.PICKUP_TOOL_2)
            """close gripper"""
            #self.gripper.open()
            self.move_to_tpose(self.PICKUP_TOOL_2_HOVER)
        elif tool_number == 3:
            self.move_to_tpose(self.PICKUP_TOOL_3_HOVER)
            self.move_to_tpose(self.PICKUP_TOOL_3)
            """close gripper"""
            #self.gripper.open()
            self.move_to_tpose(self.PICKUP_TOOL_3_HOVER)


    def pixel_to_world_backup(self, x, y):
        # Transformiere Pixelkoordinaten in Weltkoordinaten (in mm)
        scale_x = 0.001  # Skalierungsfaktor für x
        scale_y = 0.001  # Skalierungsfaktor für y
        offset_x = -0.365  # Offset für x 
        offset_y = 0.3   # Offset für y 

        world_y = offset_x + x * scale_x
        world_x = offset_y + y * scale_y
        # world_z = 0  # z-Komponente ist 0
        # print(f"World coordinates pixel to world: ({world_x} m, {world_y} m")
        return world_x, world_y #, world_z  # Convert to meters
    
    def pixel_to_world_backup2(self, pixel_x, pixel_y):
        """
        Transform pixel coordinates to world coordinates based on calibration points:
        pixel(198, 347) -> world(-0.295, -0.21)
        pixel(198, 235) -> world(-0.098, -0.21)
        pixel(325, 235) -> world(-0.098, -0.44)
        pixel(325, 347) -> world(-0.3, -0.44)
        
        Args:
            pixel_x (float): x coordinate in pixel space
            pixel_y (float): y coordinate in pixel space
            
        Returns:
            tuple: (world_x, world_y) coordinates in meters
        """
        # Calculate scaling factors
        dx_pixel = 325 - 198  # = 127 pixels
        dy_pixel = 347 - 235  # = 112 pixels
        
        dx_world = -0.44 - (-0.21)  # = -0.23 meters
        dy_world = -0.3 - (-0.295)  # = -0.005 meters
        
        # Calculate scaling factors
        scale_x = dx_world / dx_pixel  # meters per pixel in x direction
        scale_y = dy_world / dy_pixel  # meters per pixel in y direction
        
        # Calculate offsets using one of the calibration points
        # Using pixel(198, 347) -> world(-0.295, -0.21)
        offset_x = -0.21 - (198 * scale_x)
        offset_y = -0.295 - (347 * scale_y)
        
        # Transform coordinates
        world_x = pixel_x * scale_x + offset_x
        world_y = pixel_y * scale_y + offset_y
        
        return world_x, world_y
    

    def pixel_to_world(self, pixel_x, pixel_y):
        # Bottom Left in world coordinates
        A1_x_world = -0.29505
        A1_y_world = -0.20990
        # Bottom Right in world coordinates
        K1_x_world = -0.30040
        K1_y_world = -0.43423
        # Top Left in world coordinates
        A2_x_world = -0.09682
        A2_y_world = -0.21371
        # Top Right in world coordinates
        K2_x_world = -0.09999
        K2_y_world = -0.44149
        
        # Bottom Left in pixel coordinates
        A1_x_pixel = 194
        A1_y_pixel = 347
        # Bottom Right in pixel coordinates
        K1_x_pixel = 326
        K1_y_pixel = 343
        # Top Left in pixel coordinates
        A2_x_pixel = 198
        A2_y_pixel = 235
        # Top Right in pixel coordinates
        K2_x_pixel = 325
        K2_y_pixel = 238
        
        # Calculate scaling factors
        scale_x = (K2_x_world - A1_x_world) / (K2_x_pixel - A1_x_pixel)
        scale_y = (K2_y_world - A1_y_world) / (K2_y_pixel - A1_y_pixel)
        
        # Calculate offsets
        offset_x = A1_x_world - A1_x_pixel * scale_x
        offset_y = A1_y_world - A1_y_pixel * scale_y
        
        # Transform coordinates
        world_x = pixel_x * scale_x + offset_x
        world_y = pixel_y * scale_y + offset_y
        
        return world_x, world_y

    
    def perform_trajectory(self, x1, y1, x2, y2):
        self.move_to_wait_for_input_pose()
        self.TRAJECTORY_WAVEPOINT = (
            math.radians(-120), # Base
            math.radians(-75), # Shoulder
            math.radians(-100), # Elbow
            math.radians(-95), # Wrist 1
            math.radians(88), # Wrist 2
            math.radians(60) # Wrist 3
        )

        self.move_to_jpose(self.TRAJECTORY_WAVEPOINT)
        # Berechnung der Start- und Endpunkte
        start_point = (x1, y1)
        end_point = (x2, y2)
        print("STARTPOINTS" + str(start_point))
        print("Endpoints" +str(end_point))

        # Beispielwerte für die Höhe und Werkzeugbreite
        #component_height = 0.2  # in Metern
        tool_width = 0.03  # in Metern

        # Generiere die Trajektorie basierend auf den Weltkoordinaten
        trajectory = self.generate_trajectory_path(
            start_point=start_point,
            end_point=end_point,
            component_height=self.component_height,
            tool_width=tool_width
        )

        # Fahre die generierte Trajektorie ab
        for point in trajectory:
            try:
                self.move_to_tpose(point)
            except Exception as e:
                print(f"Error moving to point {point}: {str(e)}")
                self.robot.stopl(a=self.acceleration)  # Smooth deceleration in case of error

        self.move_to_wait_for_input_pose()
                
    def generate_trajectory_path(self, start_point, end_point, component_height, tool_width):
        """
        Generate corner points for TCP movement over a rectangular area in a diagonal spiral pattern.
        Args:
            start_point (tuple): Starting (x, y) coordinate in meters
            end_point (tuple): Ending (x, y) coordinate in meters
            component_height (float): Height of component in meters
            tool_width (float): Width of tool in meters
        Returns:
            list: List of tuples containing (x,y,z,rx,ry,rz) coordinates for each corner point
        """
        corner_points = []
        # Fixed rotation values
        rx = 2.188
        ry = 2.188
        rz = 0
        z = self.component_height  # Fixed height
        
        # Initialize boundaries
        left_y = start_point[1]
        right_y = end_point[1]
        bottom_x = start_point[0]
        top_x = end_point[0]

        # start from bottom-left corner
        a1_x = bottom_x - tool_width / 2
        a1_y = left_y + tool_width / 2
        corner_points.append((a1_x, a1_y, z, rx, ry, rz))
        
        # next bottom right corner
        a2_x = bottom_x - tool_width / 2
        a2_y = right_y - tool_width / 2
        corner_points.append((a2_x, a2_y, z, rx, ry, rz))
        
        # next top right corner
        a3_x = top_x + tool_width / 2
        a3_y = right_y - tool_width / 2
        corner_points.append((a3_x, a3_y, z, rx, ry, rz))
        
        # next top left corner
        a4_x = top_x + tool_width / 2
        a4_y = left_y + tool_width / 2
        corner_points.append((a4_x, a4_y, z, rx, ry, rz))
        
        # next bottom left corner
        a5_x = bottom_x - tool_width
        a5_y = left_y + tool_width / 2
        corner_points.append((a5_x, a5_y, z, rx, ry, rz))

        current_y = a5_y
        next_y = a5_y
        counter = 0
        
        while current_y >= right_y + tool_width:
            if counter % 2 == 0:
                # Moving towards top_x
                next_x = top_x + tool_width / 2
            else:
                # Moving towards bottom_x
                next_x = bottom_x - tool_width / 2
                
            next_y = current_y - tool_width / 2
            corner_points.append((next_x, next_y, z, rx, ry, rz))
            current_y = next_y
            counter += 1

        print("\nTrajectory Corner Points:")
        print("------------------------")
        for i, point in enumerate(corner_points):
            print(f"Point {i+1:2d}: x={point[0]:7.3f}, y={point[1]:7.3f}, z={point[2]:7.3f}, rx={point[3]:7.3f}, ry={point[4]:7.3f}, rz={point[5]:7.3f}")
        print("------------------------\n")

        return corner_points


