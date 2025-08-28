import json
import openai
import pinecone
import datetime
import traceback
import pandas as pd
from flask import request
import loggerutility as logger
import commonutility as common
#from openai.embeddings_utils import get_embedding, get_embeddings, cosine_similarity


class OpenAI_PineConeVector:
    
    index_name          =   ""
    openAI_apiKey       =   ""
    pineCone_apiKey     =   ""
    queryList           =   ""
    dfJson              =   ""
    engineName          =   "text-embedding-ada-002" # Model that we want to use 
    dimensions          =   1536
    my_index            =   ""
    enterpriseName      =   ""
    modelScope          =   "E"
    entity_type         =   "" 
    enterpriseEntityInfo=   ""
    modelParameter      =   {}

    def trainData(self, pineCone_json):
        try:
            result = ""
            df     = None

            logger.log("inside PineConeVector class trainData()","0")
            if "openAI_apiKey" in pineCone_json and pineCone_json["openAI_apiKey"] != None:
                self.openAI_apiKey = pineCone_json["openAI_apiKey"]           
                logger.log(f"\n openAI_apiKey:::\t{self.openAI_apiKey} \t{type(self.openAI_apiKey)}","0")
            
            if "pineCone_apiKey" in pineCone_json and pineCone_json["pineCone_apiKey"] != None:
                self.pineCone_apiKey = pineCone_json["pineCone_apiKey"]           
                logger.log(f"\n pineCone_apiKey:::\t{self.pineCone_apiKey} \t{type(self.pineCone_apiKey)}","0")

            if "modelParameter" in pineCone_json and pineCone_json["modelParameter"] != None:
                self.modelParameter = json.loads(pineCone_json['modelParameter'])
            
            if "index_name" in pineCone_json and pineCone_json["index_name"] != None:    # Added on 20-Sept-23 because in 'DOCUMENT' Case 'index_name' Key does not come in modelParameter.
                self.index_name = pineCone_json["index_name"]
                logger.log(f"\n index_name for training 'DOCUMENT' Case:::\t{self.index_name} \t{type(self.index_name)}","0")
            
            if len(self.modelParameter) != 0 :
                if "index_name" in self.modelParameter and self.modelParameter["index_name"] != None:
                    self.index_name = self.modelParameter["index_name"]
                    logger.log(f"\n index_name:::\t{self.index_name} \t{type(self.index_name)}","0")
            
            if self.index_name == "document":                             # Added on 20-Sept-23 because in 'DOCUMENT' Case 'dfJson' Key is passed.
                if "dfJson" in pineCone_json and pineCone_json["dfJson"] != None:
                    self.dfJson = pineCone_json["dfJson"]
                    logger.log(f"\n dfJson for training 'DOCUMENT' Case :::\t{self.dfJson} \t{type(self.dfJson)}","0")
            else:
                if "modelJsonData" in pineCone_json and pineCone_json["modelJsonData"] != None:
                    self.dfJson = pineCone_json["modelJsonData"]
                
            if "enterprise" in pineCone_json and pineCone_json["enterprise"] != None:
                self.enterpriseName = pineCone_json["enterprise"]
                logger.log(f"\n enterpriseName :::\t{self.enterpriseName} \t{type(self.enterpriseName)}","0")

            if "modelScope" in pineCone_json and pineCone_json["modelScope"] != None:
                self.modelScope = pineCone_json["modelScope"]
                logger.log(f"\n modelScope:::\t{self.modelScope} \t{type(self.modelScope)}","0")
            
            if "entity_type" in self.modelParameter and self.modelParameter["entity_type"] != None:
                self.entity_type = self.modelParameter["entity_type"]
                logger.log(f"\nentity_type:::\t{self.entity_type} \t{type(self.entity_type)}","0")
            
            if type(self.dfJson) == str :
                parsed_json = json.loads(self.dfJson)
                if self.index_name == 'item' or self.index_name == 'vision-masters':
                    df = pd.DataFrame(parsed_json[1:])  # Added because actual data values start from '1' position
                    
                elif self.index_name == 'document':
                    parsed_json = self.concat_OCR_PageWise(parsed_json)
                    df = pd.DataFrame(parsed_json)      # Added because actual data values start from '0' position
                    
            else:
                df = pd.DataFrame(self.dfJson)
                
            logger.log(f"Final Training DataSet  :: \t {df}", "0")    
            pinecone.init(api_key=self.pineCone_apiKey, environment='us-west4-gcp')
            openai.api_key = self.openAI_apiKey                 

            logger.log(f"Pinecone Available indexes List  :: \t {pinecone.list_indexes()}", "0")    
            # Creating index
            if self.index_name not in pinecone.list_indexes():
                logger.log(f" \n'{self.index_name}' index not present. Creating New!!!\n", "0")
                pinecone.create_index(name = self.index_name, dimension=self.dimensions, metric='cosine')
                self.my_index = pinecone.Index(index_name=self.index_name)
            else:
                logger.log(f" \n'{self.index_name}' index is present. Loading now!!!\n", "0")
                self.my_index = pinecone.Index(index_name=self.index_name)
            logger.log(f"Pinecone Available indexes List  :: \t {pinecone.list_indexes()}", "0")    

            df.columns = ['_'.join(column.lower().split(' ')) for column in df.columns]
            df.fillna("N/A",inplace=True)
            
            if self.modelScope == "G" :
                self.enterpriseName = ""
            
            self.enterpriseEntityInfo = (self.enterpriseName + "_" +self.entity_type).upper()
            logger.log(f"enterpriseEntityInfo  ::: \t {self.enterpriseEntityInfo}", "0")    
            df['enterprise'] = self.enterpriseEntityInfo

            if self.index_name != "document":                   # Added on 20-Sept-23 because description column comes at '0'  position in 'document' index
                required_colNameList = ['id', 'description']
                logger.log(f"\nBefore df Column Name  change::  {df.columns.tolist()},\n {df.columns}", "0")    
                df.columns = required_colNameList + df.columns[len(required_colNameList):].tolist()
                logger.log(f"\n After df Column Name change:: {df.head()},\n {df.head()}", "0")    

            df['embedding'] = get_embeddings(df['description'].to_list(), engine=self.engineName)   
            logger.log(f"\n line 118", "0")    
            metadata = df.loc[:, ~df.columns.isin(['id','embedding'])].to_dict(orient='records')  # remove not required columns 
            logger.log(f"\n line 120", "0")    

            upsert = list(zip(df['id'], df['embedding'], metadata))
            logger.log(f"\n line 123", "0")    
            _ = self.my_index.upsert(vectors=upsert)
            logger.log(f"\n\nIndex stats :::\n{self.my_index.describe_index_stats()}","0")

            logger.log(f"\nOpenAI_PineConeVector class trainData:::\t{self.my_index}","0")
            result = f" '{self.index_name}' Index Creation SUCCESSFUL for filter: '{self.enterpriseEntityInfo}'. "
            logger.log(f"\nOpenAI_PineConeVector class trainData Result:::{result}\n","0")
            return result
            
        except Exception as e:
            logger.log(f" '{self.index_name}' Index Creation FAILED for filter: '{self.enterpriseEntityInfo}'. ","0")
            logger.log(f"OpenAI_PineConeVector class trainData() Issue::: \n{e}","0")
            trace = traceback.format_exc()
            descr = str(e)
            errorXml = common.getErrorXml(descr, trace)
            logger.log(f'\n OpenAI_PineConeVector class trainData() errorXml::: \n{errorXml}', "0")
            raise str(errorXml)

    def getLookupData(self):    
                   
        try:
            
            logger.log("inside PineConeVector class LookUpData()","0")
            id_list                 = []
            finalResult             = ""
            queryJson               = ""
            finalResultJson         = {}
            
            pineCone_json =  request.get_data('jsonData', None)
            pineCone_json =  json.loads(pineCone_json[9:])
            logger.log(f"\nPineConeVector class getLookupData() pineCone_json:::\t{pineCone_json} \t{type(pineCone_json)}","0")

            if "openAI_apiKey" in pineCone_json and pineCone_json["openAI_apiKey"] != None:
                self.openAI_apiKey = pineCone_json["openAI_apiKey"]          
                logger.log(f"\nPineConeVector class LookUpData() openAI_apiKey:::\t{self.openAI_apiKey} \t{type(self.openAI_apiKey)}","0")
                openai.api_key = self.openAI_apiKey                 

            if "pineCone_apiKey" in pineCone_json and pineCone_json["pineCone_apiKey"] != None:
                self.pineCone_apiKey = pineCone_json["pineCone_apiKey"]           
                logger.log(f"\nPineConeVector class LookUpData() pineCone_apiKey:::\t{self.pineCone_apiKey} \t{type(self.pineCone_apiKey)}","0")

            if "index_name" in pineCone_json and pineCone_json["index_name"] != None:
                self.index_name = pineCone_json["index_name"]
                logger.log(f"\nPineConeVector class LookUpData() index_name:::\t{self.index_name} \t{type(self.index_name)}","0")
            
            if self.index_name == "document":   
                if "queryList" in pineCone_json and pineCone_json["queryList"] != None:    # Added on 21-Sept-23 because in 'DOCUMENT' Case 'queryList' Key is passed.
                    queryJson = pineCone_json["queryList"]
                    logger.log(f"\nqueryList  for training 'DOCUMENT' Case :::\t{queryJson} has length ::: '{len(queryJson)}'\t{type(queryJson)}","0")
            else:        
                if "queryJson" in pineCone_json and pineCone_json["queryJson"] != None:
                    queryJson = pineCone_json["queryJson"]
                    logger.log(f"\nPineConeVector class LookUpData() queryJson:::\t{queryJson} has length ::: '{len(queryJson)}'\t{type(queryJson)}","0")
            
            if "enterprise" in pineCone_json and pineCone_json["enterprise"] != None:
                self.enterpriseName = pineCone_json["enterprise"]
                logger.log(f"\nPineConeVector class LookUpData() enterprise:::\t{self.enterpriseName} \t{type(self.enterpriseName)}","0")

            if "modelScope" in pineCone_json and pineCone_json["modelScope"] != None:
                self.modelScope = pineCone_json["modelScope"]
                logger.log(f"\nPineConeVector class LookUpData() modelScope:::\t{self.modelScope} \t{type(self.modelScope)}","0")
            
            if "entity_type" in pineCone_json and pineCone_json["entity_type"] != None:
                self.entity_type = pineCone_json["entity_type"]
                logger.log(f"\nentity_type:::\t{self.entity_type} \t{type(self.entity_type)}","0")
            
            if self.modelScope == "G":
                self.enterpriseName = ""

            openai.api_key  =  self.openAI_apiKey         
            pinecone.init(api_key=self.pineCone_apiKey, environment='us-west4-gcp')
            self.enterpriseEntityInfo = (self.enterpriseName + "_" +self.entity_type).upper()
            logger.log(f"\nenterpriseEntityInfo:::\t{self.enterpriseEntityInfo} \t{type(self.enterpriseEntityInfo)}","0")
            
            pinecone_IndexList = pinecone.list_indexes()
            if self.index_name in pinecone_IndexList: 
                self.my_index = pinecone.Index(index_name=self.index_name)
                if self.my_index != "":
                    logger.log(f"\n\n'{self.index_name}' index loaded successfully for filter: '{self.enterpriseEntityInfo}\n'")
            else:
                logger.log(f"OpenAI_PineConeVector class getLookUP()::: \nIndex_Name: {self.index_name} not found in pinecone_IndexList: {pinecone_IndexList}","0")
                message = f"Index_Name: '{self.index_name}' not found in pinecone_IndexList. Available IndexList: {pinecone_IndexList}"
                errorXml = common.getErrorXml(message, "")
                raise Exception(errorXml)
            
            if self.index_name == "document":
                for key in queryJson:
                    # because in document case I get directly list and not json
                    response = self.my_index.query(vector=get_embedding(key, engine=self.engineName),filter={"enterprise": self.enterpriseEntityInfo},top_k=10, include_metadata=True)
                    logger.log(f"\n\n Pinecone 'document' index response for query '{key}' is :::\n{response} \t {type(key)}\n")
                    if len(response["matches"]) > 0:
                        for each_MatchedJson in (response["matches"]):
                            if each_MatchedJson["score"] >= 0.75 and key in each_MatchedJson['metadata']['description']:
                                id_list.append(each_MatchedJson["id"])
                            else:
                                message = f"Index_Name: '{self.index_name}' returned response for query '{key}' with less than 75% Accuracy: \n{response}"
                                logger.log(f"\n{message}\n")
                                
                    else:
                        message = f"Trained Model for Index Name: '{self.index_name}' and filter '{self.enterpriseEntityInfo}' not found \t{response} \n"
                        errorXml = common.getErrorXml(message, "")
                        raise Exception(errorXml)

                logger.log(f"\n\n id_list:::{id_list} has length :::'{len(id_list)}' \t {type(id_list)}\n")
                finalResult = str(id_list)
                
            elif self.index_name == "item" or self.index_name == "vision-masters":
                for key in queryJson:
                    if len(queryJson[key]) > 0:
                        if self.index_name == "item":
                            response = self.my_index.query(vector=get_embedding(queryJson[key], engine=self.engineName),filter={"enterprise": self.enterpriseEntityInfo},top_k=1, include_metadata=True)
                            logger.log(f"response:::: {response}")
                            finalResultJson[key] = {"material_description": response["matches"][0]["metadata"]["material_description"], 
                                                    "id": response["matches"][0]["id"]}  if len(response["matches"]) > 0 else response
                        
                        elif self.index_name == "vision-masters":
                            response = self.my_index.query(vector=get_embedding(queryJson[key], engine=self.engineName),filter={"enterprise": self.enterpriseEntityInfo},top_k=1, include_metadata=True)
                            logger.log(f"response:::: {response}")
                            finalResultJson[key] = {"material_description": response["matches"][0]["metadata"]["description"], 
                                                    "id": response["matches"][0]["id"],
                                                    "score" : response["matches"][0]["score"]}  if len(response["matches"]) > 0 else response
                    else:
                        logger.log(f"Empty description found for line number:::'{key}'")
                
                logger.log(f"\n\nfinalResultJson:::{finalResultJson} has length ::: '{len(finalResultJson)}' \t {type(finalResultJson)}\n")
                finalResult = str(finalResultJson)

            else:
                logger.log(f"OpenAI_PineConeVector class getLookUP()::: \nIndex_Name: {self.index_name} not found in pinecone_IndexList: {pinecone_IndexList}","0")
                message = f"Index_Name: '{self.index_name}' not found in pinecone_IndexList. Available IndexList: {pinecone_IndexList}"
                errorXml = common.getErrorXml(message, "")
                raise Exception(errorXml)
            
            return finalResult
        
        except Exception as e:
            logger.log(f"OpenAI_PineConeVector class getLookUP() Issue::: \n{e}","0")
            trace = traceback.format_exc()
            descr = str(e)
            errorXml = common.getErrorXml(descr, trace)
            logger.log(f'\n OpenAI_PineConeVector class getLookUP() errorXml::: \n{errorXml}', "0")
            raise str(errorXml)

    def concat_OCR_PageWise(self, parsedJson):
        logger.log("Inside ")
        for jsonObj in parsedJson:
            updatedDescription = " ".join(list(json.loads(jsonObj["description"]).values()))
        parsedJson[0]["description"] = updatedDescription
        logger.log(f" \n\nparsedJson ::: \t{type(parsedJson)}\n{parsedJson}")
        return parsedJson
    

