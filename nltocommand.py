from geminillm import gemrequest
from cfllm import nsllmreq

def shouldIRespond(message):

    construct = "A chatbot has recieved the following message from a user: " + message + "\n"

    construct += "The chatbot can either try to use tools, or respond to the user directly with a multimodal LLM that can read images, documents, as well as videos and audio. Which should the bot do? Reply with 0 for tool usage (including video / image / audio conversion and image generation, as well as QR code generation and detection, and audio transcription), and 1 for LLM usage. Reply in a single number without text."

    try:
        gem = gemrequest(construct)[1]
    except:
        gem = nsllmreq("Only reply with a number. Do not contain any other text.",construct)

    try:
        return int(gem)
    except:
        return -1
def nltocommand(LoA, command):
    construct = ""

    construct += "The following is a list of actions a bot can take. \n"
    for i in LoA:
        construct += i
        construct += "\n"

    construct += "Look at the following message from a user and return only the number of the action that is most appropriate. Reply in a single number without text. \n"
    
    for i in command:
        construct += i
        construct += "\n"

    try:
        #Gemini API errored out on me once... not again.
        gem = gemrequest(construct)[1]
    except:
        #This might be less acuurate though.
        gem = nsllmreq("Only reply with a number. Do not contain any other text.",construct)

    try:
        return int(gem)
    except:
        return -1

def fileRequired(command):
    construct = "Will this command require a new file to process properly? Reply with 1 for yes and 0 for no. Reply in a single number without text. \n"

    construct += command

    try:
        gem = gemrequest(construct)[1]
    except:
        gem = nsllmreq("Only reply with a number. Do not contain any other text.",construct)

    try:
        return int(gem)
    except:
        return -1

if __name__ == "__main__":
    print(nltocommand(["0. Summary", "1. Conversation", "2. File conversion", "3. Transcription"], input("Input user message: ")))