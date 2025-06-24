from database import collection 
from models import User
from passlib.context import CryptContext #used to hash and verify passwords; impt to protect a user's password
from schemas import format_user
import re  #regex module to check if password is appropriate
from jwttoken import create_access_token

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")  #password hashing done using bycrpt

class Hasher:
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str):
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str):
        return pwd_context.hash(password)

def is_valid_name(name):
    return 2 < len(name) <= 70  # ensures that name is appropriate with at least 3-70 characters

def is_valid_email_format(email: str):
    regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"  # checks if email format is right
    return re.match(regex, email) is not None

def is_valid_email_domain(email):
    if "@" not in email:
        return False
    allowed_domains = ["gmail.com", "hotmail.com", "yahoo.com"] 
    domain = email.split("@")[1]
    return any(domain.endswith(d) for d in allowed_domains) or ".edu" in domain or ".org" in domain #checks for valid emails based on domain

def is_valid_phone(phone):
    return phone.isdigit() and len(phone) == 8  #checks if phone no. has 8 digits exact

def is_valid_password(pw):
    regex = r"^(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&]).{9,}$"  #checks if password has at least 9 char, 1 Uppercase letter, 1 Special char and 1 num
    return re.match(regex, pw)

#checks if registration is valid based on the above constraints
# if anything is invalid, the standard error message will be printed based on the error made
def register_user(user: User):
    all_errors = [] # a list created so that multiple error messages can be printed at once if >1 error is made
    
    #contains the list of conditions to check for data validation and their subsequent error message
    checks = [
        (is_valid_name(user.name), "Name must be 3-70 characters"),
        (is_valid_email_format(user.email), "Email must be a valid email address"),  
        (is_valid_email_domain(user.email), "Email must be from a valid domain (e.g., gmail.com, organisation)"),
        (is_valid_phone(user.phone), "Phone number must be exactly 8 digits"),
        (is_valid_password(user.password), "Password must have 9+ chars with uppercase, number and special character"),
        (not collection.find_one({"email": user.email}), "Email already registered")
    ]

    i = 0  #initialise to 0
    while i < len(checks):  #while loop to go through every condition to check if all requirements met
        condition, error_msg = checks[i]
        if not condition:
            all_errors.append(error_msg) #adds error message to the list all_errors
        i += 1
    
    if all_errors:
        return False, all_errors  #returns all the error messages
    
    user.password = Hasher.get_password_hash(user.password)  #hashes password before saving
    collection.insert_one(user.model_dump())  #saves user to the database
    return True, "User saved" #success message

#checks whether login is valid using email and password
def login_user(email, password):
    user = collection.find_one({"email": email})  #find user through email
    if not user:
        return False, "Email not found"   #returns this message if email not found in database
    if not Hasher.verify_password(password, user["password"]):  
        return False, "Incorrect password"   #returns this message if password does not match the hashed one
    token = create_access_token(data={"sub": user["email"]})
    return True, {"user": format_user(user), "access_token": token, "token_type": "bearer"}
