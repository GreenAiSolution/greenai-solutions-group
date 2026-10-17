# GreenBot — GreenAI Digital home cleaning robot

Open system design for a robot vacuum/mop: hardware list, firmware, and a tested control stack.

| Path | What |
|---|---|
| `hardware.html` | Visual hardware list + architecture (open in a browser) |
| `bom.csv` | Machine-readable bill of materials (~$760 full build, ~$650 without optional parts; estimates) |
| `firmware/greenbot_mcu.ino` | ESP32-S3 real-time layer: motors, cliff, bumpers, 500 ms watchdog |
| `software/greenbot/` | Pi-side stack: occupancy grid, coverage planner, state machine, safety, scheduler, REST API |
| `software/run_sim.py` | Runs the full stack in simulation with a fake robot |

## Run it (no hardware needed)

```
cd software
python3 -m unittest discover -s tests -v
python3 run_sim.py
```

## How it works

Two-brain design. The Pi 5 does the thinking (map, route, schedule, app API). The ESP32 owns motors and
safety, so a Linux crash, cliff, or lost heartbeat stops the robot without the Pi's help.
State flow: `DOCKED → CLEANING → RETURNING → CHARGING → DOCKED`; low battery or full bin sends it home and it
resumes the unfinished route after charging. Cliff, stall, tilt, or pick-up put it in `ERROR` until cleared.

## REST API (bearer token)

`GET /status` · `POST /start` · `/pause` · `/dock` · `/clear_error` · `GET|POST /schedule`

## Not done yet (honest status)

- Software runs on a simulator; no real hardware HAL (`UART` + LiDAR driver) yet.
- Coverage planner assumes a known grid. Live SLAM (suggest `slam_toolbox` on ROS 2, or BreezySLAM) is next.
- Firmware is an untested starting point: ADC battery/current readings and encoder interrupts are still TODO.
- No chassis CAD yet; the BOM assumes a ~330 mm round PETG body.
- Dock IR homing and vision obstacle detection (Hailo) are planned, not coded.
