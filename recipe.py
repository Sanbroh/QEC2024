import datetime
from typing import TypedDict

class RecipeObjectDict(TypedDict):
    name: str
    amount: int
    timestamp: datetime.datetime


class Recipe:
    def __init__(self):
        self.startTime : datetime = datetime.datetime.now()
        self.endTime : datetime = None

        self.recipeTimeSeconds : int = None

        self.shown_objects : RecipeObjectDict = []

    def add_object(self, RecipeObject: RecipeObjectDict):

        self.shown_objects.append(RecipeObject)

    def end_recipe(self):
        self.endTime = datetime.datetime.now()

        self.recipeTimeSeconds = int((self.endTime - self.startTime).total_seconds())       

    def ObjectsToGPTStringPrompt(self) -> str:
        gptString : str = '{Objects:['

        for object in self.shown_objects:
            gptString += '('
            gptString += object["name"]
            gptString += ','
            gptString += str(object["amount"])
            gptString += ','
            gptString += str(int((object["timestamp"]-self.startTime).total_seconds()))
            gptString += '),'
    
        gptString = gptString[:-1]

        gptString += '],'

        gptString += "Total Time:"
        gptString += str(self.recipeTimeSeconds)
        gptString += "}"

        return gptString
    
    def GPTresponseHandler(self, response : str) -> list[str]:
        response = response[1:-1]

        responseObject : list[str] = response.split(",")

        return responseObject