import spacy
import en_core_web_sm
nlp = en_core_web_sm.load()
nlp.max_length = 2000000 # todo check

import time

class Spacy(object):
    def sentences(self, text):
        sents = []
        sentence = []
        for t in nlp(str(text)):
            if t.is_sent_start:
                if len(sentence) > 0:
                    sents.append(sentence)
                sentence = []
            if not t.is_space and not t.is_stop and not t.is_punct:
                sentence.append(t.text)

        return sents
