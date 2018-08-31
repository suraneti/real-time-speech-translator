## Intro

Real time speech to text with multi language translation by using Google Speech-to-Text API and Google Text-Translation API,
this version will recognize Thai speech and translate to English and Deutsch. (If you want another language just change in code)

## Dependencies

Python3, google-cloud-speech, google-cloud-translate, opencv-python, pyaudio, pillow

### Getting started

1. Clone this project and create virtualenv (recommended) and activate virtualenv.
    ```
    virtaulenv -p python3 env
 
    Linux
    source env/bin/activate
    
    Windows
    env\Scripts\activate
    ```
    
2. Install require dependencies.
    ```
    pip install -r requirements.txt
    ```
    
3. You must sign up Google Cloud and create project with Google Speech-to-Text API and Google Text-Translation API and
download json secret key to use with google api (*just following google quick start).


4. Run code and speech (have fun).
    ```
    python transcribe_streaming_mic.py
    ```
  
ps. you must load json secret key in every session then you can run script (if you dont it will error).

ps2. if you dont understand how to load json secret key in session just follow google cloud api quick start.
