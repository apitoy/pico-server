# Wi-Fi configuration
SSID = ""
PASSWORD = ""

# Audio configuration
SAMPLE_RATE = 44100
MAX_VOLUME = 65535  # For 16-bit PWM

import network
import socket
import time
import machine


# Global variable for frequency
current_frequency = 2

# LED for visual feedback
#led = Pin(25, Pin.OUT)
led = machine.Pin("LED", machine.Pin.OUT)
    

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    
    # Wait for connect or fail
    max_wait = 10
    while max_wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        max_wait -= 1
        print('waiting for connection...')
        time.sleep(1)
        blinking()
    
    # Handle connection error
    if wlan.status() != 3:
        raise RuntimeError('network connection failed')
    else:
        print('connected')
        status = wlan.ifconfig()
        print('IP = ' + status[0])
    
    return status[0]  # Return IP address

def serve(ip):
    global current_frequency
    
    s = socket.socket()
    s.bind((ip, 80))
    s.listen(5)
    print('listening on', ip)
    
    while True:
        try:
            conn, addr = s.accept()
            print('Got a connection from', addr)
            request = conn.recv(1024)
            request = str(request)
            
            # Check if it's a POST request to update frequency
            if "POST /update_frequency" in request:
                freq_start = request.find("frequency=") + 10
                freq_end = request.find("HTTP", freq_start)
                new_frequency = int(request[freq_start:freq_end])
                current_frequency = new_frequency
                print(f"Updated frequency to {current_frequency} Hz")
                blinking()
            
            # Prepare the response
            response = "HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n"
            response += f"<h1>Current frequency: {current_frequency} Hz</h1>"
            response += "<form method='POST' action='/update_frequency'>"
            response += "<input type='number' name='frequency' value='" + str(current_frequency) + "'>"
            response += "<input type='submit' value='Update Frequency'>"
            response += "</form>"
            
            conn.send(response)
            conn.close()
        
        except Exception as e:
            print(f"Error: {e}")
            conn.close()
        
        print('Connection closed')
        
        
def blinking():
    led.off()  # Visual feedback
    time.sleep(1/current_frequency)
    led.on()
    time.sleep(1/current_frequency)

    
def main():
    ip = connect_wifi()
    serve(ip)
    
        

if __name__ == "__main__":
    main()

