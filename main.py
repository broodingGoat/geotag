from flask import Flask, render_template
from flask_ask import Ask, statement, session, question
from mydata import constants, city_state, county_state
import random
import string
import wikipedia as wk

app = Flask(__name__)
app.config['ASK_VERIFY_REQUESTS'] = False
ask = Ask(app, '/')

def get_place_starting_with(last_character):
    city_list = filter(lambda x:x[0] == last_character.upper(), constants.city_list)
    return random.choice(city_list)

def get_information_for(keyword, location_type):
    if location_type == 'USCity':
        return wk.summary(keyword + ' ' + city_state.dic[keyword])
    if location_type == 'USState':
        return wk.search(keyword + ' ' + city_state.dic[keyword])


def validate_if_correct_word_by_player(last_word_by_player, last_word_by_geotag):
    if last_word_by_geotag[-1].lower() == last_word_by_player[0].lower():
        return True
    else:
        return False

@ask.intent('GetScore')
def get_score():

    if 'score' not in session.attributes.keys():
        return statement(render_template('no_score'))
    else:
        return question(render_template('score', Score=session.attributes['score']))


@ask.intent('GiveMeHint')
def give_hint():
    last_word_by_geotag = session.attributes['last_word_by_geotag']
    location = get_place_starting_with(last_word_by_geotag[-1])
    text = render_template('hint', Location = location)
    return question(text)

@ask.intent('TellMeAbout', mapping={'USCity': 'USCity', 'USState': 'USState'})
def tell_me_about(USCity, USState):
    print "here"
    if USCity is not None:
        session.attributes['previous_action'] = "info"
        return question(get_information_for(USCity, 'USCity'))
    if USState is not None:
        session.attributes['previous_action'] = "info"
        return question(get_information_for(USState, 'UState'))


@ask.intent('AMAZON.StopIntent')
def stop():
    if session.attributes['previous_action'] == "info":
        """
        # previous action was player getting info
        if player has ongoing play, ask if they want to cancel the game
        else continue
        this section needs more work
        """
        if session.attributes['last_word_by_geotag'] is None:
            text = render_template('lets lets_play')
            return statement(text)
        else:
            text = render_template('incorrect_word_by_player')
            return question(text)

@ask.intent('AMAZON.HelpIntent')
def help():
    text = render_template('help')
    return statement(text)

@ask.intent('GetLocationInfo')
def get_location_info():
    last_word_by_geotag = session.attributes['last_word_by_geotag']
    text = get_information_for(last_word_by_geotag,'USCity')
    session.attributes['previous_action'] = "info"
    return question(text)

@ask.intent('Start')
def start():
    start_char = random.choice(list(string.ascii_lowercase))
    text = get_place_starting_with(start_char)
    session.attributes['last_word_by_geotag'] = text
    session.attributes['time_elapsed'] = 0
    session.attributes['score'] = 0
    return question(text)

@ask.intent('Location', mapping={'USCity': 'USCity', 'USState' : 'USState'})
def location(USCity, USState):

    if 'last_word_by_geotag' not in session.attributes:
        return statement(render_template('no_score'))


    else:
        if USCity is not None:
            location_type = 'USCity'
            word_recieved = USCity
        else:
            location_type = 'USState'
            word_recieved = USState
    last_word_by_geotag = session.attributes['last_word_by_geotag']
    if validate_if_correct_word_by_player(word_recieved, last_word_by_geotag) is False:
        text = render_template('incorrect_word_by_player', Location=last_word_by_geotag)
        return question(text)

    text = get_place_starting_with(word_recieved[-1])
    session.attributes['last_word_by_geotag'] = text
    session.attributes['location_type'] = location_type
    session.attributes['time_elapsed'] = 0
    session.attributes['previous_action'] = "play"
    if 'score' in session.attributes.keys():
        session.attributes['score'] = int(session.attributes['score']) + 1
    else:
        session.attributes['score'] = 0
    return question(text)

if __name__ == '__main__':
    app.run(debug=True)