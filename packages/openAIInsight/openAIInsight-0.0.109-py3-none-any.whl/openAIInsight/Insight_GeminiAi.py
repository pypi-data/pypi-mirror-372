import requests, json, traceback
from flask import request
import loggerutility as logger
import commonutility as common
import os
from openai import OpenAI

import google.generativeai as genai

class InsightGeminiAI:
    userId = ""
    def getCompletionEndpoint(self,jsonData,final_instruction):
        try:

            finalResult     =  {}
            insightInput    =  ""
            geminiAI_APIKey =  ""

            if 'GeminiAI_APIKey' in jsonData.keys():
                geminiAI_APIKey = jsonData['GeminiAI_APIKey'] 

            if 'insight_input' in jsonData.keys():
                insightInput = jsonData['insight_input'] 

            if 'userId' in jsonData.keys():
                self.userId = jsonData['userId'] 

            messageList  = str(final_instruction)  
            logger.log(f"messageList::: {messageList}")
            
            generation_config = {
                                    "temperature"       : 0 ,
                                    "top_p"             : 1 ,
                                    "top_k"             : 1 ,
                                    "max_output_tokens" : 2048 ,
                                }
            if len(geminiAI_APIKey) != 0 :
                genai.configure(api_key = geminiAI_APIKey)
                model       = genai.GenerativeModel('gemini-1.0-pro')
                response    = model.generate_content(messageList)

                logger.log(f"  Input Question ::: {insightInput}\n gemini-1.0-pro Response::: {finalResult = } {type(finalResult)}")
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
                            logger.log(f"Exception : Invalid JSON Response GEMINI 1.5: {finalResult} {type(finalResult)}" )  # changes till here
                return finalResult
            else:
                raise Exception("Please provide a valid API Key to request GEMINI AI. ")         
            
        except Exception as e:
            logger.log(f'\n In getCompletionEndpoint exception stacktrace : ', "1")
            trace = traceback.format_exc()
            descr = str(e)
            returnErr = common.getErrorXml(descr, trace)
            logger.log(f'\n Print exception returnSring inside getCompletionEndpoint : {returnErr}', "0")
            return str(returnErr)
