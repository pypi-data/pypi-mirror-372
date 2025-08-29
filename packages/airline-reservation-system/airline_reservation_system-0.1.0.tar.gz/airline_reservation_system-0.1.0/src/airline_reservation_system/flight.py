from . import db
import json


def list_All_flights():
    response = db.supabase.table("flights").select("*").execute()
    print(json.dumps(response.data, indent = 4))

def get_flight_details():
    
    flight_no = input("Enter the Flight Number to Get Details : ")
    response = db.supabase.table("flights").select("*").eq("flight_no",flight_no).execute()
    
    if response.data:
        print(json.dumps(response.data, indent = 4))
    
    else:
        print("Invalid Flight Number !!!")
        
def search_your_flight():
    
    num_flight = input("Enter the ID to Search the Flight : ")
    
    res = db.supabase.table("users").select("*").eq("user_id",num_flight).execute()
    if res.data:
        response = db.supabase.table("bookings").select("*").eq("user_id",num_flight).execute()
        
        if response.data:
            print(json.dumps(response.data, indent = 4))
            
        else:
            print("You have Not Booked any Flights")
    
    else:
        print("Enter Valid ID !!!!")
        return
    

    
