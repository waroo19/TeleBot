import spacy
from spacy.matcher import Matcher

nlp = spacy.load("en_core_web_sm")


def identify_intent(text):
    
    matcher = Matcher(nlp.vocab)

    doc = nlp(text.lower())
    ############ Light pattern #########################

    pattern_light_on = [
         [{"LEMMA": "turn"}, {"LEMMA": "on"}], 
        [{"LEMMA": "switch"}, {"LEMMA": "on"}],
        [{"LEMMA": "activate"}],
        [{"POS": "DET", "OP": "?"}, {"LEMMA": "light"}],
        [{"POS": "DET", "OP": "?"}, {"LEMMA": "light", "TAG": "NNS"}],
        [{"LEMMA": "on"},{"OP": "?"}],
    ]
    # Add the pattern to the matcher
    matcher.add("TURN_ON_LIGHT", pattern_light_on)
    
    
    pattern_light_off = [
         [{"LEMMA": "turn"}, {"LEMMA": "off"}], 
        [{"LEMMA": "switch"}, {"LEMMA": "off"}],
        [{"LEMMA": "activate"}],
        [{"POS": "DET", "OP": "?"}, {"LEMMA": "light"}],
        [{"POS": "DET", "OP": "?"}, {"LEMMA": "light", "TAG": "NNS"}],
        [{"LEMMA": "off"},{"OP": "?"}],
    ]
    matcher.add("TURN_OFF_LIGHT", pattern_light_off)

    ############ Alarm pattern #########################
    alarm_verbs = ["set", "switch", "activate", "start", "trigger", "engage"]
    pattern_alarm_on = [
    [{"LEMMA": {"IN":alarm_verbs}}],
    [{"LEMMA": "on"},{"OP": "?"}],
    [{"POS": "DET", "OP": "?"}],  
    [{"LEMMA": "alarm"}],
    [{"LEMMA": "on"},{"OP": "?"}],
        ]
    matcher.add("TURN_ON_ALARM", pattern_alarm_on)
    #################### Help pattern #########################
    pattern_help = [
    [{"LEMMA": "help"}],
    [{"LEMMA": "what"}, {"LEMMA": "can"}, {"LEMMA": "you"}, {"LEMMA": "do"}],
    [{"LEMMA": "need"}, {"LEMMA": "assistance"}],
    [{"LEMMA": "show"}, {"LEMMA": "command"}],
    [{"LEMMA": "be"}, {"POS": "PRP"}, {"LEMMA": "stuck"}],  # "I'm stuck"
    [{"LEMMA": "can"}, {"LEMMA": "you"}, {"LEMMA": "show"}, {"LEMMA": "me"}, {"LEMMA": "how"}, {"LEMMA": "to"}, {"LEMMA": "use"}]
    ]
    matcher.add("HELP", pattern_help)

    ########################## Greeting Pattern ###############################
    pattern_greet = [
    [{"LOWER": "hey"}],
    [{"LOWER": "hello"}],
    [{"LOWER": "hi"}],
    [{"LOWER": "hello"}, {"LOWER": "there"}],
    [{"LOWER": "good"}, {"LOWER": {"IN": ["morning", "afternoon", "evening"]}}],
    [{"LOWER": "moin"}], 
    [{"LOWER": "hey"}, {"LOWER": "there"}],
    [{"LOWER": "let's"}, {"LOWER": "go"}],
    [{"LOWER": "hey"}, {"LOWER": "dude"}],
    [{"LOWER": "goodmorning"}],
    [{"LOWER": "goodevening"}],
    [{"LOWER": "good"}, {"LOWER": "afternoon"}]
]

    matcher.add("GREETING", pattern_greet)


    # Apply the matcher to the doc
    matches = matcher(doc)
    for match_id, start, end in matches:
        matched_pattern_id = match_id  
        if matched_pattern_id == matcher.vocab.strings["TURN_ON_LIGHT"]:
            print("Turn the light on pattern detected!")
            return "turn_on_light"
        elif matched_pattern_id == matcher.vocab.strings["TURN_OFF_LIGHT"]:
            print("Turn the light off pattern detected!")
            return "turn_off_light"
        elif matched_pattern_id == matcher.vocab.strings["TURN_ON_ALARM"]:
            print("Turn the alarm on pattern detected!")
            return "turn_on_alarm"
        elif matched_pattern_id == matcher.vocab.strings["HELP"]:
            print("help pattern detected!")
            return "help"
        elif matched_pattern_id == matcher.vocab.strings["GREETING"]:
            print("Hi pattern detected!")
            return "start"
        
        
        else:
             return "nothing"


    
if __name__ == '__main__':
   identify_intent("switch on the lights ")
