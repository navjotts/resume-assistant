import spacy
import en_core_web_sm
nlp = en_core_web_sm.load()
nlp.max_length = 2000000 # todo check

import time

class Spacy(object):
    def sentences(self, text, drop_stop_words):
        sents = []
        sentence = []
        for t in nlp(str(text)):
            if t.is_sent_start:
                if len(sentence) > 0:
                    sents.append(sentence)
                sentence = []
            if not t.is_space and not (drop_stop_words and t.is_stop) and not t.is_punct:
                sentence.append(t.text)

        return sents

    def tokenize(self, text, drop_stop_words):
        tokens = []
        for t in nlp(str(text)):
            if not t.is_space and not (drop_stop_words and t.is_stop) and not t.is_punct:
                tokens.append(t.text)

        return tokens
