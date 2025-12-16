---
sidebar_position: 3
---

# ROS 2 Examples for Physical AI and Humanoid Robotics

## Introduction to ROS 2 Examples

This section provides practical ROS 2 examples that demonstrate key concepts in Physical AI and humanoid robotics. Each example builds upon the foundational ROS 2 concepts and shows how to implement specific capabilities relevant to embodied intelligence.

## Basic Communication Patterns

### Publisher-Subscriber Pattern

#### C++ Example: Sensor Data Publisher
```cpp
#include "rclcpp/rclcpp.hpp"
#include "sensor_msgs/msg/joint_state.hpp"

class JointStatePublisher : public rclcpp::Node
{
public:
    JointStatePublisher() : Node("joint_state_publisher")
    {
        publisher_ = this->create_publisher<sensor_msgs::msg::JointState>(
            "joint_states", 10);
        timer_ = this->create_wall_timer(
            50ms, std::bind(&JointStatePublisher::publish_joint_states, this));
    }

private:
    void publish_joint_states()
    {
        auto message = sensor_msgs::msg::JointState();
        message.header.stamp = this->now();
        message.name = {"hip_joint", "knee_joint", "ankle_joint"};
        message.position = {0.1, 0.2, 0.3};

        publisher_->publish(message);
    }

    rclcpp::TimerBase::SharedPtr timer_;
    rclcpp::Publisher<sensor_msgs::msg::JointState>::SharedPtr publisher_;
};

int main(int argc, char * argv[])
{
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<JointStatePublisher>());
    rclcpp::shutdown();
    return 0;
}
```

#### Python Example: Sensor Data Subscriber
```python
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState

class JointStateSubscriber(Node):
    def __init__(self):
        super().__init__('joint_state_subscriber')
        self.subscription = self.create_subscription(
            JointState,
            'joint_states',
            self.listener_callback,
            10)
        self.subscription  # prevent unused variable warning

    def listener_callback(self, msg):
        self.get_logger().info(f'Received joint positions: {msg.position}')

def main(args=None):
    rclpy.init(args=args)
    joint_state_subscriber = JointStateSubscriber()
    rclpy.spin(joint_state_subscriber)
    joint_state_subscriber.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Control Systems Examples

### Joint Control Interface

#### Joint Trajectory Controller
```cpp
#include "rclcpp/rclcpp.hpp"
#include "control_msgs/msg/joint_trajectory_controller_state.hpp"
#include "trajectory_msgs/msg/joint_trajectory.hpp"

class JointTrajectoryClient : public rclcpp::Node
{
public:
    JointTrajectoryClient() : Node("joint_trajectory_client")
    {
        client_ = this->create_client<control_msgs::srv::SetTrajectoryParameters>(
            "set_joint_trajectory");
    }

    void send_trajectory()
    {
        auto request = std::make_shared<control_msgs::srv::SetTrajectoryParameters::Request>();
        request->trajectory.joint_names = {"hip_joint", "knee_joint", "ankle_joint"};

        trajectory_msgs::msg::JointTrajectoryPoint point;
        point.positions = {0.5, 0.3, 0.1};
        point.time_from_start.sec = 1;
        request->trajectory.points.push_back(point);

        while (!client_->wait_for_service(std::chrono::seconds(1))) {
            if (!rclcpp::ok()) {
                RCLCPP_ERROR(this->get_logger(), "Interrupted while waiting for the service.");
                return;
            }
            RCLCPP_INFO(this->get_logger(), "Service not available, waiting again...");
        }

        auto result = client_->async_send_request(request);
    }

private:
    rclcpp::Client<control_msgs::srv::SetTrajectoryParameters>::SharedPtr client_;
};
```

## Perception Examples

### Vision Processing Node

#### Image Processing with OpenCV
```python
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import numpy as np

class ImageProcessor(Node):
    def __init__(self):
        super().__init__('image_processor')
        self.subscription = self.create_subscription(
            Image,
            'camera/image_raw',
            self.image_callback,
            10)
        self.publisher = self.create_publisher(Image, 'camera/image_processed', 10)
        self.bridge = CvBridge()

    def image_callback(self, msg):
        # Convert ROS Image message to OpenCV image
        cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')

        # Apply some processing (edge detection example)
        gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)

        # Convert back to ROS Image message
        processed_msg = self.bridge.cv2_to_imgmsg(edges, encoding='mono8')
        processed_msg.header = msg.header

        self.publisher.publish(processed_msg)

def main(args=None):
    rclpy.init(args=args)
    image_processor = ImageProcessor()
    rclpy.spin(image_processor)
    image_processor.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Humanoid Robot Examples

### Balance Control Node

#### Center of Mass Controller
```cpp
#include "rclcpp/rclcpp.hpp"
#include "geometry_msgs/msg/vector3.hpp"
#include "std_msgs/msg/float64_multi_array.hpp"

class BalanceController : public rclcpp::Node
{
public:
    BalanceController() : Node("balance_controller")
    {
        com_subscriber_ = this->create_subscription<geometry_msgs::msg::Vector3>(
            "center_of_mass", 10,
            std::bind(&BalanceController::com_callback, this, std::placeholders::_1));

        joint_command_publisher_ = this->create_publisher<std_msgs::msg::Float64MultiArray>(
            "joint_commands", 10);
    }

private:
    void com_callback(const geometry_msgs::msg::Vector3::SharedPtr msg)
    {
        // Simple balance control algorithm
        double desired_com_x = 0.0;  // Desired center of mass x position
        double error_x = desired_com_x - msg->x;

        // Generate joint commands based on CoM error
        auto joint_cmd = std_msgs::msg::Float64MultiArray();
        joint_cmd.data = {error_x * 0.1, error_x * 0.05};  // Simplified control

        joint_command_publisher_->publish(joint_cmd);
    }

    rclcpp::Subscription<geometry_msgs::msg::Vector3>::SharedPtr com_subscriber_;
    rclcpp::Publisher<std_msgs::msg::Float64MultiArray>::SharedPtr joint_command_publisher_;
};
```

## AI Integration Examples

### ROS 2 with AI Services

#### Vision-Language-Action Node
```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist
from cv_bridge import CvBridge
import cv2
import openai  # Example AI API

class VLAAgent(Node):
    def __init__(self):
        super().__init__('vla_agent')

        # Subscriptions for vision and language
        self.image_sub = self.create_subscription(
            Image, 'camera/image_raw', self.image_callback, 10)
        self.command_sub = self.create_subscription(
            String, 'voice_commands', self.command_callback, 10)

        # Publisher for robot actions
        self.cmd_vel_pub = self.create_publisher(Twist, 'cmd_vel', 10)

        self.bridge = CvBridge()
        self.current_image = None

    def image_callback(self, msg):
        self.current_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')

    def command_callback(self, msg):
        command = msg.data
        if self.current_image is not None:
            # Process command with current image
            action = self.process_command_with_image(command, self.current_image)
            self.execute_action(action)

    def process_command_with_image(self, command, image):
        # This would integrate with an AI model to understand the command
        # in the context of the visual scene
        self.get_logger().info(f'Processing: {command}')
        # For now, return a simple action based on command
        if 'forward' in command.lower():
            return 'move_forward'
        elif 'stop' in command.lower():
            return 'stop'
        else:
            return 'unknown'

    def execute_action(self, action):
        twist = Twist()
        if action == 'move_forward':
            twist.linear.x = 0.5
        elif action == 'stop':
            twist.linear.x = 0.0

        self.cmd_vel_pub.publish(twist)

def main(args=None):
    rclpy.init(args=args)
    vla_agent = VLAAgent()
    rclpy.spin(vla_agent)
    vla_agent.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Simulation Examples

### Gazebo Integration

#### Robot State Publisher
```xml
<!-- URDF snippet for a simple humanoid robot -->
<?xml version="1.0"?>
<robot name="simple_humanoid">
  <link name="base_link">
    <visual>
      <geometry>
        <box size="0.5 0.2 0.2"/>
      </geometry>
    </visual>
    <collision>
      <geometry>
        <box size="0.5 0.2 0.2"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="1.0"/>
      <inertia ixx="1.0" ixy="0.0" ixz="0.0" iyy="1.0" iyz="0.0" izz="1.0"/>
    </inertial>
  </link>

  <joint name="hip_joint" type="revolute">
    <parent link="base_link"/>
    <child link="upper_leg"/>
    <axis xyz="0 0 1"/>
    <limit lower="-1.57" upper="1.57" effort="100" velocity="1"/>
  </joint>

  <link name="upper_leg">
    <visual>
      <geometry>
        <box size="0.1 0.4 0.1"/>
      </geometry>
    </visual>
  </link>
</robot>
```

## Learning Objectives

After studying these examples, you should be able to:

1. Implement basic ROS 2 communication patterns for robotics
2. Create nodes for sensor processing and actuator control
3. Integrate perception systems with ROS 2
4. Design control systems for humanoid robots using ROS 2
5. Integrate AI components with ROS 2 for Physical AI applications

## Running the Examples

### Build and Run
```bash
# Build your workspace
cd ~/ros2_physical_ai_ws
colcon build --packages-select physical_ai_examples

# Source the environment
source install/setup.bash

# Run the example nodes
ros2 run physical_ai_examples joint_state_publisher
ros2 run physical_ai_examples image_processor
```

### Launch Multiple Nodes
```xml
<!-- launch/physical_ai_example.launch.py -->
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='physical_ai_examples',
            executable='joint_state_publisher',
            name='joint_publisher'
        ),
        Node(
            package='physical_ai_examples',
            executable='image_processor',
            name='image_processor'
        ),
    ])
```

These examples provide a foundation for implementing Physical AI and humanoid robotics systems using ROS 2. Each example can be extended and modified to suit specific application requirements.