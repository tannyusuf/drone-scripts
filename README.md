# 🚁 ArduPilot + Gazebo Automatic Installation Script

This project provides a `bash` script to easily set up the **ArduPilot** simulation environment and **Gazebo** integration on an Ubuntu system. It handles all required dependencies and configurations automatically.

---

## 📌 Overview

The script performs the following steps **sequentially**:

- Updates the system
- Installs Git and required Python packages
- Clones the ArduPilot repository and its submodules
- Sets up environment variables for ArduPilot tools
- Installs dependencies like MAVProxy, pymavlink, and empy
- Installs Gazebo and integrates the ArduPilot Gazebo plugin

---

## ⚙️ Installation Steps

### 1️⃣ Create the Script File

Create a file named `full_setup.sh` and copy the script in the full_setup.md and paste.

---

### 2️⃣ Make the Script Executable

````bash
chmod +x ardupilot_setup.sh

---

### 3️⃣ Run the Script

```bash
./ardupilot_setup.sh


---

### Notes

The script adds important environment variables to your ~/.bashrc file to ensure ArduPilot tools and Gazebo work properly.
After the installation is complete, run the following command to apply the changes:

```bash
source ~/.bashrc

````

```

```

```

```
