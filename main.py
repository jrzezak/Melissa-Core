import os
import re
import sys
import random
import sqlite3
from datetime import datetime

import yaml
import pywapi
import tweepy
import pyaudio
import wikipedia
from tweepy import OAuthHandler
import speech_recognition as sr
from selenium import webdriver

profile = open('profile.yaml')
profile_data = yaml.safe_load(profile)
profile.close()

# Functioning Variables
name = profile_data['name']
music_path = profile_data['music_path']
city_name = profile_data['city_name']
city_code = profile_data['city_code']
proxy_username = profile_data['proxy_username']
proxy_password = profile_data['proxy_password']
access_token = profile_data['twitter']['access_token']
access_token_secret = profile_data['twitter']['access_token_secret']
consumer_key = profile_data['twitter']['consumer_key']
consumer_secret = profile_data['twitter']['consumer_secret']

conn = sqlite3.connect('memory.db')

def tts(message):
    """
    This function takes a message as an argument and converts it to speech depending on the OS.
    """
    if sys.platform == 'darwin':
        tts_engine = 'say'
        return os.system(tts_engine + ' ' + message)
    elif sys.platform == 'linux2' or sys.platform == 'linux':
        tts_engine = 'espeak'
        return os.system(tts_engine + ' "' + message + '"')

def music_player(file_name):
    """
    This function takes the name of a music file as an argument and plays it depending on the OS.
    """
    if sys.platform == 'darwin':
        player = "afplay '" + file_name + "'"
        return os.system(player)
    elif sys.platform == 'linux2' or sys.platform == 'linux':
        player = "mpg123 '" + file_name + "'"
        return os.system(player)

tts('Welcome ' + name + ', systems are now ready to run. How can I help you?')

while True:
    speech_text = None
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Say something!")
        audio = r.listen(source)

    try:
        speech_text = r.recognize_google(audio).lower().replace("'", "")
        print("Melissa thinks you said '" + speech_text + "'")
    except sr.UnknownValueError:
        print("Melissa could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))

    def check_message(check):
        """
        This function checks if the items in the list (specified in argument) are present in the user's input speech.
        """
        if speech_text == None:
            sys.exit()
        else:
            words_of_message = speech_text.split()
            if set(check).issubset(set(words_of_message)):
                return True
            else:
                return False

    def mp3gen():
        """
        This function finds all the mp3 files in a folder and it's subfolders and returns a list.
        """
        music_list = []
        for root, dirs, files in os.walk(music_path):
            for filename in files:
                if os.path.splitext(filename)[1] == ".mp3":
                    music_list.append(os.path.join(root, filename.lower()))
        return music_list

    if check_message(['who','are', 'you']):
        messages = ['I am Melissa, your lovely personal assistant.',
        'Melissa, didnt I tell you before?',
        'You ask that so many times! I am Melissa.']
        tts(random.choice(messages))

    elif check_message(['how', 'i', 'look']) or check_message(['how', 'am', 'i']):
        replies =['You are goddamn handsome!', 'My knees go weak when I see you.', 'You are sexy!', 'You look like the kindest person that I have met.']
        tts(random.choice(replies))

    elif check_message(['all', 'note']) or check_message(['all', 'notes']) or check_message(['notes']):
        tts('Your notes are as follows:')

        cursor = conn.execute("SELECT notes FROM notes")

        for row in cursor:
            tts(row[0])

        conn.commit()
        conn.close()

    elif check_message(['note']):
        words_of_message = speech_text.split()
        words_of_message.remove('note')
        cleaned_message = ' '.join(words_of_message)

        conn.execute("INSERT INTO notes (notes, notes_date) VALUES (?, ?)", (cleaned_message, datetime.strftime(datetime.now(), '%d-%m-%Y')))
        conn.commit()
        conn.close()

        tts('Your note has been saved.')

    elif check_message(['define']):
        words_of_message = speech_text.split()
        words_of_message.remove('define')
        cleaned_message = ' '.join(words_of_message)

        try:
            wiki_data = wikipedia.summary(cleaned_message, sentences=5)

            regEx = re.compile(r'([^\(]*)\([^\)]*\) *(.*)')
            m = regEx.match(wiki_data)
            while m:
                wiki_data = m.group(1) + m.group(2)
                m = regEx.match(wiki_data)

            wiki_data = wiki_data.replace("'", "")
            tts(wiki_data)
        except wikipedia.exceptions.DisambiguationError as e:
            tts('Can you please be more specific? You may choose something from the following.')
            print("Could not request results from Google Speech Recognition service; {0}".format(e))

    elif check_message(['time']):
        tts("The time is " + datetime.strftime(datetime.now(), '%H:%M:%S'))

    elif check_message(['tell', 'joke']):
        jokes = ['What happens to a frogs car when it breaks down? It gets toad away.', 'Why was six scared of seven? Because seven ate nine.', 'What is the difference between snowmen and snowwomen? Snowballs.', 'No, I always forget the punch line.']
        tts(random.choice(jokes))

    elif check_message(['who', 'am', 'i']):
        tts('You are ' + name + ', a brilliant person. I love you!')

    elif check_message(['where', 'born']):
        tts('I was created by a magician named Tanay, in India, the magical land of himalayas.')

    elif check_message(['how', 'are', 'you']):
        tts('I am fine, thank you.')

    elif check_message(['my', 'tweets']):
        # This needs formatting, not currently fit to be run.
        tts('Loading your tweets, ' + name)
        auth = OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(auth)
        timeline = api.user_timeline(count=10, include_rts=True)

    elif check_message(['play', 'music']) or check_message(['music']):
        try:
            music_listing = mp3gen()
            music_playing = random.choice(music_listing)
            tts("Now playing: " + music_playing)
            music_player(music_playing)
        except IndexError as e:
            tts('No music files found.')
            print("No music files found: {0}".format(e))

    elif check_message(['play']):
        words_of_message = speech_text.split()
        words_of_message.remove('play')
        cleaned_message = ' '.join(words_of_message)
        music_listing = mp3gen()

        for i in range(0, len(music_listing)):
            if cleaned_message in music_listing[i]:
                music_player(music_listing[i])

    elif check_message(['how', 'weather']):
        weather_com_result = pywapi.get_weather_from_weather_com(city_code)
        weather_result = "Weather.com says: It is " + weather_com_result['current_conditions']['text'].lower() + " and " + weather_com_result['current_conditions']['temperature'] + "degree celcius now in " + city_name
        tts(weather_result)

    elif check_message(['connect', 'proxy']):
        tts("Connecting to proxy server.")
        browser = webdriver.Firefox()
        browser.get('http://10.1.1.9:8090/httpclient.html')

        id_number = browser.find_element_by_name('username')
        password = browser.find_element_by_name('password')

        id_number.send_keys(proxy_username)
        password.send_keys(proxy_password)

        browser.find_element_by_name('btnSubmit').click()


    elif check_message(['bye']) or check_message(['goodbye']):
        tts('Goodbye!')

    elif check_message(['open', 'Firefox']):
        tts('Aye aye captain, opening Firefox')
        webdriver.Firefox()

    else:
        tts('I dont know what that means!')
