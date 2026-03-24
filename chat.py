from ai import model
import re
import csv
#paths = [r'C:\Users\Rafae\Downloads\en_test_human.txt']
paths =[
    r"C:\Users\Rafae\Downloads\amazon_rt_yelp.csv"
 ]
def open_and_save():
    entire_text = ''
    for path in paths:
        with open(path,'r',encoding='utf-8') as f:#r+ allows bot reading and writing
            if path.endswith('txt'):
                text = f.read()
            elif path.endswith('csv'):
                text = ''
                tex = csv.reader(f)
                for row in tex:
                    text += f'\n{row}'
            pattern = r'SPEECH\s+[0-9]+'
            text = re.sub(pattern,'',text)#ALWYAY SAVE re.sub 
            #re.sub replaces all found patters with a gives str
            pattern = r'__eou__\s*(\s*[0-9]){0,}'
            text= re.sub(pattern,' ',text)
            pattern = r'[?.!]\s+(\s+[0-9]){2,5}'
            text = re.sub(pattern,' ',text)
            pattern = r'\s[.]\s*(\s*[0-9]){0,}'
            text= re.sub(pattern,'. ',text)
            pattern = r'\s[,]'
            text= re.sub(pattern,', ',text)
            pattern = r'\s[’]'
            text= re.sub(pattern,'’ ',text)
            pattern = r'\s[!]\s*(\s*[0-9]){0,}'
            text= re.sub(pattern,'! ',text)
            pattern = r'\s[?]\s*(\s*[0-9]){0,}'
            text= re.sub(pattern,'? ',text)
            f.seek(0)#VERY IMPORTANT else it would write it at the end
            counter = 0
            for i in text.split('\n'):
                counter += 1
                if counter >= 100:
                    break
                print(i)
        with open(path,'w',encoding='utf-8') as f:
            f.write(text)
            entire_text += f'\n{text}'
    bulk_train(text)
def bulk_train(text:str):
    confirmation = input('Are you 100% sure that you want to perform this bulk training?')
    if confirmation == 'YesForSureYes100%YesYesYes':
        model.training(text)

def chat_ai():
    while True:
        question = input('What is your question to the ai (exit to exit)?')
        if question.lower() == 'exit':
            break
        print(model.ask(question))

if __name__ == '__main__':
    chat_ai()
    with open(r"C:\Users\Rafae\Downloads\MovieCorpus.txt", "r", encoding="utf8") as f:
        lines = sum(1 for _ in f)

    print(lines)
    import pickle
    with open(r"pickle_trained_data.pkl", "rb") as f:
        data = pickle.load(f)
        print(len(data))