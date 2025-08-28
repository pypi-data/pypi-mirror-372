import weaviate
import base64
import loggerutility as logger
import traceback
import commonutility as common
from DatabaseConnectionUtility import Oracle, SAPHANA, InMemory, Dremio, MySql, ExcelFile, Postgress, MSSQLServer
import json
from flask import request
import os

class Image_TrainingPrediction :

    modelParameter          =  ""
    ref_Series              =  ""
    attributes              =  ""
    additional_properties   =  []
    dbDetails               =  None
    flag                    =  ""
    modelScope              =  "E"
    group_size              =  10000
    entity_type             =  ""
    schema_name             =  ""
    server_url              =  ""
    openAI_apiKey           =  ""
    enterpriseName          =  ""
    image_blob_data         =  "" 

    def imageTraining(self,weaviate_jsondata):

        # Added by YashS on [ 30-08-24 ] for train weaviate image model through [START]
        domData = request.get_data('jsonData', None)
        domData = domData[9:]
        calculationData = json.loads(domData)
        logger.log(f'\n Inside getQueryData jsonData image:\n\n {calculationData}\n\n', "0")

        if "modelParameter" in weaviate_jsondata and weaviate_jsondata["modelParameter"] != None:
            self.modelParameter = json.loads(weaviate_jsondata['modelParameter'])

        if "ref_Series" in self.modelParameter and (self.modelParameter["ref_Series"]).strip() != None:
            self.ref_Series = (self.modelParameter["ref_Series"]).capitalize().replace("-","_").strip()
            logger.log(f"\nWeaviate Hybrid class Refference Series:::\t{self.ref_Series} \t{type(self.ref_Series)}","0")

        if "document_type" in self.modelParameter and (self.modelParameter["document_type"]).strip() != None:
            self.document_type = (self.modelParameter["document_type"]).capitalize().replace("-","_").strip()
            logger.log(f"\nWeaviate Hybrid class Document Type:::\t{self.document_type} \t{type(self.document_type)}","0")

        if "attributes" in self.modelParameter and (self.modelParameter["attributes"]).strip() != None:
            self.attributes = (self.modelParameter["attributes"]).capitalize().replace("-","_").strip()
            logger.log(f"\nWeaviate Hybrid class Attributes:::\t{self.attributes} \t{type(self.attributes)}","0")

        if "entity_type" in weaviate_jsondata and weaviate_jsondata["entity_type"] != None:
            self.entity_type = (weaviate_jsondata['entity_type']).lower().strip()
            logger.log(f'\n Tranin Weaviate vector entity_type veraible value :::  \t{self.entity_type} \t{type(self.entity_type)}')

        if "enterprise" in weaviate_jsondata and weaviate_jsondata["enterprise"] != None:
            self.enterpriseName = weaviate_jsondata["enterprise"]
            logger.log(f"\nWeaviate Hybrid class TrainData enterprise:::\t{self.enterpriseName} \t{type(self.enterpriseName)}","0")

        if "index_name" in self.modelParameter and (self.modelParameter["index_name"]).strip() != None:
            self.schema_name = (self.modelParameter["index_name"]).capitalize().replace("-","_").strip()
            logger.log(f"\ntrain_Weaviate Hybrid index_name:::\t{self.schema_name} \t{type(self.schema_name)}","0")

        elif "index_name" in weaviate_jsondata and (weaviate_jsondata["index_name"]).strip() != None:
            self.schema_name = (weaviate_jsondata["index_name"]).capitalize().replace("-","_").strip()
            logger.log(f"\ntrain_Weaviate Hybrid index_name:::\t{self.schema_name} \t{type(self.schema_name)}","0")
        
        environment_weaviate_server_url = os.getenv('weaviate_server_url')
        logger.log(f"environment_weaviate_server_url ::: [{environment_weaviate_server_url}]")

        if environment_weaviate_server_url != None and environment_weaviate_server_url != '':
            self.server_url = environment_weaviate_server_url
            logger.log(f"\nWeaviate Hybrid class LookUpData server_url:::\t{self.server_url} \t{type(self.server_url)}","0")
        else:
            if "server_url" in weaviate_jsondata and weaviate_jsondata["server_url"] != None:
                self.server_url = weaviate_jsondata["server_url"]
                logger.log(f"\nWeaviate Hybrid class TrainData server_url:::\t{self.server_url} \t{type(self.server_url)}","0")

        if "openAI_apiKey" in weaviate_jsondata and weaviate_jsondata["openAI_apiKey"] != None:
            self.openAI_apiKey = weaviate_jsondata["openAI_apiKey"]           
            logger.log(f"\ntrain_Weaviate Hybrid openAI_apiKey:::\t{self.openAI_apiKey} \t{type(self.openAI_apiKey)}","0")
            
        if "modelJsonData" in weaviate_jsondata and weaviate_jsondata["modelJsonData"] != None:
            self.dfJson = weaviate_jsondata["modelJsonData"]
        elif "dfJson" in weaviate_jsondata and weaviate_jsondata["dfJson"] != None:
            self.dfJson = weaviate_jsondata["dfJson"]
        logger.log(f"\ntrain_Weaviate Hybrid dfJson:::\t{self.dfJson} \t{type(self.dfJson)}","0")

        if "dbDetails" in self.modelParameter and (self.modelParameter["dbDetails"]).strip() != None:
            self.dbDetails = (self.modelParameter["dbDetails"]).capitalize().replace("-","_").strip()
            logger.log(f"\ntrain_Weaviate Hybrid index_name:::\t{self.dbDetails} \t{type(self.dbDetails)}","0")

        client = weaviate.Client(self.server_url, additional_headers={"X-OpenAI-Api-Key": self.openAI_apiKey})

        self.additional_properties = self.attributes.split(',')
        schemaName_Updated = self.enterpriseName + "_" + self.schema_name + "_" + self.entity_type
        logger.log(f'\nschemaName_Updated ::: \t{schemaName_Updated}')

        schema = {
            "classes": [
                    {
                        "class": schemaName_Updated,
                        "description": f"Images of different {self.schema_name}",
                        "moduleConfig": {
                            "img2vec-neural": {
                                "imageFields": [
                                    "image"
                                ]
                            }
                        },
                        "vectorIndexType": "hnsw",
                        "vectorizer": "img2vec-neural",
                        "properties": [
                            {
                                "name": "image",
                                "dataType": ["blob"],
                                "description": "image",
                            },
                        ]
                    }
                ]
            }
        
        if self.additional_properties != ['']:
            for prop in self.additional_properties:
                logger.log(f"prop::: {prop}")
                schema['classes'][0]['properties'].append({
                    "name": prop,
                    "dataType": ["string"],  
                    "description": f"Description of {prop}",
                })
        logger.log(f"schema::; {schema}")

        if schemaName_Updated in [i['class'] for i in client.schema.get()['classes']]:
            client.schema.delete_class(schemaName_Updated)
            client.schema.create(schema)
        else:
            client.schema.create(schema)

        if type(self.dfJson) == str :
            parsed_json = json.loads(self.dfJson)
        else:
            parsed_json = self.dfJson
        
        self.set_up_batch(client)
        final_data = self.get_Image_Dataset( parsed_json, self.dbDetails, self.ref_Series )

        if final_data == []:
            logger.log('Images not found')
            self.flag = "UNSUCCESSFUL"

        self.train_model(client, schemaName_Updated, final_data)

        if self.flag == "SUCCESSFUL":
            logger.log('Model created')
            result = f" {schemaName_Updated} Index Creation SUCCESSFUL."
        else :
            result = f" {schemaName_Updated} Index Creation FAILED."

        return result
    
        # Added by YashS on [ 30-08-24 ] for train weaviate image model through [END]

    # started here for adding condition for global case [30-08-2024]- Akash Singh
    def Prediction_Image(self,return_row_count=10):
    
        weaviate_json =  request.get_data('jsonData', None)
        weaviate_json = json.loads(weaviate_json[9:])
        logger.log(f"\nWeaviate hybrid class getLookupData() weaviate_json:::\t{weaviate_json} \t{type(weaviate_json)}","0")

        encoded_string = []
        if "Doc_Type" in weaviate_json and weaviate_json["Doc_Type"] != None:
            self.Doc_Type = weaviate_json["Doc_Type"]
            logger.log(f"self.Doc_Type  :::: {self.Doc_Type} ")

        if "Ref_Series" in weaviate_json and weaviate_json["Ref_Series"] != None:
            self.Ref_Series = weaviate_json["Ref_Series"]
            logger.log(f"self.Ref_Series  :::: {self.Ref_Series} ")

        if "Attributes" in weaviate_json and weaviate_json["Attributes"] != None:
            self.Attributes = weaviate_json["Attributes"]
            logger.log(f"self.Attributes  :::: {self.Attributes} ")

        if "Train_Type" in weaviate_json and weaviate_json["Train_Type"] != None:
            self.Train_Type = weaviate_json["Train_Type"]
            logger.log(f"self.Train_Type  :::: {self.Train_Type} ")

        if "image_data" in weaviate_json and weaviate_json["image_data"] != None:
            self.image_data = weaviate_json["image_data"]
            logger.log(f"self.image_data  :::: {self.image_data} ")

        if "return_row_count" in weaviate_json and weaviate_json["return_row_count"] != None:
            self.return_row_count = weaviate_json["return_row_count"]
            logger.log(f"self.return_row_count  :::: {self.return_row_count} ")

        if "entity_type" in weaviate_json and weaviate_json["entity_type"] != None:
            self.entity_type = (weaviate_json['entity_type']).lower()
            logger.log(f'\n Tranin Weaviate vector entity_type veraible value :::  \t{self.entity_type} \t{type(self.entity_type)}')

        if "enterprise" in weaviate_json and weaviate_json["enterprise"] != None:
            self.enterpriseName = weaviate_json["enterprise"]
            logger.log(f"\nWeaviate Hybrid class TrainData enterprise:::\t{self.enterpriseName} \t{type(self.enterpriseName)}","0")

        if "index_name" in weaviate_json and weaviate_json["index_name"] != None:
            self.schema_name = weaviate_json["index_name"]
            logger.log(f"\nWeaviate Hybrid class TrainData index_name:::\t{self.schema_name} \t{type(self.enterpriseName)}","0")

        if "modelScope" in weaviate_json and weaviate_json["modelScope"] != None:
            self.modelScope = weaviate_json["modelScope"]
            logger.log(f"\nWeaviate hybrid class LookUpData() modelScope:::\t{self.modelScope} \t{type(self.modelScope)}","0")

        if "image_blob_data" in weaviate_json and weaviate_json["image_blob_data"] != None:
            self.image_blob_data = weaviate_json["image_blob_data"]
            logger.log(f"\nWeaviate hybrid class LookUpData() modelScope:::\t{self.image_blob_data} \t{type(self.image_blob_data)}","0")
        
        client = weaviate.Client(self.server_url, additional_headers={"X-OpenAI-Api-Key": self.openAI_apiKey})
        schemaClasslist = [i['class'] for i in client.schema.get()["classes"]]  

        if isinstance(return_row_count, str):
            try:
                return_row_count = int(return_row_count)
            except ValueError:
                logger.log(f"Invalid return_row_count: '{return_row_count}' is not a valid number. Using default value of 10.")
                return_row_count = 10
        elif not isinstance(return_row_count, int):
            logger.log(f"return_row_count is not a valid integer, using default value of 10.")
            return_row_count = 10

        img_str =self.image_blob_data 
        
        # Perform Weaviate image search with row limit defined by return_row_count
        sourceImage = {"image": img_str}

        if self.modelScope == "G": 
            group_of_schema_list = [schema for schema in schemaClasslist if schema.startswith(self.enterpriseName)]
            logger.log(f"appvis_schemas:: {group_of_schema_list}")
            for schemaName_Updated in group_of_schema_list:
                weaviate_results = client.query.get(
                    schemaName_Updated, ["_additional { certainty distance }", "image"]
                ).with_near_image(
                    sourceImage, encode=False
                ).with_limit(return_row_count).do() 

                # Check if 'data' is in the response and proceed only if it exists
                if 'data' in weaviate_results and "Get" in weaviate_results["data"] and schemaName_Updated in weaviate_results["data"]["Get"]:
                    for image in weaviate_results["data"]["Get"][schemaName_Updated]:
                        # If certainty is above the threshold, store the image filename
                        # if image["_additional"]["certainty"] > 0.85:
                        encoded_string.append(image['image'])
                else:
                    logger.log(f"No results found for schema: {schemaName_Updated} or 'data' key missing in response")
            # Return the list of filenames from all schemas
            logger.log(f"Len of list ::: {len(encoded_string)}")
            return encoded_string
        
        else:
            if self.schema_name in schemaClasslist:
                weaviate_results = client.query.get(
                    self.schema_name, ["_additional { certainty distance }", "image"]
                ).with_near_image(
                    sourceImage, encode=False
                ).with_limit(return_row_count).do()  

                # Check if 'data' is in the response and proceed only if it exists
                if 'data' in weaviate_results and "Get" in weaviate_results["data"] and self.schema_name in weaviate_results["data"]["Get"]:
                    for image in weaviate_results["data"]["Get"][self.schema_name]:
                        # If certainty is above the threshold, store the image filename
                        # if image["_additional"]["certainty"] > 0.85:
                        encoded_string.append(image['image'])
                else:
                    logger.log(f"No results found for schema: {self.schema_name} or 'data' key missing in response")
            else:
                raise Exception("schema name not found please train for image")
            logger.log(f" final encoded_string::: {encoded_string}")
            logger.log(f"Len of list ::: {len(encoded_string)}")
            return encoded_string
        # ended here for adding condition for global case [30-08-2024]- Akash Singh
   
    def get_database_connection(self, dbDetails):
        try:
            klass = globals()[dbDetails['DB_VENDORE']]
            dbObject = klass()
            connection_obj = dbObject.getConnection(dbDetails)
            return connection_obj
        except Exception as e:
            logger.log(f"Error in get_database_connection function: {str(e)}", "1")
            return None
    
    # Added by YashS on [ 30-08-24 ] for train weaviate image model through [START]
    def set_up_batch(self,client):
        client.batch.configure(
            batch_size=100,
            dynamic=True,
            timeout_retries=3,
            callback=None,
        )

    def get_Image_Dataset(self,json_Data,dbDetails,ref_Series):
        try:
            connection_obj = self.get_database_connection(dbDetails)
            if connection_obj:
                logger.log("Database connection established successfully.", "0")

            # Final image dataset list
            final_image_clob_dataset = []
            for data in json_Data[1:]:  # 0th index is blank
                first_value = next(iter(data.values()))
                logger.log(f"Data in for loop first_value: {first_value}\n", "0")   
                # sql = f"select d.doc_object, d.doc_name, d.doc_type, dl.doc_type_attach from doc_contents d join doc_transaction_link dl on d.doc_id = dl.doc_id where dl.ref_ser = '{ref_Series}' and dl.ref_id = '{ref_id}' and ( upper(dl.file_type_attach) = 'PNG' or upper(dl.file_type_attach) = 'JPG' or upper(dl.file_type_attach) = 'JPEG')"
                sql = f"SELECT DC.DOC_OBJECT, DC.DOC_NAME, DC.DOC_TYPE, DL.DOC_TYPE_ATTACH FROM DOC_CONTENTS DC JOIN DOC_TRANSACTION_LINK DL ON DC.DOC_ID = DL.DOC_ID WHERE DL.DOC_TYPE_ATTACH = '{self.document_type}' AND DL.REF_SER = '{ref_Series}' AND DL.REF_ID = '{first_value.strip()}' AND ( UPPER(DL.FILE_TYPE_ATTACH) = 'PNG' OR UPPER(DL.FILE_TYPE_ATTACH) = 'JPG' OR UPPER(DL.FILE_TYPE_ATTACH) = 'JPEG') AND DC.DOC_OBJECT IS NOT NULL"
                logger.log(f"sql::312  {sql}")
                cursor = connection_obj.cursor()
                cursor.execute(sql)
                result_lst = cursor.fetchall()
                logger.log(f"result_lst :::::316\n\n{len(result_lst)}\n\n", "0")

                if result_lst:
                    blob_data = result_lst[0][0] 
                    if blob_data:
                        image_blob_data = blob_data.read() 
                        sub_dict = {}
                        new_dict = {}
                        if self.additional_properties != ['']:
                            for prop in self.additional_properties:
                                prop = prop.lower()
                                new_dict[prop] = data[prop] if data[prop] is not None else ''
                        logger.log(f"new_dict :::: {new_dict}", "0")
                        sub_dict['imageblob'] = image_blob_data
                        sub_dict['attribute'] = new_dict
                        final_image_clob_dataset.append(sub_dict)
            return final_image_clob_dataset

        except Exception as e:
            logger.log(f"Error in fetch_column_details function: {str(e)}", "1")
            trace = traceback.format_exc()
            descr = str(e)
            returnErr = common.getErrorXml(descr, trace)
            logger.log(f'\n Exception ::: {returnErr}', "0")
            return str(returnErr)

    def train_model(self, client, schema,final_list):
        client.batch.configure(batch_size=100)  
        with client.batch as batch:
            for image_list in final_list:

                base64_encoding = base64.b64encode(image_list['imageblob']).decode()                    
                base64_encoding = base64_encoding.replace("\n", "").replace(" ", "")

                data_properties = {
                    "image": base64_encoding,
                }
                if self.additional_properties != ['']:
                    for prop in self.additional_properties:
                        prop = prop.lower()
                        data_properties[prop] = image_list['attribute'][prop]
                batch.add_data_object(data_properties, schema)
                self.flag = "SUCCESSFUL"

    # Added by YashS on [ 30-08-24 ] for train weaviate image model through [END]