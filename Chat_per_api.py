import codecs, secrets, string, datetime, time, random, os.path
from flask import request, jsonify, send_file, Flask
from random import randint
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
app = Flask(__name__)
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["24000 per day", "1000 per hour"]
)
wsgi_app = app.wsgi_app
systemRandom = random.SystemRandom()


max_lines = 100 #change this value if you want longer chats, default is 100
#generate ids with 6 numbers, you can change it
start_id = 100000
end_id = 999999
#################
token_length = 512 #how long a token will be



#Here the client can request an ID
@app.route('/request/id')
@limiter.limit("100/hour;5/minute") #Set a Limit to avoid spamming
def request_id():
        id = randint(start_id, end_id)
        my_file = ("dm_chats/0_user_ids/"+str(id))
        try:
            f = open("dm_chats/0_user_ids/"+str(id))
            # Do something with the file
        except IOError:
            return ("Error, please try again")
        finally:
            with codecs.open("dm_chats/0_user_ids/"+str(id), 'a', 'utf-8', 'strict') as fh:
                token = secrets.token_hex(token_length)  
                fh.write(token)
            return (str(id)+"&token="+token)

@app.route('/send/dm')
def send_dm():
    sender_id = request.args.get('sender_id', None)
    recipient_id = request.args.get('recipient_id', None)
    text = request.args.get('text', None)
    token = request.args.get('token', None)
    nickname = request.args.get('nickname', sender_id)
    if sender_id is None:
       return {"ERROR": "You have to submit a sender"}, 400
    if sender_id is not None:
        if recipient_id is None:
            return {"ERROR": "You have to submit a recipient"}, 400
        if recipient_id is not None:
            if text is None:
                print (open("dm_chats/0_user_ids/"+sender_id))
                fileObject = open("dm_chats/0_user_ids/"+sender_id, "r")
                token_file = fileObject.read()
                if not(token_file == token):
                    print("Error")
                    return ("ERROR")
                if (token_file == token):
                    #Den Namen mit einem Algorythmen bestimmen damit es immer eindeutig die gleiche Datei ist
                    if(sender_id < recipient_id):
                        filename = (sender_id+recipient_id)
                        file = ("dm_chats/"+filename+'.txt')
                        return send_file(file, mimetype='text/plain')
                    else:
                        filename = (recipient_id+sender_id)
                        file = ("dm_chats/"+filename+'.txt')
                        return send_file(file, mimetype='text/plain')
            if text is not None:
                #Token überprüfen
                print (open("dm_chats/0_user_ids/"+sender_id))
                fileObject = open("dm_chats/0_user_ids/"+sender_id, "r")
                token_file = fileObject.read()
                if not(token_file == token):
                    print("Error")
                    return ("ERROR")
                if (token_file == token):
                    #Den Namen mit einem Algorythmen bestimmen damit es immer eindeutig die gleiche Datei ist
                    if(sender_id < recipient_id):
                        filename = (sender_id+recipient_id)
                    else:
                        filename = (recipient_id+sender_id)
                    with codecs.open("dm_chats/"+filename+'.txt', 'a', 'utf-8', 'strict') as fh:
                       print (nickname+":"+ text)
                       fh.write(nickname+":"+ text+"\n")
                       file = open("dm_chats/"+filename+'.txt', "r")
                       line_count = 0
                       for line in file:
                           if line != "\n":
                               line_count += 1
                       file.close()
                       if line_count > max_lines:
                            with open("dm_chats/"+filename+'.txt', 'r') as fin:
                                data = fin.read().splitlines(True)
                            with open("dm_chats/"+filename+'.txt', 'w') as fout:
                                fout.writelines(data[1:])
                            file = ("dm_chats/"+filename+'.txt')
                            return send_file(file, mimetype='text/plain')
                       else:
                            file = ("dm_chats/"+filename+'.txt')
                            return send_file(file, mimetype='text/plain')









#   mmm  #               m           mmmmm
# m"   " # mm    mmm   mm#mm         #   "#  mmm    mmm   mmmmm   mmm
# #      #"  #  "   #    #           #mmmm" #" "#  #" "#  # # #  #   "
# #      #   #  m"""#    #     """   #   "m #   #  #   #  # # #   """m
#  "mmm" #   #  "mm"#    "mm         #    " "#m#"  "#m#"  # # #  "mmm"




#Add message to the chat room, example: "/send?room=test2&author=Xenic&text=Welcome to this api"
@app.route('/send')
def send_message():
    room = request.args.get('room', None)
    author = request.args.get('author', None)
    text = request.args.get('text', None)
    if room is None:
       return {"ERROR": "You have to submit a room name"}, 400
    if room is not None:
        if author is None:
            return {"ERROR": "You have to submit a author name"}, 400
        if author is not None:
            if text is None:
                return {"ERROR": "You have to submit the text"}, 400
            if text is not None:
                with codecs.open("chats/"+room+'.txt', 'a', 'utf-8', 'strict') as fh:
                   print (author+":"+ text)
                   fh.write(author+":"+ text+"\n")
                   file = open("chats/"+room+'.txt', "r")
                   line_count = 0
                   for line in file:
                       if line != "\n":
                           line_count += 1
                   file.close()
                   if line_count > max_lines:
                        with open("chats/"+room+'.txt', 'r') as fin:
                            data = fin.read().splitlines(True)
                        with open("chats/"+room+'.txt', 'w') as fout:
                            fout.writelines(data[1:])
                        return ("Posted, you can get the room with /get?room="+room)
                   else:
                        return ("Posted, you can get the room with /get?room="+room)
#Get messages from a room, example is: "/get?room=test"
@app.route('/get')
def get_dm_chat():
    room = request.args.get('room', None)
    if room is None:
       return {"ERROR": "You have to submit a room name"}, 400
    if room is not None:
           if os.path.isfile("chats/"+room+'.txt'):
                file = ("chats/"+room+'.txt')
                return send_file(file, mimetype='text/plain')
           else:
                return ("Room is not created, just start chatting into the room to create it")

#Download the room text file instant, example: "/download?room=test"
@app.route('/download')
def download_room():
    room = request.args.get('room', None)
    if room is None:
       return {"ERROR": "You have to submit a room name"}, 400
    if room is not None:
           if os.path.isfile("chats/"+room+'.txt'):
                filename = "chats/"+room+'.txt'
                return send_file(filename, as_attachment=True)
           else:
                return ("Room is not created, just start chatting into the room to create it")

@app.errorhandler(Exception)
def handle_error(e):
    return ("Route doesn't exist")

@app.route("/ping")
@limiter.exempt
def ping():
    return "PONG"

if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True,)