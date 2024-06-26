import spacy
from spacy.matcher import Matcher

nlp = spacy.load("en_core_web_sm")


def identify_intent(text):
    
    matcher = Matcher(nlp.vocab)

    doc = nlp(text.lower())
    ############ Light pattern #########################

    pattern_light_on = [
        [{"LEMMA":{"IN": ["turn on", "switch on","activate"]}}], 
        [{"LEMMA": "light"}],
        [{"LEMMA": "light", "TAG": "NNS"}],
    ]
    # Add the pattern to the matcher
    matcher.add("TURN_ON_LIGHT", pattern_light_on)
    
    
    pattern_light_off = [
        [{"LEMMA":{"IN": ["turn off", "switch off","deactivate"]}}], 
        [{"LEMMA": "light"}],
        [{"LEMMA": "light", "TAG": "NNS"}],
    ]
    matcher.add("TURN_OFF_LIGHT", pattern_light_off)

    ############ Alarm pattern #########################
    
    pattern_alarm_on = [
            [{"LEMMA":{"IN": ["turn on", "switch on","activate"]}}], 
            [{"LEMMA": "alarm"}],
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

    ###########################Thermostat########################
    pattern_temp_complaint = [
    [{"LOWER": {"IN": ["too", "way", "really", "freezing", "chilly"]}}], 
    [{"LOWER": {"IN": ["hot", "warm", "cold"]}}],
    [{"LOWER": "?", "OP": "?"}],
    
]
    
    pattern_ac_on = [
        [{"LEMMA":{"IN": ["turn on", "switch on","activate"]}}], 
        [ {"LEMMA":{"IN": ["air conditioner", "ac"]}}],
        [{"LEMMA": {"IN": ["air conditioner", "ac"]}, "TAG": "NNS"}],
    ]
    pattern_ac_off = [
        [{"LEMMA":{"IN": ["turn off", "switch off","deactivate"]}}], 
        [{"LEMMA":{"IN": ["air conditioner", "ac"]}}],
        [{"LEMMA": {"IN": ["air conditioner", "ac"]}, "TAG": "NNS"}],
    ]

   
    matcher.add("AC_ON", pattern_ac_on)
    matcher.add("AC_OFF", pattern_ac_off)
    matcher.add("TEMP_COMP", pattern_temp_complaint) 


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
        elif matched_pattern_id == matcher.vocab.strings["AC_ON"]:
            print("AC ON pattern detected!")
            return "turn_on_ac"
        elif matched_pattern_id == matcher.vocab.strings["AC_OFF"]:
            print("AC OFF pattern detected!")
            return "turn_off_ac"
        elif matched_pattern_id == matcher.vocab.strings["TEMP_COMP"]:
            print("room temp pattern detected!")
            return "temperature"
        
        
        
        
        else:
             return "nothing"


    
if __name__ == '__main__':
    identify_intent("help")
    identify_intent("turn on the alarm")
