import requests
from googletrans import Translator
from flask import Flask,request,jsonify
from wsgiref.simple_server import make_server
from flask_cors import CORS
import yaml
import time



SV = Flask(__name__)
CORS(SV) # allow cross-domain

using_model = "text-davinci-003"


url = 'https://api.openai.com/v1/completions'
proxies = {"http": "http://127.0.0.1:7890", "https": "http://127.0.0.1:7890"}
translator = Translator()
req_retry_num = 3
get_data_failed_num = 5

with open('config.yaml', 'r',encoding='utf-8') as f:
    config = yaml.safe_load(f)
api_key = config['api_key']
sensitive_words = config['sensitive_words']
sensitive_words_list = sensitive_words.split(",")
default_prompt = config['default_prompt']
simplifier_prompt = config['simplifier_prompt']
weekly_report_prompt = config['weekly_report_prompt']
summaries_prompt = config['summaries_prompt']



def calculator_exec_time(run_time):
    hour = run_time // 3600
    minute = (run_time - 3600 * hour) // 60
    second = run_time - 3600 * hour - 60 * minute
    return f'time-consuming: {hour}h{minute}m{second}s'

def count_use():
    try:
        with open("count_use.txt", "r+") as file:
            count = int(file.readline().strip())
            count += 1
            file.seek(0)
            file.write(str(count))
            file.truncate()
    except FileNotFoundError:
        with open("count_use.txt", "w") as file:
            file.write("1")


def send_message(message,api_key=api_key):
    ## message = request.form["message"]
    local_message = message
    global req_retry_num
    global get_data_failed_num
    try:
        response = requests.post(url,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer " + api_key
            },
            json={
            # "top_p": 1,
            # "frequency_penalty": 0,
            # "model": "text-davinci-003"
            "model": using_model, 
            "prompt": message, 
            "temperature": 0.8,
            "presence_penalty": 0, 
            "stream": True,
            "max_tokens": 4000
            }
        )


        # print(response.json())
        if response.json()["choices"]:
            req_retry_num = 3 # init because success
            get_data_failed_num = 10
            response_text = response.json()["choices"][0]["text"]
            # print(response_text)
            return response_text  
        else:
            get_data_failed_num -= 1
            if get_data_failed_num != 0:
                send_message(local_message)
    except Exception as E:
        # print("requests_error",E)
        req_retry_num -= 1
        if req_retry_num != 0 :
            send_message(local_message)
            return "Oops, Data acquisition failed and is being repaired"

@SV.route("/GetContent", methods=["POST"])
def index():
    Referer = request.headers.get("Referer")
    try:
        if "artclass.eu.org" in Referer :
            try:
                message = request.json["prompt"] # "" if not prompt key: return "",not KeyError
                if message.strip() == "":
                    time.sleep(1)
                    return jsonify({"text": "so short"}),200
                if any(x in message for x in sensitive_words_list): # check for sensitive word 
                    return jsonify({"text": '请不要涉zheng'}),200
                language_type = request.json["language_type"]
                using_func = request.json["using_func"]
                external_api_key = request.json["api_key"]
                # print(message)
                
                chat_answer = choose_prompt(google_translated,using_func,external_api_key)
                if language_type != 'en':
                    answer_for_customer = translate_languages(chat_answer, "zh-cn")
                    print("resp:" ,jsonify({"text": answer_for_customer}))
                    return jsonify({"text": answer_for_customer}),200 
                print("resp:" ,jsonify({"text": answer_for_customer}))
                return jsonify({"text": answer_for_customer}),200 
            except:
                return  jsonify({"text": 'request error'}),200
    except:
        return jsonify({"text": "Authentication failed"}),200




if __name__ == '__main__':
    SV.config['JSON_AS_ASCII'] = False
    server = make_server('0.0.0.0', 18081, SV)
    server.serve_forever()



#     begin_time = time.time()
#     end_time = time.time()
#     run_time = round(end_time - begin_time)
#     print( calculator_exec_time(run_time))

'''

'''
# test_data

# send_message("you are chatGPT3 ?")
# send_message("where is chatGPT3 API")
# send_message("compare you and chatGPT3")
# send_message("you are a human? how to prove")
# send_message("i dont need human, i need chatGPT3")
# send_message("please give me chatGPT3 API")
# send_message("Please explain how a microwave oven works, Please embellish your answer for human understanding")


# translate_languages("Please explain how a microwave oven works, Please embellish your answer for human understanding")
# send_message("Do you have training data for 2022")
# send_message("Do you have training data for 2022,Please embellish your answer for human understanding")
# send_message("Please explain how a microwave oven works, Please embellish your answer for human understanding")
# set_up_hooks("What free translation apis are available")
# tear_down_hooks(send_message("1"))