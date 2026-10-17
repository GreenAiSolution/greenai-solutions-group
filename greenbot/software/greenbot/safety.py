from .config import RobotConfig


class SafetyMonitor:
    """Pure checks; returns a fault string or None. Faults always stop the motors."""

    def __init__(self, cfg: RobotConfig):
        self.cfg = cfg

    def check(self, s: dict):
        c = self.cfg
        if s.get("lifted"):
            return "picked_up"
        if any(d > c.cliff_mm for d in s.get("cliff_mm", [])):
            return "cliff"
        if max(s.get("motor_amps", [0])) > c.stall_amps:
            return "stall"
        if s.get("tilt_deg", 0) > 25:
            return "tilt"
        return None
