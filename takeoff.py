from dronekit import connect, VehicleMode, LocationGlobalRelative
import time

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


takeoff(20)
location = LocationGlobalRelative(-35.36261281, 149.16515128, 20)

drone.simple_goto(location)