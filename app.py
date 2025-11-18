import sys
import os

import certifi

from networksecurity.utils.ml_utils.model.estimator import NetworkModel
ca=certifi.where()
from urllib.parse import quote_plus
from dotenv import load_dotenv
load_dotenv()


USERNAME = os.getenv("MONGO_DB_USERNAME")
PASSWORD = os.getenv("MONGO_DB_PASSWORD")
CLUSTER_URL = os.getenv("MONGO_DB_CLUSTER_URL")
APP_NAME = os.getenv("MONGO_DB_APP_NAME")

quoted_username = quote_plus(USERNAME)
quoted_password = quote_plus(PASSWORD)

MONGO_DB_URL = (
    f"mongodb+srv://{quoted_username}:{quoted_password}@{CLUSTER_URL}/"
    f"?appName={APP_NAME}"
)

import pymongo
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.pipeline.training_pipeline import TrainingPipeline

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, File, UploadFile, Request # Corrected line
from uvicorn import run as app_run
from fastapi.responses import Response
from starlette.responses import RedirectResponse
import pandas as pd

from networksecurity.utils.main_utils.utils import load_object

from networksecurity.constant.training_pipeline import DATA_INGESTION_COLLECTION_NAME
from networksecurity.constant.training_pipeline import DATA_INGESTION_DATABASE_NAME


client= pymongo.MongoClient(MONGO_DB_URL, tlsCAFile=ca)
database= client[DATA_INGESTION_DATABASE_NAME]
collection=client[DATA_INGESTION_COLLECTION_NAME]

app=FastAPI()
origins=["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

from fastapi.templating import Jinja2Templates
templates= Jinja2Templates(directory="./templates")







@app.get("/",tags=["authentication"])
async def index():
    return RedirectResponse(url="/docs")

@app.get("/train")
async def train_route():
    try:
        train_pipeline=TrainingPipeline()
        train_pipeline.run_pipeline()
        return Response("Training is Successfull")
    except Exception as e:
        raise NetworkSecurityException(e,sys)


@app.post("/predict")
async def predict_route(request:Request,file:UploadFile=File(...)):
    try:
        df=pd.read_csv(file.file)
        preprocessor=load_object("final_model/preprocessor.pkl")
        final_model=load_object("final_model/model.pkl")
        network_model= NetworkModel(preprocessor=preprocessor,model=final_model)
        print(df.iloc[0])
        y_pred=network_model.predict(df)
        print(y_pred)
        df['predicted_column']=y_pred
        print(df['predicted_column'])
        df.to_csv("prediction_output/output.csv")
        table_html=df.to_html(classes='table table-striped')
        return templates.TemplateResponse("table.html",{"request":request,"table":table_html})
    
    except Exception as e:
        raise NetworkSecurityException(e,sys)
    
    
if __name__=="__main__":
    app_run(app,host="localhost",port=5252)    
    
    