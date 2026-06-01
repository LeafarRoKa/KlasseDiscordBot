import re
from datetime import date
if __name__ == '__main__':
    #num = 0
    #print(num > 0)
    #DATE_STR = '12-11-2026' 
    #boolean = bool(not re.sub(r'[0-3]\d-[01]\d-\d{4}','', DATE_STR) and date.today().year >= int(DATE_STR[-4:]))
    #print(boolean)
    #print(re.findall(r'((\d){2}-){2}-\d{4}','02-21-3333'))
    #print(' abcd \n '.strip(' \n'))
    #print(' abcd \n '.strip('\n '))
    ...
class Commands:
    pass
    def run(self):
        return 'command executed.'
class PingCommand(Commands):
    def run(self):
        return 'Pong!'
class AddCommand(Commands):
    @staticmethod
    def run(a:int,b:int):
        if type(a) is not int or type(b) is not int:
            if not type(a) is str or not type(b) is str and not a.isdigit() or not b.isdigit():
                return 'Invalid types were given in the given parameters.'
            a,b = int(a),int(b)
        return a + b
    
    def internal_run(self):
        a,b = getattr(self,'a', None), getattr(self,'b', None)
        if not a or not b:
            return 'Either a or b is missing as a value of the instance using the command.'
        if type(a) is not int or type(b) is not int:
            if not type(a) is str or not type(b) is str and not a.isdigit() or not b.isdigit():
                return 'Invalid types were given in the given parameters.'
            a,b = int(a),int(b)
        return a + b

commands = {}
commands['ping'] = {'func': PingCommand().run, 'amount_params':0}
commands['add'] = {'func': AddCommand.run, 'amount_params':2}
def execute(command_name:str,*args):
    if all(k.lower() != command_name.lower() for k in commands.keys()):
        return f'The command {command_name} does not exist.'
    data = commands[command_name]
    if len(args) != data['amount_params']:
        return 'You have given an invalid amount of parameters.'
    return data['func']() if not args else data['func'](*args)

name = input('Enter the function name you want to execute?')
params = input('enter the params separated by ,').split(',')
print(execute(name,*params))

def register(cmd):
    commands[cmd.__qualname__.split('.')[0]] = cmd
    return cmd.__qualname__.split('.')[0]

print(register(AddCommand.run))

