#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import html2text
import sys
from TTS.api import TTS
import pyaudio
import wave
import logging


def setupLogger():
    logger = logging.getLogger(__name__)
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    return logger

logger = setupLogger()

def page2text(url):
    # Send a GET request
    response = requests.get(url)

    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the main content by searching for the appropriate HTML element.
    # This will depend on the specific structure of the web page.
    # In this example, we will look for the <body> tag, but you might need to adjust this.
    main_content = soup.find('body')

    # Create an html2text object
    h = html2text.HTML2Text()

    # Ignore converting links into markdown
    h.ignore_links = True

    # Convert the HTML to Markdown
    markdown = h.handle(main_content.prettify())

    # Return the markdown
    return markdown

def text2speach(text: str, output: str):
    # Reference documentation https://tts.readthedocs.io/en/latest/inference.html
    # List available 🐸TTS models and choose the first one
    # model_name = TTS.list_models()[0]
    # use `tts --list_models`
    model_name = 'tts_models/en/ljspeech/tacotron2-DDC'
    # Init TTS
    tts = TTS(model_name)
    # Text to speech to a file
    logger.debug("Available speakers: %s", tts.speakers)
    logger.debug("Available languages: %s", tts.languages)
    tts.tts_to_file(text=text, file_path=output)


def play_audio(wav_filename: str):
    # Set chunk size of 1024 samples per data frame
    chunk = 1024

    # Open the sound file
    with wave.open(wav_filename, 'rb') as wf:

        # Create an interface to PortAudio
        p = pyaudio.PyAudio()

        # Open a .Stream object to write the WAV file to
        # 'output = True' indicates that the sound will be played rather than recorded
        stream = p.open(format = p.get_format_from_width(wf.getsampwidth()),
                        channels = wf.getnchannels(),
                        rate = wf.getframerate(),
                        output = True)

        # Read data in chunks
        data = wf.readframes(chunk)

        # Play the sound by writing the audio data to the stream
        while data != '':
            stream.write(data)
            data = wf.readframes(chunk)

        # Close and terminate the stream
        stream.close()
        p.terminate()


url = sys.argv[1]
logger.debug("URL: %s", url)
text = page2text(url)
logger.debug("Page text: %s", text)
text2speach(text, "output.wav")
logger.info("Speaking: %s", text)
play_audio("output.wav")
