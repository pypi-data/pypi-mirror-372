import os
import cv2
import PyPDF2
import pathlib
import docx2txt
import traceback
import pdftotext
import pdfplumber
import pytesseract
import pandas as pd
from PIL import Image
import commonutility as common
import loggerutility as logger
from pdf2image import convert_from_path
from tempfile import TemporaryDirectory
from striprtf.striprtf import rtf_to_text

class Extract_OCR:
    
    def get_OCR(self, file_path, processingMethod_list):
        OCR_Text = {}
        try :
            fileExtension = (pathlib.Path(file_path).suffix)
            logger.log(f"\nfileExtention::: {fileExtension}","0")
            self.fileExtension_lower = fileExtension.lower()
            logger.log(f"\nfileExtention_lower()::: {self.fileExtension_lower}","0")

            if '.pdf' == self.fileExtension_lower:

                if 'PP' == processingMethod_list[0] :
                    logger.log("\tCASE PP\n")
                    OCR_Text=self.pdfplumber_ocr(file_path)

                elif 'PT' == processingMethod_list[0]:
                    logger.log("\tCASE PT\n")
                    OCR_Text=self.pdftotext_ocr(file_path)

                elif 'PO' == processingMethod_list[0]:
                    logger.log("\tCASE PO\n")
                    OCR_Text=self.pytesseract_ocr(file_path)
                
                elif 'PPO' == processingMethod_list[0] :
                    logger.log("\tCASE PPO\n")
                    OCR_Text=self.pdfplumber_overlap(file_path)
                
                elif 'PPF' == processingMethod_list[0]:
                    logger.log("\tCASE PPF\n")
                    OCR_Text=self.PyPDF_ocr(file_path)

                keys_with_blank_values = [key for key, value in OCR_Text.items() if not value]
                if len(keys_with_blank_values) != 0:      
                    OCR_Text=self.pytesseract_ocr(file_path)

                logger.log(f" PDF OCR ::::: \n{OCR_Text}\n","0")
        
            elif '.docx' == self.fileExtension_lower :
                dict[str(1)] = docx2txt.process(file_path)
                OCR_Text = dict
                logger.log(f"DOCX OCR ::::: {OCR_Text}","0")

            elif ".xls" == self.fileExtension_lower or ".xlsx" ==  self.fileExtension_lower :
                logger.log(f"inside .xls or .xlsx condition","0")
                df = pd.read_excel(file_path)
                xls_ocr = df.to_csv()
                dict[str(1)] = xls_ocr.replace(","," ").strip()
                OCR_Text = dict
                logger.log(f"\nxls_ocr type ::::: \t{type(OCR_Text)}","0")
                logger.log(f"\nxls_ocr ::::: \n{OCR_Text}\n","0")
                
            elif ".csv" == self.fileExtension_lower :
                logger.log(f"inside .csv condition","0")
                df = pd.read_csv(file_path)
                csv_ocr = df.to_csv()           # to handle multiple spaces between columns
                dict[str(1)] = csv_ocr.replace(","," ")
                OCR_Text = dict
                logger.log(f"\ncsv_ocr type ::::: \t{type(OCR_Text)}","0")
                logger.log(f"\ncsv_ocr ::::: \n{OCR_Text}\n","0")
            
            elif ".rtf" == self.fileExtension_lower :
                logger.log(f"inside .rtf condition","0")
                with open(file_path) as infile:
                    content = infile.read()
                    dict[str(1)] = rtf_to_text(content, errors="ignore")  # to handle encoding error
                OCR_Text = dict
                logger.log(f"\nrtf_ocr type ::::: \t{type(OCR_Text)}","0")
                logger.log(f"\nrtf_ocr ::::: \n{OCR_Text}\n","0")
            
            else:
                logger.log(f"\nInvalid File Type ::::: \t{self.fileExtension_lower }","0")

            return OCR_Text

        except Exception as e :
            logger.log(f"\n Issue::: \n{e}\n","0")
            trace = traceback.format_exc()
            descr = str(e)
            errorXml = common.getErrorXml(descr, trace)
            logger.log(f'\n Weaviate hybrid class getLookUP() errorXml::: \n{errorXml}', "0")
            raise str(errorXml)

        
    def pytesseract_ocr(self,PDF_file):
        image_file_list = []
        dict = {}
        with TemporaryDirectory() as tempdir:
            pdf_pages = convert_from_path(PDF_file, 500)
            for page_enumeration, page in enumerate(pdf_pages, start=1):
                filename = f"{tempdir}\page_{page_enumeration:03}.jpg"
                page.save(filename, "JPEG")
                image_file_list.append(filename)

            for page_no,image_file in enumerate(image_file_list):
                text = cv2.imread(image_file)
                image_file = self.resizing(text, 50)
                dict[str(page_no+1)] = str(((pytesseract.image_to_string(image_file)))).strip()

            logger.log(f"pytesseract for image ::::: 61 {dict}","0")
            return dict
        
    def pdfplumber_ocr(self,PDF_file):
        OCR_lst = []
        ocr_text_final = ""
        dict = {}
        
        file = pdfplumber.open(PDF_file)
        ocr_text = file.pages
        logger.log(f"file.pages::: {file.pages}", "0")
        for page_no in range (len(ocr_text)):
            ocr_text_final = ocr_text[page_no].extract_text()
            dict[str(page_no+1)] = ocr_text_final.strip()
            # OCR_lst.append(ocr_text_final)
        # print(len(dict.values()))
        # print(dict)
        return dict
    
    def pdftotext_ocr(self,PDF_file):
        with open(PDF_file, "rb") as f:
            pdf = pdftotext.PDF(f)

        OCR_Text = "\n\n".join(pdf)
        return OCR_Text
    
    def pdfplumber_overlap(self, fileName):
        ocr_text_final  = ""
        OCR_dict        = {}
        
        pdf = pdfplumber.open(fileName)
        ocr_text = pdf.pages
        for page_no in range (len(ocr_text)):
            ocr_text_final = ocr_text[page_no].extract_text(layout=True, x_tolerance=1)
            OCR_dict[str(page_no+1)] = ocr_text_final.strip()
        
        logger.log(f"OCR_dict after overlap:::: \t{type(OCR_dict)}\n{OCR_dict}\n")
        return OCR_dict

    def PyPDF_ocr(self, fileName):
        ocr_text_final  = ""
        OCR_dict        = {}

        pdfFileObj = open(fileName, 'rb')
        pdfReader = PyPDF2.PdfReader(pdfFileObj)
        ocr_text = pdfReader.pages
        
        for page_no in range (len(ocr_text)):
            ocr_text_final = ocr_text[page_no].extract_text()
            OCR_dict[str(page_no+1)] = ocr_text_final.strip()

        logger.log(f"OCR_dict PyPDF :::: \t{type(OCR_dict)}\n{OCR_dict}\n")
        return OCR_dict
