#actual python modules
import os, json, subprocess, datetime, cv2, qrcode, PIL.Image, pypdf
import google.generativeai as genai
from dotenv import load_dotenv
from pathlib import Path
from qreader import QReader

#my own python files
from geminillm import gemrequest
from urlextract import URLExtract
from cfradar import urlScan
from cfsd import sdgen
from UploadFile import uploadFileToCloud
import localconverters, cfllm, whispercf, nltocommand

load_dotenv()

def stripExt(fileName):
    splitname = fileName.split(".")

    noext = ""

    for i in range(len(splitname)-1):
        noext += splitname[i]
    
    return noext

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
    inputFilePath = input("Drag video/audio file here: ")

    fileName = inputFilePath.split("\\")[-1]

    filePath = inputFilePath[:-len(fileName)]

    fileName_noext = stripExt(fileName)

    targetFormat = input("Which format do you want?\n> ")

    subprocess.run(["ffmpeg","-i",inputFilePath,filePath+fileName_noext+"."+targetFormat])

    print("Conversion OK, check the same path as the origin!")

def imageConvertInteractive():
    print("I'll help you use imagemagick!")
    inputFilePath = input("Drag image file here: ")

    fileName = inputFilePath.split("\\")[-1]

    filePath = inputFilePath[:-len(fileName)]

    targetFormat = input("Which format do you want?\n> ")

    subprocess.run(["magick", "mogrify", "-format", targetFormat, "-path", filePath, inputFilePath])

    print("Conversion OK, check the same path as the origin!")

if __name__ == "__main__":
    if not Path.exists(Path("config.json")):
        setup()
        print("Setup complete!")        

    with open("config.json", "r") as f:
        config = json.load(f)

    print("Welcome, "+config["name"]+"!")

    while True:
        msg = input("> ")

        if msg == "":
            continue

        if msg[0] == "/":
            if msg[1] == "c":#clear
                for i in fullConstruct:
                    construct += i["parts"][0]
                    construct += "\n"

                modelReply = gemrequest(construct)

                if modelReply[0] == False:
                    print("Something went wrong!")
                    print(modelReply[1])
                    continue
                else:
                    print(modelReply[1])
                    config["ltmemory"] += str(datetime.datetime.today()) + ": " + modelReply[1]

                    with open("config.json", "w") as f:
                        json.dump(config, f)
                    
                    continue

            elif msg[1] == "e":#exit
                print("Exiting! (Just a moment while I save the conversation...)")
                construct = "The following is a conversation between a chatbot and a user. Summarize the interaction briefly.\n"

                for i in fullConstruct:
                    construct += i["parts"][0]
                    construct += "\n"

                modelReply = gemrequest(construct)

                if modelReply[0] == False:
                    print("Something went wrong!")
                    print(modelReply[1])
                    continue
                else:
                    print(modelReply[1])
                    config["ltmemory"] += str(datetime.datetime.today()) + ": " + modelReply[1]

                    with open("config.json", "w") as f:
                        json.dump(config, f)

                    break
                

        responseType = nltocommand.shouldIRespond(msg)

        if responseType == 1:#LLM response
            filesList = []
            
            print("Any files you'd like to attach? Return empty to stop adding files.")
            print("Note: I'll extract text only from PDF files!")
            
            while True:
    
                filePath = input("Drag file here: ")
                
                if filePath == "": break

                filesList.append(filePath)
            
            construct = str(datetime.datetime.now()) + ": " + msg + "\n"

            filesUploadedList = []

            if len(filesList) > 0:
                documentIndex = 1    

                for i in filesList:
                    fileName = i.split("\\")[-1]

                    fileName_noext = stripExt(fileName)

                    extension = fileName.split(".")[-1]
            
                    if extension == "pdf":

                        construct += "PDF document " + str(documentIndex) + ":\n"

                        documentIndex += 1

                        reader = pypdf.PdfReader(i)

                        for j in range(reader.pages):
                            text = reader.pages[j].extract_text()

                            construct += text

                        construct += "\n"

                    else:
                        file = genai.upload_file(path=i,display_name=fileName)
                        filesUploadedList.append(genai.get_file(name=file.name))
            
            fullConstruct = [{'role':'user','parts':\
                            [config["personality"] + "\n The user is named " + config["name"] + \
                            ".\n These are summaries of your previous conversations with the user for context: " + config["ltmemory"]\
                            +"\n Do not include a timestamp in your reply."]}]

            

            fullConstruct.append({'role':'user','parts':[construct]+filesUploadedList})

            modelReply = gemrequest(fullConstruct)

            if modelReply[0] == False:
                print("Something went wrong... This information may be of use:")
                print(modelReply[1])
            else:
                print(modelReply[1])

        elif responseType == 0:#Tool response
            listOfActions = ["0. video/audio conversion", "1. image conversion", "2. QR code scanning", "3. Image generation"]
            task = nltocommand.nltocommand(listOfActions, msg)

            if task == -1:
                print("Sorry, I couldn't figure out what to do.")
                continue
            elif task == 0:
                videoConvertInteractive()
            elif task == 1:
                imageConvertInteractive()
            elif task == 2:
                continue

        else:
            print("E: Something went wrong while I tried to understand you. Please try again.")