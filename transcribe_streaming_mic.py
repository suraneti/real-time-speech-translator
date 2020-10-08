#!/usr/bin/env python

# Copyright 2017 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Google Cloud Speech API sample application using the streaming API.

NOTE: This module requires the additional dependency `pyaudio`. To install
using pip:

    pip install pyaudio

Example usage:
    python transcribe_streaming_mic.py
"""

# [START import_libraries]
from __future__ import division

import numpy as np
import pyaudio
import re
import sys
import threading
import time

from PIL import ImageFont, ImageDraw, Image
from google.cloud import translate_v2 as translate
from google.cloud import speech_v1 as speech
from google.cloud.speech_v1 import enums
from google.cloud.speech_v1 import types
from six.moves import queue
# [END import_libraries]

# Audio recording parameters
RATE = 16000
CHUNK = int(RATE / 10)  # 100ms

# Instantiates a client
translate_client = translate.Client()

raw_input_data = 'listening...'
previous_raw_input_data = None
translated_data = None


class MicrophoneStream(object):
    """Opens a recording stream as a generator yielding the audio chunks."""
    
    def __init__(self, rate, chunk):
        
        self._rate = rate
        self._chunk = chunk

        # Create a thread-safe buffer of audio data
        self._buff = queue.Queue()
        self.closed = True

    def __enter__(self):
        
        self._audio_interface = pyaudio.PyAudio()
        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paInt16,
            # The API currently only supports 1-channel (mono) audio
            # https://goo.gl/z757pE
            channels=1, rate=self._rate,
            input=True, frames_per_buffer=self._chunk,
            # Run the audio stream asynchronously to fill the buffer object.
            # This is necessary so that the input device's buffer doesn't
            # overflow while the calling thread makes network requests, etc.
            stream_callback=self._fill_buffer,
        )

        self.closed = False

        return self

    def __exit__(self, type, value, traceback):
        
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True
        # Signal the generator to terminate so that the client's
        # streaming_recognize method will not block the process termination.
        self._buff.put(None)
        self._audio_interface.terminate()

    def _fill_buffer(self, in_data, frame_count, time_info, status_flags):
        """Continuously collect data from the audio stream, into the buffer."""
        
        self._buff.put(in_data)
        return None, pyaudio.paContinue
    
    def _clear_buffer(self):
        
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        # self.closed = True
        # Signal the generator to terminate so that the client's
        # streaming_recognize method will not block the process termination.
        self._buff.put(None)
        self._audio_interface.terminate()

    def generator(self):

        while not self.closed:
            # Use a blocking get() to ensure there's at least one chunk of
            # data, and stop iteration if the chunk is None, indicating the
            # end of the audio stream.
            chunk = self._buff.get()
            if chunk is None:
                return
            data = [chunk]

            # Now consume whatever other data's still buffered.
            while True:
                try:
                    chunk = self._buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break

            yield b''.join(data)
# [END audio_stream]

def initial_video():

    import cv2
    
    # Inital text translation
    text_translation()

    # Start microphone stream threading
    threading.Thread(target=main).start()

    # Set camera device
    camera = cv2.VideoCapture(0)
    # Set camera width
    camera.set(3,1200)
    # Set camera height
    camera.set(4,1200)

    # Set font
    fontpath = "Kanit-Regular.ttf"
    font = ImageFont.truetype(fontpath, 32)

    while True:
        ret, frame = camera.read()
        if ret:
            if translated_data:
                # Draw background of text
                cv2.rectangle(frame, (0, 0), (1400, 40), (0,0,0), -1)
                cv2.rectangle(frame, (70, 515), (1200, 545), (0,0,0), -1)                    
                cv2.rectangle(frame, (70, 555), (1200, 585), (0,0,0), -1)
                cv2.rectangle(frame, (70, 595), (1200, 625), (0,0,0), -1)
                cv2.rectangle(frame, (70, 635), (1200, 665), (0,0,0), -1) 

                # Set draw text frame
                img_pil = Image.fromarray(frame)
                draw = ImageDraw.Draw(img_pil)

                # Write microphone input
                draw.text((100, 505), "Microphone: " + raw_input_data, font=font, fill=(255,255,255,0))
                # Write Thai text
                draw.text((75, 545),  "TH: " + translated_data['th'], font=font, fill=(255,255,255,0))
                # Write English text
                draw.text((75, 585),  "EN: " + translated_data['en'], font=font, fill=(255,255,255,0))
                # Write Deutsch text     
                draw.text((75, 625),  "DE: " + translated_data['de'], font=font, fill=(255,255,255,0))
                # Write demo word text
                draw.text((20, -5),  "Demo", font=font, fill=(255,255,255,0))
                # Write timestamp
                draw.text((910, -5), time.strftime("%Y/%m/%d %H:%M:%S %Z", time.localtime()), font=font, fill=(255,255,255,0))   
                # Write all text into frame
                frame = np.array(img_pil)
                # Draw green circle
                frame = cv2.circle(frame, (85, 530), 6, (0,255,0), -1)
               
            # Display the resulting frame
            cv2.imshow('Speech-to-Text Demo', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    camera.release()
    cv2.destroyAllWindows()

def text_translation(input_text="Hello"):

    # Translates text input to English
    translation_en = translate_client.translate(input_text, target_language='en')
    # Translates text input to Deutsch
    translation_de = translate_client.translate(translation_en['translatedText'], target_language='de')

    print(u'Text input: {}'.format(input_text))
    print(u'Translation to english: {}'.format(translation_en['translatedText']))
    print(u'Translation to deutsch: {}'.format(translation_de['translatedText']))

    # Set global variable
    global translated_data
    global previous_raw_input_data
    translated_data = {'th': input_text, 'en': translation_en['translatedText'].replace("&#39;", "'"), 'de': translation_de['translatedText'].replace("&#39;", "'")}
    previous_raw_input_data = input_text
 
def listen_print_loop(responses):
    """Iterates through server responses and prints them.

    The responses passed is a generator that will block until a response
    is provided by the server.

    Each response may contain multiple results, and each result may contain
    multiple alternatives; for details, see https://goo.gl/tjCPAU.  Here we
    print only the transcription for the top alternative of the top result.

    In this case, responses are provided for interim results as well. If the
    response is an interim one, print a line feed at the end of it, to allow
    the next result to overwrite it, until the response is a final one. For the
    final one, print a newline to preserve the finalized transcription.
    """

    num_chars_printed = 0
    for response in responses:
        if not response.results:
            continue

        # The `results` list is consecutive. For streaming, we only care about
        # the first result being considered, since once it's `is_final`, it
        # moves on to considering the next utterance.
        result = response.results[0]
        if not result.alternatives:
            continue

        # Display the transcription of the top alternative.
        transcript = result.alternatives[0].transcript
        print('Microphone input: ' + transcript)

        # Assign raw input
        global raw_input_data
        raw_input_data = transcript

        # Display interim results, but with a carriage return at the end of the
        # line, so subsequent lines will overwrite them.
        #
        # If the previous result was longer than this one, we need to print
        # some extra spaces to overwrite the previous result
        overwrite_chars = ' ' * (num_chars_printed - len(transcript))

        # if len(raw_input_data) >= 15:
        #     sys.stdout.write(transcript + overwrite_chars + '\r')
        #     sys.stdout.flush()

        #     num_chars_printed = len(transcript)

        #     print('Send to translate !')

        #     text_translation(transcript + overwrite_chars)

        ########################
        #      NEW VERSION     #
        ########################
        print(result.stability)
        if result.stability >= 0.899:
            responses = transcript + overwrite_chars
            text_translation(responses)
            MicrophoneStream(RATE, CHUNK)._clear_buffer()
        else:
            sys.stdout.write(transcript + overwrite_chars + '\r')
            sys.stdout.flush()
            
            num_chars_printed = len(transcript)

        ########################
        #      OLD VERSION     #
        ########################
        # if not result.is_final:
        #     sys.stdout.write(transcript + overwrite_chars + '\r')
        #     sys.stdout.flush()

        #     num_chars_printed = len(transcript)

        # else:
        #     print(transcript + overwrite_chars)
        #     resp = transcript + overwrite_chars
        #     text_translation(resp)

            # Exit recognition if any of the transcribed phrases could be
            # one of our keywords.
            if re.search(r'\b(exit|quit)\b', transcript, re.I):
                print('Exiting..')
                break

def main():
    # See http://g.co/cloud/speech/docs/languages
    # for a list of supported languages.
    # The language code you speak.
    language_code = 'th-TH'  # a BCP-47 language tag

    client = speech.SpeechClient()
    config = types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=RATE,
        language_code=language_code)
    streaming_config = types.StreamingRecognitionConfig(
        config=config,
        interim_results=True)

    # Initial loop value
    rounds = 1
    while True:
        try:
            print('streaming loop :' + str(rounds))
            with MicrophoneStream(RATE, CHUNK) as stream:
                audio_generator = stream.generator()
                # Create request data
                requests = (types.StreamingRecognizeRequest(audio_content=content) for content in audio_generator)
                # POST data to google cloud speech
                responses = client.streaming_recognize(streaming_config, requests)
                # Now, put the transcription responses to use.
                listen_print_loop(responses)
        except Exception as err:
            print(err)
            rounds += 1


if __name__ == '__main__':
    initial_video()
