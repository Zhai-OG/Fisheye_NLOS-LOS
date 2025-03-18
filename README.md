# GNSS PPS-Based Time Synchronization with Raspberry Pi

## Introduction
Accurate timekeeping is crucial for a variety of applications, including GNSS-based positioning, scientific experiments, and network synchronization. The combination of a **Raspberry Pi** and a **GPS module with a Pulse Per Second (PPS) signal** enables microsecond-level time accuracy. This article explores how to achieve precise synchronization using **GNSS PPS** with a Raspberry Pi, optimizing for **low latency and high stability**.

## Why Use GNSS PPS for Time Synchronization?
A **PPS signal** is emitted by GNSS receivers once per second, synchronized with atomic clocks in satellites. Standard system clocks on computers and Raspberry Pis are often limited by **network latency and drift**, making them unsuitable for high-precision tasks. GNSS PPS provides a way to **achieve microsecond-level accuracy**, significantly outperforming Network Time Protocol (NTP) alone.

## Required Hardware
To set up a GNSS-based time synchronization system, the following components are recommended:

### **1. Raspberry Pi**
- **Raspberry Pi 5** *(Recommended)* – Supports **Precision Time Protocol (PTP)**, allowing synchronization within **nanoseconds**.
- **Raspberry Pi 4** *(Acceptable Alternative)* – Decent performance, but lacks native PTP support.
- Avoid Raspberry Pi 3 or older models, as Ethernet is USB-connected, which increases jitter.

### **2. GNSS Receiver with PPS Support**
- **Timing-Specific GPS Modules** – Optimized for precise timing.
- **u-blox LEA-6T / LEA-M8T** – Affordable and widely available.
- **u-blox ZED-F9T** *(Overkill but highly precise, rated to 4 ns accuracy)*.
- Any **u-blox module ending in 'T' (Time)** is suitable for this purpose.

### **3. GNSS Antenna**
- A high-quality **active GNSS antenna** improves signal reception.
- Ideally, mount it in an open area with a clear sky view.

### **4. Required Accessories**
- **SMB to SMA connector** (for certain GNSS modules).
- **Jumper wires** *(2.00 mm to 2.54 mm)* to connect the module to the Pi.
- **Project box** – Helps maintain temperature stability, reducing oscillator drift.

## Step-by-Step Setup

### **1. Update Raspberry Pi and Install Required Packages**
Ensure your Raspberry Pi is up-to-date and install necessary software:
```bash
sudo apt update
sudo apt upgrade
sudo apt install pps-tools gpsd gpsd-clients chrony
```

### **2. Enable PPS and Serial Communication**
Modify the Raspberry Pi configuration to enable PPS and UART:
```bash
sudo bash -c "echo 'dtoverlay=pps-gpio,gpiopin=18' >> /boot/firmware/config.txt"
sudo bash -c "echo 'enable_uart=1' >> /boot/firmware/config.txt"
sudo bash -c "echo 'init_uart_baud=9600' >> /boot/firmware/config.txt"
```
Also, add PPS support in the kernel:
```bash
sudo bash -c "echo 'pps-gpio' >> /etc/modules"
sudo reboot
```

### **3. Connecting the GNSS Receiver to Raspberry Pi**
Connect the GNSS receiver to the Raspberry Pi using the following pins:
| GNSS Receiver | Raspberry Pi GPIO |
|--------------|-----------------|
| **5V**       | **Pin 2 (5V)**  |
| **GND**      | **Pin 6 (GND)** |
| **RX**       | **Pin 8 (TXD0)** |
| **TX**       | **Pin 10 (RXD0)** |
| **PPS**      | **Pin 12 (GPIO18)** |

### **4. Verify PPS Signal Reception**
Load the PPS kernel module and check for PPS signals:
```bash
sudo modprobe pps-gpio
dmesg | grep pps
```
Expected output:
```
pps pps0: registered IRQ 169 as PPS source
```
To test PPS signal:
```bash
sudo ppstest /dev/pps0
```

### **5. Configure GPSd for Time Synchronization**
Edit the GPSd configuration file:
```bash
sudo nano /etc/default/gpsd
```
Modify the following lines:
```
DEVICES="/dev/ttyAMA0 /dev/pps0"
GPSD_OPTIONS="-n"
START_DAEMON="true"
USBAUTO="true"
```
Restart the service:
```bash
sudo reboot
```

### **6. Configuring Chrony for Time Synchronization**
Edit Chrony’s configuration file:
```bash
sudo nano /etc/chrony/chrony.conf
```
Add the following lines:
```
refclock SHM 0 refid NMEA offset 0.268 precision 1e-3 poll 0 filter 3
refclock PPS /dev/pps0 refid PPS lock NMEA offset 0.0 poll 3 trust
log tracking measurements statistics
```
Restart Chrony:
```bash
sudo systemctl restart chrony
```
Verify synchronization:
```bash
chronyc tracking
chronyc sources
```

### **7. Achieving Microsecond Precision with PTP (Raspberry Pi 5 Only)**
For **nanosecond-level accuracy**, install and configure PTP:
```bash
sudo apt install linuxptp
sudo ptp4l -i eth0 -m
```

## Results and Accuracy
Once configured, your Raspberry Pi should achieve **sub-microsecond accuracy** using GNSS PPS. Using PTP on Raspberry Pi 5, synchronization can be improved further to the **double-digit nanosecond range**, making it suitable for scientific and industrial applications.

## Conclusion
Using **GNSS PPS-based time synchronization** with a Raspberry Pi provides a highly accurate and cost-effective solution for applications requiring precise timing. With **proper configuration**, it outperforms traditional NTP-based synchronization, achieving **microsecond-level accuracy**, and with PTP on Raspberry Pi 5, even **nanosecond precision**.

By following this guide, you can set up a reliable GNSS-based timekeeping system, ensuring robust and accurate time synchronization for your projects.
