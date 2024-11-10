import torch
from torchvision import models, transforms
from PIL import Image
import os
import numpy as np
from collections import Counter
from datetime import datetime, timedelta
import cv2


# Load pre-trained ResNet model with weights argument (since 'pretrained' is deprecated)

from torchvision.models import ResNet50_Weights


# Load the pre-trained ResNet50 model with default ImageNet weights
model = models.resnet50(weights=ResNet50_Weights.DEFAULT)
model.eval()  # Set the model to evaluation mode


# Define ImageNet-specific transformations for input image preprocessing

transform = transforms.Compose([
   transforms.Resize(256),  # Resize image to 256x256
   transforms.CenterCrop(224),  # Crop the center 224x224 area
   transforms.ToTensor(),  # Convert image to tensor
   transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),  # Normalize with ImageNet stats

])


# Get the class labels from the ResNet50 model's weights
LABELS = ResNet50_Weights.DEFAULT.meta['categories']


# Function to process each image and make a prediction

def predict_image(cv2_frame):
    rgb_frame = cv2.cvtColor(cv2_frame, cv2.COLOR_BGR2RGB)
    # Convert the RGB frame (numpy array) to a PIL Image
    img = Image.fromarray(rgb_frame)

    if img.mode == 'RGBA':
        img = img.convert('RGB')


    img = transform(img)  # Apply necessary transformations

    # Add batch dimension (since the model expects a batch of images)
    img = img.unsqueeze(0)


    # Make prediction with the model
    with torch.no_grad():  # Disable gradients for inference
        outputs = model(img)
        probabilities = torch.nn.functional.softmax(outputs, dim=1)

        # Get the class with the highest probability and its confidence score
        confidence, predicted_class = torch.max(probabilities, 1)

    # Get the predicted object label and the confidence (as a percentage)
    object_type = LABELS[predicted_class.item()]
    confidence_score = confidence.item() * 100  # Convert to percentage

    object_count = 1

    return (object_type, object_count, confidence_score)
