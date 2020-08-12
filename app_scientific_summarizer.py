#!/usr/bin/env python
# coding: utf-8

# In[1]:

# required modules
import streamlit as st 
from PIL import Image
import numpy as np
import os
import pandas as pd
from numpy import asarray
from nltk.tokenize import sent_tokenize
import xml.etree.ElementTree as ET
from transformers import *
from summarizer import Summarizer
import bs4
import requests
import SessionState
from urllib.parse import urlparse
import urllib.request, urllib.error
import pyttsx3
import keyboard

### App title
st.title("... Scientific Content Summarizer ...")
st.title("")
st.title("")

# session = SessionState.get(run_id=0)
def main():
    # session run id - needed to clear the widgets cached values from the previous user iteration - see Reset button below in the sidebar section
    # session = SessionState.get(run_id=0)
    session = SessionState.get(run_id=0)

    # --- Functions def section BEGIN --

    # Function to get text from URL page
    def url_get_text(web_url_text):
        res = requests.get(web_url_text)
        res.raise_for_status()
        content = bs4.BeautifulSoup(res.text,"html.parser")
        title = content.title.text.split(' - Wikipedia')[0]
        with open("cache.txt", 'w+',encoding='utf-8') as f:
            for i in content.select('p'):
                f.write(i.getText())
        f = open("cache.txt", "r",encoding='utf-8')
        text = f.read()
        text = remove_text_inside_brackets(text)
        f.close()
        return text, title


    # Function to parse a XML file 
    def tree(path):
        tree = ET.parse(path)  
        root = tree.getroot()
        title = root[0].text
        textbody=[]
        for elem in root:
            for subelem in elem:
                textbody.append(subelem.text)
        separator = ''
        text = separator.join(textbody)
        text = remove_text_inside_brackets(text)
        return text,title

    # Function to extract text from a TXT file
    
    def text_file(path):
        text = path.getvalue()
        text = text.replace('\n',' ')
        text = text.replace('al.','al')
        text = remove_text_inside_brackets(text)
        title = sent_tokenize(text)[0]
        title = title.replace('.','')
        return text, title

    # Function to remove square brackets and text within (e.g. citation number) from text in, if any
    def remove_text_inside_brackets(text, brackets="[]()"):
        count = [0] * (len(brackets) // 2) # count open/close brackets
        saved_chars = []
        for character in text:
            for i, b in enumerate(brackets):
                if character == b: # found bracket
                    kind, is_close = divmod(i, 2)
                    count[kind] += (-1)**is_close # `+1`: open, `-1`: close
                    if count[kind] < 0: # unbalanced bracket
                        count[kind] = 0  # keep it
                    else:  # found bracket to remove
                        break
            else: # character is not a [balanced] bracket
                if not any(count): # outside brackets
                    saved_chars.append(character)
        return ''.join(saved_chars)   

    def re_run():
        keyboard.press_and_release('shift+ctrl+r')

    # # Function to read summary lines
    @st.cache(suppress_st_warning=True, show_spinner=False)
    def say(text):
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        engine.setProperty('voice', voices[0].id)
        rate = engine.getProperty('rate')
        engine.setProperty('rate', rate+0)
        def onWord(name, location, length): 
            print ('word', name, location, length)
            if keyboard.is_pressed("esc"):
                engine.stop()
                engine.endLoop()
                engine.destroy()
                session.run_id += 1
        engine.connect('started-word', onWord)
        engine.say(text)
        engine.runAndWait()

    # Function to read summary lines (the interruption command does not work well)
    # @st.cache(persist = False,suppress_st_warning=True, show_spinner=False)
    # def say(text):
    #     engine = pyttsx3.init()
    #     voices = engine.getProperty('voices')
    #     engine.setProperty('voice', voices[0].id)
    #     rate = engine.getProperty('rate')
    #     engine.setProperty('rate', rate+0)
    #     try: 
    #         while True:
    #             engine.say(text)
    #             engine.runAndWait() 
    #     except KeyboardInterrupt:
    #         engine.stop()
    #         engine.endLoop()
    #         engine.destroy()
    #         session.run_id += 1
       
    
    # function to get the full body of the article and title - ideally the UI has 3 options: PDF file; TXT file or XML file
    def getArticle(filePath):
        try:
            full,title = tree(filePath)
            return full,title
            pass
        except:
            full,title = text_file(filePath)
            return full,title
            pass
        finally:   
            full = ''
            title = ' Summarization of PDF files is not available in the current version'
        return full,title

    # Distilbert model for summarization 
    # Summary (detail level user defined)
    @st.cache(persist = True,suppress_st_warning=True, show_spinner=False)
    def extSumm_distilbert(full_text,level, model="distilbert-base-uncased", min_length=5):
        model = Summarizer(model=model)
        return model(full_text, min_length=min_length, ratio = level)

    # Full document (detail level 100%) - this funtion is needed to align the sentences from the summary 
    # with the sentences of the full doc for highlighting
    @st.cache(persist = True,suppress_st_warning=True, show_spinner=False)
    def extSumm_distilbert_full(full_text, model="distilbert-base-uncased",ratio=1, min_length=5):
        model = Summarizer(model=model)
        return model(full_text, min_length=min_length, ratio = ratio)


    # Scibert model for summarization
    # Summary (detail level user defined)
    @st.cache(persist = True,suppress_st_warning=True, show_spinner=False)
    def extSumm_scibert(full_text,level,min_length=5):
        custom_config = AutoConfig.from_pretrained('allenai/scibert_scivocab_uncased')
        custom_config.output_hidden_states=True
        custom_model = AutoModel.from_pretrained('allenai/scibert_scivocab_uncased', config=custom_config)
        model = Summarizer(custom_model=custom_model)
        return model(full_text,min_length=min_length,ratio = level)

    # Full document (detail level 100%) - this funtion is needed to align the sentences from the summary
    #  with the sentences of the full doc for highlighting
    @st.cache(persist = True,suppress_st_warning=True, show_spinner=False)
    def extSumm_scibert_full(full_text,min_length=5,ratio=1):
        custom_config = AutoConfig.from_pretrained('allenai/scibert_scivocab_uncased')
        custom_config.output_hidden_states=True
        custom_model = AutoModel.from_pretrained('allenai/scibert_scivocab_uncased', config=custom_config)
        model = Summarizer(custom_model=custom_model)
        return model(full_text,min_length=min_length,ratio=1)

    def urlProperlyFormed(url):
        """
        Test whether URL is properly formed.
        Args:
            url (str): Full web URL to article
        Returns:
            bool
        """
        try:
            result = urlparse(url)
            # all() returns true if all the variables inside it return true
            return all([result.scheme, result.netloc])
        except ValueError:
            return False


    def urlReachable(url):
        """
        Test whether URL is reachable.
        Args:
            url (str): Full web URL to article
        Returns:
            bool
        """
        try:
            conn = urllib.request.urlopen(url)
        except urllib.error.HTTPError as e:
            st.warning("There is a HTTP error. Please check.")
            return False
        except urllib.error.URLError as e:
            st.warning("There is an URL error. Please check.")
            return False
        else:
            return True

    # Functions to get the summary (change the model below) - to be optimized into one function only
    @st.cache(persist = True,suppress_st_warning=True, show_spinner=False)
    def getSummary1(filePath,level):
        full,title = getArticle(filePath)
        full_summ = extSumm_scibert_full(full)
        short_summ = extSumm_scibert(full,level)
        
        list1 = sent_tokenize(full_summ)
        list2 = sent_tokenize(short_summ)
        
        return list1, list2, title

    @st.cache(persist = True,suppress_st_warning=True, show_spinner=False)
    def getSummary2(filePath,level):
        full,title = getArticle(filePath)
        full_summ = extSumm_distilbert_full(full)
        short_summ = extSumm_distilbert(full,level)
        
        list1 = sent_tokenize(full_summ)
        list2 = sent_tokenize(short_summ)
        
        return list1, list2, title

    @st.cache(persist = True,suppress_st_warning=True, show_spinner=False)
    def getSummary3(web_url_text,level):
        if (
        not urlProperlyFormed(web_url_text)
        or (web_url_text == "http://" or web_url_text == "https://")
        or not urlReachable(web_url_text)
    ):
            return ("", "", "")

        full,title = url_get_text(web_url_text)
        full_summ = extSumm_scibert_full(full)
        short_summ = extSumm_scibert(full,level)
        
        list1 = sent_tokenize(full_summ)
        list2 = sent_tokenize(short_summ)
        
        return list1, list2, title
    
    @st.cache(persist = True,suppress_st_warning=True, show_spinner=False)
    def getSummary4(web_url_text,level):
        if (
        not urlProperlyFormed(web_url_text)
        or (web_url_text == "http://" or web_url_text == "https://")
        or not urlReachable(web_url_text)
    ):
            return ("", "","")

        full,title = url_get_text(web_url_text)
        full_summ = extSumm_distilbert_full(full)
        short_summ = extSumm_distilbert(full,level)
        
        list1 = sent_tokenize(full_summ)
        list2 = sent_tokenize(short_summ)
        
        return list1, list2, title

    # --- Functions def section END --


    # --- Sidebar Section BEGIN ---

    # sidebar slider for level of detail  in summarization
    st.sidebar.title("Select detail level:")
    level1 = st.sidebar.slider('Shorter summary   <-----( % )----->   Longer summary', 0, 100,(20))
    level=level1/100
    st.sidebar.title("")

    # sidebar radio button for choosing summarization model 
    st.sidebar.title("Select text type:")
    sel_model = st.sidebar.radio("",('Scientific text','General text'))
    st.sidebar.title("")  


    # sidebar url input
    st.sidebar.title("Paste a Web Site URL:") 
    WEB_URL_TEXT_DEFAULT = "http://"
    web_url_text = st.sidebar.text_input("Web Site URL:", WEB_URL_TEXT_DEFAULT)
    if web_url_text is not None:
        if sel_model == 'Scientific text':
            list1, list2, title_txt = getSummary3(web_url_text,level)
        else:
            list1, list2, title_txt = getSummary4(web_url_text,level)
    # else:
    #     st.write('')
    
    # Button to listen the summary (does not work with the summary from file uploader because I didn't figured out how to 
    # clean the uploader cache value to allow for furtehr queries in url_uploader)
    if st.sidebar.button('Listen Summary (Esc to stop)'):
        for sent in list2:
            say(sent)
        
    # sidebar file uploader - accepts xml and txt, in future should also accept pdf once
    # the function to extract pdf content is implemented
    st.sidebar.title("or Upload a file:")
    uploaded_file = st.sidebar.file_uploader("Choose a file to upload...", type=("xml","txt"),encoding='utf-8',key=session.run_id)
    if uploaded_file is not None:
        if sel_model == 'General text':
            list1, list2, title_txt = getSummary1(uploaded_file,level)
            WEB_URL_TEXT_DEFAULT = "http://"
            session.run_id += 1
        else:
            list1, list2, title_txt = getSummary2(uploaded_file,level)
            WEB_URL_TEXT_DEFAULT = "http://"
            session.run_id += 1

    # sidebar button to refresh (needed because couldn't find a way to clear the file_uploader cache)
    if st.sidebar.button('Upload new file'):
        re_run()   
    
    # Credits
    st.sidebar.title("")
    st.sidebar.title("")
    st.sidebar.markdown('***TIPP 2020 - Batch2***')

    # --- Sidebar section END --


    # --- Main section BEGIN --

    # logos images
    rp_logo_img = Image.open(os.path.join("img", "rplogo.png"))
    rp_logo_array = asarray(rp_logo_img)
    nvidia_logo_img = Image.open(os.path.join("img", "nvidia_logo.png"))
    nvidia_logo_array = asarray(nvidia_logo_img)

    st.image([nvidia_logo_array, rp_logo_array], width=300, format="PNG")
    st.markdown("<hr>", unsafe_allow_html=True)

    
    # shows title of the article
    st.title(title_txt)
    st.write('')

    # shows full text (list1) with sentences also present in the summarization result (list2) highlighted in yellow
    s = set(list2)
    for m in list1:
        if m in s: 
            st.write(f'<span style="background-color:yellow">{m}</span>', unsafe_allow_html=True)
        else:
            st.write(m)


    # hide the 'Make with Streamlit' footer at bottom of web page
    hide_streamlit_style = """
                <style>
                //#MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                </style>
                """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)


    @st.cache(persist = True,suppress_st_warning=True, show_spinner=False)
    def update_request():
        """
        Update the summarizer machine with the indexes.
        Takes in JSON via GET/POST request, returns the result as a JSON
        """
        url_req = request.json
        print("\n-----------")
        print("File to replace: ", url_req["filename"])
        print("Indexes updated by user: ", url_req["indexes"])

        # read the 'before' file content
        df = pd.read_csv(url_req["filename"])

        # convert the indexes to be change to a string of comma separated int
        df.iloc[0][0] = ",".join(str(i) for i in url_req["indexes"])
        # rename the filename by adding a '_changed' followed by '.csv' extension
        updated_filename = os.path.splitext(url_req["filename"])[0] + "_changed.csv"
        print("Updated filename: ", updated_filename)
        # save the dataframe as csv file
        df.to_csv(updated_filename, index=False, header=True, encoding="utf-8")
        print("-----------\n")

        return jsonify(success=True)


if __name__ == '__main__':
    main()

# --- Main section END -- 

# TIPP 2020; Batch2

# In[ ]:




