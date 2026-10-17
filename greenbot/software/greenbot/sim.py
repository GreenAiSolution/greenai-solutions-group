"""Simulated HAL so the whole stack runs and is testable without hardware."""


class SimHAL:
    def __init__(self, battery=100.0, drain_per_move=0.15, charge_per_tick=5.0):
        self.battery = battery
        self.drain, self.charge_rate = drain_per_move, charge_per_tick
        self.cleaning = False
        self.inject = {}  # fault injection: e.g. {"cliff_mm": [90]}
        self.bin = 0.0

    def battery_pct(self):
        return self.battery

    def read_sensors(self):
        s = {"battery_pct": self.battery, "bin_pct": self.bin, "cliff_mm": [20, 20, 20, 20],
             "motor_amps": [0.8, 0.8], "tilt_deg": 0, "lifted": False}
        s.update(self.inject)
        return s

    def set_cleaning(self, on):
        self.cleaning = on

    def move_to(self, cell):
        self.battery = max(0.0, self.battery - self.drain)
        self.bin += 0.01

    def charge(self):
        self.battery = min(100.0, self.battery + self.charge_rate)
        self.bin = 0.0

    def stop(self):
        self.cleaning = False
