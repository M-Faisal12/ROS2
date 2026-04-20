import rclpy
from rclpy.node import Node
from my_robot_interfaces.srv import Schedule
import sqlite3


conn = sqlite3.connect("schedule.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS schedule (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    time TEXT,
    event TEXT
)
""")
conn.commit()


class ScheduleServer(Node):

    def __init__(self):
        super().__init__("node2_schedule_server")

        self.srv = self.create_service(
            Schedule,
            "schedule_service",
            self.callback
        )

        self.get_logger().info(" Node2 Schedule Server Running")

    def callback(self, request, response):

        if request.request_type == "store":

            cur.execute(
                "INSERT INTO schedule (time, event) VALUES (?, ?)",
                (request.time, request.event)
            )
            conn.commit()

            response.response = "Schedule stored"

        elif request.request_type == "fetch":

            cur.execute("SELECT time, event FROM schedule")
            rows = cur.fetchall()

            response.response = str(rows)

        return response


def main():
    rclpy.init()
    node = ScheduleServer()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()