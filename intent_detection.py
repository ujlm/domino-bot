import requests
import json

# This function sends every message of the user to the NLP module and then returns a json containing the top intent
# and all detected entities, if there are any
# In order for this module to work properly, the server should be running and accessible
def get_intent(text):
    url = "https://rasa-nlu-template.herokuapp.com/model/parse"
    userinput = {
        "text": text,
        "message_id": "domino"
    }

    response = requests.post(url, json=userinput, timeout=1.2)
    return json.loads(response.text)

def intent_detection(text):
    intents = ["greet", "back", "end"]
    threshold = 0.90
    
    try:
        print('Get intent')
        user_intent = get_intent(text)["intent"]
    except:
        return text

    if(user_intent["name"] in intents and user_intent["confidence"] > threshold):
        print("%s converted to %s"%(text, user_intent["name"]))
        return user_intent["name"]
    else:
        return text