import json, os
import pandas as pd
import traceback
import datetime
import loggerutility as logger
import commonutility as common
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.retrievers.weaviate_hybrid_search import WeaviateHybridSearchRetriever
from langchain.schema import Document
from langchain_community.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import DocArrayInMemorySearch
from langchain.indexes import VectorstoreIndexCreator
from langchain_community.embeddings import OpenAIEmbeddings
from .Extract_OCR import Extract_OCR
from pathlib import Path

class Document_TrainingPrediction :

    docType_SchemaName      =  ""
    
    def documentTraining(self,client, parsedJson, documentProperty_dict,enterpriseName,schema_name ):
        logger.log(f"\nparsed Json::: \n{parsedJson}\n\n")
        logger.log(f'Connection is establish : {client.is_ready()}')
        
        self.docType_SchemaName     = enterpriseName + "_" + schema_name 
        retriever                   = ""
        propertyFilter_list         = []
        logger.log(f"self.docType_SchemaName::: {self.docType_SchemaName}")

        if len(documentProperty_dict) != 0 :
            for propertyName, propertyValue in documentProperty_dict.items():
                documentSchema_properties = {}
                documentSchema_properties["name"]       =  propertyName
                documentSchema_properties["dataType"]   =  ["text"]
                propertyFilter_list.append(documentSchema_properties)
            logger.log(f"\n\n propertyFilter_list ::: {propertyFilter_list}\n\n")

            class_obj = {
                            "class"         : self.docType_SchemaName ,
                            "properties"    : propertyFilter_list     ,
                            "vectorizer"    : "text2vec-openai"   
                            }
        else:    
            class_obj = {
                            "class"         : self.docType_SchemaName ,
                            "vectorizer"    : "text2vec-openai"
                            }

        weaviate_IndexRespository = client.schema.get()["classes"]
        schemaClasslist = [i['class'] for i in weaviate_IndexRespository]     
        logger.log(f"schemaClasslist::: {schemaClasslist}")          
        
        if self.docType_SchemaName not in schemaClasslist:
            client.schema.create_class(class_obj)
            logger.log(f"\n Schema: '{self.docType_SchemaName}' not present. Creating New !!!\n ")
            
            weaviate_IndexRespository = client.schema.get()["classes"]      # Updating variable value after new index creation
            schemaClasslist = [i['class'] for i in weaviate_IndexRespository]  # Updating variable value after new index creation
            logger.log(f"\nAvailable schema list::: {schemaClasslist} \n ")

        else:
            logger.log(f"'{self.docType_SchemaName}' already present. Loading Now !!!\n ")
        
        retriever = WeaviateHybridSearchRetriever(
                                                    client      = client,
                                                    index_name  = self.docType_SchemaName,
                                                    text_key    = "text",
                                                    attributes  = [],
                                                    metadata    = {"metadata":"doc_id"},
                                                    create_schema_if_missing=True,
                                                )

        OCRText = list(json.loads(parsedJson["description"]).values()) if type(parsedJson["description"]) == str else list(parsedJson["description"].values())
        logger.log(f"OCRText::: \n{OCRText}\n\n{type(OCRText)} ")

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)  # for txtFileObject
        texts = text_splitter.create_documents(OCRText)
        logger.log(f"texts - First 2 chunks::: \n{texts[:2]}\n Divided Chunks length:::\n{len(texts)} ")

        for i in range(len(texts)):
            texts[i].metadata["doc_id"] = str(parsedJson["id"]) + "__" + str(i)
        logger.log(f"\n\n--- Using Langchain approach --- \n\nTexts - Last 2 Chunks::: {texts[-2:]} {type(texts)}\n\n")

        if len(documentProperty_dict) > 0 :
            logger.log("inside metadata filter condition")
            for eachFilter_Key, eachFilter_Value in documentProperty_dict.items() :
                logger.log(f"\n\neachFilter_Key ::: {eachFilter_Key}\t eachFilter_Value ::: {eachFilter_Value} \n")
                for i in range(len(texts)):
                    texts[i].metadata[eachFilter_Key.lower()]   = str(eachFilter_Value) # + "__" + str(i)
            logger.log(f"\n\n texts ::: {texts}\n\n")
        
        retriever.add_documents(texts)
        logger.log(f"retriever::: {type(retriever)}\n retriever value::: \n{retriever}\n\n")
        if retriever != "":
            message = f"SUCCESSFUL"
        else:
            message = f"UNSUCCESSFUL"
        logger.log(f"Message:::\t Document training {message} for '{self.docType_SchemaName}' ")
        return message
        
    def documentLookup_search(self, client, queryJson, alphaValue, enterpriseName, schema_name, modelScope ):
        id_list             = set()
        chunkResponse_list  = set()
        # started here for adding condition for global case [30-08-2024]- Akash Singh
        if modelScope == "G":
            logger.log("GLOBAL Case")
            schemaClasslist = [i['class'] for i in client.schema.get()["classes"]]  
            group_of_schema_list = [schema for schema in schemaClasslist if schema.startswith(enterpriseName)]
            logger.log(f" Enterprise-wise Schemas List:: {group_of_schema_list}")
                
            return_data = []
            for schemaName_Updated in group_of_schema_list:
                logger.log(f"\n\n Inside group_of_schema_list '{schemaName_Updated}'")
                try:
                    retriever = WeaviateHybridSearchRetriever(
                                                        client      = client,
                                                        index_name  = schemaName_Updated,
                                                        text_key    = "text",
                                                        attributes  = ["doc_id"],
                                                        create_schema_if_missing = True,
                                                        alpha       = alphaValue
                                                    )

                    for key in queryJson:
                        
                        if len(key) > 0 and key.strip() != "":
                            logger.log(f"key::: {key}")
                            response = retriever.get_relevant_documents(key)
                            logger.log(f"\n\nResponse for query '{key}'::: {type(response)}\n{response}\n")

                            if len(response) > 0 :
                                for result in response:
                                    chunkResponse_list.add(result.page_content)
                                    id_list.add(result.metadata['doc_id'])
                                    
                                logger.log(f"\n\nid_list::: \t{id_list}\n\n Chunk Response::: \n{chunkResponse_list}\n\n")

                                id_list = [eachId[ : eachId.find("_")] if "_" in eachId else eachId for eachId in id_list ]
                                logger.log(f"After removing '_' id_list::: \t{id_list} {type(id_list)}")
                                id_list = list(id_list)
                                logger.log(f"After removing duplicates id_list::: \t{id_list} {type(id_list)}")
                                if id_list:
                                    return_data.append(id_list)
                except:
                    logger.log(f"Document Search not supported for the Schema name ::: '{schemaName_Updated}'")
                    continue
            logger.log(f"return_data:: {return_data}")
            return return_data
    
        else:
            logger.log("ENTERPRISE Case")
            schemaName_Updated  = enterpriseName + "_" + schema_name 
            retriever = WeaviateHybridSearchRetriever(
                                                    client      = client,
                                                    index_name  = schemaName_Updated,
                                                    text_key    = "text",
                                                    attributes  = ["doc_id"],
                                                    create_schema_if_missing = True,
                                                    alpha       = alphaValue
                                                )
            for key in queryJson:
                
                if len(key) > 0 and key.strip() != "":
                    logger.log(f"key::: {key}")
                    response = retriever.get_relevant_documents(key)
                    logger.log(f"\n\nResponse for query '{key}'::: {type(response)}\n{response}\n")

                    if len(response) > 0 :
                        for result in response:
                            chunkResponse_list.add(result.page_content)
                            id_list.add(result.metadata['doc_id'])
                            
                        logger.log(f"\n\nid_list::: \t{id_list}\n\n Chunk Response::: \n{chunkResponse_list}\n\n")

                        id_list = [eachId[ : eachId.find("_")] if "_" in eachId else eachId for eachId in id_list ]
                        logger.log(f"After removing '_' id_list::: \t{id_list} {type(id_list)}")
                        id_list = list(id_list)
                        logger.log(f"After removing duplicates id_list::: \t{id_list} {type(id_list)}")
                        return id_list
   
        # ended here for adding condition for global case [30-08-2024]- Akash Singh

    def documentLookup_getAnswer(self, client, queryJson, alphaValue, enterpriseName, schema_name, modelScope, openAI_apiKey, operatorValue="", documentFilter_list=[], limit=50):
        
        logger.log("Inside documentLookup_getAnswer () line 190")
        try:

            response            = ""
            finalJson           = {}
            doc_id_list         = []
            id_content_json     = {} 
            fileName            = "document_instructions.txt"
            finalJson_list      = []
            where_filter        = {}

            if modelScope == "G":
                logger.log(f" GLOBAL CASE")

                schemaClasslist = [i['class'] for i in client.schema.get()["classes"]]  
                group_of_schema_list = [schema for schema in schemaClasslist if schema.startswith(enterpriseName)]
                logger.log(f" Enterprise-wise Schemas List:: {group_of_schema_list}")
                return_data = []

                for schemaName_Updated in group_of_schema_list:
                    logger.log(f"\n\n Inside group_of_schema_list '{schemaName_Updated}'")
                    try:
                        retriever = WeaviateHybridSearchRetriever(
                                                                client                   = client,
                                                                index_name               = schemaName_Updated,
                                                                text_key                 = "text",
                                                                attributes               = ["doc_id"],
                                                                create_schema_if_missing = True,
                                                                alpha                    =  alphaValue,
                                                                # k                      =  limit    # 50
                                                            )
                    
                        embeddings = OpenAIEmbeddings(openai_api_key=openAI_apiKey)
                        
                        where_filter = self.createDocument_whereFilter(operatorValue, documentFilter_list)

                        for key in queryJson:
                            
                            if len(key) > 0 and key.strip() != "":
                                logger.log(f"key::: {key}")

                                logger.log(f'\n\n START Time Similarity Search : {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n\n')
                                
                                if len(where_filter) != 0 :
                                    retriever = retriever.get_relevant_documents(key, where_filter=where_filter)               # used because weaviate vector db was unable to return required 'page_content' key directly
                                else:
                                    retriever = retriever.get_relevant_documents(key)
                                logger.log(f"\n\nretriever::: \t{len(retriever)}\n")

                                db = DocArrayInMemorySearch.from_documents(retriever, embeddings )
                                docs = db.similarity_search(key)
                                logger.log(f"Similarity serach response::: \n\n{docs}\n")       
                                logger.log(f'\n\n END Time Similarity Search : {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n\n')

                                retriever = db.as_retriever()
                                qdocs = "".join([docs[i].page_content for i in range(len(docs))])
                                llm = ChatOpenAI(openai_api_key=openAI_apiKey, model_name='gpt-4.1-mini', temperature=0)

                                with open(fileName, "r") as file :
                                    doc_instruction = file.read()
                                    logger.log(f"doc_instruction before::: \t{type(doc_instruction)} \n{doc_instruction}")
                                    doc_instruction = doc_instruction.replace("<qdocs>", f"{qdocs}").replace("<question>",f"{key}").replace("<docs>", f"{docs}")
                                    logger.log(f"doc_instruction after::: \t{type(doc_instruction)} \n{doc_instruction}")

                                logger.log(f'\n\n START Time Document QA : {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n\n')
                                response = llm.call_as_llm(doc_instruction)
                                logger.log(f"response::: \t{type(response)}\n\n{response}\n")
                                logger.log(f'\n\n END Time Document QA : {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n\n')

                            else : 
                                logger.log(f"\n\nEmpty Question case ::: \t'{key}'\n")

                        if response != "":
                            response = response.replace('`','').replace('json','')
                            response = json.loads(response)
                            logger.log(f"response after json conversion ::: \t{type(response)}\n\n{response}\n")
                            
                            for key,value in response.items():
                                if key == "doc_id":
                                    logger.log(f"{key} case, value ::{value} ")
                                    
                                    if type(value) == list :
                                        logger.log("'doc_id' value is of type list")
                                        for index in range(len(value)):
                                            logger.log(f"value index before ::: {value[index]}\n")
                                            if "_" in value[index] :
                                                value[index] = value[index][ : value[index].find("_")] 
                                                logger.log(f"value index after ::: {value[index]}\n")
                                            id_content_json[value[index]] = response["page_content"][index]
                                    
                                    elif type(value) == str:
                                        logger.log("'doc_id' value is of type str")
                                        if "_" in value :
                                            logger.log(f"value before ::: {value}\n")
                                            value = value[ : value.find("_")] 
                                            logger.log(f"value after ::: {value}\n")
                                            id_content_json[value] = response["page_content"]
                                    
                                    else:
                                        logger.log("Invalid datatype for 'doc_id' ")
                                            
                            doc_id_list.append(id_content_json)
                            
                            finalJson["answer"]      = response["answer"]
                            finalJson["doc_id_list"] = doc_id_list

                        finalJson_list.append(finalJson)
                        logger.log(f"finalJson_list::: \t{type(finalJson_list)}\n\n{finalJson_list}\n")
                        return_data.append(finalJson_list)
                    
                    except Exception:
                        logger.log(f"\n\n Document Question-Answer not supported for the Schema name ::: '{schemaName_Updated}'")
                logger.log(f"\n\n return_data 298::: {return_data}")    
                return return_data


            else :
                logger.log(f"ENTERPRISE CASE")
                docType_SchemaName  = enterpriseName + "_" + schema_name 
                logger.log(f"DocType Schema Name ::: {docType_SchemaName}")

                retriever = WeaviateHybridSearchRetriever(
                                                            client                   = client,
                                                            index_name               = docType_SchemaName,
                                                            text_key                 = "text",
                                                            attributes               = ["doc_id"],
                                                            create_schema_if_missing = True,
                                                            alpha                    =  alphaValue,
                                                            # k                      =  limit    # 50
                                                        )
                
                embeddings = OpenAIEmbeddings(openai_api_key=openAI_apiKey)
                
                where_filter = self.createDocument_whereFilter(operatorValue, documentFilter_list)

                for key in queryJson:
                    
                    if len(key) > 0 and key.strip() != "":
                        logger.log(f"key::: {key}")

                        logger.log(f'\n\n START Time Similarity Search : {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n\n')
                        
                        if len(where_filter) != 0 :
                            retriever = retriever.get_relevant_documents(key, where_filter=where_filter)               # used because weaviate vector db was unable to return required 'page_content' key directly
                        else:
                            retriever = retriever.get_relevant_documents(key)
                        logger.log(f"\n\nretriever::: \t{len(retriever)}\n")

                        db = DocArrayInMemorySearch.from_documents(retriever, embeddings )
                        docs = db.similarity_search(key)
                        logger.log(f"Similarity serach response::: \n\n{docs}\n")       
                        logger.log(f'\n\n END Time Similarity Search : {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n\n')

                        retriever = db.as_retriever()
                        qdocs = "".join([docs[i].page_content for i in range(len(docs))])
                        llm = ChatOpenAI(openai_api_key=openAI_apiKey, model_name='gpt-4.1-mini', temperature=0)

                        with open(fileName, "r") as file :
                            doc_instruction = file.read()
                            logger.log(f"doc_instruction before::: \t{type(doc_instruction)} \n{doc_instruction}")
                            doc_instruction = doc_instruction.replace("<qdocs>", f"{qdocs}").replace("<question>",f"{key}").replace("<docs>", f"{docs}")
                            logger.log(f"doc_instruction after::: \t{type(doc_instruction)} \n{doc_instruction}")

                        logger.log(f'\n\n START Time Document QA : {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n\n')
                        response = llm.call_as_llm(doc_instruction)
                        logger.log(f"response::: \t{type(response)}\n\n{response}\n")
                        logger.log(f'\n\n END Time Document QA : {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n\n')

                    else : 
                        logger.log(f"\n\nEmpty Question case ::: \t'{key}'\n")

                if response != "":
                    response = response.replace('`','').replace('json','')
                    response = json.loads(response)
                    logger.log(f"response after json conversion ::: \t{type(response)}\n\n{response}\n")
                    
                    for key,value in response.items():
                        if key == "doc_id":
                            logger.log(f"{key} case, value ::{value} ")
                            
                            if type(value) == list :
                                logger.log("'doc_id' value is of type list")
                                for index in range(len(value)):
                                    logger.log(f"value index before ::: {value[index]}\n")
                                    if "_" in value[index] :
                                        value[index] = value[index][ : value[index].find("_")] 
                                        logger.log(f"value index after ::: {value[index]}\n")
                                    id_content_json[value[index]] = response["page_content"][index]
                            
                            elif type(value) == str:
                                logger.log("'doc_id' value is of type str")
                                if "_" in value :
                                    logger.log(f"value before ::: {value}\n")
                                    value = value[ : value.find("_")] 
                                    logger.log(f"value after ::: {value}\n")
                                    id_content_json[value] = response["page_content"]
                            
                            else:
                                logger.log("Invalid datatype for 'doc_id' ")
                                    
                    doc_id_list.append(id_content_json)
                    
                    finalJson["answer"]      = response["answer"]
                    finalJson["doc_id_list"] = doc_id_list

                finalJson_list.append(finalJson)
                logger.log(f"finalJson_list::: \t{type(finalJson_list)}\n\n{finalJson_list}\n")
                return finalJson_list
        
        except Exception as e :
            logger.log(f"\n Issue::: \n{e}\n","0")
            trace = traceback.format_exc()
            descr = str(e)
            errorXml = common.getErrorXml(descr, trace)
            logger.log(f'\n Weaviate hybrid class getLookUP() errorXml::: \n{errorXml}', "0")
            raise str(errorXml)

    def get_FileOCR(self, fileObj):
        try:
            fileName = fileObj.filename                                         # extract filename from file object
            file_path = os.path.join(self.file_storage_path, fileName)
            
            Path(self.file_storage_path).mkdir(parents=True, exist_ok=True)     # Initialize directory
            fileObj.save(file_path)

            logger.log(f"\n fileName ::: \t{fileName}\n filePath ::: \t{file_path}\n File object stored successfully.")

            ext_OCR = Extract_OCR()
            OCR_Text = ext_OCR.get_OCR(file_path, self.processingMethod_list)
            logger.log(f"\nOCR_Text::: \n{OCR_Text}\n")
            return OCR_Text
        
        except Exception as e :
            logger.log(f"\n Issue::: \n{e}\n","0")
            trace = traceback.format_exc()
            descr = str(e)
            errorXml = common.getErrorXml(descr, trace)
            logger.log(f'\n Weaviate hybrid class get_FileOCR() errorXml::: \n{errorXml}', "0")
            raise str(errorXml)

    def createDocument_whereFilter(self, operatorValue, documentFilter_list):
        try :
            where_filter = { "operator" : operatorValue } 
            operands_list = []
            if len(documentFilter_list) != 0 and operatorValue != "" :
                
                for documentFilter_dict in documentFilter_list:
                
                    filter                =  {}
                    filter["path"]        =  documentFilter_dict["name"]
                    filter["valueString"] =  documentFilter_dict["value"]
                    filter["operator"]    =  documentFilter_dict["operator"] if documentFilter_dict["operator"] != "" else "Equal"
                    logger.log(f"\n\nfilter line 716 ::: {filter}\n ")
                    
                    operands_list.append(filter)
                logger.log(f"\n operands_list ::: {operands_list}\n")

                where_filter["operands"]    = operands_list
                logger.log(f"\n where_filter ::: {where_filter}\n")
            else:
                logger.log(f"\n\n Where filter not received.\n")
                where_filter = {}
            return where_filter
        
        except Exception as e:
            logger.log(f"Issue ::: {e}","1")
            trace = traceback.format_exc()
            descr = str(e)
            errorXml = common.getErrorXml(descr, trace)
            logger.log(f'\n createDocument_whereFilter() errorXml::: \n{errorXml}', "0")
            raise str(errorXml)
