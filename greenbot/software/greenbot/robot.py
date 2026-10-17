"""High-level state machine. Hardware access goes through a `hal` object (real or simulated)."""
from enum import Enum

from .config import RobotConfig
from .coverage import plan_coverage
from .safety import SafetyMonitor


class State(str, Enum):
    DOCKED = "docked"
    CLEANING = "cleaning"
    PAUSED = "paused"
    RETURNING = "returning"
    CHARGING = "charging"
    ERROR = "error"


class Robot:
    def __init__(self, grid, hal, cfg=RobotConfig(), dock=(0, 0)):
        self.grid, self.hal, self.cfg, self.dock = grid, hal, cfg, dock
        self.safety = SafetyMonitor(cfg)
        self.state = State.DOCKED
        self.fault = None
        self.pos = dock
        self.path = []
        self.resume_after_charge = False

    # -- commands (from app / schedule) --
    def start(self):
        if self.state in (State.DOCKED, State.PAUSED, State.CHARGING):
            if self.hal.battery_pct() < self.cfg.low_battery_pct:
                return False
            if not self.path:
                self.path = plan_coverage(self.grid, self.pos)
            self.state = State.CLEANING
            self.grid.mark_cleaned(*self.pos)
            self.hal.set_cleaning(True)
            return True
        return False

    def pause(self):
        if self.state == State.CLEANING:
            self.state = State.PAUSED
            self.hal.set_cleaning(False)

    def go_dock(self):
        if self.state in (State.CLEANING, State.PAUSED):
            self.state = State.RETURNING
            self.hal.set_cleaning(False)

    def clear_error(self):
        if self.state == State.ERROR:
            self.fault, self.state = None, State.PAUSED

    # -- one control tick --
    def tick(self):
        s = self.hal.read_sensors()
        fault = self.safety.check(s)
        if fault and self.state != State.ERROR:
            self.hal.stop()
            self.fault, self.state = fault, State.ERROR
            return
        if self.state == State.CLEANING:
            if s["battery_pct"] < self.cfg.low_battery_pct or s.get("bin_pct", 0) >= self.cfg.bin_full_pct:
                self.resume_after_charge = s["battery_pct"] < self.cfg.low_battery_pct
                self.go_dock()
            elif self.path:
                self.pos = self.path.pop(0)
                self.hal.move_to(self.pos)
                self.grid.mark_cleaned(*self.pos)
            else:
                self.go_dock()
        elif self.state == State.RETURNING:
            self.pos = self.dock
            self.hal.move_to(self.dock)
            self.state = State.CHARGING
        elif self.state == State.CHARGING:
            self.hal.charge()
            if self.hal.battery_pct() >= self.cfg.resume_battery_pct:
                if self.resume_after_charge and self.path:
                    self.resume_after_charge = False
                    self.start()
                else:
                    self.state = State.DOCKED

    def status(self):
        return {
            "state": self.state.value,
            "fault": self.fault,
            "battery_pct": round(self.hal.battery_pct(), 1),
            "coverage_pct": round(self.grid.coverage() * 100, 1),
            "position": list(self.pos),
        }
