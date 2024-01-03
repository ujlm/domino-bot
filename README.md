# Domino: A user-friendly conversational agent to improve decision support for online businesses
## Design  for an easy-to-use embedded chatbot to enhance DMN execution
An easy-to-implement, user-friendly chatbot that guides users through DMN models in a conversational manner.

# Features
## For developers
- Include the chatbot in any website by pasting 2 lines of code in your HTML
- Manage models and model metadata as-a-service
- DMN executor as-a-service
- Supports multiple concurrent sessions

## For end-users
- Select model from uploaded models by bot owner
- Communicate in natural typed language
- Implementation of NLU engine to recognize intents
- Word-to-number conversion (e.g. eighty-one becomes 81)
- Ability to go back if there was a mistake in the previous step
- Get explanation on why a certain decision is reached
- Exit current model
- Choose a new model
- Multiple scenarios supported (see thesis)
- Context-aware help system with action buttons

### Assumptions
- DMN model is correctly formatted for cDMN
- Predefined questions in annotations should be indicated with *?:

### Project Structure
- This repo: the chatbot itself, including:

| File          | Description                                                  |
| ------------- | -------------------------------------------------------------|
| app.py        | Flask endpoint (server)                                      |
| solver.py     | The logic of the chatbot                                     |
| intent_detecti| Rasa intent detection                                        |
| extract_contex| Get relevant information out of XML (dmn) file               |
| buttons.py    | Helper to display buttons                                    |
| /static/      | Frontent "client" script, styling and assets for local run   |
| /env/         | Configuration info for Firebase (don't show it in prod mode) |
| /embedded/    | Files to set up remote embedding, together with some examples|
| /demo_models/ | Valid DMN models to test the chatbot                         |

- The control panel (other repo)

- The NLU engine (other repo)

### Current issues
- cDMN currently doesn't support Dates (will hopefully change in the future)
- "What should..." scenario doesn't support multilevel inputs
- Special actions with numerical inputs not always supported


### Dependencies
See requirements.txt

a.o.
- Flask (backend server)
- React (client-side nodeJS framework)(open source, but developed by facebook)
- Firebase (storage, cloud hosting)(Google)
- Rasa (NLP module)
- Duckling (NLP module extension: entity extraction)(open source, but developed by facebook)
- cDMN IDP API for DMN models
- word2number: convert typed numbers to number format


## Run app (after setup)
Start flask server
```
venv\Scripts\activate
python app.py

```
And visit http://127.0.0.1:5000/

## Installation
### On Windows
#### 1. Install Python
Open powershell and run
```
python3
```

#### 2. Create virtual env
```
python3 -m venv venv
```

#### 3. Activate virtual env
```
venv\Scripts\activate
```

#### 4. Install requirements
```
pip install Flask==2.0 cdmn requests firebase_admin word2number bs4 lxml flask_cors regex
```

#### 5. Run app
```
python app.py
```

#### Troubleshooting
- IDP error in CDMN API: change relative path to absolute path
    * Create folder tmp and copy the absolute path
    * Convert backslash \ in this absolute path to / forward slash
    * Go to your venv folder and look for cdmn-.../API.py
    * Search and replace '/tmp/idp_temp.txt' with 'ABSOLUTE_URL/idp_temp.txt' 
- Problems with venv:
    * Use IDE venv OR
    * Run powershell as admin and execute:
        ```
        Set-ExecutionPolicy RemoteSigned
        ```

        If you would want to reset after running these scripts:
        ```
        Set-ExecutionPolicy Restricted
        ```
- Problems with remote hosting:
    * Set proper HOST in client-side script
    * Remote script can be found at: https://baleine.be/BCE/domino/dominodmnchatbot.js
    * Remote stylesheet can be found at: https://baleine.be/BCE/domino/dominodmnchatbot.css

## Credits:
This repo was used as starting point for this project:
https://github.com/hitchcliff/front-end-chatjs

This codepen was used for the loading animation:
https://codepen.io/livehelp/pen/VwajoBR


## Tests
#### Windows 11
- Local run control panel
- Local run chatbot
- Hosted control panel using ngrok
- Hosted chatbot using ngrok
- Remotely accessed control panel through ngrok url
- Remotely accessed chatbot through ngrok url

#### Windows 10
- Local run control panel
- Local run chatbot
	* With fix in cdmn API.py: relative to absolute path
- Remotely accessed control panel through ngrok url
- Remotely accessed chatbot through ngrok url