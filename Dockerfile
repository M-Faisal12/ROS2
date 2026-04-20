FROM ubuntu:24.04

# Set environment variables
ENV LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    ROS_DISTRO=jazzy \
    PYTHON_VERSION=3.12

# Install dependencies
RUN apt-get update && apt-get install -y \
    locales \
    curl \
    gnupg2 \
    lsb-release \
    python${PYTHON_VERSION}-pip \
    python${PYTHON_VERSION}-rosdep \
    build-essential \
    && locale-gen en_US en_US.UTF-8 \
    && rm -rf /var/lib/apt/lists/*

# Add ROS2 repository
RUN curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key | apt-key add - \
    && echo "deb http://packages.ros.org/ros2/ubuntu noble main" > /etc/apt/sources.list.d/ros2-latest.list \
    && apt-get update && apt-get install -y \
    ros-${ROS_DISTRO}-ros-core \
    python${PYTHON_VERSION}-colcon-common-extensions \
    && rm -rf /var/lib/apt/lists/*

# Initialize rosdep
RUN rosdep init || true
RUN rosdep update || true

# Install Python packages with specific versions
RUN pip3 install --upgrade pip==24.0 \
    && pip3 install setuptools==69.0.3 pytest==8.1.1

# Set the working directory
WORKDIR /root/ros2_ws
COPY . /root/ros2_ws/src

# Build the workspace
SHELL ["/bin/bash", "-lc"]
RUN source /opt/ros/${ROS_DISTRO}/setup.sh \
    && rosdep install --from-paths src --ignore-src -r -y \
    && colcon build --symlink-install

# Source the setup files
RUN echo "source /opt/ros/${ROS_DISTRO}/setup.bash" >> /root/.bashrc \
    && echo "source /root/ros2_ws/install/setup.bash" >> /root/.bashrc

# Set environment variables for ROS
ENV PATH=/root/ros2_ws/install/bin:/opt/ros/${ROS_DISTRO}/bin:$PATH
ENV ROS_PACKAGE_PATH=/root/ros2_ws/src:$ROS_PACKAGE_PATH

# Default command
CMD ["/bin/bash"]
