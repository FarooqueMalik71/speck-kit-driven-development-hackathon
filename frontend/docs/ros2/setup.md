---
sidebar_position: 2
---

# Setting up ROS 2 for Physical AI Development

## Prerequisites

Before installing ROS 2, ensure your system meets the following requirements:

### System Requirements
- **Operating System**: Ubuntu 20.04/22.04, Windows 10/11, or macOS
- **RAM**: Minimum 8GB recommended (16GB+ for complex simulations)
- **Storage**: At least 20GB of free space
- **Processor**: Multi-core processor (Intel i5 or equivalent recommended)

### Software Dependencies
- **Python 3.8+**: Required for ROS 2 tools and packages
- **CMake 3.12+**: Build system for C++ packages
- **GCC 7.4+**: C++ compiler (Linux)
- **Git**: Version control for package management

## Installation Methods

### Ubuntu Installation

#### Setup
```bash
# Add ROS 2 GPG key
sudo apt update && sudo apt install -y curl gnupg lsb-release
curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key | sudo gpg --dearmor -o /usr/share/keyrings/ros-archive-keyring.gpg

# Add ROS 2 repository
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(source /etc/os-release && echo $UBUNTU_CODENAME) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null

# Update package list
sudo apt update
```

#### Install ROS 2
```bash
# Install ROS 2 Desktop (includes GUI tools)
sudo apt install ros-humble-desktop

# Install development tools
sudo apt install python3-rosdep python3-rosinstall python3-rosinstall-generator python3-wstool build-essential
```

### Windows Installation

#### Using Chocolatey
```powershell
# Install Chocolatey if not already installed
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Install ROS 2
choco upgrade ros-humble-desktop -y
```

### Source Installation
For the latest features or development work:
```bash
# Clone the ROS 2 source code
git clone -b humble https://github.com/ros2/ros2.git
cd ros2

# Install dependencies
rosdep update
rosdep install --from-paths src --ignore-src -r -y

# Build ROS 2
colcon build --symlink-install
```

## Environment Setup

### Source ROS 2 Environment
```bash
# Ubuntu
source /opt/ros/humble/setup.bash

# Add to bashrc for automatic loading
echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
```

### Create a Workspace
```bash
# Create workspace directory
mkdir -p ~/ros2_physical_ai_ws/src
cd ~/ros2_physical_ai_ws

# Source ROS 2 environment
source /opt/ros/humble/setup.bash

# Build the workspace
colcon build
```

### Source Workspace Environment
```bash
# Source the workspace
source install/setup.bash

# Add to bashrc
echo "source ~/ros2_physical_ai_ws/install/setup.bash" >> ~/.bashrc
```

## Essential Tools

### Development Tools
- **rviz2**: 3D visualization tool for robotics
- **rqt**: Graphical user interface for ROS 2
- **ros2cli**: Command-line tools for ROS 2
- **Gazebo**: Robot simulation environment

### Installation
```bash
# Install development tools
sudo apt install ros-humble-rviz2 ros-humble-rqt ros-humble-gazebo-* ros-humble-ros2-control-* ros-humble-ros2-controllers
```

## Physical AI Specific Setup

### Install Physical AI Related Packages
```bash
# Navigation stack for mobile robots
sudo apt install ros-humble-navigation2 ros-humble-nav2-bringup

# Manipulation packages
sudo apt install ros-humble-moveit ros-humble-moveit-resources

# Perception packages
sudo apt install ros-humble-vision-opencv ros-humble-cv-bridge ros-humble-image-transport

# Humanoid robotics packages
sudo apt install ros-humble-hardware-interface ros-humble-controller-manager
```

### Create Physical AI Package
```bash
# Navigate to workspace
cd ~/ros2_physical_ai_ws/src

# Create a new package for Physical AI examples
ros2 pkg create --build-type ament_cmake --dependencies rclcpp rclpy std_msgs sensor_msgs geometry_msgs physical_ai_interfaces physical_ai_control -- physical_ai_examples

# Build the workspace
cd ~/ros2_physical_ai_ws
colcon build --packages-select physical_ai_examples
```

## Verification

### Test Installation
```bash
# Check ROS 2 version
ros2 --version

# List available commands
ros2

# Check for running ROS 2 nodes
ros2 node list
```

### Run a Simple Test
```bash
# Terminal 1: Start a talker node
ros2 run demo_nodes_cpp talker

# Terminal 2: Start a listener node (after sourcing ROS 2 environment)
ros2 run demo_nodes_cpp listener
```

## Troubleshooting

### Common Issues
- **Permission Issues**: Ensure proper setup of ROS 2 environment variables
- **Dependency Issues**: Run `rosdep install --from-paths src --ignore-src -r -y` in workspace
- **Build Issues**: Check for missing dependencies and correct CMakeLists.txt
- **Network Issues**: Configure ROS 2 for multi-machine communication if needed

### Environment Variables
```bash
# Set ROS domain ID to avoid conflicts
export ROS_DOMAIN_ID=42

# Enable security features
export ROS_SECURITY_ROOT_DIRECTORY=/path/to/security/config
```

## Learning Objectives

After completing this section, you should be able to:

1. Install ROS 2 on your preferred operating system
2. Set up a development workspace for Physical AI projects
3. Install essential tools and packages for robotics development
4. Verify your ROS 2 installation with basic tests

## Next Steps

With ROS 2 installed, you can begin exploring the practical examples throughout this textbook. The examples will demonstrate how to use ROS 2 for implementing Physical AI and humanoid robotics systems, building on the foundation established in this setup process.