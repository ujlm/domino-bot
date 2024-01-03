import os
import re
import requests
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS, cross_origin
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from intent_detection import intent_detection
import buttons

from solver import get_res, Model
app = Flask(__name__)

# Enable CORS
# TODO In production environment: work with whitelisted domain names only
# (need to be registered in control panel)
cors = CORS(app)
#app.config['CORS_HEADERS'] = 'Content-Type'


sessions = {}
models =  {}

def fetchModelList(apikey):
    ## FIREBASE
    # Fetch the service account key JSON file contents
    try:
        ref = db.reference('users/' + str(apikey) + '/models')
        data = ref.get()
        m = []
        for key in data.keys():
            m.append(data[key])
        return m
    except Exception as e:
        print(e)
        print('Invalid API key')
        return 'error'
    ### END FIREBASE


@app.get("/")
def index_get():
    print('User conn')
    return render_template("base.html")


@app.post("/predict")
@cross_origin()
def predict():
    global sessions
    global models

    req_body = request.get_json()
    # Check session
    sessionId = req_body.get("sessionId").strip()
    session = getSession(sessionId)
    # Get message from client
    text = req_body.get("message").strip()
    # Get business client API key
    auth = request.get_json().get("apikey")

    # Convert to intent if it detected
    text = intent_detection(text)

    if text.lower() in ("exit", "choose new model", "again", "quit", "new model", "restart", "stop", "end") or (text.lower() in ('hi', 'greet') and session["chosen_file"] != ""):
        session["chosen_file"] = ""
        try:
            response = get_res(session["m"],"RESET")
        except:
            response = "Something went wrong"
        return showModels(auth)


    if session["chosen_file"] == "":
        if session["selection_sent"]:
            if text[:6] == "file__":
                f = models[auth][int(text[6:])]["file"]
                print("model set: " + f["name"])
                session["m"] = setModel(f["name"], f["url"])
                session["chosen_file"] = models[auth][int(text[6:])]["file"]
                text = "ok"
        else:
            # First message, so init api key
            models[auth] = fetchModelList(auth)
            if models[auth] != 'error':  
                # Then,  load models
                session["selection_sent"] = True
                return showModels(auth)
            else:
                return "Firebase auth failure"
    
    response = "I'm sorry, the chosen model is invalid." + buttons.create_button("exit", "Choose another model")
    if session["m"] != None:
        try:
            session["m"]
        except NameError:
            response = {"Hi I'm DaBot. Type 'start' to begin."}
        except:
            response = {"The model is invalid"}
        else:
            try:
                response = get_res(session["m"], text)
            except Exception as e:
                print(e)
                response = "I'm sorry, something went wrong."
    message = {"answer": response}
    return jsonify(message)


@app.post("/target")
@cross_origin()
def target():
    req_body = request.get_json()
    sessionId = req_body.get("sessionId").strip()
    session = getSession(sessionId)
    type = req_body.get("type").strip()
    text = req_body.get("message").strip()
    print("Fetch options for " + type)
    print("Message received: " + text)
    y = get_res(session["m"], "GET ALL Y")
    if text == "" or text == "no-value" or text == "..." or text == "loading...":
        text = y[0]
    x = get_res(session["m"], "GET ALL X FOR:" + text)
    message = {"options": {"x": x, "y": y}}
    return jsonify(message)


###### Functions ######
def getSession(sessionId):
    global sessions
    session = {}
    if sessionId not in sessions:
        # Create session
        sessions[sessionId] = {
            "chosen_file": "",
            "selection_sent": False,
            "m": None
        }    
    return sessions[sessionId]


def setModel(filename: str, fileUrl: str):
    # If the file is on a remote location, download it in temp folder (how to automatically remove? -> on session_timeouts)
    if(is_url(fileUrl)):
        if(download(fileUrl, filename, dest_folder="temp")):
            filename = "temp/" + filename.split("/")[-1]
    print("Loading " + filename)
    try:
        m = Model(filename)
    except Exception as e:
        print("model error")
        print(e)
        m = None
    return m

def showModels(auth):
    global selection_sent
    global models

    response = "Hi I am Domino, how can I help you?<br/>"
    for model in models[auth]:
        response += "<button class='modelSelectBtn' data-target='%s'><span class='title'>%s</span>&nbsp;<span class='description'>%s</span></button>"%("file__" + str(models[auth].index(model)), model['title'], model['description'])
    message = {"answer": response}
    return jsonify(message)


#### Helpers ####
def download(url: str, filename: str, dest_folder: str):
    file_path = os.path.join(dest_folder, filename)
    if not os.path.exists(file_path):
        # Don't download model that is already downloaded
        print("Download model, as it is not downloaded yet")
        if not os.path.exists(dest_folder):
            os.makedirs(dest_folder)  # create folder if it does not exist

        filename = filename.split('/')[-1].replace(" ", "_")  # be careful with file names

        r = requests.get(url, stream=True)
        if r.ok:
            print("saving to", os.path.abspath(file_path))
            with open(file_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024 * 8):
                    if chunk:
                        f.write(chunk)
                        f.flush()
                        os.fsync(f.fileno())
        else:  # HTTP status code 4XX/5XX
            print("Download failed: status code {}\n{}".format(r.status_code, r.text))
            return False
    return True


def is_url(location: str):
    regex = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return re.match(regex, location) is not None


if __name__ == "__main__":
    cred = credentials.Certificate('env/dmnbot-2b8f9-firebase-adminsdk-89oim-9c59d955c0.json')
    # Initialize the app with a service account, granting admin privileges
    firebase_admin.initialize_app(cred, {
        'databaseURL': "https://dmnbot-2b8f9-default-rtdb.europe-west1.firebasedatabase.app/"
    })

    app.run(debug=False, host='0.0.0.0')