# Differential Drive Robot Hardware

Planned hardware for a compact two-wheel differential-drive robot built around an **NVIDIA
Jetson Orin Nano Super**. An **ESP32-DevKitC-32E** handles the real-time
motor and encoder interface, while the Jetson runs ROS 2,
`ros2_control`, localization, SLAM, Nav2, and vision workloads.

The proposed physical design uses a **165 × 120 × 68 mm uxcell enclosure** as the
chassis, two **65 mm wheels with encoder-equipped motors**, and a **1-inch swivel caster**.

> **Design status:** This is a hardware plan, not a validated assembly or an
> implemented hardware driver. Product specifications, electrical compatibility,
> mechanical fit, and loaded performance must be checked before assembly.

## Table of Contents

- [Hardware Architecture](#hardware-architecture)
- [Components](#components)
- [Power](#power)
- [Drive System](#drive-system)
- [Sensors](#sensors)
- [ROS 2 Data Flow](#ros-2-data-flow)
- [Physical Layout](#physical-layout)
- [Software Mapping](#software-mapping)
- [Physical Bring-Up Order](#physical-bring-up-order)
- [Notes](#notes)

## Hardware Concept

![Differential-drive robot hardware concept](../../images/differential_drive_robot.png)

Concept illustration; dimensions and component placement are provisional.

## Hardware Architecture

```mermaid
flowchart TB
    battery["Zeee 3S LiPo<br/>11.1 V 2200 mAh"]
    fuse["Inline fuse"]
    switch["Main ON/OFF switch"]
    jetson["NVIDIA Jetson Orin Nano Super<br/>ROS 2 / Nav2 / SLAM / Vision"]
    esp["ESP32-DevKitC-32E<br/>Motor + encoder interface"]
    driver["Cytron MDD10A<br/>Dual motor driver"]
    motorL["Left 12 V motor<br/>130 RPM + encoder"]
    motorR["Right 12 V motor<br/>130 RPM + encoder"]
    lidar["RPLIDAR C1"]
    imu["BNO055 IMU"]
    camera["Arducam IMX219<br/>CSI camera"]

    battery --> fuse --> switch
    switch --> jetson
    switch --> driver

    jetson <-->|USB / serial| esp
    esp -->|PWM + direction| driver
    driver --> motorL
    driver --> motorR
    motorL -->|encoder A/B| esp
    motorR -->|encoder A/B| esp

    lidar -->|USB| jetson
    imu -->|I2C| esp
    camera -->|MIPI CSI-2| jetson
```

## Components

Quantities below retain the listed purchase quantities. A multipack does not mean
all units will be installed; verify each linked listing before ordering.

| Part | Model / Specification | Qty | Connection / Role | Amazon US |
| --- | --- | --- | --- | --- |
| Main computer | NVIDIA Jetson Orin Nano Super Developer Kit, 8 GB | 1 | Runs ROS 2, Nav2, SLAM, EKF and vision | NVIDIA / already owned |
| LiDAR | SLAMTEC RPLIDAR C1, 360°, up to 12 m | 1 | USB to Jetson, publishes `/scan` | [Product](https://www.amazon.com/dp/B0CT31PH8S) |
| IMU | Adafruit BNO055 9-DOF | 1 | I2C; orientation/angular velocity/acceleration | [Product](https://www.amazon.com/dp/B017PEIGIG) |
| Camera | Arducam IMX219, 8 MP, 160°, autofocus, MIPI CSI-2 | 1 | CSI to Jetson | [Product](https://www.amazon.com/dp/B0GS5814J8) |
| Motors + wheels | SatcOp 12 V encoder gear motor, 130 RPM, 65 mm wheel, bracket | 2 | MDD10A drive + encoder feedback to ESP32 | [Product](https://www.amazon.com/dp/B0CKSZTD4B) |
| Motor driver | Cytron MDD10A, dual-channel 10 A | 1 | PWM/direction from ESP32; drives both motors | [Search](https://www.amazon.com/s?k=Cytron+MDD10A) |
| Microcontroller | ESP32-DevKitC-32E / ESP32-WROOM-32E, USB-C | 2-pack | Real-time motor commands and encoder acquisition | [Search](https://www.amazon.com/s?k=ESP32-DevKitC-32E+USB-C) |
| Battery | Zeee 3S LiPo, 11.1 V, 2200 mAh, 50C, XT60 | 2-pack | Main robot battery | [Search](https://www.amazon.com/s?k=Zeee+3S+2200mAh+11.1V+50C+XT60) |
| LiPo charger | 2S/3S balance charger for 7.4/11.1 V LiPo | 1 | Balance-charges the 3S battery | [Search](https://www.amazon.com/s?k=2S+3S+LiPo+Balance+Charger+11.1V) |
| Chassis | uxcell PP project enclosure, 165 × 120 × 68 mm | 1 | Main structural enclosure | [Product](https://www.amazon.com/dp/B019I89TKG) |
| Caster | 1-inch swivel caster, ~35 mm overall height | 1 used / 4-pack | Third support point | [Product](https://www.amazon.com/dp/B0D5D7TYM2) |
| XT60 wiring | RioRand XT60 pigtails, 14 AWG, 100 mm | 1 pair used | Battery connection | [Search](https://www.amazon.com/s?k=RioRand+XT60+pigtail+14AWG) |
| Main fuse holder | Waterproof inline low-profile fuse holder, 12 AWG | 1 | Main battery protection | [Search](https://www.amazon.com/s?k=Waterproof+inline+Low+Profile+LED+Fuse+Holder+12+AWG) |
| Main switch | Gebildet SPST ON/OFF switch, 10 A | 1 | Master power switch | [Search](https://www.amazon.com/s?k=Gebildet+SPST+Water+Drop+Switch+10A) |
| Jetson DC lead | uxcell DC5525 male pigtail, 5.5 × 2.5 mm, 18 AWG, 30 cm, 10 A | 1 | Battery power branch to Jetson barrel input | [Product](https://www.amazon.com/dp/B08JKRT68C) |
| Jumper wires | HiLetgo 200-piece jumper-wire kit | 1 | Low-current signal wiring | [Product](https://www.amazon.com/dp/B077X99KX1) |
| Standoffs / screws | M2.5 nylon standoff, screw and nut kit | 1 | Electronics mounting | [Product](https://www.amazon.com/dp/B0FPMC9917) |
| Crimp/connectors | SOMELINE JST + Dupont crimping kit | 1 | Custom sensor and signal harnesses | [Product](https://www.amazon.com/dp/B0C8N77PFF) |

## Power

The proposed supply is one **3S LiPo battery** at a time:

| Parameter | Planned Value |
| --- | --- |
| Nominal voltage | 11.1 V |
| Fully charged voltage | 12.6 V |
| Capacity per pack | 2200 mAh |
| Connector | XT60 |

The diagram below shows the intended direct battery branches. Before using a
direct Jetson supply, verify the exact carrier board's documented input range,
connector dimensions, polarity, and power requirements against the battery's
operating range and motor-induced transients. The need for regulation or additional
protection is not established by this document.

```text
Zeee 3S LiPo
     │
    XT60
     │
 Main fuse
     │
 Main switch
     │
     ├──────────────> Jetson Orin Nano Super
     │                 5.5 × 2.5 mm barrel
     │
     └──────────────> Cytron MDD10A
                          │
                    ┌─────┴─────┐
                    │           │
                 Motor L     Motor R
```

### Power Checks Before Connection

- Verify **voltage and center-positive polarity with a multimeter** before
    connecting the custom Jetson lead.
- Select fuse ratings from the wiring limits and measured/expected loads;
    a fuse holder alone does not specify the protection rating.
- Verify motor stall current against the driver's per-channel capability and
    the switch, connectors, wiring, and battery ratings.
- Provide appropriate LiPo undervoltage protection and use a compatible balance
    charger. The final cutoff threshold and protection circuit remain to be defined.
- The ESP32 and sensor supply rails are not shown in the simplified power diagram;
    define their voltage requirements and a common signal reference before wiring.

## Drive System

The robot uses two independent 12 V geared DC motors with integrated
encoders.

| Parameter | Planned Physical Value |
| --- | --- |
| Drive type | Two-wheel differential drive |
| Motor voltage | 12 V |
| Listed gearmotor speed | 130 RPM; loaded output speed to be verified |
| Wheel diameter | 65 mm |
| Wheel radius | 32.5 mm |
| Motor driver | Cytron MDD10A |
| Feedback | Integrated wheel encoders |
| Motor/encoder MCU | ESP32-DevKitC-32E |
| ROS controller | `diff_drive_controller` |

The exact **encoder CPR/PPR** and **wheel separation** should be
measured/calibrated on the assembled robot before finalizing the
physical ROS 2 configuration.

## Sensors

### RPLIDAR C1

Mounted at the highest practical point with an unobstructed 360° field
of view.

ROS 2 output:

```text
/scan
```

Used by SLAM and Nav2.

### BNO055

The BNO055 provides inertial measurements for state estimation.

Expected ROS 2 output:

```text
/imu/data
```

Wheel odometry and IMU measurements are fused using
`robot_localization`.

### Arducam IMX219

The front-facing IMX219 camera connects directly to the Jetson through
MIPI CSI-2. It is reserved for later perception work such as OpenCV,
object detection, and Physical AI experiments.

## ROS 2 Data Flow

The command chain retains the simulation's stamped velocity pipeline. The
Jetson-to-ESP32 hardware interface below is planned, not implemented:

```text
Nav2
 │
 ▼
/cmd_vel_nav → velocity_smoother → /cmd_vel_smoothed
 │
 ▼
collision_monitor → /diff_drive_controller/cmd_vel (TwistStamped)
 │
 ▼
diff_drive_controller
 │
 ▼
ros2_control hardware plugin on Jetson
 │
 └───────── USB/Serial ───── ESP32
                              │
                              ▼
                           MDD10A
                          /      \
                         ▼        ▼
                     Motor L    Motor R
                        │          │
                     Encoder    Encoder
                        └────┬─────┘
                             ▼
                           ESP32
                             │
                             ▼
                        Wheel joint position/velocity
                             │
                             ▼
                        diff_drive_controller → /odom

RPLIDAR C1 ───────────────> /scan
BNO055 ───────────────────> /imu/data
IMX219 ───────────────────> image stream
```

The intended TF/state-estimation chain remains:

```text
map → odom → base_footprint → base_link → sensors / wheels
```

The hardware plugin must expose wheel velocity commands and wheel position/velocity
feedback. Encoder scaling, message format, MCU control rate, and command-loss
behavior still need to be defined. EKF owns `odom → base_footprint`; SLAM or AMCL
owns `map → odom`.

## Physical Layout

The enclosure is significantly smaller than the original simulation
chassis, so the URDF dimensions will be updated after physical assembly.

Approximate starting dimensions:

| Parameter | Approximate Planned Value |
| --- | --- |
| Chassis enclosure | 165 × 120 × 68 mm |
| Drive wheel diameter | 65 mm |
| Caster wheel diameter | ~25 mm |
| Caster overall height | ~35 mm |
| Battery dimensions | 75 × 34 × 26.5 mm |
| Battery mass | ~137 g |

Confirm usable internal enclosure space, mounting clearances, axle height, and
caster height on the actual parts. These dimensions do not establish that all
electronics fit or that the assembled robot is stable.

Planned layout:

-   **Two encoder motors** mounted on the left and right sides.
-   **65 mm wheels** directly outside the chassis.
-   **One swivel caster** underneath the opposite end of the axle
    support.
-   **Battery, ESP32, MDD10A, fuse and wiring** inside the enclosure
    where practical.
-   **Jetson Orin Nano** mounted on top with airflow kept unobstructed.
-   **RPLIDAR C1** mounted above the Jetson on standoffs for a clear
    360° scan.
-   **IMX219 camera** mounted at the front.
-   **BNO055** mounted rigidly near the robot center and away from
    strong magnetic/current sources where practical.

## Software Mapping

| Hardware / Software | Intended Responsibility |
| --- | --- |
| Jetson Orin Nano Super | ROS 2 compute, Nav2, SLAM, EKF, perception |
| ESP32 | Motor command execution and encoder acquisition |
| Cytron MDD10A | Electrical motor drive |
| Encoders | Wheel position/velocity feedback for odometry |
| BNO055 | IMU data |
| RPLIDAR C1 | Laser scans |
| IMX219 | Camera images |
| `ros2_control` | Hardware/controller abstraction |
| `diff_drive_controller` | Differential-drive kinematics, wheel commands, and wheel odometry |
| `robot_localization` | Wheel odometry + IMU fusion; `odom → base_footprint` |
| SLAM / AMCL localization | `map → odom` |
| Nav2 | Autonomous navigation |

## Physical Bring-Up Order

1.  Test the Jetson using its original AC power adapter.
2.  Charge and inspect the 3S LiPo with the balance charger.
3.  Verify supply compatibility and protection, then build the fused/switched battery harness.
4.  Verify **voltage and polarity with a multimeter before connecting
    the Jetson**.
5.  Bench-test ESP32 + MDD10A + one motor with the wheel raised and power readily disconnectable.
6.  Add the second motor and both encoders.
7.  Mount the motors, wheels and caster to the chassis.
8.  Measure wheel radius, wheel separation and chassis geometry.
9.  Update the URDF/Xacro to match the physical robot.
10. Integrate `ros2_control`.
11. Integrate BNO055 and EKF.
12. Integrate RPLIDAR C1.
13. Validate SLAM and Nav2 on the physical robot.
14. Add the IMX219 perception pipeline.

## Notes

-   The simulation currently uses larger dimensions than the physical
    chassis. **Do not copy the simulated dimensions into the hardware
    configuration without measuring the assembled robot.**
-   The final wheel separation must be measured center-to-center.
-   Encoder CPR/PPR must be verified experimentally.
-   Keep the LiDAR scan plane unobstructed.
-   Keep the Jetson cooling fan and heatsink unobstructed.
-   Secure the LiPo so it cannot move or be punctured.
-   Use the inline fuse close to the battery branch.
