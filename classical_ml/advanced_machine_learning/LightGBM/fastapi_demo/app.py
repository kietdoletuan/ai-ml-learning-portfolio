from fastapi import FastAPI
import pandas as pd
import joblib
from pydantic import BaseModel
from typing import Literal


app = FastAPI()
model = joblib.load("titanic_lightgbm.pkl")


class PredictInput(BaseModel):
    Pclass : int
    Sex : Literal["male", "female"]
    Embarked : Literal["Q", "C", "S"]
    SibSp : int
    Parch : int
    Fare : float
    Age : float
    
class Prediction(BaseModel):
    Survived : int
    Probability: float

@app.get("/health")
def read_root():
    return {"status" : "healthy"}

@app.post("/predict")
def predicts(predictInput: PredictInput):
    EmbarkedMap = {"Q": 0, "S" : 0, "C" : 0}
    EmbarkedMap[predictInput.Embarked] = 1
    
    Sex = 1 if predictInput.Sex == "male" else 0
    
    Family = predictInput.SibSp + predictInput.Parch + 1
    
    IsAlone = 1 if Family == 1 else 0
    
    features = pd.DataFrame([[
        predictInput.Pclass,
        predictInput.Age,
        predictInput.Fare,
        EmbarkedMap["C"],
        EmbarkedMap["Q"],
        EmbarkedMap["S"],
        Sex,
        Family,
        IsAlone
    ]], columns = ["Pclass", "Age", "Fare", "Embarked_C", "Embarked_Q", "Embarked_S", "Sex_Encoded", "Family", "IsAlone"])
    
    prediction = model.predict(features)
    probability = model.predict_proba(features)
    
    return Prediction(
        Survived = int(prediction[0]),
        Probability = float(probability[0][1])
    )
    
    
    



