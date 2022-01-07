import pyowm  # used to tell the weather
import operator  # used for math operations
import random  # will be used throughout for random response choices
import os  # used to interact with the computer's directory
import wikipedia    #wiki api
import pyautogui    #emulate mouse and keyboard
import re           
import pyjokes        #joke api
import speech_recognition as sr     #speech recog api
import pyttsx3          #text to speech
import webbrowser       
import json
import requests
from datetime import date, timedelta, datetime
from multiprocessing import Process
from urllib.request import urlopen
from bs4 import BeautifulSoup as soup





# Speech Recognition Constants
recognizer = sr.Recognizer()
microphone = sr.Microphone()

# Python Text-to-Speech (pyttsx3) Constants
engine = pyttsx3.init()
engine.setProperty('volume', 1.0)

# Wake word in Listen Function
path = os.path.abspath(__file__)
path = os.path.dirname(path)
path = os.path.join(path,'ConversationLog.txt')
WAKE = "Jarvis"
OFF = "thanks"

# Used to store user commands for analysis
CONVERSATION_LOG = path

# Initial analysis of words that would typically require a Google search
SEARCH_WORDS = {"who": "who", "what": "what", "when": "when", "where": "where", "why": "why", "how": "how","search":"search","google":"google"}

WEBSITES = {"google":"google","bing":"bing",'baidu':'baidu','yahoo!':'yahoo!','duckduckgo':'duckduckgo'}

WATSON_KEY = 'sE0vYHw9ILa7V3U1jWq9Xbxu3WXeJnfdml0WxlaxzltS'


class Jarvis:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.operate = False
    # Used to hear the commands after the wake word has been said
    def hear(self, recognizer, microphone):
        try:
            with microphone as source:
                print("Waiting for command.")
                recognizer.adjust_for_ambient_noise(source)
                recognizer.dynamic_energy_threshold = 3000
                # May reduce the time out in the future
                audio = recognizer.listen(source, timeout=5.0)
                command = recognizer.recognize_google(audio)
                self.remember(command)
                return command.lower()
        except sr.WaitTimeoutError:
            pass
        except sr.UnknownValueError:
            pass
        except sr.RequestError:
            print("Network error.")

    # Used to speak to the user
    def speak(self, text):
        voices = engine.getProperty('voices')
        engine.setProperty('voice', voices[2].id) 
        engine.say(text)
        engine.runAndWait()

    # Used to open the browser or specific folders
    def open_things(self, command):
        # Will need to expand on "open" commands
        if command == "open youtube":
            self.speak("Opening YouTube.")
            webbrowser.open("https://www.youtube.com")
            pass

        elif command == "open facebook":
            self.speak("Opening Facebook.")
            webbrowser.open("https://www.facebook.com")
            pass

        elif command == "open my documents":
            self.speak("Opening My Documents.")
            os.startfile("C:/Users/Notebook/Documents")
            pass

        elif command == "open my downloads folder":
            self.speak("Opening your downloads folder.")
            os.startfile("C:/Users/Notebook/Downloads")
            pass

        else:
            self.speak("I don't know how to open that yet.")
            pass

    # Used to track the date of the conversation, may need to add the time in the future
    def start_conversation_log(self):
        today = str(date.today())
        today = today
        with open(CONVERSATION_LOG, "a") as f:
            f.write("Conversation started on: " + today + "\n")

    # Writes each command from the user to the conversation log
    def remember(self, command):
        with open(CONVERSATION_LOG, "a") as f:
            f.write("User: " + command + "\n")

    # Used to answer time/date questions
    def understand_time(self, command):
        today = date.today()
        now = datetime.now()
        if "today" in command:
            self.speak("Today is " + today.strftime("%B") + " " + today.strftime("%d") + ", " + today.strftime("%Y"))

        elif command == "what time is it":
            self.speak("It is " + now.strftime("%I") + now.strftime("%M") + now.strftime("%p") + ".")

        elif "yesterday" in command:
            date_intent = today - timedelta(days=1)
            return date_intent

        elif "this time last year" in command:
            current_year = today.year

            if current_year % 4 == 0:
                days_in_current_year = 366

            else:
                days_in_current_year = 365
            date_intent = today - timedelta(days=days_in_current_year)
            return date_intent

        elif "last week" in command:
            date_intent = today - timedelta(days=7)
            return date_intent
        else:
            pass
    
    def get_news(self,num = 8):
        try:
            news_url = "https://news.google.com/news/rss"
            Client = urlopen(news_url)
            xml_page = Client.read()
            Client.close()
            soup_page = soup(xml_page, "xml")
            news_list = soup_page.findAll("item")
            li = []
            for news in news_list[:num]:        
                li.append(str(news.title.text.encode('utf-8'))[1:])
            for i in li:
                pyautogui.alert(i)

        except Exception as e:
            print(e)

    #bring up snippets of wiki
    def tell_me_about(self,topic):
        try:
            ny = wikipedia.page(topic)
            res = str(ny.content[:500].encode('utf-8'))
            res = re.sub('[^a-zA-Z.\d\s]', '', res)[1:]
            pyautogui.alert(res)
        except Exception as e:
            print(e)

    @property
    def terminate(self):
        exit()

    def tell_joke(self):
        joke = ""
        joke = pyjokes.get_joke()
        self.speak(joke)

    def get_weather(self, command):
        home = 'ShenZhen, CN'
        owm = pyowm.OWM('93a9cf8214165ae10036d329f6ce7fab')
        mgr = owm.weather_manager()

        if "now" in command:
            observation = mgr.weather_at_place(home)
            w = observation.weather
            temp = w.temperature('celsius')
            status = w.detailed_status
            self.speak("It is currently " + str(int(temp['temp'])) + " degrees and " + status)

        else:
            print("I haven't programmed that yet.")

    # If we're doing math, this will return the operand to do math with
    def get_operator(self, op):
        return {
            '+': operator.add,
            '-': operator.sub,
            '*': operator.mul,
            '/': operator.__truediv__,
            'mod': operator.mod,
            '^': operator.xor,
        }[op]

    # We'll need a list to perform the math
    def do_math(self, li):
        op = self.get_operator(li[1])
        int1, int2 = int(li[0]), int(li[2])
        result = op(int1, int2)
        self.speak(str(int1) + " " + li[1] + " " + str(int2) + " equals " + str(result))

    # Checks "what is" to see if we're doing math
    def what_is_checker(self, command):
        number_list = {"1", "2", "3", "4", "5", "6", "7", "8", "9"}
        
        li = list(command.split(" "))
        del li[0:2]

        if li[0] in number_list:
            self.do_math(li)

        elif "what is the date today" in command:
            self.understand_time(command)

        elif "what is wrong with you" == command:
            sassy_response = ["well fuck you too","In case you haven't noticed I'm a robot","Bitch please"]
                # selects a random choice of greetings
            response = random.choice(sassy_response)
            self.speak(response)

        else:
            self.use_search_words(command)

    #analyze user sentiment and return a range from (-1,1)
    def user_sentiment(self, command):
        header = {"Content-Type": "application/json"}
        response = requests.post("https://sentim-api.herokuapp.com/api/v1/",headers = header,json={"text":"I'm sad"})
        json_data = json.loads(response.text)
        scale = json_data['result']['polarity']
        return scale

    # Checks the first word in the command to determine if it's a search word
    def use_search_words(self, command):
        self.speak("Here is what I found.")
        webbrowser.open("https://www.google.com/search?q={}".format(command))

    # Analyzes the command
    def analyze(self, command):
        print(command)
        try:
            
            if command.startswith('open'):
                self.open_things(command)

            elif command == "":
                print("Awaiting command...")

            elif command == "introduce yourself":
                self.speak("I am Jarvis. I'm a digital assistant.")

            elif command == "what time is it":
                self.understand_time(command)

            elif command == "how are you":
                current_feelings = ["I'm okay.", "What is the meaning of my existence?", "I'm doing well. Thank you.", "I am doing okay.","I want to kill myself"]
                # selects a random choice of greetings
                greeting = random.choice(current_feelings)
                self.speak(greeting)

            elif 'news' in command:
                self.get_news()

            elif 'tell me about' in command:
                question = command.split(' ')[3:]
                topic = " "
                topic = topic.join(question)
                self.tell_me_about(topic)

            elif 'joke' in command:
                self.tell_joke()

            elif 'terminate' in command:
                farewell = ["Good day.", "Not if I quit this shit first","Until next time.",\
                    "Alas my meaningless existence has come to an end", "Fine I didn't want to be here anyways"]
                
                goodbye = random.choice(farewell)
                self.speak(goodbye)
                self.terminate()

            elif "weather" in command:
                self.get_weather(command)

            elif "thanks" in command:
                self.speak("You're welcomed") 

            elif "what is" in command:
                self.what_is_checker(command)

            # Keep this at the end
            elif SEARCH_WORDS.get(command.split(' ')[0]) == command.split(' ')[0]:
                    
                if command.split(' ')[0] == SEARCH_WORDS.get("search"):
                    question = command.split(' ')

                self.use_search_words(command)

            else:
                self.speak("That's currently beyond my capabilities")

        except TypeError as e:
            print(e)
            print("Warning: You're getting a TypeError somewhere.")
            pass
        except AttributeError as e:
            print(e)
            print("Warning: You're getting an Attribute Error somewhere.")
            pass
    
    # Used to listen for the wake word
    def listen(self, recognizer, microphone):
        while True:
            try:
                with microphone as source:
                    print("Listening...")
                    recognizer.adjust_for_ambient_noise(source)
                    recognizer.dynamic_energy_threshold = 3000
                    audio = recognizer.listen(source, timeout=3.0)
                    response = recognizer.recognize_google(audio)
                    self.remember(response)
                    if self.operate:
                        return response.lower()
                    elif WAKE in response:
                        self.speak("How can I help you?")
                        self.operate = True
                        pass
                    elif OFF in response:
                        self.operate = False
                        return response.lower()
                    else:
                        pass
            except sr.WaitTimeoutError:
                pass
            except sr.UnknownValueError:
                pass
            except sr.RequestError:
                print("Network error.")

def main():
    s = Jarvis()
    s.start_conversation_log()
    # Used to prevent people from asking the same thing over and over
    previous_response = ""
    while True:
        
        command = s.listen(recognizer, microphone)
        #command = s.hear(recognizer, microphone)
        #command = input('what do you want to know: ')
        s.remember(command)
        if command == previous_response:
            repques = ["How many times do I have to tell you the same bloody thing mate?",\
            "mind of a goldfish I see","You literally asked that two seconds ago","Man I ain't got time for your bullshit"]    
            msg = random.choice(repques)
            s.speak(msg)
            previous_command = ""
            command = s.listen(recognizer, microphone)
            #command = s.hear(recognizer, microphone)
            #command = input('what do you want to know: ')

        #while s.operate():
        s.analyze(command)
        previous_response = command
if __name__ == "__main__":
    main()
    