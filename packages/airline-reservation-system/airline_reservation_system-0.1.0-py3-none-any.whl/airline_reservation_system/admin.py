from . import db
import json


def add_flight():
    print("To Add the Flight Enter the Details")
    
    id = input("Enter Flight ID : ")
    origin = input("Enter the Origin of Flight : ")
    destination = input("Enter the Detination of the Flight : ")
    date = input("Enter the Date of the Flight : ")
    seats = input("Enter the total Number of Seats in the Flight : ")
    available_seats = input("Enter the Seats Available in the Flight : ")
    flight_no = input("Enter Flight Number : ")
    
    flight_dict = {
        "id" : id,
        "origin" : origin,
        "destination" : destination,
        "date" : date,
        "seats" :seats,
        "available_seats" : available_seats,
        "flight_no" : flight_no
    }
    
    response = db.supabase.table("flights").insert(flight_dict).execute()
    
    if response.data:
        print("Flight Added successfully registered !!!")
        return
    else:
        print("Falied to register the Flight !!!")
        return
def update_flight_details():
    
    print("To Update the Flight Enter the Details")
    
    print("1. Origin of Flight")
    print("2. Destination of Flight")
    print("3. Date of Flight")
    print("4. Seats of Flight")
    print("5. To change the Available Flights")
    print("6. To Change Flight Number")
    
    id = input("Enter Flight ID : ")
    flight_num = int(input("Enter the Number to Update : "))
    flight_dict = {}
    
    if flight_num == 1:
    
        origin = input("Enter the Origin of Flight to Modify : ")
        flight_dict["origin"] = origin
    
    elif flight_num == 2:
        
        destination = input("Enter the Detination of the Flight : ")
        flight_dict["destination"] = destination
        
    elif flight_num == 3:
        
        date = input("Enter the Date of the Flight : ")
        flight_dict["date"] = date
        
    elif flight_num == 4 :
        
        seats = input("Enter the total Number of Seats in the Flight : ")
        flight_dict["seats"] = seats
        
    elif flight_num == 5:
        
        available_seats = input("Enter the Seats Available in the Flight : ")
        flight_dict["available_seats"] = available_seats
        
    elif flight_num == 6:
        
        flight_no = input("Enter Flight Number : ")
        flight_dict["flight_no"] = flight_no
    
    elif flight_num == 7:
        
        return
    
    response = db.supabase.table("flights").update(flight_dict).eq("id",id).execute()
    if response.data:
        print(json.dumps(response.data, indent = 4))
    
    else:
        print("Invalid To Modify !!!")    
    
        

def delete_flight():
    
    flight_no = input("Enter the Flight Number to Delete : ")
    
    response = db.supabase.table("flights").delete().eq("flight_no",flight_no).execute()
    
    if response.data:
        print(json.dumps(response.data, indent = 4))
    
    else:
        print("Invalid Flight Number !!!")
        
def view_all_bookings():
    
    response = db.supabase.table("bookings").select("*").execute()
    
    if response.data:
        print(json.dumps(response.data,indent = 4))
        return
    else:
        print("Falied to fetch !!!")
        return
    
def view_all_users():
    
    response = db.supabase.table("users").select("*").execute()
    
    if response.data:
        print(json.dumps(response.data,indent = 4))
        return
    else:
        print("Falied to fetch !!!")
        return
    
def view_all_flights():
    
    response = db.supabase.table("flights").select("*").execute()
    
    if response.data:
        print(json.dumps(response.data,indent = 4))
        return
    else:
        print("Falied to fetch !!!")
        return
    


