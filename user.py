from werkzeug.security import check_password_hash

# To be created when using the Flask-login, Check documentation
class User:
    def __init__(self, username, email, password) -> None:
        self.username = username
        self.email = email
        self.password = password
        pass

    def is_authenticated():
        return True
    
    def is_active():
        return True
    
    def is_anonymous():
        # return True
        return False
    
    def get_id(self):
        return self.username
        
    def check_password(self, password_input):
        return check_password_hash(self.password, password_input)
