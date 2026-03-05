#!/usr/bin/env python3

# Copyright (c) 2026 Lev Romanov RTU MIREA (Russia)
# SPDX-License-Identifier: MIT
# Details in the LICENSE file in the root of the package.

'''
АННОТАЦИЯ
Узел для телеуправления роботом JetBot с клавиатуры. Публикует команды 
скорости в топик /cmd_vel на основе нажатых клавиш. Поддерживает плавное
ускорение и торможение.

ANNOTATION  
Node for JetBot robot teleoperation via keyboard. Publishes velocity commands
to /cmd_vel topic based on key presses. Supports smooth acceleration and
deceleration.
'''

import sys
import select
import termios
import tty
import time
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist


# Константы управления
MAX_LINEAR_VELOCITY = 0.5   # м/с
MAX_ANGULAR_VELOCITY = 0.5  # рад/с
LINEAR_STEP = 0.01          # Шаг изменения линейной скорости
ANGULAR_STEP = 0.05          # Шаг изменения угловой скорости

# Управляющие клавиши
KEYS = {
    'w': 'forward',
    's': 'backward', 
    'a': 'left',
    'd': 'right',
    'q': 'rotate_left',
    'e': 'rotate_right',
    'x': 'stop',
    ' ': 'stop',
}

HELP_MSG = """\n========== JETBOT KEYBOARD TELEOPERATION ==========\nMovement:
  W - forward        S - backward
  A - left           D - right
Rotation (in place):
  Q - left           E - right
Control:
  X or Space - stop  Ctrl+C - exit
====================================================\n"""


class TeleopKeyboard(Node):
    """Node for keyboard teleoperation of JetBot."""

    def __init__(self):
        super().__init__('teleop_keyboard')
        
        # Publisher for velocity commands
        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)
        
        # Current velocities
        self.linear_vel = 0.0
        self.angular_vel = 0.0
        
        # Terminal settings (only if stdin is a TTY)
        self.settings = None
        self.is_interactive = sys.stdin.isatty()
        if self.is_interactive and sys.platform != 'win32':
            try:
                self.settings = termios.tcgetattr(sys.stdin)
            except Exception as e:
                self.get_logger().warn(f'Failed to get terminal settings: {e}')
                self.is_interactive = False
        
        self.get_logger().info('Keyboard teleoperation node started')
        self.print_help()

    def print_help(self):
        """Print help message."""
        print(HELP_MSG)
    
    def print_status(self):
        """Print current velocity status."""
        print(f"Linear: {self.linear_vel:.3f} m/s | Angular: {self.angular_vel:.3f} rad/s", end='\r')

    def get_key(self, timeout=0.1):
        """Get keyboard input with timeout."""
        if not self.is_interactive:
            # No interactive terminal available
            return None
            
        if sys.platform == 'win32':
            # Windows (не поддерживается полностью)
            import msvcrt
            if msvcrt.kbhit():
                return msvcrt.getch().decode('utf-8')
            return None
        else:
            # Linux/Unix
            try:
                tty.setraw(sys.stdin.fileno())
                rlist, _, _ = select.select([sys.stdin], [], [], timeout)
                if rlist:
                    key = sys.stdin.read(1)
                    return key
            except Exception:
                pass
            return None

    def update_velocity(self, key):
        """Update velocity based on key press."""
        action = KEYS.get(key.lower())
        
        if action == 'forward':
            self.linear_vel = min(self.linear_vel + LINEAR_STEP, MAX_LINEAR_VELOCITY)
            self.angular_vel = 0.0
        elif action == 'backward':
            self.linear_vel = max(self.linear_vel - LINEAR_STEP, -MAX_LINEAR_VELOCITY)
            self.angular_vel = 0.0
        elif action == 'left':
            self.linear_vel = min(self.linear_vel + LINEAR_STEP, MAX_LINEAR_VELOCITY)
            self.angular_vel = MAX_ANGULAR_VELOCITY * 0.5
        elif action == 'right':
            self.linear_vel = min(self.linear_vel + LINEAR_STEP, MAX_LINEAR_VELOCITY)
            self.angular_vel = -MAX_ANGULAR_VELOCITY * 0.5
        elif action == 'rotate_left':
            self.linear_vel = 0.0
            self.angular_vel = MAX_ANGULAR_VELOCITY
        elif action == 'rotate_right':
            self.linear_vel = 0.0
            self.angular_vel = -MAX_ANGULAR_VELOCITY
        elif action == 'stop':
            self.linear_vel = 0.0
            self.angular_vel = 0.0
            
        return action is not None

    def publish_velocity(self):
        """Publish current velocity to /cmd_vel topic."""
        twist = Twist()
        twist.linear.x = self.linear_vel
        twist.angular.z = self.angular_vel
        self.publisher.publish(twist)

    def run(self):
        """Main loop for teleoperation."""
        if not self.is_interactive:
            self.get_logger().warn(
                'No interactive terminal available. '
                'Run directly: ros2 run teleop_jetbot teleop_keyboard'
            )
            # Still keep the node alive but with slow loop
            try:
                while rclpy.ok():
                    self.publish_velocity()
                    time.sleep(0.1)
            except KeyboardInterrupt:
                pass
            return
        
        try:
            while rclpy.ok():
                key = self.get_key(timeout=0.1)
                
                if key:
                    if key == '\x03':  # Ctrl+C
                        break
                    
                    if self.update_velocity(key):
                        pass  # Velocity updated
                
                # Update status display and publish velocity
                self.print_status()
                self.publish_velocity()
                
        except Exception as e:
            self.get_logger().error(f'Error: {e}')
        finally:
            # Stop the robot
            self.linear_vel = 0.0
            self.angular_vel = 0.0
            self.publish_velocity()
            
            # Restore terminal settings
            if self.settings is not None and sys.platform != 'win32':
                try:
                    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.settings)
                except Exception:
                    pass


def main(args=None):
    """Main function to initialize and run the node."""
    rclpy.init(args=args)
    node = TeleopKeyboard()
    
    try:
        node.run()
    except KeyboardInterrupt:
        node.get_logger().info('Keyboard teleoperation stopped')
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
