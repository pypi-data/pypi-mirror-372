import requests, json, traceback
from flask import request
import loggerutility as logger
import commonutility as common
import os
from openai import OpenAI

class InsightOpenAI:
    userId = ""
    def getCompletionEndpoint(self,jsonData,final_instruction):
        try:
            
            finalResult      =  ""
            openai_api_key   =  ""

            if "license_key" in jsonData.keys():
                openai_api_key = jsonData["license_key"]                    # "sk-svcacct-xoSzrEWzvU4t1fbEluOkT3BlbkFJkj7Pvc8kU98y1P3LdI1c"
            
            if 'userId' in jsonData.keys():
                self.userId = jsonData['userId'] 
            
            if "insight_input" in jsonData.keys():
                insightInput = jsonData["insight_input"]

            if len(openai_api_key) != 0 :
                client = OpenAI(
                                    api_key = openai_api_key 
                                )

                if self.userId and self.userId != "":
                    response = client.chat.completions.create(
                                                                    model               =  "gpt-4.1-mini" ,
                                                                    messages            =  final_instruction ,
                                                                    temperature         =  0.25 ,
                                                                    max_tokens          =  350 ,
                                                                    top_p               =  0.5 ,
                                                                    frequency_penalty   =  0 ,
                                                                    presence_penalty    =  0 ,
                                                                    user                = self.userId 
                                                                )
                else:
                    response = client.chat.completions.create(
                                                                    model               =  "gpt-4.1-mini" ,
                                                                    messages            =  final_instruction ,
                                                                    temperature         =  0.25 ,
                                                                    max_tokens          =  350 ,
                                                                    top_p               =  0.5 ,
                                                                    frequency_penalty   =  0 ,
                                                                    presence_penalty    =  0 
                                                                )
                logger.log(f"\n\n Input Question ::: {insightInput}\nResponse openAI ChatCompletion endpoint::::: {response} \n{type(response)}","0")
                finalResult=str(response.choices[0].message.content)
                logger.log(f"\n\n OpenAI ChatCompletion endpoint finalResult ::::: {finalResult} \n{type(finalResult)}","0")
                return finalResult
            else:
                raise Exception("Please provide a valid API Key to request Open AI. ")         
            
        except Exception as e:
            logger.log(f'\n In getCompletionEndpoint exception stacktrace : ', "1")
            trace = traceback.format_exc()
            descr = str(e)
            returnErr = common.getErrorXml(descr, trace)
            logger.log(f'\n Print exception returnSring inside getCompletionEndpoint : {returnErr}', "0")
            return str(returnErr)
