from pydantic import BaseModel

# a user's information is taken from the database and impt info like name, email and phone number is returned
# password not returned for personal data protection
def format_user(user):
    return {
        "name": user["name"],
        "email": user["email"],
        "phone": user["phone"],
    }

#returns the data of all the users in the database
def all_users(users):
    return [format_user(user) for user in users]

# defines data model for when user is logging in
#purpose of putting here is so that when user is prompted to login, it is viewed in this format
class LoginRequest(BaseModel):
    email: str
    password: str
