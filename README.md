# Extractive Summarization of Scientific Articles

1. Install PyTorch if you don't already have it

2. `pip install -r requirements.txt`

3. The module SessionState.py needs to be in the same folder as the app. This module is needed to reset the file_uploader cahed values from the previous query   


### Running and operatingthe Module

3. `streamlit run app_scientific_summarizer.py`, launches the web UI on port 8501

	- File-uploader (*.txt and *.xml (not all xml types)
		- Some example files are in the Articles_xml and Articles_txt folders)
	
	- URL uploader - works best with simple websites heavy in text (e.g. Wikipedia or Scientific papers from PlosOne)


4. User can choose:
	- the level of detail for the summary in the sidebar slider
	- the type of summarization model (Scientifics or General)

5. User must press the reset button before a new query (this is needed because the file_uploader widget in streamlit does not clear the last entry from cache (https://discuss.streamlit.io/t/how-can-i-clear-a-specific-cache-only/1963/7)

