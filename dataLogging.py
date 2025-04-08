from dronekit import connect
import time


drone = connect("127.0.0.1:14550", wait_ready= True) 

# print(f'Drone Arm Durumu: {drone.armed}')

# print(f'Konum: {drone.location.global_frame}') 


# print(f'Konum: {drone.location.global_relative_frame}')

# print(f'İrtifa: {drone.location.global_relative_frame.alt}')


while drone.location.global_relative_frame.alt is not 0:

    print(f'Altitude: {drone.location.global_relative_frame.alt}')
    time.sleep(1)
    if drone.location.global_relative_frame.alt < 0.2:
        break