#actual python modules
import os, json, subprocess, datetime, cv2, qrcode, PIL.Image
from dotenv import load_dotenv
from pathlib import Path
from qreader import QReader

#my own python files
from geminillm import gemrequest
from urlextract import URLExtract
from cfradar import urlScan
from cfsd import sdgen
from htmlify import makePage
from UploadFile import uploadFileToCloud
import localconverters, cfllm, whispercf, nltocommand

load_dotenv()

def stripExt(fileName):
    splitname = fileName.split(".")

    noext = ""

    for i in range(len(splitname)-1):
        noext += splitname[i]

def setup():
    print("Hello! Could you tell me your name?")
    userName = input("> ")

    print("Hello, "+userName+"!")

    print("Next, you can decide my personality. Please write it in third person, and include my name.")
    print("Example: You are a helpful assistant named Gemini.")
    personality = input("> ")

    config = {
        "name": userName,
        "personality": personality,
        "ltmemory": "",
        "stmemory": []
    }

    with open("config.json", "w") as f:
        json.dump(config, f)
    
def videoConvertInteractive():
    print("I'll help you use ffmpeg!")
    inputFilePath = input("Drag video file here: ")

def imageConvertInteractive():
    print("I'll help you use imagemagick!")
    inputFilePath = input("Drag image file here: ")

if __name__ == "__main__":
    if not Path.exists("config.json"):
        setup()
    else:
        print("Welcome back!")

    while True:
        msg = input("> ")

        responseType = nltocommand.shouldIRespond(msg)

        if responseType == 1:#LLM response
            filesList = []

            while True:
                print("Any files you'd like to attach? Return empty to stop adding files.")
    
                filePath = input("Drag file here: ")
                
                if filePath == "": break

                filesList.append(filePath)
            
            if len(filesList) > 0:
                for i in filesList:
                    fileName = i.split("\\")[-1]

                    extension = stripExt(fileName)
            
                    if extension in ["png", "jpg", "jpeg", "webp", "avif"]# is image


        elif responseType == 0:#Tool response
            pass

        else:
            print("E: Something went wrong while I tried to understand you. Please try again.")