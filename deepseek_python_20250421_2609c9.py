from dronekit import connect, VehicleMode, Command
import time
import threading
import logging
from pymavlink import mavutil

# ------------------ Ayarlar ------------------
#CONNECTION_STRING = "/dev/ttyUSB0"  # APM 2.8 bağlantı portu
#BAUD_RATE = 57600
TARGET_ALTITUDE = 10  # Metre cinsinden
LOGFILE_NAME = "drone_log.txt"

# ------------------ Global Değişkenler ------------------
takeoff_completed = threading.Event()
mission_completed = threading.Event()
logging_active = threading.Event()

# ------------------ Drone Bağlantısı ------------------
print("Drone'a bağlanılıyor...")
#vehicle = connect(CONNECTION_STRING, baud=BAUD_RATE, wait_ready=True)
vehicle = connect("127.0.0.1:14550",wait_ready=True)

# ------------------ Veri Loglama Thread'i ------------------
class DataLoggerThread(threading.Thread):
    def run(self):
        logging_active.set()
        with open(LOGFILE_NAME, "w") as log_file:
            log_file.write("timestamp,altitude(m),battery(%),lat,lon\n")
            while logging_active.is_set():
                data = vehicle.location.global_relative_frame
                log_line = f"{time.time()},{data.alt},{vehicle.battery.level},{data.lat},{data.lon}\n"
                log_file.write(log_line)
                log_file.flush()  # Veriyi anında diske yaz
                time.sleep(0.5)
        print("Loglama durduruldu.")

# ------------------ Takeoff Thread'i ------------------
class TakeoffThread(threading.Thread):
    def run(self):
        print("Takeoff başlatılıyor...")
        vehicle.mode = VehicleMode("GUIDED")
        vehicle.armed = True
        
        while not vehicle.armed:
            print("Arm bekleniyor...")
            time.sleep(1)
        
        vehicle.simple_takeoff(TARGET_ALTITUDE)
        
        while True:
            current_alt = vehicle.location.global_relative_frame.alt
            if current_alt >= TARGET_ALTITUDE * 0.95:
                print(f"Takeoff tamamlandı: {current_alt:.1f}m")
                takeoff_completed.set()
                break
            time.sleep(1)

# ------------------ Otonom Görev Thread'i ------------------
class AutonomousMissionThread(threading.Thread):
    def run(self):
        takeoff_completed.wait()  # Takeoff'ın bitmesini bekle
        
        print("Otonom görev başlıyor...")
        
        # Waypoint'leri tanımla (Örnek: Kare çiz)
        waypoints = [
            {"lat": -35.36282061, "lon": 149.16475283},
            {"lat": vehicle.location.global_relative_frame.lat + 0.0001, "lon": vehicle.location.global_relative_frame.lon + 0.0001},
            {"lat": vehicle.location.global_relative_frame.lat, "lon": vehicle.location.global_relative_frame.lon + 0.0001},
            {"lat": vehicle.location.global_relative_frame.lat, "lon": vehicle.location.global_relative_frame.lon}
        ]
        
        # Waypoint'lere git
        for wp in waypoints:
            cmd = Command(
                0, 0, 0,
                mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
                mavutil.mavlink.MAV_CMD_NAV_WAYPOINT,
                0, 0, 0, 0, 0, 0,
                wp["lat"], wp["lon"], TARGET_ALTITUDE
            )
            vehicle.commands.clear()
            vehicle.commands.add(cmd)
            vehicle.commands.upload()
            print(f"Waypoint'e gidiliyor: {wp}")
            time.sleep(10)  # Waypoint'e ulaşma süresi
        
        # RTL (Return to Launch) moduna geç
        print("Kalkış konumuna dönülüyor...")
        vehicle.mode = VehicleMode("RTL")
        
        # RTL'nin tamamlanmasını bekle
        while vehicle.armed:
            time.sleep(1)
        
        mission_completed.set()

# ------------------ Main Program ------------------
try:
    # Thread'leri başlat
    logger_thread = DataLoggerThread()
    takeoff_thread = TakeoffThread()
    mission_thread = AutonomousMissionThread()

    logger_thread.start()
    takeoff_thread.start()
    mission_thread.start()

    # Tüm thread'lerin bitmesini bekle
    mission_thread.join()
    takeoff_thread.join()
    
finally:
    # Temizlik
    logging_active.clear()
    logger_thread.join()
    vehicle.close()
    print("Program sonlandırıldı.")