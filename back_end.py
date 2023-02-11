# -*- coding: UTF-8 -*-
import requests
from googletrans import Translator
import time
from flask import Flask, request,jsonify
from wsgiref.simple_server import make_server
from flask_cors import CORS






SV = Flask(__name__)
CORS(SV) # allow cross-domain

using_model = "text-davinci-003"
api_key = "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"
url = 'https://api.openai.com/v1/completions'
# url = 'https://api.openai.com/v1/engines/text-davinci-003'
# openai.api_key = api_key
# openai.Model.list()
proxies = {"http": "http://127.0.0.1:7890", "https": "http://127.0.0.1:7890"}

model = "text-ada-001,text-babbage-001,text-curie-001,text-davinci-003"
# translator = Translator(service_urls=['translate.google.com','translate.google.co.kr'])
translator = Translator()


def calculator_exec_time(run_time):
    hour = run_time // 3600
    minute = (run_time - 3600 * hour) // 60
    second = run_time - 3600 * hour - 60 * minute
    return f'time-consuming: {hour}h{minute}m{second}s'

# def set_up_hooks(coustomer_messages,dest='en'):
#     try :
#         tranlated = translate_languages(coustomer_messages,dest=dest)
#         print(tranlated)
#         return tranlated
#     except Exception as E:
#         print("translate error: ",E)


# def tear_down_hooks(coustomer_messages):
#     translate_languages(coustomer_messages,dest='zh-cn')
#     pass


def translate_languages(translate_messages,dest='en') :
    try:
        tranlated = translator.translate(translate_messages, dest=dest)
        print(tranlated.text)
        return tranlated.text
    except Exception as E:
        print("translate error: ", E)
        return "translate error"

def send_message(message):
    ## message = request.form["message"]
    local_message = message
    req_retry_num = 3
    get_data_failed_num = 10
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
            "model": using_model, "prompt": message, "temperature": 0.5,"presence_penalty": 0, "max_tokens": 2048
            }
        )


        print(response.json())
        if response.json()["choices"]:
            req_retry_num = 3
            get_data_failed_num = 10
            response_text = response.json()["choices"][0]["text"]
            print(response_text)
            return response_text  # "A microwave oven works by using a special type of energy called microwaves.  These microwaves are generated by a device called a magnetron, which is located inside the oven.  The microwaves are then directed into the oven's cooking chamber, where they bounce off the walls and penetrate the food.  The microwaves cause the water molecules in the food to vibrate, which generates heat and cooks the food.  The microwaves are then absorbed by the walls of the oven, preventing them from escaping and keeping the heat inside.  The heat is then evenly distributed throughout the food, cooking it quickly and evenly."
        else:
            get_data_failed_num -= 1
            if get_data_failed_num != 0:
                send_message(local_message)
    except Exception as E:
        print("requests_error",E)
        req_retry_num -= 1
        if req_retry_num != 0 :
            send_message(local_message)
            return "oops, Data acquisition failed and is being repaired"


@SV.route("/GetContent", methods=["POST"])
def index():
    Referer = request.headers.get("Referer")
    if "artclass.eu.org" in Referer :
        try:
            message = request.json["prompt"]
            print(message)
            # google_translated = translate_languages("微波炉的工作原理","en")
            google_translated = translate_languages(message,"en")
            chat_answer = send_message(google_translated + ",Please embellish your answer for human understanding")
            answer_for_customer = translate_languages(chat_answer, "zh-cn")
            # 执行函数内容
            resp = jsonify({"text": answer_for_customer})
            return resp.encode('utf-8')  # + " Function executed successfully"
        except:
            return 'request error'

    else:
        return "Authentication failed"



if __name__ == '__main__':
    SV.config['JSON_AS_ASCII'] = False
    server = make_server('0.0.0.0', 18081, SV)
    server.serve_forever()

#     begin_time = time.time()
#     end_time = time.time()
#     run_time = round(end_time - begin_time)
#     print( calculator_exec_time(run_time))


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