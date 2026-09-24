from datetime import datetime, date, timedelta, timezone
events = {}
def quiz_setup():
    global events
    change_functions = {1:{'func':is_unique,'param':'What would you like to call this event?','save_var':''},2:{'func':enter_frequency,'param':'','save_var':''},3:{'func':input,'param':'What role (enter the name) would you like to get pinged for this quiz?(None for no ping, Everyone to ping everyone.)','save_var':''},
                                4:{'func':num_checking_input,'param':'In wich channel would you like the questions to be sent? (enter channelid)','save_var':''},5:{'func':can_respond_bool,'param':'Would you like that people can respond to the question by using a bot cmd. (y,n)','save_var':''},
                                6:{'func':question_asking,'param':'','save_var':''}}
    change_functions[1]['save_var'] = is_unique('What would you like to call this event?')
    change_functions[2]['save_var'] = enter_frequency()
    change_functions[3]['save_var'] = input('What role (enter the name) would you like to get pinged for this quiz?(None for no ping, Everyone to ping everyone.)')
    change_functions[5]['save_var'] = num_checking_input('In wich channel would you like the questions to be sent? (enter channelid)')
    change_functions[4]['save_var'] = can_respond_bool('Would you like that people can respond to the question by using a bot cmd. (y,n)')
    change_functions[6]['param'] = change_functions[4]['save_var']
    change_functions[6]['save_var'] = question_asking(change_functions[6]['param'])
    
    def save_events():
        global events
        events[change_functions[1]['save_var']] = {'frequency':change_functions[2]['save_var'],'role_pinged':change_functions[3]['save_var'],'question_channel':change_functions[4]['save_var'],'can_respond':change_functions[5]['save_var'],'question_response':change_functions[6]['save_var']}
    
    def better_event_desc():
            event_description = f'This event is called {change_functions[1]['save_var']} and will occour every {change_functions[2]['save_var']}. '
            event_description += f'It will ping the role {change_functions[3]['save_var']}. ' if change_functions[3]['save_var'].lower() != 'none' else 'It won\'t ping any role. '
            event_description += f'The members of this server ' 
            event_description += 'will' if change_functions[4]['save_var'] else 'won\'t'
            event_description +=' be able to respond to questions asked. '
            event_description += f'Questions will be sent in the channel {change_functions[5]['save_var']}. '
            event_description += f'The question and responses are {change_functions[6]['save_var']}.' if event_description else ''
            return event_description
    #TODO fix that quesiton chaan
    #totally
    event_description = better_event_desc()
    response = input(f'This is the final event description {event_description}\n If you want to change someting enter **change** else your event will be saved and start at the next date.')
    
    def change_menu():
        global events
        change = input('The options are the following: 1 event name, 2 frequency, 3 role pinged, 4 question channel, 5 if users can respond' + ', 6 questions and responses\nWhat would you like to change (exit to exit)?' if change_functions[4]['save_var'] else '')
        if len(change) == 1 and change.isdigit() and int(change) in range(1,7) if change_functions[4]['save_var'] else int(change) in range(1,5):
            change = int(change)
            change_functions[change]['save_var'] = change_functions[change]['func'](change_functions[change]['param']) if change_functions[change]['param'] else change_functions[change]['func']()
            save_events()
            print(f'The updated event description is: {better_event_desc()}')
            return change_menu()
        elif change == 'exit':
            return events
        else:
            print('Invalid input.')
            return change_menu()

    if response.lower() != 'change':
        return events
    else:
        events = change_menu()

def can_respond_bool(prompt:str):
    user_input = input(prompt)
    if user_input in ['y','yes']:
        return True
    return False

def question_asking(need_response:bool=True):
    question_and_response = {}
    question_count = num_checking_input('How many questions would you like there to be?')
    for num in range(question_count):
        question  = input(f'What would your {num+1}. question be?')
        if need_response:
            answer_amount = num_checking_input('How many answers to this question would you like there to be?\nIf you would like that there is no clear response enter 0.')
            responses = []
            for i in range(answer_amount):
                responses.append(input(f'What would the {i+1}. response be to the question?'))
            question_and_response[question] = responses
    return question_and_response

def is_unique(prompt:str):
    event_name = input('What would you like to call this event?')
    if event_name in events.keys():
        print(f'An event called {event_name} already exists please choose a different name.')
        return is_unique(prompt)
    return event_name

def enter_frequency():
    often = input('What would you like the event frequency to be?\n1) every x days 2) every x weeks 3)every x hours. Input the option like: 1)(amount of times)')
    if len(often) != 3 or not often[0].isdigit or not often[2].isdigit or not any(often.startswith(str(num)) for num in [1,2,3]):
        print(f'{often} is not a valid input.')
        return enter_frequency()
    return f'{often[2]} ' + {'1':'days','2':'weeks','3':'hours'}[often[0]]

def num_checking_input(prompt:str,lower_bound:int|None=None,upper_bound:int|None=None):
    question_count = input(prompt)
    if not question_count.isdigit() or lower_bound and int(question_count) < lower_bound or upper_bound and int(question_count) > upper_bound:
        print(f'{question_count} is not a valid input.')
        return num_checking_input(prompt)
    return int(question_count)

def time_diff(day:str|int):
    user_day,_ = get_day(day)
    today = datetime.now(timezone.utc)
    this_day = today.weekday() + 1
    to_wait = 7 - this_day  if this_day < user_day else 7-this_day + user_day
    user_hour = num_checking_input('At what hour would you like the event to happen (utc)?', 0 ,23)
    user_day  = today.replace(hour=0,minute=0,second=0,microsecond=0) + timedelta(days=to_wait,hours=user_hour)
    diff = (user_day-today).total_seconds()
    return int(diff)

def get_day(day_str:str):
    day_str = day_str.strip()
    days = ['monday','tuesday','wendsday','thursday','friday','saturday','sunday']
    day = days.index(day_str)+1 if day_str in days else int(day_str) if day_str.isdigit() and int(day_str) in range(1,7) else None
    if not day:
        print('Invalid day.')
        return time_diff(day_str)
    return day, days[day-1]

if __name__ == '__main__':
    print(time_diff(input('What day would you like the quiz to occour?')))
    #quiz_setup()
