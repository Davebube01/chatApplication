from flask import Flask, render_template, url_for, request, redirect
from flask_login import LoginManager, login_required, logout_user, login_user, current_user, UserMixin
from flask_socketio import SocketIO, join_room, leave_room
from pymongo.errors import DuplicateKeyError
from database import get_user, save_new_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(username):
    return get_user(username)

# Login page
@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    message = ''
    if request.method == "POST":
        username = request.form["username"]
        password = request.form['password']
        user = get_user(username)

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            message = 'Failed to Login!'
    return render_template ("login.html", message = message)   

# Regcister page 
@app.route("/signup", methods=['GET', 'POST'])
def signup():
    message = ''
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form['password']
        try:
            save_new_user(username, email, password)
            return redirect(url_for('login'))
        except DuplicateKeyError:
            message = 'Username already exists'
    return render_template ("signup.html", message = message)

# index page
@app.route("/index")
@login_required
def index():
    return render_template ("index.html")

#Other pages
@app.route("/<string:page_name>")
def page(page_name):
    return render_template (page_name)

# for logging out to login page
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect('login')

# To enter chatroom.
@app.route("/chat_login", methods=['POST','GET'])
def chat():
    try:
        if request.method == 'POST':
            username = request.form['username']
            room = request.form['roomId']
            if username and room:
                return render_template('chat-room.html', username=username, room=room)
            else:
                return redirect(url_for('index'))
    except Exception as e:
        print(e)

@socketio.on("connect")
def connection():
    print('client connected')

# To monitor the room joining events. i.e when one joins a chat room.
@socketio.on('join_room_event')
def join_room_event_handler(data):
    # print(f"User {data['username']} has joined the room {data['room']}")
    app.logger.info(f"User {data['username']} has joined room {data['room']}")
    
    join_room(data['room'])
    # This will send an announcement to other people in the room that someone has joined the room
    socketio.emit('join_room_announcement', data)
    # check the script tag for continuation of code

# For new messages
@socketio.on("new_message")
def handle_new_message(data):
    print(f"New message: {data['message']}")
    socketio.emit("reciever_message", data, room=data['room'])

if __name__=='__main__':
    socketio.run(app, debug=True)
