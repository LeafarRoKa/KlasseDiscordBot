import json
import re
import pickle
#training

class simple_ai():
    def __init__(self):
        self.step = 3
        self.pattern = r'\b[a-zA-Z0-9]+\b[.?!]?'# the *,+ etc. comes after what you want to have or more times  
        self.open_efficient_trained_data()
        self.open_training_data()
        #self.training()

    def open_trained_data(self):# just tuple(str) takes every single char thats why i have to only tuple what i want so the values
        with open('trained_data.json','r') as f:
            unformated_trained_data = json.load(f)
        self.trained_data = {}
        for key,value in unformated_trained_data.items():
            if type(key) == str:
                key = key[1:-1]
                key = key.strip()
                key = [keypart[1:-1] for keypart in key.split(', ')]
                key = tuple(key)
            self.trained_data[key] = value
    def open_training_data(self):
        with open('ai_text.json','r') as f:
            self.training_data = json.load(f)

    def save_trained_data(self):
        json_dict = {}
        for key,value in self.trained_data.items():
            json_dict[str(key)] = value

        with open('trained_data.json', 'w') as f: 
            json.dump(json_dict,f)

    def save_efficient_trained_data(self):
        with open('pickle_trained_data.pkl','wb') as f:
            pickle.dump(self.trained_data,f)

    def open_efficient_trained_data(self):
        try:
            with open('pickle_trained_data.pkl','rb') as f:
                self.trained_data = pickle.load(f)
        except (TypeError,EOFError):
            self.trained_data = {}
            self.save_efficient_trained_data()
        

    def training(self,training_data:str = None,trained_data:dict = None):
        if training_data is None:
            training_data = self.training_data
        if trained_data is None:
            trained_data = self.trained_data
        split_by_lines = training_data.split('\n')
        if len(split_by_lines) > 1:
            for line in split_by_lines:
                self.training(line)
            return
        words = re.findall(self.pattern, training_data)
        words_sets = []
        for i in range(0,len(words)):
            wordset = tuple(words[i:i+self.step])
            words_sets.append(wordset)#from i to and without i+3 so word1 and word2 no word3
            if wordset not in trained_data.keys():
                trained_data[wordset] = {}
            if len(words) <= i+self.step:
                next_word = '.'
            else:  
                next_word = str(words[i+self.step])
            if next_word not in trained_data[wordset]:
                trained_data[wordset][next_word] = 0
            trained_data[wordset][next_word] += 1
            if next_word == '.':
                break
        self.save_efficient_trained_data()

    def ask(self,question:str,step:int=None,response:str='',end_response:bool=False):
        question = question.strip('?!.')
        if step is None:
            step = self.step
        if step-self.step <= 0:
            last_words_in_question = tuple([obj.lower() for obj in re.findall(self.pattern, question)][-step:])#everyting after -3
        else:
            last_words_in_question = tuple([obj.lower() for obj in re.findall(self.pattern, question)][-step:-int(step-self.step)])
        step = self.step
        #if any(word in ['the','a','an','to','of','and','is'] for word in last_words_in_question):
        #    return self.ask(question,step+1)
        if all(last_words_in_question != tuple(d.lower() for d in data) for data in self.trained_data.keys()):
            if len(last_words_in_question) <= step:
                if not response:
                    return 'No Answer'
                return response
            return self.ask(question,step+1)
        words = case_insensitive_get(last_words_in_question, self.trained_data)
        word = max(words,key=words.get)
        if word in ['.','!','?'] or any(char in word for char in ['.','!','?']):
            return response +word
        if end_response and word[-1] == '.':
            return response
        if response:
            response += f' {word}'
        else:
            response += word
        question += f' {word}'
        if len(response) > 30:
            return self.ask(question,response=response,end_response=True)
        return self.ask(question,response=response)   

def case_insensitive_get(key,dict):
    def lowerer(key):
        if isinstance(key,tuple):
            key = tuple(k.lower() for k in key)
        elif isinstance(key,list):
            key = [k.lower() for k in key]
        elif isinstance(key,str):
            key = key.lower()
        else:
            raise SyntaxError('Not a valid type.')
        return key
    key = lowerer(key)
    for ke,val in dict.items():
        ke = lowerer(ke)
        if key == ke:
            return val
    return None   
model = simple_ai()