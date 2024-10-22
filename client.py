
import socket
 
def convert_to_hex(address, data):
    # Format address and data to 8-character hexadecimal strings
    address_hex = f"{address:08X}"
    data_hex = f"{data:08X}"
    return address_hex, data_hex
 
def update_icon_status(client_socket):
    icon_status = 0b00000000  # Initialize all icons to OFF (0)
 
    # Function to update a specific icon's status and print address and data
    def set_icon_status(icon_index, state):
        nonlocal icon_status
        if state:  # If the icon should be ON
            icon_status |= (1 << icon_index)  # Set the specific bit to 1
        else:  # If the icon should be OFF
            icon_status &= ~(1 << icon_index)  # Set the specific bit to 0
           
        # After updating the icon status, print address and data
        address = 0x04  # Use the same address for all icons
        address_hex, data_hex = convert_to_hex(address, icon_status)
        print(f"Address Code: {address_hex}, Data Code: {data_hex}")
 
    while True:
        try:
            # Get individual icon status from user input
            left_indicator = input("Is Left Indicator ON? (yes/no): ").strip().lower() == 'yes'
            set_icon_status(0, left_indicator)  # Icon index 0 for Left Indicator
           
            right_indicator = input("Is Right Indicator ON? (yes/no): ").strip().lower() == 'yes'
            set_icon_status(1, right_indicator)  # Icon index 1 for Right Indicator
           
            seatbelt = input("Is Seatbelt ON? (yes/no): ").strip().lower() == 'yes'
            set_icon_status(2, seatbelt)  # Icon index 2 for Seatbelt
           
            engine_heat = input("Is Engine Heat ON? (yes/no): ").strip().lower() == 'yes'
            set_icon_status(3, engine_heat)  # Icon index 3 for Engine Heat
           
            parking_indicator = input("Is Parking Indicator ON? (yes/no): ").strip().lower() == 'yes'
            set_icon_status(4, parking_indicator)  # Icon index 4 for Parking Indicator
           
            beam_status = input("Is High/Low Beam ON? (high/low): ").strip().lower()
            set_icon_status(5, beam_status == 'high')  # Icon index 5 for High/Low Beam
           
            door_locked = input("Is Door Locked? (yes/no): ").strip().lower() == 'yes'
            set_icon_status(6, door_locked)  # Icon index 6 for Door Locked
           
            tcs = input("Is Traction Control System (TCS) ON? (yes/no): ").strip().lower() == 'yes'
            set_icon_status(7, tcs)  # Icon index 7 for TCS
           
            # Send the combined icon status after all inputs
            address = 0x04  # Use a unique address for the icons
            address_hex, data_hex = convert_to_hex(address, icon_status)
            combined_message = f"{address_hex} {data_hex}"
           
            # Print the combined message before sending
            print(f"Sending icon status: {combined_message}")
            client_socket.sendall(combined_message.encode())
           
        except (KeyboardInterrupt, EOFError):
            print("\nExiting icon status update.")
            break
 
def start_client():
    # Set up socket client
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect(('localhost', 8080))
    except ConnectionRefusedError:
        print("Unable to connect to the server. Make sure the server is running.")
        return
 
    while True:
        try:
            # Get car status from the user
            car_status = input("Enter car status (on/off) or 'exit' to quit: ").strip().lower()
            if car_status == 'exit':
                break
           
            address = 0x00  # Address for car status
            data = 0x01 if car_status == 'on' else 0x00  # 0x01 for ON, 0x00 for OFF
            address_hex, data_hex = convert_to_hex(address, data)
            combined_message = f"{address_hex} {data_hex}"
            print(f"Sending: {combined_message}")
            print(f"Address Code: {address_hex}, Data Code: {data_hex}")
            client_socket.sendall(combined_message.encode())
 
            # Get additional inputs when the car is ON
            if car_status == 'on':
                # Get speed input
                speed_input = input("Enter speed (0-220): ").strip()
                if speed_input.isdigit() and 0 <= int(speed_input) <= 220:
                    address = 0x01  # Address for speed
                    data = int(speed_input)  # Speed as data
                    address_hex, data_hex = convert_to_hex(address, data)
                    combined_message = f"{address_hex} {data_hex}"
                    print(f"Sending: {combined_message}")
                    print(f"Address Code: {address_hex}, Data Code: {data_hex}")
                    client_socket.sendall(combined_message.encode())
                else:
                    print("Invalid speed. Please enter a number between 0 and 220.")
                    continue  # Skip RPM and Fuel input if speed is invalid
 
                # Get RPM input
                rpm_input = input("Enter RPM (0-8000): ").strip()
                if rpm_input.isdigit() and 0 <= int(rpm_input) <= 8000:
                    address = 0x02  # Address for RPM
                    data = int(rpm_input)  # RPM as data
                    address_hex, data_hex = convert_to_hex(address, data)
                    combined_message = f"{address_hex} {data_hex}"
                    print(f"Sending: {combined_message}")
                    print(f"Address Code: {address_hex}, Data Code: {data_hex}")
                    client_socket.sendall(combined_message.encode())
                else:
                    print("Invalid RPM. Please enter a number between 0 and 8000.")
                    continue  # Skip Fuel input if RPM is invalid
 
                # Get Fuel Level input
                fuel_input = input("Enter fuel level (0-100): ").strip()
                if fuel_input.isdigit() and 0 <= int(fuel_input) <= 100:
                    address = 0x03  # Address for Fuel Level
                    data = int(fuel_input)  # Fuel level as data
                    address_hex, data_hex = convert_to_hex(address, data)
                    combined_message = f"{address_hex} {data_hex}"
                    print(f"Sending: {combined_message}")
                    print(f"Address Code: {address_hex}, Data Code: {data_hex}")
                    client_socket.sendall(combined_message.encode())
                else:
                    print("Invalid Fuel Level. Please enter a number between 0 and 100.")
           
            # Call the function to update icon status
            update_icon_status(client_socket)
           
        except (KeyboardInterrupt, EOFError):
            print("\nClient shutting down.")
            break
 
    # Close socket
    client_socket.close()
 
if __name__ == "__main__":
    start_client()
 
 