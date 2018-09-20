import re

import spacy
import en_core_web_sm
nlp = en_core_web_sm.load()
nlp.max_length = 2000000 # todo check this limit

class Spacy(object):
    def anonymize_token(self, t):
        if t.like_email:
            return t.shape_

        # todo we need a better way - this is also hiding some tools names which we need in our analysis (eg: Docker, Jenkins etc)
        # if t.ent_type_ == 'PERSON':
        #     return t.shape_

        return t.text

    # todo: case to check Cc @Antonio - how does the search function behaves if there are more than 1 matches (what happens if there are 2 phone numbers in 1 sentence)
    def anonymize_phone_number(self, text):
        phone_number = re.search(r'(\+\s?1\s?)|(?:(?:(\s*\(?([2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9])\s*)|([2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9]))\)?\s*(?:[.-]\s*)?)([2-9]1[02-9]|[2-9][02-9]1|[2-9][02-9]{2})\s*(?:[.-]\s*)?([0-9]{4})', text)
        if phone_number:
            return ''.join(['X' if (not char.isspace() and i >= phone_number.start() and i <= phone_number.end()) else char for i, char in enumerate(text)])

        return text

    def sentences(self, text, drop_stop):
        sents = []
        sentence = []
        for t in nlp(str(text)):
            if t.is_sent_start:
                if len(sentence) > 0:
                    sents.append(sentence)
                sentence = []
            if not t.is_space and not (drop_stop and t.is_stop):
                sentence.append(Spacy.anonymize_token(self, t))

        if len(sents) == 0 and len(sentence) > 0:
            sents.append(sentence)

        return sents

    def tokenize(self, text, drop_stop, drop_punct):
        tokens = []
        text = Spacy.anonymize_phone_number(self, text)
        for t in nlp(str(text)):
            if not t.is_space and not (drop_stop and t.is_stop) and not (drop_punct and t.is_punct):
                tokens.append(Spacy.anonymize_token(self, t))

        return tokens