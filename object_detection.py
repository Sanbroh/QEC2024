import cv2
import os
import numpy as np
import model

class VideoAnalysis:
    def __init__(self):
        self.detected_objects = []
        self.fgbg = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=100, detectShadows=True)

    def processFrame(self, frame: np.ndarray):
        # Apply background subtraction to detect moving objects
        fgmask = self.fgbg.apply(frame)

        # Apply some morphological operations to clean up the mask (remove noise)
        fgmask = cv2.morphologyEx(fgmask, cv2.MORPH_CLOSE, None)
        fgmask = cv2.morphologyEx(fgmask, cv2.MORPH_OPEN, None)

        # Find contours of the detected objects in the foreground mask
        contours, _ = cv2.findContours(fgmask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
        object = []

        for contour in contours:
            if cv2.contourArea(contour) > 1000:  # Ignore small contours (you can adjust the area threshold)
                # Get the bounding box of the detected contour
                x, y, w, h = cv2.boundingRect(contour)

                # Check if the object has already been detected
                object_exists = False
                for existing_box in self.detected_objects:
                    # Compare the new bounding box with existing ones using IoU
                    if self.iou((x, y, w, h), existing_box) > 0.5:  # 50% IoU threshold
                        object_exists = True
                        break

                if not object_exists:
                    self.detected_objects.append((x, y, w, h))  # Store the bounding box of the detected object
                    object = model.predict_image(frame)

        return object

        
    def iou(self, box1, box2):
       # Box format: (x, y, w, h)
       x1, y1, w1, h1 = box1
       x2, y2, w2, h2 = box2

       # Coordinates of the intersection rectangle
       xi1 = max(x1, x2)
       yi1 = max(y1, y2)
       xi2 = min(x1 + w1, x2 + w2)
       yi2 = min(y1 + h1, y2 + h2)

       # Compute the area of intersection
       inter_area = max(0, xi2 - xi1) * max(0, yi2 - yi1)

       # Compute the area of both bounding boxes
       box1_area = w1 * h1
       box2_area = w2 * h2

       # Compute the Intersection over Union (IoU)
       union_area = box1_area + box2_area - inter_area
       return inter_area / union_area if union_area != 0 else 0



'''
def capture_live_frames():
   cap = cv2.VideoCapture(0) 

   if not cap.isOpened():

       print("Error: Could not open video stream.")
       exit()


   fgbg = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=100, detectShadows=True)


   output_folder = 'outputFrames'

   if not os.path.exists(output_folder):
       os.makedirs(output_folder)


   frame_counter = 0

   detected_objects = []

   # IoU function to check if the current object overlaps with a previously detected object

   def iou(box1, box2):

       # Box format: (x, y, w, h)

       x1, y1, w1, h1 = box1

       x2, y2, w2, h2 = box2

       

       # Coordinates of the intersection rectangle

       xi1 = max(x1, x2)

       yi1 = max(y1, y2)

       xi2 = min(x1 + w1, x2 + w2)

       yi2 = min(y1 + h1, y2 + h2)

       

       # Compute the area of intersection

       inter_area = max(0, xi2 - xi1) * max(0, yi2 - yi1)

       

       # Compute the area of both bounding boxes

       box1_area = w1 * h1

       box2_area = w2 * h2

       

       # Compute the Intersection over Union (IoU)

       union_area = box1_area + box2_area - inter_area

       return inter_area / union_area if union_area != 0 else 0


   while True:

       # Capture the frame from the video feed
       ret, frame = cap.read()

       # Apply background subtraction to detect moving objects
       fgmask = fgbg.apply(frame)


       # Apply some morphological operations to clean up the mask (remove noise)
       fgmask = cv2.morphologyEx(fgmask, cv2.MORPH_CLOSE, None)

       fgmask = cv2.morphologyEx(fgmask, cv2.MORPH_OPEN, None)


       # Find contours of the detected objects in the foreground mask

       contours, _ = cv2.findContours(fgmask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)


       # If there are any contours, it means new objects or movement was detected

       new_objects_detected = False

       for contour in contours:

           if cv2.contourArea(contour) > 1000:  # Ignore small contours (you can adjust the area threshold)

               # Get the bounding box of the detected contour

               x, y, w, h = cv2.boundingRect(contour)


               # Check if the object has already been detected

               object_exists = False

               for existing_box in detected_objects:

                   # Compare the new bounding box with existing ones using IoU

                   if iou((x, y, w, h), existing_box) > 0.5:  # 50% IoU threshold

                       object_exists = True

                       break


               if not object_exists:

                   # If the object hasn't been detected before, save the frame

                   frame_filename = os.path.join(output_folder, f"frame_{frame_counter:04d}.jpg")

                   cv2.imwrite(frame_filename, frame)

                   frame_counter += 1

                   detected_objects.append((x, y, w, h))  # Store the bounding box of the detected object

                   new_objects_detected = True

                   print(f"Saved frame: {frame_filename}")


               # Draw the bounding box around the detected object

               cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)


       # If new objects were detected, display the frame

       if new_objects_detected:

           cv2.imshow('Detected New Object', frame)


       # Display the frame with detected objects and movement

       cv2.imshow('Live Video Feed', frame)


       # Check for the 'q' key to exit the loop

       if cv2.waitKey(1) & 0xFF == ord('q'):

           break


   # Release the video capture and close all OpenCV windows



   cap.release()

   cv2.destroyAllWindows()



capture_live_frames()
'''