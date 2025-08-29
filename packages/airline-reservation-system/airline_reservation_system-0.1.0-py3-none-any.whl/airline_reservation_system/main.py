from . import user
from . import admin
from . import flight
from . import booking

def main():
    """Main function to run the airline reservation system"""
    
    while True:  # Main application loop
        print("\n=== AIRLINE RESERVATION SYSTEM ===")
        print("1. Register User")
        print("2. Login User")
        print("3. Delete User")
        print("4. Update User")
        print("5. Admin")
        print("6. Quit")
        
        try:
            num = int(input("Enter the Number of the choice : "))
        except ValueError:
            print("Please enter a valid number!")
            continue
        
        if num == 1:
            user_id = input("Enter User ID : ")
            name = input("Enter Name : ")
            email = input("Enter E-Mail : ")
            password = input("Enter Password : ")
            phone = input("Enter Phone Number : ")
            
            user.register_user(user_id, name, email, password, phone)
            
        elif num == 2:
            email = input("Enter E-Mail : ")
            password = input("Enter Password : ")
            
            valid = user.login_user(email, password)
            
            if valid:
                while True:  # User menu loop
                    print("\n=== USER MENU ===")
                    print("1. Flights Details")
                    print("2. Booking Tickets of Flights")
                    print("3. Payments")
                    print("4. Quit")
                    
                    try:
                        num_login = int(input("Enter the Choice : "))
                    except ValueError:
                        print("Please enter a valid number!")
                        continue
                    
                    if num_login == 1:
                        while True:  # Flight details loop
                            print("\n=== FLIGHT DETAILS ===")
                            print("1. List All Flights")
                            print("2. Get Flight Details")
                            print("3. Search Your Flight")
                            print("4. Quit")
                            
                            try:
                                num_flight = int(input("Enter Number to Search Flight or Get Details of Flight: "))
                            except ValueError:
                                print("Please enter a valid number!")
                                continue
                            
                            if num_flight == 1:
                                flight.list_All_flights()
                            elif num_flight == 2:
                                flight.get_flight_details()
                            elif num_flight == 3:
                                flight.search_your_flight()
                            elif num_flight == 4:
                                print("Returning to User Menu...")
                                break
                            else:
                                print("Invalid Number! Please choose 1-4.")
                                
                    elif num_login == 2:
                        while True:  # Booking loop
                            print("\n=== BOOKING MENU ===")
                            print("1. Book Flight Tickets")
                            print("2. Cancel Booking")
                            print("3. See Booking History")
                            print("4. Modify Booking")
                            print("5. Quit")
                            
                            try:
                                num_book = int(input("Enter the Number to View : "))
                            except ValueError:
                                print("Please enter a valid number!")
                                continue
                            
                            if num_book == 1:
                                booking.book_tickets()
                            elif num_book == 2:
                                booking.cancel_booking()
                            elif num_book == 3:
                                booking.view_booking_history()
                            elif num_book == 4:
                                booking.modify_booking()
                            elif num_book == 5:
                                print("Returning to User Menu...")
                                break
                            else:
                                print("Invalid Number! Please choose 1-5.")
                                
                    elif num_login == 3:
                        flight.search_your_flight()
                        
                    elif num_login == 4:
                        print("Logging out...")
                        break
                    else:
                        print("Invalid Number! Please choose 1-4.")
        
        elif num == 3:
            email = input("Enter E-Mail to Delete the user : ")
            user.delete_user(email)
            
        elif num == 4:
            user.update_profile()
        
        elif num == 5:
            while True:  # Admin menu loop
                print("\n=== ADMIN MENU ===")
                print("1. To Add a Flight")
                print("2. To Modify the Flight Detail")
                print("3. Delete the Flight")
                print("4. View all Bookings")
                print("5. View all Users")
                print("6. View all flights")
                print("7. Quit")
                
                try:
                    admin_num = int(input("Enter The Number to View or Modify : "))
                except ValueError:
                    print("Please enter a valid number!")
                    continue
                
                if admin_num == 1:
                    admin.add_flight()
                elif admin_num == 2:
                    admin.update_flight_details()
                elif admin_num == 3:
                    admin.delete_flight()
                elif admin_num == 4:
                    admin.view_all_bookings()
                elif admin_num == 5:
                    admin.view_all_users()
                elif admin_num == 6:
                    admin.view_all_flights()
                elif admin_num == 7:
                    print("Returning to Main Menu...")
                    break
                else:
                    print("Invalid Number! Please choose 1-7.")
                    
        elif num == 6:
            print("Thank you for using Airline Reservation System!")
            break
        else:
            print("Invalid Number! Please choose 1-6.")

if __name__ == "__main__":
    main()