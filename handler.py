import spacy
from spacy.matcher import Matcher

nlp = spacy.load("en_core_web_sm")


def identify_intent(text):
    
    matcher = Matcher(nlp.vocab)

    doc = nlp(text.lower())
   
    pattern_light = [
         [{"LEMMA": "turn"}, {"LEMMA": "on"}], 
        [{"LEMMA": "switch"}, {"LEMMA": "on"}],
        [{"LEMMA": "activate"}],
        [{"POS": "DET", "OP": "?"}, {"LEMMA": "light"}],
        [{"POS": "DET", "OP": "?"}, {"LEMMA": "light", "TAG": "NNS"}],
        [{"LEMMA": "on"},{"OP": "?"}],
    ]
    # Add the pattern to the matcher
    matcher.add("TURN_ON_LIGHT_PATTERN", pattern_light)
    
    # Apply the matcher to the doc
    matches = matcher(doc)
    for match_id, start, end in matches:
        matched_pattern_id = match_id  
        if matched_pattern_id == matcher.vocab.strings["TURN_ON_LIGHT_PATTERN"]:
            print("Turn the light on pattern detected!")
            return "turn_on_light"
        else:
             return "help"


    
if __name__ == '__main__':
   identify_intent("switch on the lights ")
