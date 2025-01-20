from robot_movements import RobotMovements
from terminal import UserInterface
from robotiq_gripper import RobotiqGripper


class RobotTerminalController:
    def __init__(self):

        """Base Initialization"""
        self.robot_ip = '192.168.56.101'
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
            #gripper=self.gripper,
            acceleration=0.7,
            velocity=0.7
        )
        self.current_position = "start"
        self.timer_running = False
        self.current_tool = None

        self.user_interface = UserInterface(robot=self.robot)


    def run(self):
        """Start the robot terminal interface"""
        try:
            self.user_interface.run()
        finally:
            self.user_interface.cleanup()

def main():
    controller = RobotTerminalController()
    controller.run()

if __name__ == "__main__":
    main()