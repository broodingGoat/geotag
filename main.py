from flask import Flask, render_template
from flask_ask import Ask, statement
from mydata import constants, city_state, county_state
import random
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

@ask.intent('AMAZON.HelpIntent')
def help():
    text = render_template('help')
    return statement(text)

@ask.intent('Location', mapping={'USCity': 'USCity', 'USState' : 'USState'})
def hello(USCity, USState):
    if USCity is not None:
        word_recieved = USCity
        word_type = "USCity"
        text = get_place_starting_with(word_recieved[-1])
        get_information_for(text, word_type)
        return statement(text)

    if USState is not None:
        text = USState
        return statement(text)

if __name__ == '__main__':
    app.run(debug=True)