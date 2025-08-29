from . import db
import json
def book_tickets():
    
    print("To Book the Tickets Please Enter the Following Details")
    user_id = input("Enter the User ID : ")
    flight_id = input("Enter the Flight Number : ")
    booking_time = input("Enter the Booking Time : ")
    
    data = {"user_id":user_id , "flight_id":flight_id , "booking_time":booking_time}
    response = db.supabase.table("bookings").insert(data).execute()
    
    if response.data:
        print("Booking Successfull !!!")
        print("The Flight of",flight_id,"is booked for User",user_id,"is Conformed at Timing",booking_time)
        
    else:
        print("Booking Unsuccessful !!!")
        
def cancel_booking():
    
    print("To Cancel the Tickets Please Enter the Following Details")
    user_id = input("Enter the User ID : ")
    flight_id = input("Enter the Flight Number : ")
    booking_time = input("Enter the Booking Time : ")
    
    data = {"user_id":user_id , "flight_id":flight_id , "booking_time":booking_time}
    response = db.supabase.table("bookings").delete().match(data).execute()
    
    if response.data:
        print("Cancellation Successfull !!!")
        print("The Flight of",flight_id,"is Cancelled for User",user_id,"is Conformed at Timing",booking_time)
        
    else:
        print("Cancellation Unsuccessful !!!")
    
    

def view_booking_history():
    print("To view the Booked Tickets Please Enter the Following Details")
    user_id = input("Enter the User ID : ")
    
    response = db.supabase.table("bookings").select("*").eq("user_id",user_id).execute()
    
    if response.data:
        print(json.dumps(response.data ,indent = 4))
    else:
        print("No History Found !!!!")
    

def modify_booking():

    print("To Modify the Tickets Please Enter the Following Details")
    id = input("Enter the Booking ID : ")
    
    print("1. Flight ID")
    print("2. Booking Timing")
    
    num_mod = int(input("Enter the Number to Modify : "))
    mod_dict = {}
    
    if num_mod == 1:
        flight_id = input("Enter the Flight Number : ")
        mod_dict["flight_id"] = flight_id
        
    elif num_mod == 2:
        booking_time = input("Enter the Booking Time : ")
        mod_dict["booking_time"] = booking_time
        
    elif num_mod == 3:
        return
    
    response = db.supabase.table("bookings").update(mod_dict).eq("id",id).execute()
    print(response.data)
    if response.data:
        print("Flight Details Has Been Modified successfully")
    else:
        print("Modification is Not Successfull")

