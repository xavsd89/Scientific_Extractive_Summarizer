Extractive Summarization of Scientific Articles
Install PyTorch if you don't already have it

pip install -r requirements.txt

The module SessionState.py needs to be in the same folder as the app. This module is needed to reset the file_uploader cahed values from the previous query

Running and operatingthe Module
streamlit run app_scientific_summarizer.py, launches the web UI on port 8501

File-uploader (*.txt and *.xml (not all xml types)

Some example files are in the Articles_xml and Articles_txt folders)
URL uploader - works best with simple websites heavy in text (e.g. Wikipedia or Scientific papers from PlosOne)

User can choose:

the level of detail for the summary in the sidebar slider
the type of summarization model (Scientific or General)
Type of content loading (from URL or from File)
Listen the summary from a URL with the speech synthesizer embedded
if the speech synthesizer does not work:
pip uninstall pyttsx3
pip install pyttsx3==2.6