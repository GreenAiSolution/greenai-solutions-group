"""python3 run_sim.py  -> cleans a sample apartment in simulation and prints progress."""
import os, secrets, threading, time
from greenbot.api import serve
from greenbot.grid import Grid
from greenbot.robot import Robot, State
from greenbot.scheduler import Scheduler
from greenbot.sim import SimHAL

ROOM = [
    "..................",
    "..####......##....",
    "..####............",
    "..................",
    "........XX........",
    "..................",
    "...........####...",
    "..................",
]

if __name__ == "__main__":
    grid, hal, sched = Grid.from_ascii(ROOM), SimHAL(), Scheduler()
    robot = Robot(grid, hal)
    token = os.environ.get("GREENBOT_TOKEN") or secrets.token_urlsafe(16)
    print("API token:", token)
    threading.Thread(target=serve, args=(robot, sched, token, "127.0.0.1", 8080), daemon=True).start()
    robot.start()
    while robot.state != State.DOCKED:
        robot.tick()
        time.sleep(0.005)
    print(robot.status())
