

# Using Fisheye Imaging to Classify NLOS and LOS Signals

In complex urban environments, GNSS signals are often affected by multipath interference, leading to significant positioning errors.  Classifying NLOS and LOS signals to mitigate multipath errors is crucial for improving positioning accuracy.  Utilizing a fisheye lens to assist in detecting NLOS/LOS signals has been demonstrated as an effective approach.  However, achieving precise synchronization between the timestamps of captured images and GNSS data is a key challenge.  The default timestamp resolution of the Raspberry Pi is insufficient for this task.  A promising solution is to use a GPS PPS (Pulse Per Second) signal to achieve microsecond-level timing accuracy on the Raspberry Pi.
This blog is structured as follows:
1) Required Hardware Setup – Introduction to the necessary hardware components.
2) GNSS PPS-Based Time Synchronization – Using GPS PPS to achieve high-precision timing on the Raspberry Pi.
3) Time synchronization - Synchronizing GNSS Timestamps with Fisheye Camera Image Timestamps
4) Sky-View Image Analysis – Determining the 180° field of view for sky visibility assessment.
5) GNSS-Based Orientation Estimation – Applying GNSS data for directional positioning.
6) Segmentation Algorithm – Implementing image segmentation techniques for NLOS/LOS classification.
   
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

### Results and Accuracy
Once configured, your Raspberry Pi should achieve **sub-microsecond accuracy** using GNSS PPS. Using PTP on Raspberry Pi 5, synchronization can be improved further to the **double-digit nanosecond range**, making it suitable for scientific and industrial applications.

### Conclusion
Using **GNSS PPS-based time synchronization** with a Raspberry Pi provides a highly accurate and cost-effective solution for applications requiring precise timing. With **proper configuration**, it outperforms traditional NTP-based synchronization, achieving **microsecond-level accuracy**, and with PTP on Raspberry Pi 5, even **nanosecond precision**.

By following this guide, you can set up a reliable GNSS-based timekeeping system, ensuring robust and accurate time synchronization for your projects.

### Citation

This guide is inspired by: [Revisiting Microsecond Accurate NTP for Raspberry Pi with GPS PPS in 2025](https://austinsnerdythings.com/2025/02/14/revisiting-microsecond-accurate-ntp-for-raspberry-pi-with-gps-pps-in-2025/).

Special thanks to [Austin](https://austinsnerdythings.com/author/austin/) for the insights.


# Synchronizing GNSS Timestamps with Fisheye Camera Image Timestamps

## **1.Setting Up the Raspberry Pi and HQ Camera**

To capture sky images with precise time alignment, we will use a **Raspberry Pi HQ Camera** with a **fisheye lens (FOV ≥ 180°)**. The camera is controlled by the Raspberry Pi, which will synchronize image capture with **GNSS PPS signals**.
![7de971af01d121f599acd5d224302e1](https://github.com/user-attachments/assets/86b48fae-6ded-4cc3-8db1-124f40c322a5)
<img src= "https://github.com/user-attachments/assets/dee9c658-4311-425d-b025-8e8b1f716b24" alt="Image description" width="500">

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

<img src= "https://github.com/user-attachments/assets/dee9c658-4311-425d-b025-8e8b1f716b24" alt="Image description" width="500">


## **2. Synchronizing Image Capture with GNSS PPS**

The PPS signal provides a **high-accuracy time reference**. Our goal is to capture **5 images per second**, ensuring that the camera starts capturing precisely **on each PPS pulse**.

Since **GNSS PPS-Based Time Synchronization with Raspberry Pi** has already been set up, the PPS signal is functioning correctly.

## **3. Capturing Images at PPS Timing**

We use a **Python script** to detect PPS pulses and trigger the camera:

```python
import time
import subprocess
import RPi.GPIO as GPIO

# GPIO pin for PPS signal
PPS_PIN = 18

# Configure GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(PPS_PIN, GPIO.IN)

def capture_images():
    """Captures 5 images per second triggered by PPS."""
    for i in range(5):
        timestamp = time.strftime("%Y%m%d_%H%M%S") + f"_{i}"
        subprocess.run(["libcamera-still", "-o", f"image_{timestamp}.jpg", "--immediate"])
        time.sleep(0.2)  # 5 FPS (1s / 5 = 0.2s per image)

def pps_callback(channel):
    """Triggered on each PPS pulse."""
    print("PPS pulse detected, capturing images...")
    capture_images()

# Attach interrupt to PPS pin
GPIO.add_event_detect(PPS_PIN, GPIO.RISING, callback=pps_callback)

print("Waiting for PPS signal...")
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    GPIO.cleanup()
```

## **4. Expected Output**
When a PPS pulse is received, the script will capture **5 images per second**, naming them with timestamps:

```
image_20250318_123456_0.jpg
image_20250318_123456_1.jpg
image_20250318_123456_2.jpg
image_20250318_123456_3.jpg
image_20250318_123456_4.jpg
```

## **Conclusion**

By leveraging **GNSS PPS signals**, the Raspberry Pi HQ Camera can achieve **precise image timestamping** for sky-view analysis. This method ensures **accurate synchronization** between GNSS data and image capture, making it useful for **atmospheric studies, satellite tracking, and environmental monitoring**.

# Sky-View Image Analysis and Satellite Projection in Camera Coordinate System

## Introduction

If you're lucky, you'll get an image with clear boundaries. Using Canny edge detection and Hough Circle Transform, you can accurately determine the image boundaries.

<img src= "https://github.com/user-attachments/assets/feba4297-b041-4854-8c49-5aafad01fabc" alt="Image description" width="500">

In most cases, due to lighting conditions, it is challenging to accurately determine the image boundaries, as shown：

<img src="https://github.com/user-attachments/assets/d51b3db4-47ad-4ee3-afe2-850c13bec36d" alt="Image description" width="500">

This means that it is not possible to precisely define the **horizontal 180° field of view (FOV)**. Generally, fisheye lenses use an **equidistant projection model**, but without clearly defined boundaries, mapping between camera coordinates and **ECEF coordinates** becomes difficult. Therefore, we need to address this issue.

## **Step 1: Creating a Reference Boundary**

To establish a clear boundary for the 180° field of view, we use a **cylindrical object** at the same height as the camera’s horizontal plane. A continuous **reference line** is drawn around the cylinder at this level, as illustrated:

<img src="https://github.com/user-attachments/assets/e120fbfa-1333-4a01-9dc8-4551d9628a47" alt="Image description" width="500">

- The camera captures an image of this setup, providing a controlled reference for further calculations.

## **Step 2: Detecting the Circle with find_circle.py**

To extract the camera's **pixel center** and the **effective pixel radius corresponding to 180°**, use `find_circle.py`.Then you can see

<img src="https://github.com/user-attachments/assets/e1bf98e2-47f2-4c5f-ad9d-551b0113d76e" alt="Image description" width="500">

Since a FOV of exactly 180° might make boundary detection difficult, it is recommended to use a FOV **greater than 180°** for better results.

### **Expected Output:**
- The **image center (pixel coordinates)**.
- The **radius (in pixels) corresponding to the 180° FOV**.

## **Step 3: Satellite Coordinate Projection**

Next, satellite positions are projected onto the camera image. The steps involved are:

1. **Compute Azimuth and Elevation Angles**:  
   - Use **RTKLIB’s `rtkplot` tool** to determine the satellite’s azimuth and elevation angles.

2. **Establish Projection Relationships**:  
   - Compute the transformation between the **satellite's angular position** and **image pixel coordinates**.

3. **Perform the Projection**:  
   - Use the script `ecef_to_camera.py` to map satellite coordinates onto the image.

### **Expected Result:**

After completing these steps, you should obtain an image where **satellite positions** are accurately overlaid, as shown below:

<img src="https://github.com/user-attachments/assets/a043852a-478f-43fe-a049-0b47383b4403" alt="Image description" width="500">

This method ensures precise alignment of GNSS satellite data with the camera's fisheye image, providing an effective solution for sky-view analysis.

# **GNSS-Based Orientation Estimation – Applying GNSS data for directional positioning**

To estimate orientation using GNSS, a dual-antenna setup is implemented. Two GNSS antennas are placed **8 meters apart** in a front-rear configuration to determine heading direction. By analyzing the differential position data from both antennas, the heading angle can be accurately calculated.

---

## **System Setup**
- **GNSS Receiver**: A multi-frequency GNSS receiver capable of processing dual-antenna inputs.
- **Antenna Configuration**:  
  - **Front antenna** (Primary)  
  - **Rear antenna** (Secondary, positioned 8m behind the primary)  

---

## **Calculation Method**  
The heading angle **θ** is derived from the position coordinates of the two GNSS antennas:

1. **Obtain ECEF coordinates** (X, Y, Z) for both antennas.
2. **Convert to local ENU coordinates** (East, North, Up).
3. **Compute the heading angle** using the formula:
$$
   \[
   \theta = \tan^{-1} \left( \frac{\Delta E}{\Delta N} \right)
   \]
$$
   where:
   - $$\( \Delta E \)$$ = Easting difference between the two antennas.
   - $$\( \Delta N \)$$ = Northing difference between the two antennas.

4. **Heading Correction**:  
   - If GNSS is in motion, corrections based on velocity vector may be applied.
   - When stationary, the computed heading remains accurate as long as both antennas maintain a stable position.

---

## **Advantages of This Approach**  
- **High Accuracy**: A longer baseline (8m) improves heading precision.
- **No External Sensors Needed**: Unlike IMU-based heading estimation, this method relies solely on GNSS data.
- **Reliable in Low-Dynamics Scenarios**: Effective even in stationary or slow-moving applications.

This method provides a **robust GNSS-based heading solution** suitable for **vehicle navigation, robotics, and geospatial applications**.

# **Segmentation Algorithm – Implementing image segmentation techniques for NLOS/LOS classification**

When trying to classify NLOS and LOS regions in fisheye images, the key challenge is getting reliable training data without manually labeling everything.  Instead of manually marking LOS and NLOS areas, I take a different approach—I use the differences in satellite observations between a choke ring antenna and a regular GNSS antenna, along with observation residuals, to automatically identify these points.

The idea is pretty straightforward: choke ring antennas are designed to suppress multipath signals, so they mostly receive direct LOS signals.  On the other hand, a standard GNSS antenna picks up both LOS and NLOS signals.  By comparing what each antenna detects, I can figure out which satellites are seen under LOS conditions and which ones are affected by multipath.  If a satellite shows up with low residuals on both antennas, it’s likely LOS.  But if it only appears on the regular antenna or has large observation residuals, it's likely NLOS.

Once I have this classification, I project the satellites' azimuth and elevation angles onto the fisheye image using the camera’s lens model.  This automatically marks certain parts of the image as LOS or NLOS, giving me a set of reference points for training a segmentation model.

From there, I train the model to recognize patterns in the image that correspond to LOS and NLOS regions.  Since fisheye cameras follow an equidistant projection model, I make sure to account for that in the mapping.  The result is a model that can take a fisheye image and accurately segment which areas are likely to be LOS or NLOS, without needing manual labeling.

This whole setup makes it much easier to filter out multipath-affected signals in GNSS positioning.  Instead of guessing or relying on hand-labeled data, I’m using real GNSS observations to drive the classification, making the whole process much more reliable and scalable.


