# ESP32 + Cytron MDD10A Hardware Guide

## Table of Contents

- [Differential Drive Robot — Low-Level Control Architecture](#differential-drive-robot--low-level-control-architecture)
- [1. Architecture Overview](#1-architecture-overview)
  - [Responsibilities](#responsibilities)
- [2. ESP32](#2-esp32)
  - [2.1 Board used in this robot](#21-board-used-in-this-robot)
  - [2.2 Firmware development workflow](#22-firmware-development-workflow)
  - [2.3 Serial communication](#23-serial-communication)
- [3. ESP32 GPIO Fundamentals](#3-esp32-gpio-fundamentals)
  - [3.1 PWM](#31-pwm)
- [4. ESP32 Terminal Breakout Board](#4-esp32-terminal-breakout-board)
- [5. Cytron MDD10A Rev 2.0](#5-cytron-mdd10a-rev-20)
  - [5.1 Power and motor terminals](#51-power-and-motor-terminals)
  - [5.2 Control interface](#52-control-interface)
    - [PWM](#pwm)
    - [DIR](#dir)
    - [GND](#gnd)
- [6. GPIO Mapping — v1](#6-gpio-mapping--v1)
  - [6.1 ESP32 -> MDD10A](#61-esp32---mdd10a)
  - [6.2 Motor encoders -> ESP32](#62-motor-encoders---esp32)
    - [Proposed v1 mapping](#proposed-v1-mapping)
- [7. BNO055 IMU — Proposed Mapping](#7-bno055-imu--proposed-mapping)
- [8. GPIO Allocation Summary](#8-gpio-allocation-summary)
- [9. Complete Low-Level Data Flow](#9-complete-low-level-data-flow)
- [10. What Is Validated vs. Still To Verify](#10-what-is-validated-vs-still-to-verify)
  - [Validated](#validated)
  - [Must still be verified before electrical connection](#must-still-be-verified-before-electrical-connection)
- [11. Bring-Up Order](#11-bring-up-order)
  - [Key Principle](#key-principle)

## Differential Drive Robot — Low-Level Control Architecture

This document records the low-level electronics architecture learned and selected for the physical differential-drive robot.

> **Status:** ESP32 USB/serial bring-up is validated. The ESP32-to-MDD10A and sensor GPIO assignments below are the **v1 wiring plan** and should be verified during physical bring-up before being treated as final.

---

## 1. Architecture Overview

The physical robot separates high-level robotics software from low-level hardware control.

```text
PC during development / Jetson on the robot
              |
              | USB Serial
              v
           ESP32
              |
              | GPIO: PWM + DIR
              v
        Cytron MDD10A
           /      \
          v        v
     Left Motor  Right Motor
          ^        ^
          |        |
       Encoder   Encoder
          \        /
           \      /
             ESP32
```

### Responsibilities

| Component | Role |
|---|---|
| Jetson Orin Nano | ROS 2, `ros2_control`, Nav2, SLAM, EKF, perception and high-level decision making |
| ESP32 | Real-time/low-level I/O: motor command output, encoder input, serial communication |
| Cytron MDD10A | Motor power stage; converts low-power control signals into high-current motor drive |
| Motor encoders | Measure actual wheel rotation |
| BNO055 | IMU: acceleration, angular velocity and orientation/fusion data |

A useful mental model is:

```text
SBC -> MCU -> Motor Driver -> Motors
Jetson -> ESP32 -> MDD10A -> Motors
```

---

# 2. ESP32

## 2.1 Board used in this robot

The physical board is a 38-pin ESP32 development board built around an **ESP32-WROOM-32E** module.

Observed during bring-up:

- 19 pins on each side (38 total)
- USB-C connector
- CH341 USB-to-UART interface detected by Linux
- Linux serial device: `/dev/ttyUSB0`
- 3.3 V GPIO logic
- PlatformIO + Arduino framework used for firmware development

Linux detected the board as a CH341 UART converter and attached it to:

```text
/dev/ttyUSB0
```

The Linux user must have access to the `dialout` group to use this serial device without `sudo`.

---

## 2.2 Firmware development workflow

The ESP32 firmware lives separately from the ROS 2 workspace:

```text
robotics/
└── projects/
    ├── differential_drive_ws/       # ROS 2 / Jetson side
    └── differential_drive_esp32/    # ESP32 firmware
```

PlatformIO is used to:

1. Compile the C++ firmware.
2. Create the ESP32 binary image.
3. Upload it through `/dev/ttyUSB0`.
4. Monitor serial output.

The current PlatformIO environment uses the Arduino framework.

Example `platformio.ini` configuration:

```ini
[env:esp32dev]
platform = espressif32
board = esp32dev
framework = arduino
monitor_speed = 115200
```

The first validated firmware test used:

```cpp
#include <Arduino.h>

void setup()
{
    Serial.begin(115200);
    Serial.println("ESP32 started!");
}

void loop()
{
    Serial.println("ESP32 is running...");
    delay(1000);
}
```

The build, upload and serial-monitor path has been validated successfully.

---

## 2.3 Serial communication

The firmware currently uses:

```cpp
Serial.begin(115200);
```

`115200` is the selected serial baud rate. The sender and receiver must use the same baud rate.

Development:

```text
Linux PC <--- USB Serial @ 115200 ---> ESP32
```

Final robot:

```text
Jetson <--- USB Serial ---> ESP32
```

Later, this link will carry wheel commands toward the ESP32 and encoder/state information back toward the Jetson.

---

# 3. ESP32 GPIO Fundamentals

GPIO means **General Purpose Input/Output**.

A GPIO can be used to send or receive a digital electrical signal, depending on the pin and configuration.

For the ESP32 logic used here:

```text
LOW  ~= 0 V
HIGH ~= 3.3 V
```

Example output:

```cpp
pinMode(25, OUTPUT);
digitalWrite(25, HIGH);
```

A GPIO is a **control signal**, not a motor power source. A DC motor must never be powered directly from an ESP32 GPIO.

---

## 3.1 PWM

PWM means **Pulse Width Modulation**.

Instead of providing only ON/OFF control, the ESP32 switches a GPIO rapidly between HIGH and LOW. The percentage of time spent HIGH is the **duty cycle**.

```text
100%  HIGH almost all the time
 75%  HIGH 75% of the time
 50%  HIGH 50% of the time
 25%  HIGH 25% of the time
  0%  LOW
```

For this robot, PWM is used as the motor-speed command input to the MDD10A.

```text
ESP32 PWM signal -> MDD10A -> motor power modulation
```

---

# 4. ESP32 Terminal Breakout Board

The robot uses a **38-pin ESP32 terminal breakout board** compatible with the DevKitC form factor and 0.9-inch / 1.0-inch module spacing.

Its purpose is mechanical and electrical convenience:

```text
ESP32 GPIO pin
      |
      v
Breakout socket
      |
      v
Screw terminal
      |
      v
External wire
```

This avoids relying on loose Dupont jumpers in the final robot.

The terminal labels mirror the corresponding ESP32 pins, including GPIO 25, 26, 27, 14, 32, 33, etc.

> Do not assume every exposed pin is suitable for arbitrary GPIO use. Pins associated with flash/boot or input-only functions must be treated according to ESP32 restrictions. The v1 mapping below intentionally uses ordinary GPIOs for the robot interfaces.

---

# 5. Cytron MDD10A Rev 2.0

The physical motor driver has been visually identified as a **Cytron MDD10A Rev 2.0 dual-channel DC motor driver**.

Its job is to separate **control** from **power**:

```text
ESP32 ---- small logic signals ----> MDD10A
Battery -- motor power ------------> MDD10A ----> motors
```

The ESP32 cannot provide the current required by the motors. The MDD10A handles the high-current path.

---

## 5.1 Power and motor terminals

The photographed board exposes:

```text
M1B   M1A   B+   B-   M2A   M2B
```

Planned usage:

| MDD10A terminal | Purpose |
|---|---|
| `B+` | Battery positive |
| `B-` | Battery negative |
| `M1A`, `M1B` | Motor channel 1 |
| `M2A`, `M2B` | Motor channel 2 |

The final left/right convention can be adjusted after physical motor-direction testing.

The power path will eventually be:

```text
3S LiPo + -> fuse -> main switch -> MDD10A B+
3S LiPo - -----------------------> MDD10A B-
```

Do not connect the battery until the power wiring, polarity, fuse and switch have been verified.

---

## 5.2 Control interface

The MDD10A control header exposes the signals needed for both channels, including:

```text
PWM1
DIR1
PWM2
DIR2
GND
```

Conceptually:

```text
ESP32 PWM1 GPIO -> MDD10A PWM1
ESP32 DIR1 GPIO -> MDD10A DIR1
ESP32 PWM2 GPIO -> MDD10A PWM2
ESP32 DIR2 GPIO -> MDD10A DIR2
ESP32 GND       -> MDD10A GND
```

### PWM

Controls the commanded drive level/speed for the corresponding motor channel.

### DIR

Controls the commanded direction for the corresponding motor channel.

### GND

The ESP32 and MDD10A need a **common ground** so that both devices interpret the GPIO voltage levels relative to the same 0 V reference.

```text
ESP32 GND ---------------- MDD10A GND
```

---

# 6. GPIO Mapping — v1

This is the proposed wiring map for the first physical bring-up.

## 6.1 ESP32 -> MDD10A

| Function | ESP32 GPIO | Direction | MDD10A | Purpose |
|---|---:|---|---|---|
| Motor 1 PWM | GPIO 25 | Output | `PWM1` | Motor 1 speed command |
| Motor 1 direction | GPIO 26 | Output | `DIR1` | Motor 1 direction |
| Motor 2 PWM | GPIO 27 | Output | `PWM2` | Motor 2 speed command |
| Motor 2 direction | GPIO 14 | Output | `DIR2` | Motor 2 direction |
| Logic reference | GND | — | `GND` | Common electrical reference |

Diagram:

```text
ESP32                       MDD10A

GPIO 25 ------------------> PWM1
GPIO 26 ------------------> DIR1
GPIO 27 ------------------> PWM2
GPIO 14 ------------------> DIR2
GND     ------------------> GND
```

---

## 6.2 Motor encoders -> ESP32

Each quadrature encoder provides two channels, normally called **A** and **B**. Two motors therefore require four ESP32 inputs.

### Proposed v1 mapping

| Function | ESP32 GPIO | Direction | Notes |
|---|---:|---|---|
| Left encoder A | GPIO 34 | Input | Encoder pulse input |
| Left encoder B | GPIO 35 | Input | Encoder pulse input |
| Right encoder A | GPIO 36 / VP | Input | Encoder pulse input |
| Right encoder B | GPIO 39 / VN | Input | Encoder pulse input |

GPIO 34, 35, 36 and 39 are useful candidates because they are input-only pins, which matches encoder feedback use.

> **Important:** These ESP32 pins do not provide the same internal pull-up capabilities as ordinary bidirectional GPIOs. Before final wiring, verify the SatcOp encoder output type and voltage. External pull-ups or level adaptation may be required depending on the encoder electronics. Do not connect unknown encoder outputs to the ESP32 until this is verified.

Conceptually:

```text
Left encoder A  ----> GPIO 34
Left encoder B  ----> GPIO 35

Right encoder A ----> GPIO 36
Right encoder B ----> GPIO 39
```

The encoder signals allow the ESP32 to determine:

- wheel movement
- direction
- tick count
- wheel velocity

This information will later be sent back to the Jetson and exposed through the ROS 2 hardware interface.

---

# 7. BNO055 IMU — Proposed Mapping

The BNO055 can communicate over I2C.

For the v1 ESP32-centered architecture, reserve the common ESP32 I2C pins:

| Function | ESP32 GPIO | Direction | BNO055 |
|---|---:|---|---|
| I2C SDA | GPIO 21 | Bidirectional | SDA |
| I2C SCL | GPIO 22 | Output/clock | SCL |
| Ground | GND | — | GND |
| Power | TBD after breakout verification | — | VIN / 3V3 as appropriate |

Conceptually:

```text
ESP32 GPIO21 <------> BNO055 SDA
ESP32 GPIO22 -------> BNO055 SCL
ESP32 GND   -------- BNO055 GND
```

> **Not final yet:** We have not frozen whether the BNO055 will connect to the ESP32 or directly to the Jetson. GPIO 21/22 are reserved so the ESP32-I2C option remains available. Supply voltage and exact BNO055 breakout wiring must be verified before connection.

---

# 8. GPIO Allocation Summary

| ESP32 pin | Planned role | Type | Status |
|---:|---|---|---|
| GPIO 25 | MDD10A PWM1 | Output/PWM | Planned v1 |
| GPIO 26 | MDD10A DIR1 | Output | Planned v1 |
| GPIO 27 | MDD10A PWM2 | Output/PWM | Planned v1 |
| GPIO 14 | MDD10A DIR2 | Output | Planned v1 |
| GPIO 34 | Left encoder A | Input | Planned v1; encoder electrical interface TBD |
| GPIO 35 | Left encoder B | Input | Planned v1; encoder electrical interface TBD |
| GPIO 36 / VP | Right encoder A | Input | Planned v1; encoder electrical interface TBD |
| GPIO 39 / VN | Right encoder B | Input | Planned v1; encoder electrical interface TBD |
| GPIO 21 | BNO055 SDA | I2C | Reserved; architecture not frozen |
| GPIO 22 | BNO055 SCL | I2C | Reserved; architecture not frozen |
| GND | MDD10A / sensor common reference | Ground | Required |

This leaves additional GPIOs available for future functions.

---

# 9. Complete Low-Level Data Flow

When the robot is complete, the intended command path is:

```text
ROS 2 / Jetson
      |
      | wheel velocity commands
      v
ros2_control Hardware Interface
      |
      | USB Serial
      v
ESP32 firmware
      |
      | PWM + DIR
      v
Cytron MDD10A
      |
      v
DC motors
      |
      v
Wheels move
```

Feedback travels in the opposite direction:

```text
Wheel rotation
      |
      v
Encoders A/B
      |
      v
ESP32
      |
      | encoder counts / wheel state
      v
USB Serial
      |
      v
ROS 2 Hardware Interface
      |
      v
ros2_control / odometry / EKF
```

The IMU adds another feedback source:

```text
BNO055 -> ESP32 (proposed I2C) -> Jetson -> ROS 2 -> EKF
```

---

# 10. What Is Validated vs. Still To Verify

## Validated

- ESP32 is detected by Linux through CH341.
- Serial device `/dev/ttyUSB0` works.
- Linux `dialout` permissions work.
- PlatformIO builds ESP32 firmware successfully.
- PlatformIO uploads firmware successfully.
- Serial monitoring at 115200 works.
- ESP32 executes the uploaded firmware.
- Physical MDD10A is Cytron MDD10A Rev 2.0.
- MDD10A power/motor terminal labels were identified from the physical board.
- Physical ESP32 is a 38-pin ESP32-WROOM-32E development board.
- 38-pin terminal breakout is appropriate for this ESP32 form factor.

## Must still be verified before electrical connection

1. Exact MDD10A control-header pin order/orientation from the board/manual.
2. MDD10A logic-level compatibility and selected control mode.
3. SatcOp motor encoder wire colors and pinout.
4. Encoder supply voltage.
5. Encoder A/B output voltage and output type.
6. Whether external pull-ups or level shifting are needed for encoder signals.
7. Encoder CPR/PPR and resulting counts per wheel revolution.
8. Final left/right motor channel convention.
9. BNO055 connection choice: ESP32 I2C vs. Jetson I2C.
10. BNO055 exact supply wiring.
11. Main battery polarity, fuse sizing and power-distribution wiring.

---

# 11. Bring-Up Order

Do not connect everything at once.

```text
1. ESP32 USB/serial                         DONE
2. ESP32 GPIO/PWM concepts                 DONE
3. Identify MDD10A                         DONE
4. Freeze/verify GPIO map                  CURRENT
5. Verify MDD10A control header
6. Connect ESP32 -> MDD10A control only
7. Connect one motor
8. Test one motor at low command
9. Verify one encoder electrically
10. Read one encoder on ESP32
11. Add second motor + encoder
12. Implement Jetson <-> ESP32 protocol
13. Integrate real ros2_control hardware interface
14. Add IMU, LiDAR and camera
```

---

## Key Principle

The ESP32 provides **commands and measurements**. The MDD10A provides **motor power switching**.

```text
COMMAND != POWER

ESP32 GPIO -> control signal
Battery -> MDD10A -> motor power
```

That separation is the foundation of the robot's low-level electronics architecture.
