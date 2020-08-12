from summarizer import Summarizer
from transformers import *

model_list = ["distilbert-base-uncased", 'allenai/scibert_scivocab_uncased']

for m in model_list:
    print("Caching model", m)
    model = Summarizer(model=m)