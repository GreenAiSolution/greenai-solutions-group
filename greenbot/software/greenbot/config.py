from dataclasses import dataclass


@dataclass(frozen=True)
class RobotConfig:
    cell_m: float = 0.05            # occupancy grid resolution
    body_radius_m: float = 0.17     # chassis radius
    brush_width_m: float = 0.20     # cleaning swath
    max_speed_mps: float = 0.30
    low_battery_pct: float = 20.0   # head to dock
    resume_battery_pct: float = 90.0
    cliff_mm: float = 60.0          # ToF reading above this = drop-off
    stall_amps: float = 2.5         # wheel/brush stall threshold
    bin_full_pct: float = 90.0
    heartbeat_timeout_s: float = 0.5  # MCU stops motors if Pi goes silent
