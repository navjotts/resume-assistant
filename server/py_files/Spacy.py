import re

import spacy
import en_core_web_sm
nlp = en_core_web_sm.load()
nlp.max_length = 2000000 # todo check this limit

class Spacy(object):
    def anonymize_token(self, t):
        if t.like_email: # todo bring in Human Names as well
            return 'X'*len(t.text)
        return t.text

    def anonymize_phone_number(self, text):
        phone_number = re.search(r'(\+\s?1\s?)|(?:(?:(\s*\(?([2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9])\s*)|([2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9]))\)?\s*(?:[.-]\s*)?)([2-9]1[02-9]|[2-9][02-9]1|[2-9][02-9]{2})\s*(?:[.-]\s*)?([0-9]{4})', text)
        if phone_number:
            return ''.join(['X' if (not char.isspace() and i >= phone_number.start() and i <= phone_number.end()) else char for i, char in enumerate(text)])

        return text

    def sentences(self, text, drop_stop_words):
        sents = []
        sentence = []
        for t in nlp(str(text)):
            if t.is_sent_start:
                if len(sentence) > 0:
                    sents.append(sentence)
                sentence = []
            if not t.is_space and not (drop_stop_words and t.is_stop):
                sentence.append(Spacy.anonymize_token(self, t))

        if len(sents) == 0 and len(sentence) > 0:
            sents.append(sentence)

        return sents

    def tokenize(self, text, drop_stop_words):
        tokens = []
        text = Spacy.anonymize_phone_number(self, text)
        for t in nlp(str(text)):
            if not t.is_space and not (drop_stop_words and t.is_stop):
                tokens.append(Spacy.anonymize_token(self, t))

        return tokens
