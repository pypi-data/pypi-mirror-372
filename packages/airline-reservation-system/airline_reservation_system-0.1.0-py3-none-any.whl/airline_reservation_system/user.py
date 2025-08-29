from . import db 

def register_user(user_id, name, email, password, phone):
    data = {
    "user_id" : user_id,
    "name": name,
    "email": email,
    "password": password, 
    "phone": phone}
    response = db.supabase.table("users").insert(data).execute()
    if response.data:
        print("User successfully registered !!!")
        return
    else:
        print("Falied to register the user !!!")
        return

def login_user(email,password):
    
    response = db.supabase.table("users").select("*").eq("email", email).eq("password", password).execute()
    if response.data:
        print("Login successful! Welcome", response.data[0]["name"])
        return True
    
    else:
        print("Invalid email or password!")
        return False
        
def update_profile():
    
    print("Enten the data to update the detail : ")
    
    user_id = input("Enter the User ID :")
    
    print("1. Name")
    print("2. E-Mail")
    print("3. Password")
    print("4. Quit")
    update_dict = {}
    num = int(input("Enter option to update the detail : "))
    
    if num == 1:
        name = input("Enter the name to update : ")
        update_dict["name"] = name
        
    elif num == 2:
        email = input("Enter the E-Mail to update : ")
        update_dict["email"] = email
        
    elif num == 3:
        password = input("Enter the Password to update : ")
        update_dict["password"] = password
        
    elif num == 4:
        exit()
    response = db.supabase.table("users").update(update_dict).eq("user_id",user_id).execute()
    if response.data:
        print("Details has been updated !!!")
        return
    
    else:
        print("Details is not been updated !!!")
        return 
    
def delete_user(email):
    response = db.supabase.table("users").delete().eq("email", email).execute()
    if response.data:
        print(f"User with email {email} deleted successfully!")
        return
    
    else:
        print(f"User with email {email} not found or deletion failed.")
        return
    