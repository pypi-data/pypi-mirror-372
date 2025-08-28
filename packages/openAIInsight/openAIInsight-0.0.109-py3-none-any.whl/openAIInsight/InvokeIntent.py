import requests, json, traceback, openai
from flask import request
import loggerutility as logger
import commonutility as common
import os
from datetime import datetime
from .InvokeIntent_LocalAI import InvokeIntentLocalAI
from .InvokeIntent_OpenAI import InvokeIntentOpenAI
from .InvokeIntent_Gemini import InvokeIntentGemini

class InvokeIntent:
    def getInvokeIntent(self):
        logger.log(f"\n\nInside getInvokeIntent()","0")
        try:
            finalResult         = ""
            invokeIntentModel   = ""
            jsonData            = request.get_data('jsonData', None)
            intentJson          = json.loads(jsonData[9:])
            logger.log(f"\n Invoke Intent class jsonData ::: {intentJson}","0")
            
            if 'INVOKE_INTENT_MODEL' in intentJson.keys() and intentJson['INVOKE_INTENT_MODEL'] != None:
                invokeIntentModel =  intentJson['INVOKE_INTENT_MODEL']
                if len(invokeIntentModel) == 0 :
                    invokeIntentModel = "OpenAI"
            
            if 'LocalAI' == invokeIntentModel:
                invokeIntentLocalAI = InvokeIntentLocalAI()
                finalResult = invokeIntentLocalAI.getInvokeIntent(intentJson, invokeIntentModel)

            elif 'OpenAI' == invokeIntentModel:
                invokeIntentOpenAI = InvokeIntentOpenAI()
                finalResult = invokeIntentOpenAI.getInvokeIntent(intentJson, invokeIntentModel)

            elif 'GeminiAI' == invokeIntentModel:
                invokeIntentGemini = InvokeIntentGemini()
                finalResult = invokeIntentGemini.getInvokeIntent(intentJson, invokeIntentModel)
            
            else:
                return Exception(f"INVALID Invoke Intent Model ::::: '{invokeIntentModel}' ")

            logger.log(f"\n\n Invoke Intent Final Result ::::: {finalResult} \n{type(finalResult)}","0")
            return finalResult
        
        except Exception as e:
            logger.log(f'\n In getIntentService exception stacktrace : ', "1")
            trace = traceback.format_exc()
            descr = str(e)
            returnErr = common.getErrorXml(descr, trace)
            logger.log(f'\n Exception ::: {returnErr}', "0")
            return str(returnErr)
        

    
