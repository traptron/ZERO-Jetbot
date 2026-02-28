#!/usr/bin/env python3

# Copyright (c) 2026 Alice Zenina and Alexander Grachev RTU MIREA (Russia)
# SPDX-License-Identifier: MIT
# Details in the LICENSE file in the root of the package.

'''
АННОТАЦИЯ
Узел ROS 2 для фильтрации данных лазерного скана (LaserScan) по угловому
сектору. Конфигурируется параметрами: задает входной/выходной топики,
границы сектора в градусах и режим инверсии. Использует QoS с политикой
BEST_EFFORT для совместимости с лидарами.

ANNOTATION
ROS 2 node for filtering laser scan (LaserScan) data by angular sector.
Configurable via parameters: sets input/output topics, sector boundaries
in degrees, and inversion mode. Uses QoS with BEST_EFFORT policy for
lidar compatibility.
'''

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy
import math

from sensor_msgs.msg import LaserScan

class LaserSectorFilter(Node):
    def __init__(self):
        super().__init__('laser_sector_filter')
        
        # Declare parameters: sector start and end in degrees
        self.declare_parameter('start_angle_deg', -135.0)  # sector start in degrees
        self.declare_parameter('end_angle_deg', 135.0)    # sector end in degrees
        self.declare_parameter('input_topic', '/scan')   # input topic
        self.declare_parameter('output_topic', '/scan_filtered')  # output topic
        self.declare_parameter('invert_sector', False)   # invert sector (keep everything except specified)
        self.declare_parameter('output_frame_id', '')   # frame_id for output topic
        
        # Get parameters
        self.start_angle_deg = self.get_parameter('start_angle_deg').value
        self.end_angle_deg = self.get_parameter('end_angle_deg').value
        self.input_topic = self.get_parameter('input_topic').value
        self.output_topic = self.get_parameter('output_topic').value
        self.invert_sector = self.get_parameter('invert_sector').value
        self.output_frame_id = self.get_parameter('output_frame_id').value
        
        
        # Convert degrees to radians
        self.start_angle_rad = math.radians(self.start_angle_deg)
        self.end_angle_rad = math.radians(self.end_angle_deg)
        
        self.get_logger().info(
            f'Lidar sector filter initialized with parameters:'
        )
        self.get_logger().info(
            f'  Sector: {self.start_angle_deg}° to {self.end_angle_deg}°'
        )
        self.get_logger().info(f'  Input topic: {self.input_topic}')
        self.get_logger().info(f'  Output topic: {self.output_topic}')
        self.get_logger().info(f'  Invert sector: {self.invert_sector}')
        
        # Configure QoS for reliable data transmission with lidar
        qos_profile = QoSProfile(
            depth=10,
            reliability=ReliabilityPolicy.BEST_EFFORT
        )
        
        # Subscriber and publisher
        self.subscription = self.create_subscription(
            LaserScan,
            self.input_topic,
            self.scan_callback,
            qos_profile
        )
        
        self.publisher = self.create_publisher(
            LaserScan,
            self.output_topic,
            10
        )
        
        # Variables for performance monitoring
        self.scan_count = 0
        
    def normalize_angle(self, angle):
        """Normalize angle to range [-π, π]"""
        while angle > math.pi:
            angle -= 2.0 * math.pi
        while angle < -math.pi:
            angle += 2.0 * math.pi
        return angle
    
    def angle_in_sector(self, angle, start, end):
        """Check if angle is within given sector (considering cyclicity)"""
        # Normalize angles
        angle = self.normalize_angle(angle)
        start = self.normalize_angle(start)
        end = self.normalize_angle(end)
        
        # If start <= end, normal sector
        if start <= end:
            return start <= angle <= end
        else:
            # Sector crosses -π/π boundary
            return angle >= start or angle <= end
    
    def scan_callback(self, msg):
        self.scan_count += 1
        
        # Calculate angles for each beam
        num_readings = len(msg.ranges)
        filtered_ranges = []
        filtered_intensities = []
        filtered_indices = []
        
        for i in range(num_readings):
            # Calculate current beam angle
            angle = msg.angle_min + i * msg.angle_increment
            
            # Check if beam is within sector
            in_sector = self.angle_in_sector(
                angle,
                self.start_angle_rad,
                self.end_angle_rad
            )
            
            # If sector is inverted, flip condition
            if self.invert_sector:
                in_sector = not in_sector
            
            if in_sector:
                filtered_ranges.append(msg.ranges[i])
                if i < len(msg.intensities):
                    filtered_intensities.append(msg.intensities[i])
                filtered_indices.append(i)
        
        if not filtered_ranges:
            self.get_logger().warn('Sector is empty! Check angle parameters.')
            return
        
        # Calculate angles of first and last beam in filtered sector
        if filtered_indices:
            first_idx = filtered_indices[0]
            last_idx = filtered_indices[-1]
            new_angle_min = msg.angle_min + first_idx * msg.angle_increment
            new_angle_max = msg.angle_min + last_idx * msg.angle_increment
        else:
            new_angle_min = 0.0
            new_angle_max = 0.0
        
        # Create new LaserScan message
        filtered_scan = LaserScan()
        
        # Copy header (update timestamp)
        if self.output_frame_id == '':
            filtered_scan.header.frame_id = msg.header.frame_id
        else:
            filtered_scan.header.frame_id = self.output_frame_id
        filtered_scan.header.stamp = msg.header.stamp

        filtered_scan.header.stamp = self.get_clock().now().to_msg()
        
        # Set scan parameters
        filtered_scan.angle_min = new_angle_min
        filtered_scan.angle_max = new_angle_max
        filtered_scan.angle_increment = msg.angle_increment
        filtered_scan.time_increment = msg.time_increment
        filtered_scan.scan_time = msg.scan_time
        filtered_scan.range_min = msg.range_min
        filtered_scan.range_max = msg.range_max
        
        # Set data
        filtered_scan.ranges = filtered_ranges
        if filtered_intensities:
            filtered_scan.intensities = filtered_intensities
        
        # Publish filtered scan
        self.publisher.publish(filtered_scan)
        

def main(args=None):
    rclpy.init(args=args)
    
    node = LaserSectorFilter()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        # Log shutdown message BEFORE destroying node
        node.get_logger().info('Keyboard interrupt received, shutting down...')
    except Exception as e:
        # Log error BEFORE destroying node
        node.get_logger().error(f'Unexpected error: {e}')
    
    # Clean shutdown
    node.destroy_node()
    rclpy.try_shutdown()
    
    
if __name__ == '__main__':
    main()