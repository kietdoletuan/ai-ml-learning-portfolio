import gradio as gr
import pandas as pd
import joblib
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "titanic_rf.pkl"

model = joblib.load(MODEL_PATH)

def predict(Pclass, Sex, Age, Fare, Embarked, SibSp, Parch):

    sex_val = 1 if Sex == "Male" else 0

    embarked_c = 1 if Embarked == "C" else 0
    embarked_q = 1 if Embarked == "Q" else 0
    embarked_s = 1 if Embarked == "S" else 0

    family = SibSp + Parch + 1

    df = pd.DataFrame({
        "Pclass": [Pclass],
        "Age": [Age],
        "Fare": [Fare],
        "Embarked_C": [embarked_c],
        "Embarked_Q": [embarked_q],
        "Embarked_S": [embarked_s],
        "Sex_Encoded": [sex_val],
        "Family": [family]
    }).to_numpy()

    pred = model.predict(df)[0]
    prob = model.predict_proba(df)[0].max()

    label = "Survived" if pred == 1 else "Did Not Survive"

    return f"{label} ({prob:.1%} confidence)"

demo = gr.Interface(
    fn = predict,
    inputs = [
        gr.Dropdown([1, 2, 3], label = "Passenger Class"),
        gr.Dropdown(['Male', 'Female'], label = 'Sex'),
        gr.Number(label = 'Age'),
        gr.Number(label = 'Fare'),
        gr.Dropdown(['C','Q','S'], label = 'Embarked'),
        gr.Number(label = 'Siblings / Spouses'),
        gr.Number(label = 'Parents / Children')
    ],
    outputs ="text",
    title = 'Titanic Survival Predictor With Random Forest'
)

demo.launch()

