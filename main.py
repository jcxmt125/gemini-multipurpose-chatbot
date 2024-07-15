#actual python modules
import os, json, subprocess, datetime, cv2, qrcode, pypdf, whisper
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
import cfllm, nltocommand, whispercf

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

    print("Next, decide how you'd like me to handle transcription. 0 for cloud (CF AI), 1~5 for local with 5 being large and 1 being tiny")
    transcriber = int(input("> "))

    if transcriber == 0:
        whisperModel = 0
    else:
        whisperModel = ["tiny","base","small","medium","large"][transcriber-1]

    config = {
        "name": userName,
        "personality": personality,
        "transcription": whisperModel,
        "ltmemory": "",
        "stmemory": []
    }

    with open("config.json", "w") as f:
        json.dump(config, f, indent=2)
    
def fixConfig(config):
    if "transcription" not in config:
        print("Your config file doesn't seem to have selected tracription options! We'll choose a whisper model: 0 for cloud (CF AI), 1~5 for local with 5 being large and 1 being tiny")
        transcriber = int(input("> "))

        if transcriber == 0:
            whisperModel = 0
        else:
            whisperModel = ["tiny","base","small","medium","large"][transcriber-1]
    
        config["transcription"] = whisperModel
    
    with open("config.json", "w") as f:
        json.dump(config, f, indent=2)

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

    print("Running imagemagick. This might take a bit...")

    subprocess.run(["magick", "mogrify", "-format", targetFormat, "-path", filePath, inputFilePath])

    print("Conversion OK, check the same path as the origin!")

if __name__ == "__main__":
    if not Path.exists(Path("temp")):
        os.mkdir("temp")
    
    if not Path.exists(Path("config.json")):
        setup()
        print("Setup complete!")

    with open("config.json", "r") as f:
        config = json.load(f)

    fixConfig(config)

    with open("config.json", "r") as f:
        config = json.load(f)

    print("Welcome, "+config["name"]+"!")

    fullConstruct = []

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
                    print("E: Something went wrong!")
                    print(modelReply[1])
                    continue
                else:
                    print(modelReply[1])
                    config["ltmemory"] += str(datetime.datetime.today()) + ": " + modelReply[1]

                    with open("config.json", "w") as f:
                        json.dump(config, f, indent= 2)
                    
                    fullConstruct = []
                    
                    continue

            elif msg[1] == "e":#exit
                print("Exiting! (Just a moment while I save the conversation...)")
                construct = "The following is a conversation between a chatbot and a user. Summarize the interaction briefly.\n"

                for i in fullConstruct:
                    construct += i["parts"][0]
                    construct += "\n"

                modelReply = gemrequest(construct)

                if modelReply[0] == False:
                    print("E: Something went wrong!")
                    print(modelReply[1])
                    continue
                else:
                    print(modelReply[1])
                    config["ltmemory"] += str(datetime.datetime.today()) + ": " + modelReply[1]

                    with open("config.json", "w") as f:
                        json.dump(config, f)

                    break

            elif msg[1] == "f":
                fullConstruct = []
                print("Memory cleared without saving!")
                continue

            elif msg[1] == "h":
                print("Slash commands: /clear, /exit, /force clear, /help")
                print("Use + to do tool usage")
                

        if msg[0] == "+":#Abandoned "smart" analysus (LLM by default)
            responseType = 0
        else:
            responseType = 1

        if responseType == 1:#LLM response
            filesList = []
            
            print("Any files you'd like to attach? Return empty to stop adding files.")
            print("Note: I'll extract text only from PDF files, and might compress images or convert them to understand them better!")
            
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

                        for j in range(len(reader.pages)):
                            text = reader.pages[j].extract_text()

                            construct += text

                        construct += "\n"

                    elif extension == "avif":

                        fileName = i.split("\\")[-1]

                        filePath = i[:-len(fileName)]

                        targetFormat = "webp"

                        fileName_noext = stripExt(fileName)

                        print("Running imagemagick. This might take a bit...")

                        subprocess.run(["magick", "mogrify", "-format", targetFormat, "-path", os.getcwd()+"\\temp", i])

                        file = genai.upload_file(path="temp\\"+fileName_noext+"."+targetFormat,display_name=fileName_noext)
                        filesUploadedList.append(genai.get_file(name=file.name))

                        Path.unlink(Path(os.getcwd()+"\\temp\\"+fileName_noext+"."+targetFormat))

                    else:
                        file = genai.upload_file(path=i,display_name=fileName)
                        filesUploadedList.append(genai.get_file(name=file.name))
            
            if len(fullConstruct) <= 0:
                fullConstruct = [{'role':'user','parts':\
                                [config["personality"] + "\n The user is named " + config["name"] + \
                                ".\n These are summaries of your previous conversations with the user for context: " + config["ltmemory"]\
                                +"\n Do not include a timestamp in your reply."]}]


            fullConstruct.append({'role':'user','parts':[construct]+filesUploadedList})

            modelReply = gemrequest(fullConstruct)

            if modelReply[0] == False:
                print("E: Something went wrong. This information may be of use:")
                print(modelReply[1])
            else:
                print(modelReply[1])

        elif responseType == 0:#Tool response
            listOfActions = ["0. video/audio conversion", "1. image conversion", "2. QR code scanning", "3. QR code generation", "4. Image generation", "5. audio transcription"]
            task = nltocommand.nltocommand(listOfActions, msg)

            if task == -1:
                print("E: Sorry, I couldn't figure out what to do.")
                continue
            elif task == 0:
                videoConvertInteractive()

            elif task == 1:
                imageConvertInteractive()

            elif task == 2:
                qreader = QReader()

                filePath = input("Drag file with QR code here: ")

                print("Decoding QR code...")

                image = cv2.cvtColor(cv2.imread(filePath), cv2.COLOR_BGR2RGB)
                decoded_text = qreader.detect_and_decode(image=image)

                if len(decoded_text) == 0:
                    print("QR code not found!")
                
                else:
                    for j in decoded_text:
                        print(j)
            
            elif task == 3:
                img = qrcode.make(input("Content of QR code: "))
                img.save("qrcode.png")
                print("Image saved to qrcode.png in the working directory!")
            
            elif task == 4:
                sdgen(input("Input prompt for image generation: "))
                print("Image saved to output.png on the working directory!")

            elif task == 5:
                filePath = input("Drag audio file to be transcribed here: ")
                if config["transcription"] == 0:
                    print("Sending Whisper transcription request...")
                    transcriptionResults = whispercf.cfwhisper(filePath)

                    if transcriptionResults == False:
                        print("E: Something went wrong while I tried to transcribe the file with Cloudflare AI. Please try again.")
                    else:
                        print(transcriptionResults)
                else:
                    print("Loading Whisper model...")
                    model = whisper.load_model(config["transcription"])

                    print("Transcribing...")
                    result = model.transcribe(filePath)

                    print(result["text"])

        else:
            print("E: Something went wrong while I tried to understand you. Please try again.")