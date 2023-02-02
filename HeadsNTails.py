from flask import Flask, render_template, request, session,redirect,url_for
import random
import pyautogui #Finds Patterns, click and keyboard stuff
import win32gui, win32con
import win32ui
import win32api
from pynput.mouse import Listener
import logging
from threading import Thread
import os
# from Reaction_time import *
# from Scatter_Plotter import *

# Challenging seed 60
# Good seed 30


def mouse_recorder():
    logging.basicConfig(filename=f"mouse_log.txt", level=logging.DEBUG, format='%(asctime)s: %(message)s')

    def on_move(x, y):
        logging.info("M ({0}, {1})".format(x, y))

    def on_click(x, y, button, pressed):
        if pressed:
            logging.info('C ({0}, {1})'.format(x, y, button))
            time.sleep(0.2)

    with Listener(on_move=on_move, on_click=on_click) as listener:
        listener.join()

app = Flask(__name__,template_folder = "C:\eyetrack\PyTribe\Demo")
app.secret_key = "secret_key"
rect = {"top": 0, "left": 0, "width": 1920, "height": 1080}
import mss
import mss.tools
import time

def clear_local_storage():
    localStorage.clear()

@app.route("/")
def index():

    session["plays"] = 0

    session['demo'] = 0
    return render_template("index.html")

@app.route("/instructions")
def instructions():
    return render_template("instructions.html",display_winrate=display_winrate,display_results=display_results)


@app.route('/create_folder', methods=['POST'])
def create_folder():
    folder_name = request.form['folder_name']
    os.chdir("..")
    os.mkdir(folder_name)
    os.chdir(folder_name)
    try:
        os.makedirs('Screenshots')
    except:
        pass

    num = int(folder_name.split('.')[0])
    p = combinations[num-1][1]
    comb = combinations[num-1][0]
    display_winrate = combinations[num-1][2]
    display_results = combinations[num-1][3]
    random.seed(comb)
    counter = 0
    win = 0
    return redirect(url_for('index'))

@app.route("/demo", methods=["POST", "GET"])
def demo():
    global results
    global counter
    global win
    global choices
    try:
        counter += 1
    except:
        counter = 0
    if request.method == "POST":
        win32api.SetCursorPos((723, 540))
        choice = request.form["guess"]
        outcomes = ["Match", "Mismatch", "Match", "Mismatch", "Match", "Mismatch"]
        colors = ["green","red","green","red","green"]

        wincol = [0,1,1,2,2,3,3]
        win = wincol[counter]
        if outcomes[counter-1] == "Match":
            results.append(choice)
        else:
            temp = ["Heads","Tails"]
            temp.remove(choice)
            # print(temp)
            results.append(temp[0])
        if len(results) > 5:
            if results[0] == 'nothing':
                results.pop(0)
        if counter == 5:
            counter = 0
            win = 0
            return render_template("index.html")
        else:
            message = outcomes[counter-1]
            message_color = colors[counter-1]

        temp = (results[-5:])
        temp.reverse()
        return render_template("demo.html",display_winrate=display_winrate,display_results=display_results,message_color= message_color, message=message,WR = '%.2f' % ((win/[counter if counter>0 else 1][0])*100),results=temp,counter=counter,choice=choice)
    else:
        message = "please select an option"
        results = ['nothing' for _ in range(5)]
        temp = (results[-5:])
        temp.reverse()
        return render_template("demo.html", message=message,results=temp,counter=counter)



@app.route("/play", methods=["POST", "GET"])
def play():
    global results
    global counter
    global win
    global choices
    # mouse_recorder()
    if counter == 0:
        Thread(target=mouse_recorder).start()
    try:
        counter += 1
    except:
        counter = 0
    if request.method == "POST":
        win32api.SetCursorPos((723, 540))
        output = "screenshots/file_{}.png"
        with mss.mss() as sct:
            img = (sct.grab(rect))
            sct = mss.mss()
            cur = time.time()
            to_png = mss.tools.to_png
            to_png(img.rgb, img.size, output=output.format(cur))

        choice = request.form["guess"]
        try:
            choices.append(choice)
        except:
            choices = [choice]
        flip = random.choices(["Heads", "Tails"],weights=(p,1-p))[0]
        results.append(flip)
        if len(results) > 5:
            if results[0] == 'nothing':
                results.pop(0)
        if choice == "Play Again":
            results = ['nothing' for _ in range(5)]
            counter = 0
            win = 0
        if choice == "End Game":
            with open("results.txt", 'w') as output:
                for row in choices:
                    output.write(str(row) + '\n')
            # reaction()
            # Plotter()
            return render_template("index.html")
        elif choice == flip:
            message = "Match!"
            message_color = "green"

            try:
                win += 1
            except:
                win = 1
        else:
            message = "Mismatch"
            message_color = "red"
            try:
                win +=1
                win -=1
            except:
                win = 0
        temp = (results[-5:])
        temp.reverse()

        return render_template("result.html",display_winrate=display_winrate,display_results=display_results, message_color=message_color,message=message,WR = '%.2f' % ((win/[counter-1 if counter>0 else 1][0])*100),results=temp,counter=counter,choice=choice)
    else:
        results = ['nothing' for _ in range(5)]
        temp = (results[-5:])
        temp.reverse()
        return render_template("result.html", results=temp,counter=counter)

# def play():
#     if request.method == "POST":
#         # get user's guess
#         user_guess = request.form["guess"]
#
#         # generate a random outcome
#         outcomes = ["heads", "tails"]
#         outcome = random.choice(outcomes)
#
#         # check if the user's guess is correct
#         if user_guess.lower() == outcome:
#             result = "You won!"
#         else:
#             result = "You lost. The outcome was " + outcome + "."
#     else:
#         result = ""
#         user_guess = None
    return render_template("result.html", result=result,user_guess=user_guess, plays=session["plays"])


if __name__ == "__main__":
    # j = 0
    app.secret_key = "secretkey"
    # j+=1
    Name = input(r"Please enter the name of the participant: " + "\n")
    combinations = [[60, 0.6,False,False],[60, 0.68,False,False], [60, 0.68,True,False],
                    [60, 0.6,True,False], [30, 0.68,False,True], [30, .6,False,True],
                    [30, 0.6,True,True], [30, 0.6,True,True], [60, 0.6,False,True],
                    [60, 0.68,False,True], [60, 0.68,True,True], [60, 0.6,True,True],
                    [30, 0.68,False,False], [30, 0.6,False,False], [30, 0.6,True,False], [30, 0.68,True,False]]
    num = int(Name.split('.')[0])
    p = combinations[num-1][1]
    comb = combinations[num-1][0]
    # Challenging seed 60
    # Good seed 30
    random.seed(comb)
    display_winrate = combinations[num-1][2]
    display_results = combinations[num-1][3]
    os.chdir('../example/python_samples')
    try:
        os.makedirs(Name)
    except:
        pass
    os.chdir(Name)
    try:
        os.makedirs('Screenshots')
    except:
        pass
    Thread(target=app.run).start()
    # app.run()
    counter = 0
