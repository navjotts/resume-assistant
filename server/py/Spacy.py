import re

import spacy
import en_core_web_sm
nlp = en_core_web_sm.load()
nlp.max_length = 2000000 # todo check this limit

import time

class Spacy(object):
    def anonymize(self, t):
        if t.like_email: # todo bring in Human Names as well
            return 'X'*len(t.text)
        return t.text

    def is_phone_number(self, text):
        phone_regex = re.compile('(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})') # todo cover international
        return phone_regex.match(text)

    def sentences(self, text, drop_stop_words):
        sents = []
        sentence = []
        for t in nlp(str(text)):
            if t.is_sent_start:
                if len(sentence) > 0:
                    sents.append(sentence)
                sentence = []
            if not t.is_space and not (drop_stop_words and t.is_stop):
                sentence.append(Spacy.anonymize(self, t))

        return sents

    def tokenize(self, text, drop_stop_words):
        tokens = []
        is_phone_number = Spacy.is_phone_number(self, text)
        for t in nlp(str(text)):
            if not t.is_space and is_phone_number:
                tokens.append(t.text if t.is_punct else 'X'*len(t.text))
            elif not t.is_space and not (drop_stop_words and t.is_stop):
                tokens.append(Spacy.anonymize(self, t))

        return tokens
