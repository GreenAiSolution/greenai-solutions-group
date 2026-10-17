import datetime as dt
import unittest

from greenbot.coverage import plan_coverage
from greenbot.grid import Grid
from greenbot.robot import Robot, State
from greenbot.scheduler import Scheduler
from greenbot.sim import SimHAL

ROOM = ["........", ".##.....", "........", "....X...", "........"]


def run(robot, max_ticks=5000):
    for _ in range(max_ticks):
        robot.tick()
        if robot.state in (State.DOCKED, State.ERROR):
            return


class Tests(unittest.TestCase):
    def test_full_coverage(self):
        g = Grid.from_ascii(ROOM)
        r = Robot(g, SimHAL())
        self.assertTrue(r.start())
        run(r)
        self.assertEqual(r.state, State.DOCKED)
        self.assertEqual(g.coverage(), 1.0)

    def test_plan_avoids_obstacles(self):
        g = Grid.from_ascii(ROOM)
        for c in plan_coverage(g, (0, 0)):
            self.assertTrue(g.passable(*c))

    def test_cliff_stops_robot(self):
        hal = SimHAL()
        r = Robot(Grid.from_ascii(ROOM), hal)
        r.start()
        hal.inject = {"cliff_mm": [20, 120, 20, 20]}
        r.tick()
        self.assertEqual((r.state, r.fault), (State.ERROR, "cliff"))

    def test_low_battery_recharges_and_resumes(self):
        g = Grid.from_ascii(ROOM)
        hal = SimHAL(battery=25, drain_per_move=1.0)
        r = Robot(g, hal)
        r.start()
        run(r, 20000)
        self.assertEqual(g.coverage(), 1.0)

    def test_refuses_start_on_dead_battery(self):
        r = Robot(Grid.from_ascii(ROOM), SimHAL(battery=5))
        self.assertFalse(r.start())

    def test_scheduler_fires_once_per_minute(self):
        s = Scheduler()
        s.add(0, "09:00")
        t = dt.datetime(2026, 10, 19, 9, 0)  # a Monday
        self.assertTrue(s.due(t))
        self.assertFalse(s.due(t))


if __name__ == "__main__":
    unittest.main()
