import json
import loggerutility as logger
from .Image_TrainingPrediction import Image_TrainingPrediction
from .Text_TrainingPrediction import Text_TrainingPrediction
from .Document_TrainingPrediction import Document_TrainingPrediction
from flask import request
import weaviate
import os

class Weaviate:
    modelParameter          = ""
    document_type           = ""
    train_Type              = "Text"

    def traindata(self,weaviate_jsondata, fileObj=""):
        
        training_final  =  ""

        if "modelParameter" in weaviate_jsondata and weaviate_jsondata["modelParameter"] != None:
            self.modelParameter = json.loads(weaviate_jsondata['modelParameter'])

        if "train_Type" in self.modelParameter and (self.modelParameter["train_Type"]).strip() != None and (self.modelParameter["train_Type"]).strip() != '':
            self.train_Type = (self.modelParameter["train_Type"]).capitalize().replace("-","_").strip()
            logger.log(f"\nWeaviate Hybrid class Train Type:::\t{self.train_Type} \t{type(self.train_Type)}","0")

        if self.train_Type == "Img" :
            image_TrainingPrediction = Image_TrainingPrediction()
            training_final = image_TrainingPrediction.imageTraining(weaviate_jsondata)
            logger.log(f"Training result for train-type '{self.train_Type}' : {training_final}")
        
        elif self.train_Type == "Text" :
            text_TrainingPrediction = Text_TrainingPrediction()
            training_final = text_TrainingPrediction.traindata(weaviate_jsondata,'')
            logger.log(f"Training result for train-type '{self.train_Type}' : {training_final}")
        
        elif self.train_Type == "Both" :
            text_TrainingPrediction = Text_TrainingPrediction()
            training_final = text_TrainingPrediction.traindata(weaviate_jsondata,'')
            logger.log(f"Training result for train-type '{self.train_Type}' : {training_final}")

            image_TrainingPrediction = Image_TrainingPrediction()
            training_final = image_TrainingPrediction.imageTraining(weaviate_jsondata)
            logger.log(f"Training result for train-type '{self.train_Type}' : {training_final}")

        else:
            logger.log(f"Invalid doctype:: {self.train_Type}")

        return training_final
    
    def getLookupData(self):

        prediction_final  =  ""
        weaviate_jsondata =  request.get_data('jsonData', None)
        weaviate_jsondata =  json.loads(weaviate_jsondata[9:])
        logger.log(f"\nWeaviate hybrid class getLookupData() weaviate_json inside weaviate class:::\t{weaviate_jsondata} \t{type(weaviate_jsondata)}","0")

        if "modelParameter" in weaviate_jsondata and weaviate_jsondata["modelParameter"] != None:
            self.modelParameter = json.loads(weaviate_jsondata['modelParameter'])

        if "train_Type" in self.modelParameter and (self.modelParameter["train_Type"]).strip() != None and (self.modelParameter["train_Type"]).strip() != '':
            self.train_Type = (self.modelParameter["train_Type"]).capitalize().replace("-","_").strip()
            logger.log(f"\nWeaviate Hybrid class Train Type:::\t{self.train_Type} \t{type(self.train_Type)}","0")

        if self.train_Type == "Img" :
            image_TrainingPrediction  = Image_TrainingPrediction()
            prediction_final          = image_TrainingPrediction.Prediction_Image(weaviate_jsondata)
            logger.log(f"Prediction result for '{self.train_Type}' : {prediction_final}")

        elif self.train_Type == "Text" :
            text_TrainingPrediction   = Text_TrainingPrediction()
            prediction_final          = text_TrainingPrediction.getLookupData()
            logger.log(f"Prediction result for '{self.train_Type}' : {prediction_final}")

        elif self.train_Type == "Both" :
            text_TrainingPrediction   = Text_TrainingPrediction()
            prediction_final          = text_TrainingPrediction.getLookupData()
            logger.log(f"Prediction result for '{self.train_Type}' : {prediction_final}")

            image_TrainingPrediction  = Image_TrainingPrediction()
            prediction_final          = image_TrainingPrediction.Prediction_Image(weaviate_jsondata)
            logger.log(f"Prediction result for '{self.train_Type}' : {prediction_final}")

        else:
            logger.log(f"Invalid doctype:; {self.train_Type}")
        
        return prediction_final
    
    # Added by YashS on [ 29-08-24 ] for getting filtered schema list through [START]
    def getEnterpriseList(self):

        weaviate_jsondata =  request.get_data('jsonData', None)
        weaviate_jsondata = json.loads(weaviate_jsondata)['jsonData']
        logger.log(f"\nWeaviate hybrid class getLookupData() weaviate_json inside weaviate class:::\t{weaviate_jsondata} \t{type(weaviate_jsondata)}","0")

        environment_weaviate_server_url = os.getenv('weaviate_server_url')
        logger.log(f"environment_weaviate_server_url ::: [{environment_weaviate_server_url}]")

        if environment_weaviate_server_url != None and environment_weaviate_server_url != '':
            self.server_url = environment_weaviate_server_url
            logger.log(f"\nWeaviate Hybrid class LookUpData server_url:::\t{self.server_url} \t{type(self.server_url)}","0")
        else:
            if "server_url" in weaviate_jsondata and weaviate_jsondata["server_url"] != None:
                self.server_url = weaviate_jsondata["server_url"]
                logger.log(f"server_url  :::: {self.server_url} ")

        if "openAI_apiKey" in weaviate_jsondata and weaviate_jsondata["openAI_apiKey"] != None:
            self.openAI_apiKey = weaviate_jsondata["openAI_apiKey"]
            logger.log(f"openAI_apiKey  :::: {self.openAI_apiKey} ")

        if "enterprise" in weaviate_jsondata and weaviate_jsondata["enterprise"] != None:
            self.enterpriseName = weaviate_jsondata["enterprise"]
            logger.log(f"enterpriseName  :::: {self.enterpriseName} ")

        client = weaviate.Client(self.server_url, additional_headers={"X-OpenAI-Api-Key": self.openAI_apiKey})

        schema = client.schema.get()
        matching_classes = [cls['class'] for cls in schema['classes'] if cls['class'].lower().startswith(self.enterpriseName.lower())]
        
        logger.log(f"matching_classes  :::: {matching_classes} ")
        return matching_classes    
    # Added by YashS on [ 29-08-24 ] for getting filtered schema list through [END]

