import weaviate
import json, os
import pandas as pd
import traceback
import datetime
from flask import request
import loggerutility as logger
import commonutility as common
from weaviate.gql.get import HybridFusion
from .Document_TrainingPrediction import Document_TrainingPrediction
from hashlib import md5
import uuid
import hashlib

class Text_TrainingPrediction:
    modelScope              =  "E"
    group_size              =  10000
    entity_type             =  ""
    schema_name             =  ""
    modelParameter          =  ""
    server_url              =  ""
    openAI_apiKey           =  ""
    enterpriseName          =  "E"
    entity_type             =  ""
    docType_SchemaName      =  ""
    alphaValue              =  ""
    lookup_type             =  ""
    processingMethod_list   =  "" 
    file_storage_path       =  os.environ.get('de_storage_path', '/flask_downloads')
    metadata_def            = ""

    def traindata(self, weaviate_jsondata, fileObj=""):
        try:
            logger.log(f'\n Print Weaviate start time for traning : {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', "0")
            result                      = ""
            df                          = None
            columnnamelist              = []
            schemaClasslist             = []
            flag                        = ""
            propertyEmpty_flag          = "true"
            weaviate_IndexRespository   = []
            schemaName_Updated          = ""
            documentProperty_dict       = {}
            self.vector_train_type      = "F"
            
            logger.log("inside Weaviate Hybrid class trainData()","0")
            logger.log(f"jsondata Weaviate Hybrid class trainData() ::: {weaviate_jsondata} ","0")
            # logger.log(f"jsondata Weaviate keys ::: {list(weaviate_jsondata.keys())}", "0")

            if "openAI_apiKey" in weaviate_jsondata and weaviate_jsondata["openAI_apiKey"] != None:
                self.openAI_apiKey = weaviate_jsondata["openAI_apiKey"]           
                logger.log(f"\ntrain_Weaviate Hybrid openAI_apiKey:::\t{self.openAI_apiKey} \t{type(self.openAI_apiKey)}","0")
            
            if "modelParameter" in weaviate_jsondata and weaviate_jsondata["modelParameter"] != None:
                self.modelParameter = json.loads(weaviate_jsondata['modelParameter'])

            if "index_name" in self.modelParameter and (self.modelParameter["index_name"]).strip() != None:
                self.schema_name = (self.modelParameter["index_name"]).capitalize().replace("-","_").strip()
                logger.log(f"\ntrain_Weaviate Hybrid index_name:::\t{self.schema_name} \t{type(self.schema_name)}","0")

            elif "index_name" in weaviate_jsondata and (weaviate_jsondata["index_name"]).strip() != None:
                self.schema_name = (weaviate_jsondata["index_name"]).capitalize().replace("-","_").strip()
                logger.log(f"\ntrain_Weaviate Hybrid index_name:::\t{self.schema_name} \t{type(self.schema_name)}","0")

            if "entity_type" in self.modelParameter and (self.modelParameter["entity_type"]).strip() != None:
                self.entity_type = (self.modelParameter['entity_type']).lower().strip()
                logger.log(f'\n Tranin Weaviate vector entity_type veraible value :::  \t{self.entity_type} \t{type(self.entity_type)}')
            
            if "data_limit" in self.modelParameter and (self.modelParameter["data_limit"]).strip() != None and (self.modelParameter["data_limit"]).strip() != "":
                self.group_size = int(self.modelParameter['data_limit'])
                logger.log(f'\n Tranin Weaviate vector data_limit veraible value :::  \t{self.group_size} \t{type(self.group_size)}')

            if "modelScope" in weaviate_jsondata and weaviate_jsondata["modelScope"] != None:
                self.modelScope = weaviate_jsondata["modelScope"]
                logger.log(f"\ntrain_Weaviate class TrainData modelScope:::\t{self.modelScope} \t{type(self.modelScope)}","0")

            if "enterprise" in weaviate_jsondata and weaviate_jsondata["enterprise"] != None:
                self.enterpriseName = weaviate_jsondata["enterprise"]
                logger.log(f"\nWeaviate Hybrid class TrainData enterprise:::\t{self.enterpriseName} \t{type(self.enterpriseName)}","0")

            if "modelJsonData" in weaviate_jsondata and weaviate_jsondata["modelJsonData"] != None:
                self.dfJson = weaviate_jsondata["modelJsonData"]
            elif "dfJson" in weaviate_jsondata and weaviate_jsondata["dfJson"] != None:
                self.dfJson = weaviate_jsondata["dfJson"]
            logger.log(f"\ntrain_Weaviate Hybrid dfJson:::\t{self.dfJson} \t{type(self.dfJson)}","0")
            
            if "vector_train_type" in self.modelParameter and (self.modelParameter["vector_train_type"]).strip() != None:
                self.vector_train_type = (self.modelParameter['vector_train_type']).strip()
                logger.log(f'\n Train Weaviate vector_train_type variable value :::  \t{self.vector_train_type} \t{type(self.vector_train_type)}')
            
            if type(self.dfJson) == str :
                parsed_json = json.loads(self.dfJson)
            else:
                parsed_json = self.dfJson

            environment_weaviate_server_url = os.getenv('weaviate_server_url')
            logger.log(f"environment_weaviate_server_url ::: [{environment_weaviate_server_url}]")

            if environment_weaviate_server_url != None and environment_weaviate_server_url != '':
                self.server_url = environment_weaviate_server_url
                logger.log(f"\nWeaviate Hybrid class LookUpData server_url:::\t{self.server_url} \t{type(self.server_url)}","0")
            else:
                if "server_url" in weaviate_jsondata and weaviate_jsondata["server_url"] != None:
                    self.server_url = weaviate_jsondata["server_url"] 
                    logger.log(f"\nWeaviate Hybrid class TrainData server_url:::\t{self.server_url} \t{type(self.server_url)}","0")
            
            if "proc_mtd" in weaviate_jsondata and weaviate_jsondata["proc_mtd"] != None:
                self.processingMethod_list = weaviate_jsondata["proc_mtd"].split("-")
                logger.log(f"\nWeaviate Hybrid class TrainData processingMethod:::\t{self.processingMethod_list} \t{type(self.processingMethod_list)}","0")
            
            if "meta_data_def" in weaviate_jsondata and weaviate_jsondata["meta_data_def"] != None:
                self.metadata_def = json.loads(weaviate_jsondata["meta_data_def"]) if type(weaviate_jsondata["meta_data_def"]) == str else weaviate_jsondata["meta_data_def"]
                logger.log(f"\nWeaviate Hybrid class TrainData meta_data_def:::\t{self.metadata_def} \t{type(self.metadata_def)}")

            if len(self.metadata_def) != 0:
                for eachJsonObj in self.metadata_def["Details"]:
                    logger.log(f"eachJsonObj ::: {eachJsonObj}")
                    if "name" in eachJsonObj and eachJsonObj["name"] != None :
                        documentProperty_dict[eachJsonObj["name"]] = eachJsonObj["value"] 
                        logger.log(f"documentProperty_dict ::: {documentProperty_dict}")

            client = weaviate.Client(self.server_url,additional_headers={"X-OpenAI-Api-Key": self.openAI_apiKey})
            logger.log(f'Connection is establish : {client.is_ready()}')

            if self.modelScope == "G" :
                self.enterpriseName = ""
                schemaName_Updated =  self.schema_name + "_" + self.entity_type
                logger.log(f'\nschemaName_Updated ::: \t{schemaName_Updated}')
            else:
                schemaName_Updated = self.enterpriseName + "_" + self.schema_name + "_" + self.entity_type
                logger.log(f'\nschemaName_Updated ::: \t{schemaName_Updated}')

            if self.schema_name == 'Document' or self.schema_name == "document":
                if parsed_json[0]["description"] == "":
                    logger.log(f"OCR not avialable Case. \n Generating new OCR and then Training\n")
                    OCR_Text_json = self.get_FileOCR(fileObj)
                    logger.log(f"OCR_Text_json ::: {OCR_Text_json}\n")
                    parsed_json[0]["description"] = OCR_Text_json
                    logger.log(f"parsed_json upadted ::: {parsed_json}")

                copydict = parsed_json.copy()
                parsed_json = {"id" : 'String', "description" : 'String'}
                parsed_json.update(copydict[0]) # To add only document JSON Object 
                
                document_TrainingPrediction = Document_TrainingPrediction()
                flag = document_TrainingPrediction.documentTraining(client, parsed_json, documentProperty_dict,self.enterpriseName,self.schema_name)
            else:
                class_obj = {
                        "class": schemaName_Updated,
                        "vectorizer": "text2vec-openai",
                        "moduleConfig": {
                            "text2vec-openai": {},
                            "generative-openai": {}
                                        }
                            }
                weaviate_IndexRespository = client.schema.get()["classes"]
                schemaClasslist = [i['class'] for i in weaviate_IndexRespository]               
                
                if schemaName_Updated not in schemaClasslist:
                    client.schema.create_class(class_obj)
                    logger.log(f"\n Schema: '{schemaName_Updated}' not present. Creating New !!!\n ")
                    
                    weaviate_IndexRespository = client.schema.get()["classes"]      # Updating variable value after new index creation
                    schemaClasslist = [i['class'] for i in weaviate_IndexRespository]  # Updating variable value after new index creation
                    logger.log(f"\nAvailable schema list::: {schemaClasslist} \n ")
                else:
                    logger.log(f"'{schemaName_Updated}' already present. Loading Now !!!\n ")
                
                for index, schemaObj in enumerate(weaviate_IndexRespository):
                    if schemaName_Updated == weaviate_IndexRespository[index]["class"]:
                        if not len(schemaObj["properties"])  > 0:
                            logger.log(f"Property empty for Weaviate Index '{schemaName_Updated}' case")
                            propertyEmpty_flag = "false"
                    else:
                        logger.log("Schema Name not present")

                if self.vector_train_type == "F":
                    # Delete the existing data
                    if not schemaName_Updated == 'Document' :
                        if propertyEmpty_flag == "true" :
                            client.schema.delete_class(schemaName_Updated)
                            logger.log(f'\n Schema: "{schemaName_Updated}" against records are deleted ')
                            classes = [c['class'] for c in client.schema.get()['classes']]
                            assert schemaName_Updated not in classes
                            client.schema.create_class(class_obj)
                        else:
                            logger.log(f'\n {schemaName_Updated} has no filter properties. Skipping records deletion.')
                elif self.vector_train_type == "I":
                    # Preserve the schema and existing data
                    logger.log(f"Skipping schema deletion for incremental training of '{schemaName_Updated}'.")
                else:
                    logger.log(f"Invalid vector_train_type ::: '{schemaName_Updated}'.")

                columnnamelist=list(val for val in parsed_json[0])

                num_groups = len(parsed_json[1:]) // self.group_size + (len(parsed_json[1:]) % self.group_size > 0)
                logger.log(f"num_groups ::: {type(num_groups)} {num_groups}")

                groups = []
                for i in range(num_groups):
                    start_idx = i * self.group_size
                    end_idx = (i + 1) * self.group_size if i < num_groups - 1 else len(parsed_json) 
                    logger.log(f"\n Group '{i}' \t start_idx::: {start_idx} \t end_idx ::: {end_idx}")
                    group_indices = list(range(start_idx, end_idx))
                    groups.append(group_indices)
                    # logger.log(f"\n\nGroup '{i}' length::: {len(groups)}\n Total number of rows received:::  {groups}\n\n")
                
                logger.log(f'\n Number of Groups Created {len(groups)}', "0")

                logger.log(f'\n Print Weaviate Traning start time: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', "0")
                
                for val in groups:
                    with client.batch.configure(batch_size=1000) as batch:
                        logger.log(f'\n Print Weaviate Group Traning start time: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', "0")    
                        weaviate_id_list=[]
                        skipped_count = 0
                        for indexvalue in val:        
                            if not indexvalue == 0:
                                properties = {
                                    "answer": parsed_json[indexvalue][columnnamelist[0]],
                                    "description": parsed_json[indexvalue][columnnamelist[1]]
                                }
                                item_code = parsed_json[indexvalue][columnnamelist[0]]
                                if len(columnnamelist) > 2:
                                    for j,valuedata in enumerate(columnnamelist[2:]):
                                        if valuedata not in parsed_json[indexvalue]:
                                            parsed_json[indexvalue][valuedata]=""
                                        else:
                                            properties[valuedata] = parsed_json[indexvalue][valuedata]
                                
                                #Append a unique Id as well to avoid duplicate data.
                                raw_key = f"{properties['answer']}::{properties['description']}"#Creating a raw_key for eg. 0000045967::IODEX 8GM
                                logger.log(f"raw_key Id is {raw_key}")
                                unique_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, hashlib.md5(raw_key.encode()).hexdigest()))
                                logger.log(f"Unique Id is {unique_id}")
                                
                                weaviate_id = None

                                if not client.data_object.exists(unique_id, class_name=schemaName_Updated):
                                    weaviate_id = client.batch.add_data_object(
                                        properties, 
                                        schemaName_Updated,
                                        uuid=unique_id)
                                    if weaviate_id:
                                        weaviate_id_list.append(weaviate_id)
                                    else:
                                        logger.log(f"Insertion FAILED for: {item_code}", "0")
                                else:
                                    logger.log(f"Duplicate record skipped: {raw_key}", "0")
                                    skipped_count += 1
                            else:
                                weaviate_id_list.append('-')

                        logger.log(f"Inserted into Weaviate: {len(weaviate_id_list)}", "0")
                        logger.log(f"Duplicate records skipped: {skipped_count}", "0")
                        logger.log(f"Total records processed: {len(val)}", "0")

                        if len(weaviate_id_list) + skipped_count != len(val):
                            return f"Vector has not trained properly, in training found count mismatch."

                        logger.log(f'\n Print Weaviate Group Traning END time: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', "0")    
                        flag = "SUCCESSFUL"

            if flag == "SUCCESSFUL":
                result = f" {(schemaName_Updated if self.schema_name != 'Document' else self.docType_SchemaName)} Index Creation SUCCESSFUL. "
            else :
                result = f" {(schemaName_Updated if self.schema_name != 'Document' else self.docType_SchemaName)} Index Creation FAILED. "
            
            logger.log(f'\n Print Weaviate END time for traning : {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', "0")
            logger.log(f" WEaviate Training final Result::: \n{result}\n ")
            return result
        except Exception as e:
            logger.log(f" {schemaName_Updated} Index Creation FAILED for Enterprise: '{self.enterpriseName}'. ","0")
            logger.log(f"{schemaName_Updated} class trainData() Issue::: \n{e}","0")
            trace = traceback.format_exc()
            descr = str(e)
            errorXml = common.getErrorXml(descr, trace)
            logger.log(f'\n {schemaName_Updated} class trainData() errorXml::: \n{errorXml}', "0")
            raise str(errorXml)
        
    def getLookupData(self ):
        try:
            logger.log(f'\n Print Weaviate start time for getLookupData : {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', "0")
            finalResultJson     =  {}
            id_list             =  []
            queryJson           =  ""
            queryAttributesJson =  None
            schemaClasslist     =  []
            lookupParam_json    =  {}
            finalResponse       =  ""
            descr               =  ""
            id                  =  ""
            inputQuery          =  ""
            documentFilter_list =  []
            operatorValue       =  ""
            limit               =  ""
            final_text_prediction_global = []
            
            weaviate_json =  request.get_data('jsonData', None)
            weaviate_json = json.loads(weaviate_json[9:])
            logger.log(f"\nWeaviate hybrid class getLookupData() weaviate_json:::\t{weaviate_json} \t{type(weaviate_json)}","0")

            if "openAI_apiKey" in weaviate_json and weaviate_json["openAI_apiKey"] != None:
                self.openAI_apiKey = weaviate_json["openAI_apiKey"]          
                logger.log(f"\nWeaviate hybrid class LookUpData() openAI_apiKey:::\t{self.openAI_apiKey} \t{type(self.openAI_apiKey)}","0")              
            
            if "queryJson" in weaviate_json and weaviate_json["queryJson"] != None:
                queryJson = weaviate_json["queryJson"]
            elif "queryList" in weaviate_json and weaviate_json["queryList"] != None:
                queryJson = weaviate_json["queryList"]   
                logger.log(f"\nWeaviate hybrid class LookUpData() queryJson:::\t{queryJson} has length ::: '{len(queryJson)}'\t{type(queryJson)}","0")
            
            if "queryAttributesJson" in weaviate_json and weaviate_json["queryAttributesJson"] != None:
                queryAttributesJson = weaviate_json["queryAttributesJson"]
                logger.log(f"\nWeaviate hybrid class LookUpData() queryAttributesJson:::\t{queryAttributesJson} \t{type(queryAttributesJson)}","0")

            if "index_name" in weaviate_json and weaviate_json["index_name"] != None:
                self.schema_name = (weaviate_json["index_name"]).capitalize().replace("-","_")
                logger.log(f"\nWeaviate hybrid class LookUpData() schema_name:::\t{self.schema_name} \t{type(self.schema_name)}","0")
            
            if "enterprise" in weaviate_json and weaviate_json["enterprise"] != None:
                self.enterpriseName = weaviate_json["enterprise"]
                logger.log(f"\nWeaviate hybrid class LookUpData() enterprise:::\t{self.enterpriseName} \t{type(self.enterpriseName)}","0")

            environment_weaviate_server_url = os.getenv('weaviate_server_url')
            logger.log(f"environment_weaviate_server_url ::: [{environment_weaviate_server_url}]")

            if environment_weaviate_server_url != None and environment_weaviate_server_url != '':
                self.server_url = environment_weaviate_server_url
                logger.log(f"\nWeaviate Hybrid class LookUpData server_url:::\t{self.server_url} \t{type(self.server_url)}","0")
            else:
                if "server_url" in weaviate_json and weaviate_json["server_url"] != None:
                    self.server_url = weaviate_json["server_url"]
                    logger.log(f"\nWeaviate Hybrid class LookUpData server_url:::\t{self.server_url} \t{type(self.server_url)}","0")

            if "entity_type" in weaviate_json and weaviate_json["entity_type"] != None:
                self.entity_type = (weaviate_json['entity_type']).lower()
                logger.log(f'\n Tranin Weaviate vector entity_type veraible value :::  \t{self.entity_type} \t{type(self.entity_type)}')

            if "modelScope" in weaviate_json and weaviate_json["modelScope"] != None:
                self.modelScope = weaviate_json["modelScope"]
                logger.log(f"\nWeaviate hybrid class LookUpData() modelScope:::\t{self.modelScope} \t{type(self.modelScope)}","0")

            if "lookup_parameter" in weaviate_json and weaviate_json["lookup_parameter"] != None:
                if (type(weaviate_json["lookup_parameter"])  == str) and (len(weaviate_json["lookup_parameter"]) > 0) :
                    lookupParam_json = json.loads(weaviate_json["lookup_parameter"])
                else :
                    lookupParam_json = weaviate_json["lookup_parameter"]

                if lookupParam_json != "":
                    if len(lookupParam_json["alpha"]) > 0 and type(lookupParam_json["alpha"]) == str : 
                        self.alphaValue = float(lookupParam_json["alpha"])
                    else:
                        logger.log(f"\n   Alpha value EMPTY case      \n","0") 
                else:
                    logger.log(f"lookupParam_json Blank CASE:::: {lookupParam_json} ")
                logger.log(f"\nWeaviate hybrid class LookUpData() alphaValue:::\t{self.alphaValue} \t{type(self.alphaValue)}\n","0")
            
            if self.schema_name != "Document" or self.schema_name == "document":
                self.alphaValue = self.alphaValue if self.alphaValue != "" else 0.6
            else:
                self.alphaValue = self.alphaValue if self.alphaValue != "" else 1

            logger.log(f"\n\n Final alphaValue ::: \t{self.alphaValue}\n")

            if "lookup_type" in weaviate_json and weaviate_json["lookup_type"] != None:
                self.lookup_type = weaviate_json["lookup_type"]
                logger.log(f"self.lookup_type  :::: {self.lookup_type} ")

            if "meta_data_def" in weaviate_json and weaviate_json["meta_data_def"] != None:
                self.metadata_def = json.loads(weaviate_json["meta_data_def"]) if type(weaviate_json["meta_data_def"]) == str else weaviate_json["meta_data_def"]
                logger.log(f"\nWeaviate Hybrid class TrainData meta_data_def libe 340:::\t{self.metadata_def} \t{type(self.metadata_def)}")
            
            if "limit" in weaviate_json and weaviate_json["limit"] != None:
                limit = weaviate_json["limit"]
                logger.log(f"\nWeaviate hybrid class LookUpData() limit :::\t{limit} \t{type(limit)}","0")

            if len(self.metadata_def) != 0:
                for eachJsonObj in self.metadata_def["Details"]:
                    logger.log(f"eachJsonObj ::: {eachJsonObj}")
                    docFilter_json = {}
                    
                    if "operator" in eachJsonObj and eachJsonObj["operator"] != None :
                        operatorValue = eachJsonObj["operator"] if eachJsonObj["operator"] != "" else "And"
                        logger.log(f"operatorValue ::: {operatorValue}")
                        continue

                    if "name" in eachJsonObj and eachJsonObj["name"] != None :
                        docFilter_json["name"] = eachJsonObj["name"] 
                        logger.log(f"docFilter_json ::: {docFilter_json}")

                    if "value" in eachJsonObj and eachJsonObj["value"] != None :
                        docFilter_json["value"] = eachJsonObj["value"] 
                        logger.log(f"docFilter_json ::: {docFilter_json}")
    
                    if "innerOperator" in eachJsonObj and eachJsonObj["innerOperator"] != None :
                        docFilter_json["operator"] = eachJsonObj["innerOperator"]  
                        logger.log(f"docFilter_json ::: {docFilter_json}") 
                    
                    documentFilter_list.append(docFilter_json)
                logger.log(f"documentFilter_list ::: {documentFilter_list}") 

            # started here for adding condition for global case [30-08-2024]- Akash Singh
            client = weaviate.Client(self.server_url,additional_headers={"X-OpenAI-Api-Key": self.openAI_apiKey})
            logger.log(f'Connection is establish : {client.is_ready()}')

            if self.schema_name == 'document' or self.schema_name == "Document":
                logger.log("line no 373")
                doc_TrainingPrediction =  Document_TrainingPrediction()
                if self.lookup_type    == "S" :
                    logger.log("Lookup type 'SEARCH' CASE ")
                    finalResponse      =  doc_TrainingPrediction.documentLookup_search(client ,queryJson, self.alphaValue, self.enterpriseName, self.schema_name, self.modelScope)
                elif self.lookup_type  == "Q" :
                    logger.log("Lookup type 'QUESTION-ANSWERING' CASE ")
                    finalResponse      =  doc_TrainingPrediction.documentLookup_getAnswer(client , queryJson, self.alphaValue, self.enterpriseName, self.schema_name, self.modelScope, self.openAI_apiKey, operatorValue, documentFilter_list, limit)
                                                                                        
                else:
                    logger.log(f'\n\n Unexpected lookup_type recieved ::: \t{self.lookup_type}\n')

                finalResult = str(finalResponse)
                return finalResponse

            schemaName_Updated = self.enterpriseName + "_" + self.schema_name + "_" + self.entity_type
            logger.log(f'\nschemaName_Updated ::: \t{schemaName_Updated}')
            schemaClasslist = [i['class'] for i in client.schema.get()["classes"]]  
            

            if self.modelScope == "G":
                logger.log("GLOBAL Case")
                group_of_schema_list = [schema for schema in schemaClasslist if schema.startswith(self.enterpriseName)]

                for schemaName_Updated in group_of_schema_list:
                    for key in queryJson:
                        logger.log(f"key:: {key}")
                        if len(queryJson[key]) > 0 and queryJson[key].strip() != "":

                            inputQuery  = queryJson[key].upper().replace("N/A","").replace("."," ").replace(","," ").replace("-"," ").replace("_"," ")

                            if queryAttributesJson and key in queryAttributesJson:
                                response    = (
                                        client.query
                                        .get(schemaName_Updated, ["description", "answer", "phy_attrib_1", "phy_attrib_2", "phy_attrib_3", "phy_attrib_4"]) 
                                        .with_hybrid(
                                                        alpha       =  self.alphaValue ,
                                                        query       =  inputQuery.strip() ,
                                                        fusion_type =  HybridFusion.RELATIVE_SCORE
                                                    )
                                        .with_additional('score')
                                        .with_limit(20)
                                        .do()
                                        )
                            else:
                                response = (
                                    client.query
                                    .get(schemaName_Updated, ["description", "answer"]) 
                                    .with_hybrid(
                                                    alpha       =  self.alphaValue ,
                                                    query       =  inputQuery.strip() ,
                                                    fusion_type =  HybridFusion.RELATIVE_SCORE
                                                )
                                    .with_additional('score')
                                    .with_limit(20)
                                    .do()
                                    )
                            logger.log(f"Input ::: {inputQuery} \n Responsee:::: {response}")

                    if response != {}:

                        if 'data' in response.keys() :

                            response_List = response['data']['Get'][schemaName_Updated] 

                            if response_List:

                                logger.log(f'\n START time for responseDescription-InputQuery matching  : {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')

                                if queryAttributesJson and key in queryAttributesJson:
                                    logger.log(f"Inside queryAttributesJson")
                                    logger.log(f"queryAttributesJson ::: {queryAttributesJson[key]}")

                                    finalResultJson[key]= {"material_description": response_List[0]['description'] , "id": response_List[0]['answer'] } if len(response_List) > 0 else {}

                                    itemMatchedIndex = 0
                                    isItemMatched = False
                                    matchIndex = 0
                                    topScore = 0
                                    max_weight = 0
                                    max_weight_index = 0

                                    for index in range(len(response_List)):
                                        Score = response_List[index]['_additional']['score']
                                        if index == 0:
                                            topScore = float(Score)
                                        
                                        diffScore = float(topScore) - float(Score)

                                        logger.log(f"Score difference ::: {diffScore}")
                                        logger.log(f"Index ::: {index}")
                                        if diffScore > float(0.30) and index >= 10:
                                            logger.log(f"For loop breaked")
                                            break

                                        descr               = response_List[index]['description']
                                        descr               = descr.upper().replace("N/A","").replace("."," ").replace(","," ").replace("-"," ").replace("_"," ")
                                        item_code           = str(response_List[index]['answer']).split('__')[0].strip() 

                                        descr_replaced      =  descr.replace(" ", "") 
                                        inputQuery_replaced =  inputQuery.replace(" ", "")

                                        if descr_replaced == inputQuery_replaced:
                                            logger.log(f"\n Input::: '{inputQuery_replaced}' MATCHEDD with description ::: '{descr_replaced}'\n")
                                            isItemMatched = True
                                            itemMatchedIndex = index
                                            matchIndex = index
                                        else:
                                            logger.log(f"\n Input '{inputQuery_replaced}' not matched with returned response description '{descr_replaced}'\n ")

                                        weight = 0

                                        phy_attrib_1        =  response_List[index]['phy_attrib_1']
                                        phy_attrib_2        =  response_List[index]['phy_attrib_2']
                                        phy_attrib_3        =  response_List[index]['phy_attrib_3']
                                        phy_attrib_4        =  response_List[index]['phy_attrib_4']

                                        extract_phy_attrib_1 = queryAttributesJson[key]['extract_phy_attrib_1']
                                        extract_phy_attrib_2 = queryAttributesJson[key]['extract_phy_attrib_2']
                                        extract_phy_attrib_3 = queryAttributesJson[key]['extract_phy_attrib_3']
                                        extract_phy_attrib_4 = queryAttributesJson[key]['extract_phy_attrib_4']

                                        if self.safe_equals(phy_attrib_1, extract_phy_attrib_1):
                                            weight += 5
                                        if self.safe_equals(phy_attrib_2, extract_phy_attrib_2):
                                            weight += 3
                                        if self.safe_equals(phy_attrib_3, extract_phy_attrib_3):
                                            weight += 1
                                        if self.safe_equals(phy_attrib_4, extract_phy_attrib_4):
                                            weight += 1

                                        if weight > max_weight:
                                            max_weight = weight
                                            max_weight_index = index

                                    item_index = 0
                                    if isItemMatched == False:
                                        item_index = max_weight_index
                                    else:
                                        item_index = matchIndex

                                    item_code = str(response_List[item_index]['answer']).split('__')[0].strip() 
                                    item_descr = str(response_List[item_index]['description']).split('__')[0].strip()
                                    
                                    finalResultJson[key]    =  {"material_description": item_descr, "id": item_code } 
                                else:
                                    logger.log(f"Outside queryAttributesJson")
                                    finalResultJson[key]= {"material_description": response_List[0]['description'] , "id": response_List[0]['answer'] } if len(response_List) > 0 else {}

                                    for index in range(len(response_List)):
                                        descr               =  response_List[index]['description']
                                        id                  =  response_List[index]['answer']
                                        descr_replaced      =  descr.replace(" ", "") 
                                        inputQuery_replaced =  inputQuery.replace(" ", "")

                                        if descr_replaced == inputQuery_replaced:
                                            logger.log(f"\n Input::: '{inputQuery_replaced}' MATCHEDD with description ::: '{descr_replaced}' \n")
                                            finalResultJson[key]    =  {"material_description": descr, "id": id } 
                                            break
                                        else:
                                            logger.log(f"\n Input '{inputQuery_replaced}' not matched with returned response description '{descr_replaced} '\n ")  

                                logger.log(f'\n END time for responseDescription-InputQuery matching  : {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
                        else:
                            logger.log("No records found.")
                            finalResultJson = {}

                    logger.log(f"\n\n FinalResultJson line 390:::{finalResultJson} has length ::: '{len(finalResultJson)}' \t {type(finalResultJson)}\n")
                    if len(finalResultJson) != 0:
                        final_text_prediction_global.append(str(finalResultJson))
                        finalResult = final_text_prediction_global
                
            else:
                logger.log("ENTERPRISE Case")
                if schemaName_Updated in schemaClasslist:
                    for key in queryJson:
                        logger.log(f"key:: {key}")
                        if len(queryJson[key]) > 0 and queryJson[key].strip() != "":

                            inputQuery  = queryJson[key].upper().replace("N/A","").replace("."," ").replace(","," ").replace("-"," ").replace("_"," ")

                            if queryAttributesJson and key in queryAttributesJson:
                                response    = (
                                    client.query
                                    .get(schemaName_Updated, ["description", "answer", "phy_attrib_1", "phy_attrib_2", "phy_attrib_3", "phy_attrib_4"]) 
                                    .with_hybrid(
                                                    alpha       =  self.alphaValue ,
                                                    query       =  inputQuery.strip() ,
                                                    fusion_type =  HybridFusion.RELATIVE_SCORE
                                                )
                                    .with_additional('score')
                                    .with_limit(20)
                                    .do()
                                    )
                            else:
                                response    = (
                                    client.query
                                    .get(schemaName_Updated, ["description", "answer"]) 
                                    .with_hybrid(
                                                    alpha       =  self.alphaValue ,
                                                    query       =  inputQuery.strip() ,
                                                    fusion_type =  HybridFusion.RELATIVE_SCORE
                                                )
                                    .with_additional('score')
                                    .with_limit(20)
                                    .do()
                                    )
                            logger.log(f"Input ::: {inputQuery} \n Responsee:::: {response}")

                            if response != {}:

                                if 'data' in response.keys() :

                                    response_List = response['data']['Get'][schemaName_Updated] 

                                    if response_List:

                                        logger.log(f'\n START time for responseDescription-InputQuery matching  : {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')

                                        if queryAttributesJson and key in queryAttributesJson:
                                            logger.log(f"Inside queryAttributesJson")
                                            logger.log(f"queryAttributesJson ::: {queryAttributesJson[key]}")

                                            finalResultJson[key]= {"material_description": response_List[0]['description'] , "id": response_List[0]['answer'] } if len(response_List) > 0 else {}
                                            logger.log(f'\n START time for responseDescription-InputQuery matching  : {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')

                                            itemMatchedIndex = 0
                                            isItemMatched = False
                                            matchIndex = 0
                                            topScore = 0
                                            max_weight = 0
                                            max_weight_index = 0

                                            for index in range(len(response_List)):
                                                Score = response_List[index]['_additional']['score']
                                                if index == 0:
                                                    topScore = float(Score)
                                                
                                                diffScore = float(topScore) - float(Score)

                                                logger.log(f"Score difference ::: {diffScore}")
                                                logger.log(f"Index ::: {index}")
                                                if diffScore > float(0.30) and index >= 10:
                                                    logger.log(f"For loop breaked")
                                                    break

                                                descr               = response_List[index]['description']
                                                descr               = descr.upper().replace("N/A","").replace("."," ").replace(","," ").replace("-"," ").replace("_"," ")
                                                item_code           = str(response_List[index]['answer']).split('__')[0].strip() 

                                                descr_replaced      =  descr.replace(" ", "") 
                                                inputQuery_replaced =  inputQuery.replace(" ", "")

                                                if descr_replaced == inputQuery_replaced:
                                                    logger.log(f"\n Input::: '{inputQuery_replaced}' MATCHEDD with description ::: '{descr_replaced}'\n")
                                                    isItemMatched = True
                                                    itemMatchedIndex = index
                                                    matchIndex = index
                                                else:
                                                    logger.log(f"\n Input '{inputQuery_replaced}' not matched with returned response description '{descr_replaced}'\n ")
                                                    
                                                weight = 0

                                                phy_attrib_1        =  response_List[index]['phy_attrib_1']
                                                phy_attrib_2        =  response_List[index]['phy_attrib_2']
                                                phy_attrib_3        =  response_List[index]['phy_attrib_3']
                                                phy_attrib_4        =  response_List[index]['phy_attrib_4']

                                                extract_phy_attrib_1 = queryAttributesJson[key]['extract_phy_attrib_1']
                                                extract_phy_attrib_2 = queryAttributesJson[key]['extract_phy_attrib_2']
                                                extract_phy_attrib_3 = queryAttributesJson[key]['extract_phy_attrib_3']
                                                extract_phy_attrib_4 = queryAttributesJson[key]['extract_phy_attrib_4']

                                                if self.safe_equals(phy_attrib_1, extract_phy_attrib_1):
                                                    weight += 5
                                                if self.safe_equals(phy_attrib_2, extract_phy_attrib_2):
                                                    weight += 3
                                                if self.safe_equals(phy_attrib_3, extract_phy_attrib_3):
                                                    weight += 1
                                                if self.safe_equals(phy_attrib_4, extract_phy_attrib_4):
                                                    weight += 1

                                                if weight > max_weight:
                                                    max_weight = weight
                                                    max_weight_index = index

                                            logger.log(f'\n END time for responseDescription-InputQuery matching  : {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')  

                                            item_index = 0
                                            if isItemMatched == False:
                                                item_index = max_weight_index
                                            else:
                                                item_index = matchIndex

                                            item_code = str(response_List[item_index]['answer']).split('__')[0].strip() 
                                            item_descr = str(response_List[item_index]['description']).split('__')[0].strip()
                                            
                                            finalResultJson[key]    =  {"material_description": item_descr, "id": item_code } 
                                        else:
                                            logger.log(f"Outside queryAttributesJson")
                                            finalResultJson[key]= {"material_description": response_List[0]['description'] , "id": response_List[0]['answer'] } if len(response_List) > 0 else {}

                                            for index in range(len(response_List)):
                                                descr               =  response_List[index]['description']
                                                id                  =  response_List[index]['answer']
                                                descr_replaced      =  descr.replace(" ", "") 
                                                inputQuery_replaced =  inputQuery.replace(" ", "")

                                                if descr_replaced == inputQuery_replaced:
                                                    logger.log(f"\n Input::: '{inputQuery_replaced}' MATCHEDD with description ::: '{descr_replaced}' \n")
                                                    finalResultJson[key]    =  {"material_description": descr, "id": id } 
                                                    break
                                                else:
                                                    logger.log(f"\n Input '{inputQuery_replaced}' not matched with returned response description '{descr_replaced} '\n ") 

                                        logger.log(f'\n END time for responseDescription-InputQuery matching  : {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
                                        
                    finalResult = str(finalResultJson)
                else:
                    logger.log(f"Weaviate class getLookUP()::: \nIndex_Name: {schemaName_Updated} not found in weaviate_IndexList: {schemaClasslist}","0")
                    message = f"Index_Name: '{schemaName_Updated}' not found in weaviate_IndexList. \nAvailable IndexList: {schemaClasslist}"
                    errorXml = common.getErrorXml(message, "")
                    raise Exception(errorXml)

                logger.log(f'\n Print Weaviate END time for getLookupData : {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', "0")
                logger.log(f'\n FINAL Result :::{finalResult}', "0")

            logger.log(f"353 Final result:::{finalResult}\n")
            return finalResult
        
        except Exception as e:
            logger.log(f"Weaviate Hybrid class getLookUP() Issue::: \n{e}","0")
            trace = traceback.format_exc()
            descr = str(e)
            errorXml = common.getErrorXml(descr, trace)
            logger.log(f'\n Weaviate hybrid class getLookUP() errorXml::: \n{errorXml}', "0")
            raise str(errorXml)
        # ended here for adding condition for global case [30-08-2024]- Akash Singh

    def safe_equals(self, phy_attrib, extract_phy_attrib):
        if pd.isna(phy_attrib) or phy_attrib is None or str(phy_attrib).strip().lower() == 'nan':
            return False
        if pd.isna(extract_phy_attrib) or extract_phy_attrib is None or str(extract_phy_attrib).strip().lower() == 'nan':
            return False

        phy_attrib_str = str(phy_attrib).strip()
        extract_phy_attrib_str = str(extract_phy_attrib).strip()

        phy_attrib_str  = phy_attrib_str.upper().replace("N/A","").replace("."," ").replace(","," ").replace("-"," ").replace("_"," ")
        extract_phy_attrib_str  = extract_phy_attrib_str.upper().replace("N/A","").replace("."," ").replace(","," ").replace("-"," ").replace("_"," ")

        try:
            if float(phy_attrib) == float(extract_phy_attrib):
                return True
        except (ValueError, TypeError):
            pass
        return phy_attrib_str == extract_phy_attrib_str

   