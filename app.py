from flask import Flask, session, render_template, Response, request, request, url_for, flash, redirect, jsonify
import random
import os
import openai
import ast
import urllib
from PIL import Image
import io
import rembg
import traceback
import numpy as np
import cv2

from recipe import *  # Custom module for recipe-related functionality
from object_detection import *  # Custom module for object detection functionality

app = Flask(__name__)  # Initialize Flask application
app.config['TEMPLATES_AUTO_RELOAD'] = True  # Enable auto-reloading of templates

os.environ["OPENAI_API_KEY"] = 'OPEN_AI_KEY_HERE' # INSERT OPEN AI SECRET KEY HERE
openai.api_key = os.getenv("OPENAI_API_KEY")  # Set OpenAI API key from environment variable

VA = VideoAnalysis()  # Initialize video analysis instance
R = None # Create a global variable for the recipe itself

i_feedback_global = ""
r_feedback_global = ""
s_feedback_global = ""
scores_global = ""

#inputString = "[(eggnog,1,30),(Granny Smith,1,40),(French loaf,1,80),(orange,1,100),(head cabbage,1,200),(banana,1,300),(cucumber,1,500)]"

def GPTCall(inputString):
    i_feedback = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "I want you to give me feedback based on data gathered from a cooking video. The feedback is short, 6 sentences max, and comments on the healthiness of the ingredients, as well as their nutrition value."},
            {"role": "assistant", "content": "The format of the input data is an array in the format of [(ingredient, amount of ingredient, timestamp), (...), ..., (...)] where (ingredient, amount of ingredient, timestamp) is an array inside the main array that stores data on a particular ingredient"},
            {"role": "user", "content": "Given the input array = " + inputString + ", give me feedback on: 1) The general thoughts on ingredient chosen and if they are a good healthy combination, 2) what is the estimated total calories of the dish using these ingredients, 3) if the ingredient list can be improved, what the improvements are and why"}
        ]
    ).choices[0].message.content

    r_feedback = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "I want you to give me feedback based on data gathered from a cooking video. The feedback is short, 6 sentences max, and comment on the recipe and what dish you think it is/closest too."},
            {"role": "assistant", "content": "The format of the input data is an array in the format of [(ingredient, amount of ingredient, timestamp), (...), ..., (...)] where (ingredient, amount of ingredient, timestamp) is an array inside the main array that stores data on a particular ingredient"},
            {"role": "user", "content": "Given the input array = " + inputString + ", give me feedback on: 1) What this dish is from the ingredients or what it is closest to, 2) based on the timestamps, if the ingredients were put in at the right times, assume timestamp is by seconds away from start, 3) recommendations and feedback on the recipe, e.g. how it should be improved and what was done well"}
        ]
    ).choices[0].message.content

    s_feedback = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "I want you to give me feedback based on data gathered from a cooking video. The feedback is long, and detailed. Give general feedback based on the other feedbacks given, and the input string"},
            {"role": "assistant", "content": "The format of the input data is an array in the format of [(ingredient, amount of ingredient, timestamp), (...), ..., (...)] where (ingredient, amount of ingredient, timestamp) is an array inside the main array that stores data on a particular ingredient"},
            {"role": "user", "content": "Given the input array = " + inputString + ", ingredient feedback = " + i_feedback + ", recipe feedback = " + r_feedback + ". Give feedback across the board, on healthiness, how it contributes to weight loss, what needs to be done better or avoided next time, what the actual dish may be like and how this current recipe compares to the actual dish recipe. Be as detailed as possible, and make it helpful. DO NOT BOLD ANYTHING, RETURN LIKE IT'S AN ESSAY."}
        ]
    ).choices[0].message.content

    print(s_feedback)

    scores = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "I want you to give me scores based on data and feedback gathered from a cooking video. There are four scores, give the output as a python array of integers in the format [overall score, ingredient score, recipe score, goal score]. SCORES ARE OUT OF 100, WHERE 0 IS LOWEST AND 100 IS HIGHEST. JUST GIVE THE PYTHON LIST, DO NOT ADD ANY TEXT OR STRING. NEED THE SQUARE BRACKETS TOO FOR THE LIST, AS IT WILL BE CONVERTED BY LITERAL TO A PYTHON ARRAY. JUST GIVE THE LIST"},
            {"role": "assistant", "content": "The format of the input data is an array in the format of [(ingredient, amount of ingredient, timestamp), (...), ..., (...)] where (ingredient, amount of ingredient, timestamp) is an array inside the main array that stores data on a particular ingredient"},
            {"role": "user", "content": "Given the input array = " + inputString + ", and overall feedback = " + s_feedback + ", now give me four scores and save them into the array format listed. The scores: 1) overall score = score is a weighted average of the other three scores, with more weight on the ingredient and goal, less on recipe (execution), ingredient score = score given to healthiness and combination of ingredients, high scores given to great combination and choice of healthy ingredients, as well as calories (should be reasonabily low). recipe score = score on the execution of the recipe, e.g. how well the cooking process was executed if it was a real recipe, relatively to an actual recipe, goal score = how good is the ingredients, dish, execution, and everything in terms of how it contributes to weightloss and healthy eating habits"}
        ]
    ).choices[0].message.content

    return [i_feedback, r_feedback, s_feedback, scores]

    #scores = ast.literal_eval(scores)

@app.route('/')
def index():
    return render_template('index.html')  # Render homepage template

@app.route('/application')
def application():
    global R
    R = Recipe() #Starts a new recipe
    return render_template('app.html')  # Render application page template

@app.route('/score')
def score():
    return render_template('score.html', i_f = i_feedback_global, r_f = r_feedback_global, s_f = s_feedback_global, scores=scores_global)  # Render application page template

def capture_live_frames():
    global R
    # Initialize webcam video capture and stream live frames
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open video stream.")
        exit()

    while True:
        ret, frame = cap.read()
        frame = cv2.flip(frame, 0)  # Flip frame vertically

        object = VA.processFrame(frame)  # Process frame with object detection

        if object:
            RecipeObject : RecipeObjectDict = { #Creates the RecipeObject DataType from the returned data
                "name" : object[0],
                "amount" : object[1],
                "timestamp" : datetime.datetime.now()
            }

            R.add_object(RecipeObject) #Adds the object to the recipe

        ret, buffer = cv2.imencode('.jpg', frame)  # Encode frame as JPEG
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # Yield frame for streaming

@app.route('/end_session')
def end_session():
    global R
    R.end_recipe()
    GPTString = R.ObjectsToGPTStringPrompt()
    ResponseArray = GPTCall(GPTString)
    print("#################")
    print(ResponseArray)
    i_feedback_global = ResponseArray[0]
    r_feedback_global = ResponseArray[1]
    s_feedback_global = ResponseArray[2]
    scores_global = R.GPTresponseHandler(ResponseArray[3])
    
    return render_template('score.html', i_f = i_feedback_global, r_f = r_feedback_global, s_f = s_feedback_global, scores=scores_global)

@app.route('/video_feed')
def video_feed():
    return Response(capture_live_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')  # Stream live video feed

if __name__ == "__main__":
    app.run(debug=True)  # Run the application in debug mode