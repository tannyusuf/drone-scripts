from dronekit import connect, VehicleMode, LocationGlobalRelative, Command
import time
from pymavlink import mavutil

drone = connect("127.0.0.1:14550",wait_ready=True)

def takeoff(altitude):

    while drone.is_armable is not True:
        print("Drone arm edilebilir durumda değil")

    print("Drone arm edilebilir.")

    drone.mode = VehicleMode("GUIDED")
      

    drone.armed = True

    while drone.armed is not True:
        print("Drone arm ediliyor.")
        time.sleep(0.5)

    print("Drone arm edildi.")

    drone.simple_takeoff(altitude)
        

    while drone.location.global_relative_frame.alt < altitude * 0.9:
        print("Drone hedefe yükseliyor")
        time.sleep(1)


def add_mission():
    global command
    command = drone.commands
    command.clear() #Önceden tanımlanmış komutları sil
    time.sleep(1)

    #TAKEOFF
    command.add(Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, 
                        mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0, 0, 0, 0, 0, 0, 0, 0, 10))
    
    # 1. oto değişir önemsiz bir parametre
    # 2. başka bir cihaza komut gönderme 0 ayarla
    # 3. komut sırası belirler, 0 verirsen oto sıralar
    # 4. kordinat referanslarını belirler, default global_relative_frame.alt kullanır
    # 5. komutu belirler: takeoff
    # 6. değişiklik gösterir. takeoff için 0
    # sonuncu altitude

    #WAYPOINT
    command.add(Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, 
                        mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, -35.36272742, 149.16515336, 20))
    
    command.add(Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, 
                        mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, -35.36292266, 149.16484387, 30))
    
    #RTL
    command.add(Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, 
                        mavutil.mavlink.MAV_CMD_NAV_RETURN_TO_LAUNCH, 0, 0, 0, 0, 0, 0, 0, 0, 0))

    #Doğrulama
    command.add(Command(0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, 
                        mavutil.mavlink.MAV_CMD_NAV_RETURN_TO_LAUNCH, 0, 0, 0, 0, 0, 0, 0, 0, 0))
    command.upload()

    print("Komutlar yükleniyor...")

takeoff(10)
add_mission()

command.next = 0

drone.mode = VehicleMode("AUTO")

while True:
    next_waypoint = command.next
    print(f'Sıradaki komut: {next_waypoint}' )
    time.sleep(1)

    if next_waypoint is 4:
        print("Görev Tamamlandı.")
        break

print("Döngüden çıkıldı")