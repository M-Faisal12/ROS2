import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/ali-hmaza/Downloads/ROS2/ros2_ws/install/my_py_pkg'
