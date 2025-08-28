import requests, json, traceback
from flask import request
import loggerutility as logger
import commonutility as common
import os
from datetime import datetime
from openai import OpenAI
import threading
import json
import google.generativeai as genai
import os, json

class InvokeIntentGemini:
    uuid            =  ""
    user_id         =  ""
    historyCount    =  ""

    def getInvokeIntent(self, intentJson, invokeIntentModel):
        try:
            logger.log(f"\n\nInside InvokeIntentGemini getInvokeIntent()","0")
            jsonData    = request.get_data('jsonData', None)
            intentJson  = json.loads(jsonData[9:])
            logger.log(f"\njsonData openAI class::: {jsonData}","0")
            
            finalResult             =  {}
            geminiAI_APIKey         =  intentJson['GeminiAI_APIKey'] 
            intent_input            =  intentJson['intent_input'].replace("+"," ")
            enterprise              =  intentJson['enterprise']
            self.user_id            =  intentJson['user_id']
            self.uuid               =  intentJson['uuid']
            self.intent_args        =  intentJson['INTENT_LIST']
            file_data_history       =  []
            intent_training_data    =  []
            messageList             =  []

            if 'INTENT_LIST' in intentJson.keys():
                self.intent_args  = intentJson['INTENT_LIST']
                logger.log(f"\n intent_args::: {self.intent_args}","0") 

            if 'user_id' in intentJson.keys():
                self.user_id = intentJson['user_id']
                logger.log(f"\n localAIURL openAI class::: {self.user_id}","0")

            if 'uuid' in intentJson.keys():
                self.uuid = intentJson['uuid']
                logger.log(f"\n UUID openAI class::: {self.uuid}","0") 
            
            if 'history_count' in intentJson.keys():
                self.historyCount = intentJson['history_count']
                logger.log(f"\n history_Count openAI class::: {self.historyCount}","0") 

            fileName                                = "intent_Instructions.json"
            intent_training_data                    = self.read_intentInstruction_file(fileName)
            concatenated_value,fileData,messageList = self.update_intent_content(intent_training_data, intent_input, self.intent_args, invokeIntentModel, self.historyCount, self.user_id, self.uuid)
            messageList                             = str(messageList)
            
            generation_config = {
                                    "temperature"       : 0 ,
                                    "top_p"             : 1 ,
                                    "top_k"             : 1 ,
                                    "max_output_tokens" : 2048 ,
                                }
            
            genai.configure(api_key = geminiAI_APIKey)
            model       = genai.GenerativeModel('gemini-1.0-pro')
            response    = model.generate_content(messageList)

            logger.log(f"  Input Question ::: {intent_input}\n gemini-1.0-pro Response::: {finalResult = } {type(finalResult)}")
            logger.log(f"\n\nResponse GeminiAI endpoint::::: {response} \n{type(response)}","0")
            for part in response:
                finalResult = part.text
                if finalResult:
                    try:
                        finalResult = finalResult.replace("\\", "").replace('```', '').replace('json', '') 
                        if finalResult.startswith("{{") and finalResult.endswith("}}"):
                            finalResult = finalResult[1:-1]
                            finalResult = json.loads(finalResult)
                    except json.JSONDecodeError:
                        logger.log(f"Exception : Invalid JSON Response GEMINI 1.5: {finalResult} {type(finalResult)}" )

            thread = threading.Thread(target=common.write_JsonFile, args = [concatenated_value+'.json', intent_input, fileData, invokeIntentModel, finalResult])
            thread.start()
            thread.join()
            return finalResult
        
        except Exception as e:
            logger.log(f'\n In getInvokeIntent exception stacktrace : ', "1")
            trace = traceback.format_exc()
            descr = str(e)
            returnErr = common.getErrorXml(descr, trace)
            logger.log(f'\n Exception ::: {returnErr}', "0")
            return str(returnErr)
        
    def read_json_file(self, user_id, user_filename, invokeIntentModel,historyCount):
        '''
        This function is used to read JSON file with stored history count of each input query and resultant output. 
        Params  :
            user_filename     : str  --> userId_uuid.json
            user_id           : str  --> SWAPNIL
            requireAllData    : bool 
            invokeIntentModel : str  --> LocalAI / OpenAI
        '''
        
        file_data_history   = ""
        directory_fileList  = []
        directoryPath       = f"{invokeIntentModel}_Instruction"
        fileName            = directoryPath + "/" + user_filename
        
        if os.path.exists(directoryPath):
            logger.log(f"Folder LocalAI_Instruction is present:::  {directoryPath}")
            if os.path.exists(fileName):
                with open(fileName, "r") as f:
                    fileData = f.read()
                    logger.log(f"\nfileData line 25 ::: {fileData} \t {type(fileData)}\n\n")
                    if type(fileData) == str:
                        fileData = json.loads(fileData)
                    historyCount = int(self.historyCount) if historyCount != "" else -6
                    file_data_history = fileData[historyCount : ]
                    logger.log(f"\n\nfile_data_history::: {file_data_history}\n\n")
                    return fileData, file_data_history
            else:
                logger.log(f"userId_uuid File not present ::: {fileName}")
                directory_fileList = os.listdir(directoryPath)
                filesHaving_UserId =[file for file in directory_fileList if user_id in file]
                if len(filesHaving_UserId) != 0:
                    for file in filesHaving_UserId :
                        os.remove(directoryPath + "/" + file)
                        logger.log(f"File with userId deleted::: {file}\n")
                        return [], []
                else:
                    logger.log(f"Directory is empty. line 44")
                    return [], []
        else:
            logger.log(f"Directory not  present ::: {directoryPath}")
            return [], []
        
    def read_intentInstruction_file(self,file_name):
        '''
        This function is used to read and return the 'intent_instruction.json' file data.
        '''

        if os.path.exists(file_name):
            try:
                with open(file_name, 'r') as file:
                    intent_training_data = json.load(file)
                    return intent_training_data

            except Exception as e:
                logger.error(f"An error occurred while processing the file: {e}")
                trace = traceback.format_exc()
                descr = str(e)
                returnErr = common.getErrorXml(descr, trace)
                logger.log(f'\n Exception ::: {returnErr}', "0")
                return str(returnErr)
        else:
            logger.warning(f"\n\n{file_name} does not exist.\n")
            message = f"The Intent API service could not be requested due to missing '{file_name}' file."
            return message
        
    def update_intent_content(self,intent_training_data, intent_input, intent_args,invokeIntentModel,historyCount,user_id,uuid):
        '''
        This function is used to update the content tags and pass history in message list.
        Params  :
            intent_training_data     : str  --> content of instruction JSON file
            intent_input             : str  --> Create a sales order from ABC for item FG00000001 Quantity 200, item FG00000001 Quantity 100
            intent_args              : list --> intent list
            invokeIntentModel        : str  --> LocalAI / OpenAI / GeminiAI
            historyCount             : int  --> 2
            user_id                  : str  --> SWAPNIL
            uuid                     : str  --> d7e136c040974c3bbc0e 
        '''

        try:
            concatenated_value = ""
            fileData = []
            message_list = []

            intent_training_data[-1]['content']= intent_training_data[-1]['content'].replace("<current_date>", datetime.now().strftime("%d-%b-%Y").upper()).replace("<year>", str(datetime.now().year))
            intent_training_data[2]['content']= intent_training_data[2]['content'].replace("<intent_args>", intent_args)
            
            message_list = intent_training_data  

            concatenated_value = f"{user_id}_{uuid}"
            logger.log(f"\nConcatenated value: {concatenated_value}","0") 

            fileData, file_data_history = self.read_json_file(self.user_id, concatenated_value+'.json', invokeIntentModel,historyCount)

            if len(file_data_history) == 0:
                logger.log(f"json data empty in '{concatenated_value}.json' file")

            else:
                for history_element in file_data_history:
                    message_list.append(history_element)

            message_list.append({
                                    "role"      : "user",
                                    "content"   : intent_input
                                })
                
            logger.log(f"\n\nfinal messageList :::::: {message_list}","0")

            return concatenated_value,fileData,message_list
        except json.JSONDecodeError as e:
            logger.log(f"Error decoding JSON: {e}")
            logger.log(f"Invalid JSON content: {intent_training_data}")
            trace = traceback.format_exc()
            descr = str(e)
            returnErr = common.getErrorXml(descr, trace)
            logger.log(f'\n Exception ::: {returnErr}', "0")
            return str(returnErr)
            
        except Exception as e:
            logger.log(f"An error occurred while updating intent content: {e}")
            trace = traceback.format_exc()
            descr = str(e)
            returnErr = common.getErrorXml(descr, trace)
            logger.log(f'\n Exception ::: {returnErr}', "0")
            return str(returnErr)
        
    

