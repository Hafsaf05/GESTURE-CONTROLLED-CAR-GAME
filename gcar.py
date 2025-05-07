import cv2
import mediapipe as mp 
import pygame
import time
import sys


# pygame.mixer.init()

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode = False,
    max_num_hands = 2,
    min_detection_confidence = 0.7,
    min_tracking_confidence = 0.5
)

mp_drawing = mp.solutions.drawing_utils

pygame.init()
window_width, window_height = 800, 600
window = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption("Gesture-Controlled Car")
clock = pygame.time.Clock()


car_width, car_height = 120, 60
car_x = window_width // 2 - car_width // 2
car_y = window_height - car_height - 20
car_speed = 10

road_img = pygame.image.load(r"D:\HAFSA CODING STUFF\Self Projects\Real-time projects\road.jpeg")
road_img = pygame.transform.scale(road_img,(window_width, window_height))

car_reach_score = 0
last_point_time = 0

def get_gesture(hand_landmarks):
    thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
    thumb_ip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_IP]
    
    fingers_closed = True
    for finger in [mp_hands.HandLandmark.INDEX_FINGER_TIP, mp_hands.HandLandmark.MIDDLE_FINGER_TIP, mp_hands.HandLandmark.RING_FINGER_TIP, mp_hands.HandLandmark.PINKY_TIP]:
        tip = hand_landmarks.landmark[finger]
        pip = hand_landmarks.landmark[int(finger)-2]

        if tip.y < pip.y:
            fingers_closed = False

    return thumb_tip.y < thumb_ip.y and fingers_closed



def is_hand_open(hand_landmarks):
    open_fingers = 0

    for finger in [mp_hands.HandLandmark.INDEX_FINGER_TIP, mp_hands.HandLandmark.MIDDLE_FINGER_TIP, mp_hands.HandLandmark.RING_FINGER_TIP, mp_hands.HandLandmark.PINKY_TIP,]:

        tip = hand_landmarks.landmark[finger]
        pip = hand_landmarks.landmark[int(finger)-2]

        if tip.y < pip.y:
            open_fingers += 1
        
    return open_fingers >= 3
    
    print(f"Finger {finger}: TIP.y = {tip.y} PIP.y = {pip.y}")

def get_thumb_direction(hand_landmarks):
    thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]  
    thumb_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_MCP]
    wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]

    y_axis = (thumb_mcp.x - wrist.x, thumb_mcp.y - wrist.y)
    x_axis = (y_axis[1], -y_axis[0])

    thumb_x_projection = (thumb_tip.x - wrist.x) * x_axis[0] + (thumb_tip.y - wrist.y) * x_axis[1]

    threshold = 0.01

    if thumb_x_projection < -threshold:
        return "LEFT"
    elif thumb_x_projection > threshold:
        return "RIGHT"
    else:
        return "NEUTRAL"



def draw_cartoon_car(surface, x, y, w, h):
    body_points = [
        (x, y + h * 0.6),
        (x + w * 0.2, y),
        (x + w * 0.8, y),
        (x + w, y + h * 0.6),
        (x + w * 0.8, y + h),
        (x + w * 0.2, y + h)
    ]
    
    pygame.draw.polygon(surface, (200, 0, 0), body_points)

    window_points = [
        (x + w * 0.25, y + h * 0.2),
        (x + w * 0.75, y + h * 0.2),
        (x + w * 0.65, y + h * 0.5),
        (x + w * 0.35, y + h * 0.5)
    ]
    
    pygame.draw.polygon(surface, (135, 206, 250), window_points)


    wheel_radius = int(h * 0.2)

    rear_wheel_center = (int(x + w * 0.3), int(y + h))

    front_wheel_center = (int(x + w * 0.7), int(y + h))
    pygame.draw.circle(surface, (0, 0, 0), rear_wheel_center, wheel_radius)
    pygame.draw.circle(surface, (0, 0, 0), front_wheel_center, wheel_radius)


    hub_radius = wheel_radius // 2
    pygame.draw.circle(surface, (128, 128, 128), rear_wheel_center, hub_radius)
    pygame.draw.circle(surface, (128, 128, 128), front_wheel_center, hub_radius)

cap = cv2.VideoCapture(0)



running = True



while running:

    ret, frame = cap.read()
    if not ret:
        break

    # converting to rgb from bgr
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # detect hands
    # stores detected hand resukts in results
    results = hands.process(rgb_frame)

    direction = "NEUTRAL"
    hand_state = "CLOSED"

    # now if the hands are detected go thru each hand
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
        thumb_ip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_IP]

        if thumb_tip.y < thumb_ip.y:
            car_y -= max(0, car_y - car_speed)
            # drawing landmarks on the hands
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            # Checking for gestures
            # if get_gesture(hand_landmarks):
                # pygame.mixer.music.play()
            hand_state = "Open" if is_hand_open(hand_landmarks) else "Closed"


            # get thumb movement direction here

            direction = get_thumb_direction(hand_landmarks)
            cv2.putText(frame, f"Thumb: {direction}", (10,30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame, f"Hand: {hand_state}", (10, 70),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)


    # # to increase score haha
    # if direction in ["LEFT", "RIGHT"]:
    #     if time.time() - last_point_time > 1:
    #         car_reach_score += 1
    #         last_point_time = time.time()
    if direction == "LEFT":
        car_x -= car_speed
    elif direction == "RIGHT":
        car_x += car_speed
    else:
        pass
    
    

    car_x = max(0, min(window_width - car_width, car_x))  


    window.fill((0, 0, 0))
    window.blit(road_img, (0, 0))
    draw_cartoon_car(window, car_x, car_y, car_width, car_height)
    pygame.display.flip()

    cv2.imshow('Hand Tracking', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
pygame.quit()


