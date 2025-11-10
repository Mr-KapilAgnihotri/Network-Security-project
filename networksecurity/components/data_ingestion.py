from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

##configuration of data ingestion
from networksecurity.entity.config_entity import DataIngestionConfig
from networksecurity.entity.artifact_entity import DataIngestionArtifact
import os
import sys
import numpy as np
import pymongo # type: ignore
from typing import List
from sklearn.model_selection import train_test_split
import pandas as pd

from dotenv import load_dotenv
load_dotenv()

from urllib.parse import quote_plus

USERNAME = os.getenv("MONGO_DB_USERNAME")
PASSWORD = os.getenv("MONGO_DB_PASSWORD")
CLUSTER_URL = os.getenv("MONGO_DB_CLUSTER_URL")
APP_NAME = os.getenv("MONGO_DB_APP_NAME")

if not CLUSTER_URL:
    raise ValueError(
        "MONGO_DB_CLUSTER_URL environment variable is missing or empty. "
        "Please check your .env file or environment setup."
    )
if not USERNAME or not PASSWORD:
    print("Warning: MongoDB username or password may be missing.")
    
quoted_username = quote_plus(str(USERNAME))
quoted_password = quote_plus(str(PASSWORD))

MONGO_DB_URL = (
    f"mongodb+srv://{quoted_username}:{quoted_password}@{CLUSTER_URL}/"
    f"?appName={APP_NAME}"
)

class DataIngestion:
    def __init__(self,data_ingestion_config:DataIngestionConfig):
        try:
            self.data_ingestion_config=data_ingestion_config
        except Exception as e:
            raise NetworkSecurityException(e,sys)
    #read data from mongodb
    def export_collection_as_dataframe(self):
        try:
            database_name=self.data_ingestion_config.database_name
            collection_name=self.data_ingestion_config.collection_name
            self.mongo_client=pymongo.MongoClient(MONGO_DB_URL)
            collection=self.mongo_client[database_name][collection_name]
            df=pd.DataFrame(list(collection.find()))
            if "_id" in df.columns.to_list():
                df=df.drop(columns=["_id"],axis=1)
                
            df.replace({"na":np.nan},inplace=True)
            return df    
        except Exception as e:
            raise NetworkSecurityException(e,sys)
    
    def export_data_into_feature_store(self,dataframe: pd.DataFrame):
        try:
            feature_store_file_path=self.data_ingestion_config.feature_store_file_path
            #creating folder
            dir_path=os.path.dirname(feature_store_file_path)
            os.makedirs(dir_path,exist_ok=True)
            dataframe.to_csv(feature_store_file_path,index=False,header=True)
            return dataframe
        except Exception as e:
            raise NetworkSecurityException(e,sys)    
    
    def split_data_as_train_test(self,dataframe=pd.DataFrame):
        try:
            train_set, test_set= train_test_split(
                dataframe, test_size=self.data_ingestion_config.train_test_split_ratio
            )
            logging.info("Performed train test split on the dataframe")
            
            logging.info("Exited split_data_as_train_test method of Data_Ingestion class")
            
            dir_path=os.path.dirname(self.data_ingestion_config.training_file_path)
            os.makedirs(dir_path,exist_ok=True)
            logging.info(f"Exporting train and test file path")
            
            train_set.to_csv(
                self.data_ingestion_config.training_file_path,index=False,header=True
            )
            test_set.to_csv(
                self.data_ingestion_config.testing_file_path,index=False,header=True
            )
            logging.info(f"Exported Train and Test file path")
        except Exception as e:
            raise NetworkSecurityException(e,sys)
        
    def initiate_data_ingestion(self):
        try:
            dataframe=self.export_collection_as_dataframe()
            dataframe=self.export_data_into_feature_store(dataframe)
            self.split_data_as_train_test(dataframe)
            
            dataIngestionArtifact=DataIngestionArtifact(trained_file_path=self.data_ingestion_config.training_file_path,
            test_file_path=self.data_ingestion_config.testing_file_path)
            return dataIngestionArtifact
        
        except Exception as e:
            raise NetworkSecurityException(e,sys)    