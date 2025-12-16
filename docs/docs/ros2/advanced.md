---
sidebar_position: 3
---

# Advanced ROS 2 Concepts

## Custom Message Types

### Creating Custom Messages

Custom message types allow you to define application-specific data structures:

**Message Definition File (.msg):**
```
# CustomRobotState.msg
float64 x
float64 y
float64 theta
float64[] joint_positions
geometry_msgs/Point32[] obstacle_points
---
geometry_msgs/Twist command
std_msgs/ColorRGBA led_color
```

**Best Practices:**
- **Descriptive names**: Use clear, descriptive field names
- **Appropriate types**: Choose the right data types for your needs
- **Backward compatibility**: Consider future extensions
- **Documentation**: Comment your message definitions

### Service and Action Definitions

**Service Definition (.srv):**
```
# MoveToGoal.srv
geometry_msgs/PoseStamped target_pose
float64 tolerance
---
bool success
string message
float64 execution_time
```

**Action Definition (.action):**
```
# NavigateToPose.action
geometry_msgs/PoseStamped goal_pose
float64 tolerance
---
geometry_msgs/PoseStamped final_pose
float64 distance_traveled
---
float64 distance_remaining
geometry_msgs/PoseStamped current_pose
string message
```

## Advanced Node Development

### Node Composition

Running multiple nodes in a single process:

```cpp
// Composition example
#include "composition/visibility_control.h"
#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/string.hpp"

class MinimalPublisher : public rclcpp::Node
{
    // Publisher implementation
};

class MinimalSubscriber : public rclcpp::Node
{
    // Subscriber implementation
};

// Composition node
class Composition : public rclcpp::Node
{
public:
    Composition()
    : Node("composition")
    {
        // Create nodes as components
        publisher_node_ = std::make_shared<MinimalPublisher>();
        subscriber_node_ = std::make_shared<MinimalSubscriber>();
    }

private:
    std::shared_ptr<MinimalPublisher> publisher_node_;
    std::shared_ptr<MinimalSubscriber> subscriber_node_;
};
```

### Lifecycle Nodes

Managing node states explicitly:

```cpp
#include "rclcpp_lifecycle/lifecycle_node.hpp"

class LifecyclePublisher : public rclcpp_lifecycle::LifecycleNode
{
public:
    LifecyclePublisher()
    : rclcpp_lifecycle::LifecycleNode("lifecycle_publisher")
    {
    }

private:
    rclcpp_lifecycle::LifecyclePublisher::SharedPtr pub_;

    CallbackReturn on_configure(const rclcpp_lifecycle::State & state)
    {
        pub_ = this->create_publisher<std_msgs::msg::String>("topic", 10);
        return CallbackReturn::SUCCESS;
    }

    CallbackReturn on_activate(const rclcpp_lifecycle::State & state)
    {
        pub_->on_activate();
        return CallbackReturn::SUCCESS;
    }

    CallbackReturn on_deactivate(const rclcpp_lifecycle::State & state)
    {
        pub_->on_deactivate();
        return CallbackReturn::SUCCESS;
    }

    CallbackReturn on_cleanup(const rclcpp_lifecycle::State & state)
    {
        pub_.reset();
        return CallbackReturn::SUCCESS;
    }
};
```

## Real-Time Programming

### Real-Time Considerations

Developing real-time safe ROS 2 applications:

**Memory Allocation:**
- **Avoid dynamic allocation**: In time-critical paths
- **Pre-allocate buffers**: Use fixed-size containers
- **Memory pools**: Pre-allocate memory for repeated use
- **Lock-free data structures**: Reduce synchronization overhead

**Thread Priorities:**
```cpp
#include <sched.h>
#include <sys/resource.h>

void set_realtime_priority(int priority)
{
    struct sched_param param;
    param.sched_priority = priority;
    sched_setscheduler(0, SCHED_FIFO, &param);
}
```

### Time and Timing

Precise timing in ROS 2:

```cpp
// Using ROS time
rclcpp::Time start_time = this->now();
auto duration = rclcpp::Duration::from_seconds(1.0);
rclcpp::Time end_time = start_time + duration;

// Timer with specific period
auto timer = this->create_wall_timer(
    std::chrono::milliseconds(10),
    std::bind(&MyNode::timer_callback, this)
);
```

## Advanced Communication Patterns

### Transports and Middleware

Using different transport mechanisms:

```cpp
// Shared memory transport
rclcpp::QoS qos(10);
qos.durability(RMW_QOS_POLICY_DURABILITY_TRANSIENT_LOCAL);
qos.reliability(RMW_QOS_POLICY_RELIABILITY_RELIABLE);

// Different DDS implementations
// Fast DDS, Cyclone DDS, RTI Connext configuration
```

### Custom Transport Adapters

Creating specialized communication methods:

```cpp
// Example: Custom transport for specific use case
class CustomTransport
{
public:
    void send_data(const std::string& data);
    std::string receive_data();

private:
    // Implementation details
};
```

## Performance Optimization

### Memory Management

Efficient memory usage in ROS 2:

```cpp
// Using message pools to reduce allocation
auto msg = std::make_shared<std_msgs::msg::String>();
msg->data = "Hello World";

// Custom allocators for specific needs
template<typename T>
class PoolAllocator
{
    // Custom memory pool implementation
};
```

### Communication Optimization

Reducing communication overhead:

**Message Filtering:**
```cpp
// Filter messages based on content
auto filtered_sub = this->create_subscription<std_msgs::msg::String>(
    "topic", 10,
    [this](const std_msgs::msg::String::SharedPtr msg) {
        if (msg->data.find("important") != std::string::npos) {
            process_message(msg);
        }
    }
);
```

**Message Throttling:**
```cpp
// Process messages at reduced rate
int message_count = 0;
const int throttle_rate = 5; // Process every 5th message

auto throttled_sub = this->create_subscription<std_msgs::msg::String>(
    "topic", 10,
    [this, &message_count, throttle_rate](const std_msgs::msg::String::SharedPtr msg) {
        if (++message_count % throttle_rate == 0) {
            process_message(msg);
        }
    }
);
```

## Security Features

### Authentication and Authorization

Securing ROS 2 communications:

**DDS Security:**
- **Identity**: Authenticate nodes using certificates
- **Access control**: Control who can access what
- **Encryption**: Encrypt data in transit
- **Audit logging**: Track security events

### Secure Communication Setup

```yaml
# security configuration
name: "robot_control"
permissions: "permissions.xml"
governance: "governance.xml"
```

## Advanced Launch Systems

### Complex Launch Files

Creating sophisticated launch configurations:

```python
# launch/complex_system.launch.py
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node, ComposableNodeContainer
from launch_ros.descriptions import ComposableNode

def generate_launch_description():
    # Launch arguments
    use_sim_time = LaunchConfiguration('use_sim_time')

    # Composable nodes
    container = ComposableNodeContainer(
        name=' perception_container',
        namespace='',
        package='rclcpp_components',
        executable='component_container',
        composable_node_descriptions=[
            ComposableNode(
                package='image_proc',
                plugin='image_proc::RectifyNode',
                name='rectify_node'
            ),
        ],
        output='screen',
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='false',
            description='Use simulation time'
        ),
        container,
    ])
```

## Testing and Debugging

### Unit Testing

Comprehensive testing for ROS 2 nodes:

```cpp
// test/my_node_test.cpp
#include <gtest/gtest.h>
#include <rclcpp/rclcpp.hpp>
#include "my_package/my_node.hpp"

class TestMyNode : public ::testing::Test
{
protected:
    void SetUp() override
    {
        rclcpp::init(0, nullptr);
        node_ = std::make_shared<MyNode>();
    }

    void TearDown() override
    {
        rclcpp::shutdown();
    }

    std::shared_ptr<MyNode> node_;
};

TEST_F(TestMyNode, TestMethod)
{
    // Test specific functionality
    EXPECT_TRUE(node_->is_initialized());
}
```

### Integration Testing

Testing complete system behavior:

```cpp
// Integration test with multiple nodes
TEST_F(TestMyNode, TestIntegration)
{
    auto publisher = node_->create_publisher<std_msgs::msg::String>("input", 10);
    auto subscription = node_->create_subscription<std_msgs::msg::String>(
        "output", 10,
        [](const std_msgs::msg::String::SharedPtr msg) {
            // Verify message processing
        }
    );

    // Send test message and verify processing
    auto msg = std::make_shared<std_msgs::msg::String>();
    msg->data = "test";
    publisher->publish(*msg);

    // Wait for processing and verify results
    rclcpp::spin_some(node_->get_node_base_interface());
}
```

## Advanced Tools

### Custom Tools

Creating specialized development tools:

```python
# Custom CLI tool
import argparse
import rclpy
from rclpy.node import Node

class CustomToolNode(Node):
    def __init__(self):
        super().__init__('custom_tool')

    def analyze_communication(self):
        # Custom analysis logic
        pass

def main():
    parser = argparse.ArgumentParser(description='Custom ROS 2 tool')
    parser.add_argument('--analyze', action='store_true')
    args = parser.parse_args()

    rclpy.init()
    tool = CustomToolNode()

    if args.analyze:
        tool.analyze_communication()

    rclpy.shutdown()
```

## Migration Strategies

### ROS 1 to ROS 2 Migration

Approaches for migrating existing systems:

**Bridge Tools:**
- **ros1_bridge**: Connect ROS 1 and ROS 2 systems
- **Message mapping**: Handle differences in message types
- **Service conversion**: Adapt services between versions
- **Parameter translation**: Map parameters between systems

**Gradual Migration:**
- **Component-by-component**: Migrate individual components
- **Layered approach**: Migrate system layers gradually
- **Parallel operation**: Run both versions during transition
- **Testing strategy**: Ensure functionality during migration

## Future Considerations

### ROS 2 Ecosystem Evolution

Staying current with ROS 2 development:

**Rolling Releases:**
- **Latest features**: Access to newest capabilities
- **Early adoption**: Influence on future development
- **Risk management**: Handle breaking changes
- **Testing strategy**: Comprehensive testing of new features

**Standardization:**
- **REP adoption**: Follow ROS Enhancement Proposals
- **Community standards**: Adopt best practices
- **Industry standards**: Integrate with broader standards
- **Interoperability**: Ensure compatibility with other systems

<AIChat />