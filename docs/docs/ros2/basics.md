---
sidebar_position: 2
---

# ROS 2 Basics

## Core Concepts

### Nodes

Nodes are the fundamental building blocks of ROS 2 applications. They represent individual processes that perform specific functions within a robotic system.

**Node Characteristics:**
- **Process-based**: Each node typically runs as a separate process
- **Communication endpoints**: Nodes communicate through topics, services, and actions
- **Namespaced**: Nodes can be organized using namespaces
- **Parameterized**: Nodes can accept parameters for configuration

**Node Lifecycle:**
- **Unconfigured**: Node created but not yet configured
- **Inactive**: Node configured but not active
- **Active**: Node running and processing data
- **Finalized**: Node destroyed and resources released

### Topics and Publishers/Subscribers

Topics enable asynchronous, many-to-many communication between nodes:

**Publisher:**
- Sends messages to a topic
- Multiple publishers can publish to the same topic
- Uses Quality of Service (QoS) settings for reliability

**Subscriber:**
- Receives messages from a topic
- Multiple subscribers can subscribe to the same topic
- Callback functions process incoming messages

**Message Types:**
- **Standard types**: Built-in types like std_msgs, geometry_msgs
- **Custom types**: User-defined message structures
- **Serialization**: Messages are serialized for transmission

### Services and Clients

Services enable synchronous request-response communication:

**Service Server:**
- Provides a service that can be called
- Processes requests and returns responses
- Uses service definition files (.srv)

**Service Client:**
- Calls a service and waits for response
- Blocks until response is received
- Handles service call failures

### Actions

Actions enable long-running operations with feedback:

**Action Server:**
- Handles long-running goals with feedback
- Manages goal, result, and feedback messages
- Supports goal preemption and cancellation

**Action Client:**
- Sends goals to action servers
- Receives feedback during execution
- Can cancel or preempt goals

## Quality of Service (QoS)

QoS settings control communication behavior:

### Reliability Policy
- **Reliable**: All messages are guaranteed to be delivered
- **Best effort**: Messages may be lost, but delivery is attempted

### Durability Policy
- **Transient local**: Late-joining subscribers receive last message
- **Volatile**: No message persistence for late joiners

### History Policy
- **Keep last**: Maintain last N messages
- **Keep all**: Maintain all messages (use with caution)

### Lifespan and Deadline
- **Lifespan**: How long messages remain valid
- **Deadline**: Maximum time to receive messages

## Parameter System

ROS 2 provides a flexible parameter system:

### Parameter Types
- **Integer, double, string**: Basic data types
- **Boolean**: True/false values
- **Lists**: Arrays of values
- **Dictionaries**: Key-value mappings

### Parameter Management
- **Node parameters**: Parameters associated with specific nodes
- **Global parameters**: System-wide parameters
- **Parameter callbacks**: React to parameter changes
- **Parameter validation**: Ensure parameter values are valid

## Launch System

The launch system manages complex robot applications:

### Launch Files
- **XML and Python**: Multiple launch file formats
- **Node composition**: Group nodes into single processes
- **Conditional execution**: Start nodes based on conditions
- **Parameter passing**: Pass parameters to nodes

### Launch Actions
- **Node execution**: Start and manage nodes
- **Timer-based actions**: Execute actions after delays
- **Event handling**: React to system events
- **Shutdown handling**: Graceful system shutdown

## Package Structure

ROS 2 packages follow a standard structure:

### Package Manifest (package.xml)
- **Dependencies**: List of required packages
- **Maintainers**: Package maintainers and contacts
- **License**: Package licensing information
- **Description**: Brief package description

### CMakeLists.txt (for C++)
- **Build configuration**: Compiler settings and dependencies
- **Target definitions**: Executables and libraries to build
- **Install rules**: Where to install built artifacts
- **Test configuration**: Unit and integration tests

### setup.py (for Python)
- **Python modules**: Python packages to install
- **Entry points**: Console scripts and executables
- **Dependencies**: Python package dependencies
- **Data files**: Non-code files to install

## Client Libraries

### rclcpp (C++)
Modern C++ client library for ROS 2:

**Features:**
- **Object-oriented**: Clean C++ interface
- **Type safety**: Strong typing with compile-time checks
- **Performance**: Optimized for real-time applications
- **Memory management**: RAII-based resource management

**Basic Usage:**
```cpp
#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/string.hpp"

class MinimalPublisher : public rclcpp::Node
{
public:
    MinimalPublisher()
    : Node("minimal_publisher"), count_(0)
    {
        publisher_ = this->create_publisher<std_msgs::msg::String>("topic", 10);
        timer_ = this->create_wall_timer(
            500ms, std::bind(&MinimalPublisher::timer_callback, this));
    }

private:
    void timer_callback()
    {
        auto message = std_msgs::msg::String();
        message.data = "Hello, world! " + std::to_string(count_++);
        RCLCPP_INFO(this->get_logger(), "Publishing: '%s'", message.data.c_str());
        publisher_->publish(message);
    }
    rclcpp::TimerBase::SharedPtr timer_;
    rclcpp::Publisher<std_msgs::msg::String>::SharedPtr publisher_;
    size_t count_;
};
```

### rclpy (Python)
Python client library for ROS 2:

**Features:**
- **Pythonic interface**: Natural Python usage patterns
- **Type hints**: Support for type checking
- **Async support**: Asynchronous programming capabilities
- **Easy prototyping**: Rapid development and testing

## Development Tools

### Command Line Tools (ros2cli)
Essential command-line tools for ROS 2:

- **ros2 run**: Run nodes directly
- **ros2 launch**: Launch complex systems
- **ros2 topic**: Inspect and interact with topics
- **ros2 service**: Inspect and call services
- **ros2 action**: Inspect and use actions
- **ros2 param**: Manage node parameters
- **ros2 node**: List and inspect nodes

### Visualization Tools
- **RViz2**: 3D visualization for robotics
- **rqt**: Graphical user interface framework
- **PlotJuggler**: Real-time data plotting
- **Foxglove**: Web-based visualization

## Best Practices

### Design Principles
- **Modularity**: Create focused, single-purpose nodes
- **Loose coupling**: Minimize dependencies between nodes
- **Clear interfaces**: Well-defined communication contracts
- **Error handling**: Robust error management and recovery

### Performance Considerations
- **Message efficiency**: Minimize message size and frequency
- **Threading**: Use appropriate threading models
- **Memory management**: Efficient memory usage
- **Real-time constraints**: Meet timing requirements

### Safety and Security
- **Input validation**: Validate all inputs
- **Resource limits**: Prevent resource exhaustion
- **Secure communication**: Use authentication and encryption
- **Fail-safe design**: Safe behavior during failures

<AIChat />