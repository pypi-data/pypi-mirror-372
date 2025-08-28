import requests
import json
import traceback
from openai import OpenAI
from flask import request
import loggerutility as logger
import commonutility as common
import os
from datetime import datetime

import weaviate
from .Weaviate import Weaviate
import pandas as pd
from weaviate.gql.get import HybridFusion
from .Insight_LocalAI import InsightLocalAI  
from .Insight_OpenAI import InsightOpenAI    
from .Insight_GeminiAi import InsightGeminiAI  
from DatabaseConnectionUtility import Oracle, InMemory, Dremio

class Insight:
    
    insightModel = ""

    def getCompletionEndpoint(self):
        logger.log(f"\n\nInside getself.insightModel()", "0")
        try:
            finalResult         = ""
            Insight_LocalAI     = ""
            Insight_OpenAI      = ""
            Insight_GeminiAI    = ""

            jsonData = request.get_data('jsonData', None)
            jsonData = json.loads(jsonData[9:])
            logger.log(f"\n Insight Model class jsonData ::: {jsonData}", "0") 

            if 'INVOKE_INSIGHT_MODEL' in jsonData.keys() and jsonData['INVOKE_INSIGHT_MODEL'] is not None:
                self.insightModel = jsonData['INVOKE_INSIGHT_MODEL']
            if len(self.insightModel) == 0:
                self.insightModel = "OpenAI"

            final_instruction = self.schema_name_fetch_using_weviate(jsonData)
            logger.log(f"schema_name_fetch_using_weviate:: inside  {final_instruction}")
              
            if 'LocalAI' == self.insightModel:
                Insight_LocalAI = InsightLocalAI()
                finalResult = Insight_LocalAI.getCompletionEndpoint(jsonData, final_instruction)

            elif 'OpenAI' == self.insightModel:
                Insight_OpenAI = InsightOpenAI()
                finalResult = Insight_OpenAI.getCompletionEndpoint(jsonData, final_instruction)

            elif 'GeminiAI' == self.insightModel:
                Insight_GeminiAI = InsightGeminiAI()
                finalResult = Insight_GeminiAI.getCompletionEndpoint(jsonData, final_instruction) 
            
            else:
                raise Exception(f"INVALID Insight Model ::::: '{self.insightModel}' ")

            logger.log(f"\n\n Insight Model Final Result ::::: {finalResult} \n{type(finalResult)}", "0")
            return finalResult
        
        except Exception as e:
            logger.log(f'\n In getself.insightModel exception stacktrace: ', "1")
            trace = traceback.format_exc()
            descr = str(e)
            returnErr = common.getErrorXml(descr, trace)
            logger.log(f'\n Exception ::: {returnErr}', "0")
            return str(returnErr)
        
    def schema_name_fetch_using_weviate(self, jsonData):
        try :
            server_url      = ""
            openai_api_key  = ""
            inputQuery      = ""
            enterpriseName  = ""
            dbDetails       = ""
            schema_name     = "Insight"
            entity_type     = "schema"

            server_url      = jsonData["weaviate_server_url"]    if jsonData["weaviate_server_url"]     != None else ""
            openai_api_key  = jsonData["license_key"]            if jsonData["license_key"]             != None else ""
            enterpriseName  = jsonData["enterprise"]             if jsonData["enterprise"]              != None else ""
            inputQuery      = jsonData["insight_input"]          if jsonData["insight_input"]           != None else ""
            dbDetails       = jsonData["dbDetails"]              if jsonData["dbDetails"]               != None else ""
        
            client = weaviate.Client(server_url, additional_headers={"X-OpenAI-Api-Key": openai_api_key})
            weaviate_IndexRespository = client.schema.get()["classes"]
            schemaClasslist = [i['class'] for i in weaviate_IndexRespository]
            logger.log(f"\n Available schemaClasslist ::  {schemaClasslist}  {type(schemaClasslist)}\n")

            schemaName_Updated = enterpriseName + "_" + schema_name + "_" + entity_type

            if schemaName_Updated in schemaClasslist :
                response = (
                                client.query
                                    .get(schemaName_Updated, ["answer", "description"])
                                    .with_hybrid(
                                                    alpha   =   0.6,
                                                    query   =   inputQuery
                                                    )
                                    .with_additional('score')
                                    .with_limit(3)
                                    .do()
                                )
                logger.log(f"\n Weaviate Response:: \n {response} {type(response)}\n")

                first_result = response['data']['Get'][schemaName_Updated][0]
                first_answer = first_result['answer']
                logger.log(f"\n First answer: {first_answer} \n")

                final_instruction = self.fetch_column_details(dbDetails, first_answer, enterpriseName, inputQuery)
                logger.log(f"\n Final result from column_schema_name: {final_instruction} \n")
                return final_instruction
            else:
                raise Exception("The trained model for Insight is not available. Please proceed with training the Weaviate model to enable this feature.")
        except Exception as e:
            logger.log(f"Error in fetch_column_details function: {str(e)}", "1")
            trace = traceback.format_exc()
            descr = str(e)
            returnErr = common.getErrorXml(descr, trace)
            logger.log(f'\n Exception ::: {returnErr}', "0")
            return str(returnErr)
        
   
    def fetch_column_details(self, dbDetails, schema_name, enterpriseName, inputQuery):
        try:
            connection_obj  = ""
            connection_obj  = self.get_database_connection(dbDetails)
            if connection_obj:
                logger.log("Database connection established successfully.")
                
                sql     = f"select SCHEMA_MODEL from sd_schema where schema_name='{schema_name}'"
                logger.log(f"SQL Query::  {sql}")
                cursor  = connection_obj.cursor()
                cursor.execute(sql)
                result_lst = cursor.fetchall()
                logger.log(f"result_lst :::::249 {result_lst}{type(result_lst)}")

                if result_lst:
                    clob_data = result_lst[0][0] 
                    if clob_data:
                        schema_model_data = clob_data.read()  
                        logger.log(f"schema_model_data ::: {schema_model_data})")  
                        if schema_model_data:
                            final_instructions = self.extract_column_details(schema_model_data,enterpriseName,schema_name,inputQuery)
                            logger.log(f"column_details:::  {final_instructions}")
                            return final_instructions
                        else:
                            logger.log(f" Extracted clob_data found empty  case ::: {schema_model_data}")
                    else:
                        logger.log(f"clob_data emplty case ::: {clob_data}")
                else:
                    logger.log("No CLOB data found in SCHEMA_MODEL column.")
                    return None
            else:
                logger.log("No results found for the given schema_name.")
                return None
                
        except Exception as e:
            logger.log(f"Error in fetch_column_details function: {str(e)}", "1")
            trace = traceback.format_exc()
            descr = str(e)
            returnErr = common.getErrorXml(descr, trace)
            logger.log(f'\n Exception ::: {returnErr}', "0")
            return str(returnErr)
        

    def extract_column_details(self, schema_model_data, enterpriseName, schema_name, inputQuery):
        try:
            logger.log(f"enterpriseName ::  {enterpriseName}")
            logger.log(f"schema_name ::  {schema_name}")
            logger.log(f"inputQuery ::  {inputQuery}")

            schema_json = json.loads(schema_model_data)
            column_details = {}
            sql_model = schema_json.get("SQLModel", {})
            columns_data = sql_model.get("COLUMNS", [])

            for column_group in columns_data:
                for column in column_group.get("COLUMN", []):
                    standard_name = column.get('StandardName')
                    column_name = column.get('NAME')
                    description = column.get('descr')
                    data_type = column.get('COLTYPE')

                    if standard_name not in column_details:
                        column_details[standard_name] = []

                    column_details[standard_name].append({
                        'column_name': column_name,
                        'description': description,
                        'data_type': data_type
                    })

            logger.log(f"Extracted Column Details: {json.dumps(column_details, indent=2)}", "0")

            if self.insightModel == "LocalAI":
                
                json_file_path = "Insight_Instruction_LocalAI.json"

                if not os.path.exists(json_file_path):
                    logger.log(f"File not found: {json_file_path}", "0")
                    return

                with open(json_file_path, "r") as file:
                    json_data = json.load(file)

                for item in json_data:
                    if "content" in item:
                        item["content"] = item["content"].replace("<SCHEMA_NAME>", schema_name)
                        column_details_json = json.dumps(column_details, indent=2)
                        item["content"] = item["content"].replace("<SCHEMA_DETAILS>", column_details_json)
                        item["content"] = item["content"].replace("<INSIGHT_INPUT>", inputQuery)
            else:
                json_file_path = "Insight_Instruction.json"

                if not os.path.exists(json_file_path):
                    logger.log(f"File not found: {json_file_path}", "0")
                   
                with open(json_file_path, "r") as file:
                    json_data = json.load(file)
                for entry in json_data:
                    for item in entry["content"]:
                        item["text"] = item["text"].replace("<SCHEMA_NAME>", schema_name)
                        column_details_json = json.dumps(column_details, indent=2)
                        item["text"] = item["text"].replace("<SCHEMA_DETAILS>", column_details_json)
                        item["text"] = item["text"].replace("<INSIGHT_INPUT>", inputQuery)

            logger.log(f"Modified JSON Data: {json.dumps(json_data, indent=2)}")
            return json_data

        except Exception as e:
            logger.log(f'\n In extract_column_details exception stacktrace : ', "1")
            trace = traceback.format_exc()
            descr = str(e)
            returnErr = common.getErrorXml(descr, trace)
            logger.log(f'\n extract_column_details : {returnErr}', "0")
            return str(returnErr)
    
    def get_database_connection(self, dbDetails):
       
        if dbDetails != None:
            klass = globals()[dbDetails['DB_VENDORE']]
            dbObject = klass()
            connection_obj = dbObject.getConnection(dbDetails)
                
        return connection_obj
    


