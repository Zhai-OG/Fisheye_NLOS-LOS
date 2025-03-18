

# HOW TO USE Fisheye to classify the NLOS\LOS signal

In complex urban environments, GNSS signals are often affected by multipath interference, leading to significant positioning errors.  Classifying NLOS and LOS signals to mitigate multipath errors is crucial for improving positioning accuracy.  Utilizing a fisheye lens to assist in detecting NLOS/LOS signals has been demonstrated as an effective approach.  However, achieving precise synchronization between the timestamps of captured images and GNSS data is a key challenge.  The default timestamp resolution of the Raspberry Pi is insufficient for this task.  A promising solution is to use a GPS PPS (Pulse Per Second) signal to achieve microsecond-level timing accuracy on the Raspberry Pi.
This blog is structured as follows:
1) Required Hardware Setup – Introduction to the necessary hardware components.
2) GNSS PPS-Based Time Synchronization – Using GPS PPS to achieve high-precision timing on the Raspberry Pi.
3) Sky-View Image Analysis – Determining the 180° field of view for sky visibility assessment.
4) GNSS-Based Orientation Estimation – Applying GNSS data for directional positioning.
5) Segmentation Algorithm – Implementing image segmentation techniques for NLOS/LOS classification.
   
# Required Hardware Setup (main)

## 1. Fisheye Camera Equipment

•	Raspberry Pi 5 / 4 / 4B – Single-board computer for image processing and GNSS synchronization. (We use Raspberry Pi 5)

•	Raspberry Pi HQ Camera – High-quality camera module compatible with Raspberry Pi.

•	Fisheye Lens – A lens with a field of view (FOV) of H/D/V ≥ 180°, suitable for capturing wide-angle sky images. ( Isometric projection model)

## 2. GNSS Equipment

•	Two GNSS Antennas – Used for positioning and orientation estimation.

•	GNSS Receiver – Capable of processing multi-system GNSS signals for precise positioning and timing.(important: GNSS Receiver with PPS Support)



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

## Citation

This guide is inspired by: [Revisiting Microsecond Accurate NTP for Raspberry Pi with GPS PPS in 2025](https://austinsnerdythings.com/2025/02/14/revisiting-microsecond-accurate-ntp-for-raspberry-pi-with-gps-pps-in-2025/).

Special thanks to [Austin](https://austinsnerdythings.com/author/austin/) for the insights.


# Sky-View Image Analysis – Determining the 180° field of view for sky visibility assessment.

## 1.Setting Up the Raspberry Pi and HQ Camera

To capture sky images with precise time alignment, we will use a **Raspberry Pi HQ Camera** with a **fisheye lens (FOV ≥ 180°)**. The camera is controlled by the Raspberry Pi, which will synchronize image capture with **GNSS PPS signals**.

#### **Required Packages**
Ensure that the necessary camera and timing libraries are installed:
```bash
sudo apt update
sudo apt install libcamera-apps pps-tools python3-rpi.gpio
```

#### **Enable the Camera Interface**
```bash
sudo raspi-config
```
Navigate to:
- **Interface Options** → **Camera** → **Enable**
- **Reboot the Raspberry Pi** to apply changes:
```bash
sudo reboot
```
You can run 
```bash
libcamera-hello -t 0
```
Then, you maybe can see this picture 


