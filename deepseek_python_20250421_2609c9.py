def get_flight_data_summary():
    """Uçuş verileri özet raporu oluşturur"""
    try:
        summary = {
            "konum": {
                "enlem": vehicle.location.global_relative_frame.lat,
                "boylam": vehicle.location.global_relative_frame.lon,
                "yükseklik": vehicle.location.global_relative_frame.alt
            },
            "yönelim": {
                "yaw": round(vehicle.attitude.yaw * 180/3.14159, 2),  # Derece cinsinden
                "pitch": round(vehicle.attitude.pitch * 180/3.14159, 2),  # Derece cinsinden
                "roll": round(vehicle.attitude.roll * 180/3.14159, 2)  # Derece cinsinden
            },
            "hız": {
                "yer_hızı": round(vehicle.groundspeed, 2),
                "hava_hızı": round(vehicle.airspeed, 2)
            },
            "batarya": {
                "seviye": vehicle.battery.level,
                "voltaj": vehicle.battery.voltage 
            },
            "sistem": {
                "mod": vehicle.mode.name,
                "silahlı": vehicle.armed
            }
        }
        return summary
    except Exception as e:
        return {"hata": str(e)} from dronekit import connect, VehicleMode, Command
import time
import threading
import logging
import json
import os
from pymavlink import mavutil
from datetime import datetime

# ------------------ Ayarlar ------------------
#CONNECTION_STRING = "/dev/ttyUSB0"  # APM 2.8 bağlantı portu
#BAUD_RATE = 57600
TARGET_ALTITUDE = 10  # Metre cinsinden
LOGFILE_NAME = "drone_log.txt"
JSON_LOGFILE_NAME = "drone_data.json"
JSON_UPDATE_RATE = 1  # Saniye cinsinden JSON kayıt sıklığı

# ------------------ Global Değişkenler ------------------
takeoff_completed = threading.Event()
mission_completed = threading.Event()
logging_active = threading.Event()

# ------------------ Drone Bağlantısı ------------------
print("Drone'a bağlanılıyor...")
vehicle = connect("127.0.0.1:14550", wait_ready=True)
command = vehicle.commands  # Global komut nesnesi

# ------------------ Takeoff Fonksiyonu ------------------
def takeoff(target_altitude):
    print(f"{target_altitude}m yüksekliğe kalkış başlatılıyor...")
    vehicle.mode = VehicleMode("GUIDED")
    vehicle.armed = True
    
    while not vehicle.armed:
        print("Arm bekleniyor...")
        time.sleep(1)
    
    vehicle.simple_takeoff(target_altitude)
    
    while True:
        current_alt = vehicle.location.global_relative_frame.alt
        print(f"Yükseklik: {current_alt:.1f}m")
        if current_alt >= target_altitude * 0.95:
            print(f"Takeoff tamamlandı: {current_alt:.1f}m")
            takeoff_completed.set()
            break
        time.sleep(1)

# ------------------ Görev Ekleme Fonksiyonu ------------------
def add_mission():
    print("Görev komutları hazırlanıyor...")
    
    command.clear()  # Önceden tanımlanmış komutları sil
    time.sleep(1)
    
    # TAKEOFF
    command.add(Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
                         mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0, 0, 0, 0, 0, 0, 0, 0, 10))
    
    # WAYPOINT'ler
    command.add(Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
                         mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, -35.36272742, 149.16515336, 20))
    command.add(Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
                         mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, -35.36292266, 149.16484387, 30))
    
    # RTL - Kalkış noktasına dönüş
    command.add(Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
                         mavutil.mavlink.MAV_CMD_NAV_RETURN_TO_LAUNCH, 0, 0, 0, 0, 0, 0, 0, 0, 0))
    
    # Doğrulama komutu
    command.add(Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
                         mavutil.mavlink.MAV_CMD_NAV_RETURN_TO_LAUNCH, 0, 0, 0, 0, 0, 0, 0, 0, 0))
    
    # Komutları drone'a yükle
    command.upload()
    print("Komutlar yüklendi!")

# ------------------ Veri Loglama Thread'i ------------------
class DataLoggerThread(threading.Thread):
    def run(self):
        logging_active.set()
        with open(LOGFILE_NAME, "w") as log_file:
            log_file.write("timestamp,altitude(m),battery(%),lat,lon,mode\n")
            while logging_active.is_set():
                data = vehicle.location.global_relative_frame
                log_line = f"{time.time()},{data.alt},{vehicle.battery.level},{data.lat},{data.lon},{vehicle.mode.name}\n"
                log_file.write(log_line)
                log_file.flush()  # Veriyi anında diske yaz
                time.sleep(0.5)
        print("Loglama durduruldu.")

# ------------------ JSON Veri Loglama Thread'i ------------------
class JsonDataLoggerThread(threading.Thread):
    def run(self):
        logging_active.set()
        
        # JSON dosyası yoksa oluştur, varsa başlangıç yapısını hazırla
        if not os.path.exists(JSON_LOGFILE_NAME):
            with open(JSON_LOGFILE_NAME, "w") as json_file:
                json.dump({"flight_data": []}, json_file)
        
        while logging_active.is_set():
            try:
                # Mevcut dosyayı oku
                with open(JSON_LOGFILE_NAME, "r") as json_file:
                    data_dict = json.load(json_file)
                
                # Yeni veri noktası oluştur
                current_data = {
                    "timestamp": time.time(),
                    "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
                    "gps": {
                        "lat": vehicle.location.global_relative_frame.lat,
                        "lon": vehicle.location.global_relative_frame.lon,
                        "alt": vehicle.location.global_relative_frame.alt,
                    },
                    "attitude": {
                        "pitch": vehicle.attitude.pitch,
                        "roll": vehicle.attitude.roll,
                        "yaw": vehicle.attitude.yaw
                    },
                    "velocity": {
                        "vx": vehicle.velocity[0],  # x ekseni hızı (m/s)
                        "vy": vehicle.velocity[1],  # y ekseni hızı (m/s)
                        "vz": vehicle.velocity[2],  # z ekseni hızı (m/s)
                        "groundspeed": vehicle.groundspeed,  # yer hızı (m/s)
                        "airspeed": vehicle.airspeed      # hava hızı (m/s)
                    },
                    "battery": {
                        "voltage": vehicle.battery.voltage,
                        "current": vehicle.battery.current,
                        "level": vehicle.battery.level
                    },
                    "system": {
                        "mode": vehicle.mode.name,
                        "armed": vehicle.armed,
                        "is_armable": vehicle.is_armable,
                        "ekf_ok": vehicle.ekf_ok,
                        "heading": vehicle.heading
                    },
                    "waypoint": {
                        "current": vehicle.commands.next,
                        "total": vehicle.commands.count
                    }
                }
                
                # Veriyi listeye ekle
                data_dict["flight_data"].append(current_data)
                
                # Dosyaya yaz
                with open(JSON_LOGFILE_NAME, "w") as json_file:
                    json.dump(data_dict, json_file, indent=2)
                
            except Exception as e:
                print(f"JSON veri kaydetme hatası: {e}")
                
            time.sleep(JSON_UPDATE_RATE)

# ------------------ Görev İzleme Thread'i ------------------
class MissionMonitorThread(threading.Thread):
    def run(self):
        print("Görev izleme başlatıldı...")
        
        prev_waypoint = 0
        
        while not mission_completed.is_set():
            # Mevcut waypoint'i kontrol et
            current_waypoint = vehicle.commands.next
            
            if current_waypoint != prev_waypoint:
                if current_waypoint < vehicle.commands.count:
                    print(f"Waypoint {current_waypoint} gerçekleştiriliyor...")
                else:
                    print("Son waypoint'e ulaşıldı.")
                    mission_completed.set()
                
                prev_waypoint = current_waypoint
            
            # Eğer RTL veya LAND moduna geçildiyse
            if vehicle.mode.name in ['RTL', 'LAND'] and prev_waypoint >= vehicle.commands.count-1:
                print(f"{vehicle.mode.name} modunda, görev tamamlanıyor...")
                
                # Drone yere indiğinde
                if not vehicle.armed and vehicle.location.global_relative_frame.alt < 1:
                    print("Görev başarıyla tamamlandı!")
                    mission_completed.set()
            
            time.sleep(1)

# ------------------ Main Program ------------------
# ------------------ Main Program ------------------
if __name__ == "__main__":
    try:
        # Log thread'lerini başlat
        logger_thread = DataLoggerThread()
        logger_thread.daemon = True  # Ana program bitince thread de bitsin
        logger_thread.start()
        
        json_logger_thread = JsonDataLoggerThread()
        json_logger_thread.daemon = True
        json_logger_thread.start()
        
        # Görev hazırlığı
        add_mission()  # Görev komutlarını hazırla
        
        # Takeoff gerçekleştirme
        takeoff(TARGET_ALTITUDE)
        
        # Otomatik moda geç ve görevi başlat
        print("AUTO moda geçiliyor...")
        command.next = 0  # İlk komuttan başla
        vehicle.mode = VehicleMode("AUTO")
        
        # Görev izleme thread'ini başlat
        monitor_thread = MissionMonitorThread()
        monitor_thread.daemon = True
        monitor_thread.start()
        
        # Görevin tamamlanmasını bekle
        while not mission_completed.is_set():
            # Her 10 saniyede bir uçuş durumunu göster
            if int(time.time()) % 10 == 0:
                summary = get_flight_data_summary()
                print(f"Anlık durum: Mod={summary['sistem']['mod']}, "
                      f"Yükseklik={summary['konum']['yükseklik']:.1f}m, "
                      f"Hız={summary['hız']['yer_hızı']:.1f}m/s, "
                      f"Yaw={summary['yönelim']['yaw']}°")
            time.sleep(1)
            
        print("Görev tamamlandı!")
        
    except KeyboardInterrupt:
        print("Program kullanıcı tarafından durduruldu!")
    
finally:
    # Temizlik
    logging_active.clear()
    if vehicle.armed:
        print("Acil durum: RTL moduna geçiliyor...")
        vehicle.mode = VehicleMode("RTL")
    
    # Son veri kaydını yapma
    try:
        final_data = get_flight_data_summary()
        print("Son uçuş verisi:")
        print(json.dumps(final_data, indent=2, ensure_ascii=False))
        
        # Son konum ve yönelim bilgisi
        print(f"Son konum: {final_data['konum']['enlem']}, {final_data['konum']['boylam']}, {final_data['konum']['yükseklik']}m")
        print(f"Son yönelim: Yaw={final_data['yönelim']['yaw']}°, Pitch={final_data['yönelim']['pitch']}°, Roll={final_data['yönelim']['roll']}°")
    except:
        pass
    
    # Bağlantıyı kapat
    vehicle.close()
    print("Program sonlandırıldı.")