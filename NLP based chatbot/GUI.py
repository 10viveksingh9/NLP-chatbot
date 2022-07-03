import re
import nltk
from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()
import pickle
import numpy as np
import pyttsx3 as pp

#text to speech funtion
engine=pp.init()
voices = engine.getProperty('voices')
print(voices)
engine.setProperty('voices',voices[1].id)

def speak(word):
     engine.say(word)
     engine.runAndWait()

from keras.models import load_model
model = load_model('chatbot_model.h5')
import json
import random
intents = json.loads(open('intents.json').read())
words = pickle.load(open('words.pkl','rb'))
classes = pickle.load(open('classes.pkl','rb'))


def clean_up_sentence(sentence):
    # tokenize the pattern - splitting words into array
    sentence_words = nltk.word_tokenize(sentence)
    # stemming every word - reducing to base form
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words


# return bag of words array: 0 or 1 for words that exist in sentence
def bag_of_words(sentence, words, show_details=True):
    # tokenizing patterns
    sentence_words = clean_up_sentence(sentence)
    # bag of words - vocabulary matrix
    bag = [0]*len(words)  
    for s in sentence_words:
        for i,word in enumerate(words):
            if word == s: 
                # assign 1 if current word is in the vocabulary position
                bag[i] = 1
                if show_details:
                    print ("found in bag: %s" % word)
    return(np.array(bag))

def predict_class(sentence):
    # filter below  threshold predictions
    p = bag_of_words(sentence, words,show_details=False)
    res = model.predict(np.array([p]))[0]
    ERROR_THRESHOLD = 0.25
    results = [[i,r] for i,r in enumerate(res) if r>ERROR_THRESHOLD]
    # sorting strength probability
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({"intent": classes[r[0]], "probability": str(r[1])})
    return return_list

def getResponse(ints, intents_json):
    tag = ints[0]['intent']
    list_of_intents = intents_json['intents']
    for i in list_of_intents:
        if(i['tag']== tag):
            result = random.choice(i['responses'])
            break
    return result


import tkinter
from tkinter import *
def send():
    msg = EntryBox.get("1.0",'end-1c').strip()
    EntryBox.delete("0.0",END)

    if msg != '':
        ChatBox.config(state=NORMAL)
        ChatBox.insert(END, "You: " + msg + '\n\n')
        ChatBox.config(foreground="#A4A4BF", font=("Verdana", 12 ))
    
        ints = predict_class(msg)
        res = getResponse(ints, intents)
        
       
        ChatBox.insert(END, "Jarvis: " + res + '\n\n')
        speak(res)
        
            
        ChatBox.config(state=DISABLED)
        ChatBox.yview(END)
 

root = Tk()
root.title("Jarvis")
root.geometry("700x500")
root.resizable(width=TRUE, height=TRUE)
photo = PhotoImage(file = "chatbot.png")
root.iconphoto(False, photo)

#Create Chat window
ChatBox = Text(root, bd=0, bg="#132226", height="8", width="50", font="Arial",)

ChatBox.config(state=DISABLED)

#Bind scrollbar to Chat window
scrollbar = Scrollbar(root, command=ChatBox.yview, cursor="heart")
ChatBox['yscrollcommand'] = scrollbar.set

#Create Button to send message


send_btn = PhotoImage(file='submit.png')
img_label = Label(image=send_btn)
#img_label.pack(pady=20)
my_button = Button (root, image=send_btn, command=send, borderwidth=0)
my_button.pack(pady=20)
my_label= Label (root, text='')
my_label.pack(pady=20)

#Create the box to enter message
EntryBox = Text(root, bd=0, bg="#A4978E",width="29", height="5", font="Arial")
#EntryBox.bind("<Return>", send)


#Place all components on the screen
scrollbar.place(x=676,y=6, height=386)
ChatBox.place(x=6,y=6, height=386, width=670)
EntryBox.place(x=128, y=410, height=60, width=550)
my_button.place(x=6, y=410, height=60)

root.mainloop()






