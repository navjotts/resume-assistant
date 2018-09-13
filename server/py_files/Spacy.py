import re

import spacy
import en_core_web_lg  # Changed from en*_sm to en*_lg because it is easier to identify names.
nlp = en_core_web_lg.load()
nlp.max_length = 2000000 # todo check this limit

class Spacy(object):
    def anonymize_token(self, t):
        if t.like_email: # todo bring in Human Names as well
            return 'X'*len(t.text)
        return t.text
    
    def anonymize_name(self, text):
        doc = nlp(text)
        spans = list(doc.ents)

        for span in spans:
            span.merge()
        
        for person in filter(lambda w: w.ent_type_ == 'PERSON', doc):
            sentence = str(text)
            text =  sentence.replace(str(person), (len(str(person))*'X'))

        return text


    # todo: case to check Cc @Antonio - how does the search function behaves if there are more than 1 matches (what happens if there are 2 phone numbers in 1 sentence)
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
        text = Spacy.anonymize_name(self, text)
        text = Spacy.anonymize_phone_number(self, text)
        for t in nlp(str(text)):
            if not t.is_space and not (drop_stop_words and t.is_stop):
                tokens.append(Spacy.anonymize_token(self, t))

        return tokens

#findall(pattern, string, flags=0)
#Return all non-overlapping matches of pattern in string, as a list of strings. The string is scanned left-to-right, and matches are returned in the order found. If one or more groups are present in the pattern, return a list of groups; this will be a list of tuples if the pattern has more than one group. Empty matches are included in the result.
#
