import rclpy
from rclpy.node import Node
from my_robot_interfaces.srv import Notes
import sqlite3


conn = sqlite3.connect("notes.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    note TEXT
)
""")
conn.commit()

class NotesServer(Node):

    def __init__(self):
        super().__init__("node3_notes_server")

        self.srv = self.create_service(
            Notes,
            "notes_service",
            self.callback
        )

        self.get_logger().info(" Node3 Notes Server Running")

    def callback(self, request, response):

        if request.request_type == "store":

            cur.execute(
                "INSERT INTO notes (note) VALUES (?)",
                (request.note,)
            )
            conn.commit()

            response.response = "Note stored"

        elif request.request_type == "fetch":

            cur.execute("SELECT note FROM notes")
            rows = cur.fetchall()

            response.response = str(rows)

        return response


def main():
    rclpy.init()
    node = NotesServer()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()