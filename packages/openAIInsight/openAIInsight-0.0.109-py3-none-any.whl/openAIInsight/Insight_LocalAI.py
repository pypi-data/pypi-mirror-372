import requests, json, traceback, openai
from flask import request
import loggerutility as logger
import commonutility as common
import os
from openai import OpenAI

from datetime import datetime

class InsightLocalAI:
    userId          = ""
    localAIURL      = ""                                                    # http://141.148.197.63:11434/v1

    def getCompletionEndpoint(self,jsonData,final_instruction):
        try:
            
            if "license_key" in jsonData.keys():
                LocalAI_APIKey = jsonData["license_key"]                    # "sk-svcacct-xoSzrEWzvU4t1fbEluOkT3BlbkFJkj7Pvc8kU98y1P3LdI1c"

            if "insight_input" in jsonData.keys():
                insightInput = jsonData["insight_input"]

            if 'userId' in jsonData.keys():
                self.userId = jsonData['userId'] 

            if 'LOCAL_AI_URL' in jsonData.keys():
                self.localAIURL =  jsonData['LOCAL_AI_URL']
            
            if len(LocalAI_APIKey) != 0:

                openai.api_key  = LocalAI_APIKey  
                
                logger.log(f"\n\n final messageList :::::: {final_instruction}","0")

                client = OpenAI(base_url=self.localAIURL, api_key = "lm-studio" )
                completion = client.chat.completions.create(
                                                                model           =  "mistral" ,        
                                                                messages        =  final_instruction ,
                                                                temperature     =  0 ,
                                                                stream          =  False,
                                                                max_tokens      =  4096
                                                            )

                finalResult = str(completion.choices[0].message.content)
                logger.log(f"\n\n Input Question ::: {insightInput}\n LocalAI endpoint finalResult ::::: {finalResult} \n{type(finalResult)}","0")
                finalResult = str(finalResult).replace("\\","")
                logger.log(f"\n\nLocalAI endpoint finalResult filtered ::::: {finalResult} \n{type(finalResult)}","0")
                logger.log(f'\n Print time on end : {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', "0")
                logger.log(f"\n\nLocalAI endpoint finalResult ::::: {finalResult} \n{type(finalResult)}","0")
                return finalResult
            else:
                raise Exception("Please provide a valid API Key to request LOCAL AI. ")         
            
        except Exception as e:
            logger.log(f'\n In getCompletionEndpoint exception stacktrace : ', "1")
            trace = traceback.format_exc()
            descr = str(e)
            returnErr = common.getErrorXml(descr, trace)
            logger.log(f'\n Print exception returnSring inside getCompletionEndpoint : {returnErr}', "0")
            return str(returnErr)
