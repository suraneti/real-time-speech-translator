# Real Time Speech Translator

> implement with Google Cloud Service

## Intro

Real time speech to text with multi language translation by using Google Speech-to-Text API and Google Text-Translation API,
this version will recognize Thai speech and translate to English and Deutsch. (If you want another language just change in code)

## Dependencies

Python3, google-cloud-speech, google-cloud-translate, opencv-python, pyaudio, pillow

## Getting started

1. Clone this project and create virtualenv (recommended) and activate virtualenv.
    ```
    # Create virtualenv
    virtualenv -p python3 env
 
    # Linux/MacOS
    source env/bin/activate
    
    # Windows
    env\Scripts\activate
    ```
    
2. Install require dependencies.
    ```
    pip install -r requirements.txt
    ```
    
3. You must sign up Google Cloud account and create project with [Google Speech-to-Text API](https://cloud.google.com/speech-to-text/) and [Google Text-Translation API](https://cloud.google.com/translate/) and download json secret key to use with google api (just following google quick start [here](https://cloud.google.com/iam/docs/quickstart-client-libraries)).


4. Run code and speech (have fun).
    ```
    python transcribe_streaming_mic.py
    ```
  
### Caution!

You must load json secret key in every session then you can run a script (if you dont it will error).  
If you don't know how to load json secret key in session just follow google cloud api quick start [here](https://cloud.google.com/iam/docs/quickstart-client-libraries).
