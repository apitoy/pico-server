import network
import socket
import json
import time
import board
import usb_hid
import digitalio
from math import sqrt, atan2, cos, sin
import _thread
from machine import Timer


class VectorMouse:
    def __init__(self):
        # LED do sygnalizacji
        self.led = digitalio.DigitalInOut(board.LED)
        self.led.direction = digitalio.Direction.OUTPUT

        # Inicjalizacja myszy USB HID
        self.mouse_report = bytearray(4)  # [buttons, x, y, wheel]
        self.mouse = usb_hid.devices[1]  # Zwykle drugie urządzenie to mysz

        # Parametry wektora ruchu
        self.vector = {"x": 0, "y": 0, "speed": 0}
        self.current_pos = {"x": 0, "y": 0}
        self.target_pos = {"x": 0, "y": 0}

        # Parametry sterowania
        self.is_moving = False
        self.update_interval = 0.01  # 10ms
        self.acceleration = 1.0
        self.max_speed = 10

        # Timer do aktualizacji pozycji
        self.update_timer = Timer()

        # Stan przycisków
        self.buttons = 0

    def setup_wifi_ap(self):
        """Konfiguracja punktu dostępowego WiFi"""
        self.ap = network.WLAN(network.AP_IF)
        self.ap.active(True)
        self.ap.config(essid='MouseControl', password='mouse123')

        while not self.ap.active():
            time.sleep(0.1)

        print('Access Point aktywny')
        print('IP:', self.ap.ifconfig()[0])
        self.blink_led(3)  # Sygnalizacja gotowości

    def blink_led(self, times=1):
        """Mignij LED-em"""
        for _ in range(times):
            self.led.value = True
            time.sleep(0.1)
            self.led.value = False
            time.sleep(0.1)

    def set_vector(self, x, y, speed):
        """Ustaw wektor ruchu"""
        self.vector["x"] = x
        self.vector["y"] = y
        self.vector["speed"] = min(speed, self.max_speed)

    def move_to(self, x, y, speed=5):
        """Rozpocznij ruch do punktu docelowego"""
        self.target_pos["x"] = x
        self.target_pos["y"] = y

        # Oblicz wektor
        dx = x - self.current_pos["x"]
        dy = y - self.current_pos["y"]
        distance = sqrt(dx * dx + dy * dy)

        if distance > 0:
            # Normalizuj wektor i ustaw prędkość
            self.vector["x"] = dx / distance
            self.vector["y"] = dy / distance
            self.vector["speed"] = min(speed, self.max_speed)
            self.is_moving = True

    def update_position(self, timer):
        """Aktualizuj pozycję myszy na podstawie wektora"""
        if not self.is_moving:
            return

        # Oblicz nową pozycję
        dx = self.vector["x"] * self.vector["speed"]
        dy = self.vector["y"] * self.vector["speed"]

        # Aktualizuj pozycję
        self.current_pos["x"] += dx
        self.current_pos["y"] += dy

        # Sprawdź czy osiągnięto cel
        distance_to_target = sqrt(
            (self.target_pos["x"] - self.current_pos["x"]) ** 2 +
            (self.target_pos["y"] - self.current_pos["y"]) ** 2
        )

        if distance_to_target < self.vector["speed"]:
            self.is_moving = False
            dx = self.target_pos["x"] - self.current_pos["x"]
            dy = self.target_pos["y"] - self.current_pos["y"]

        # Wyślij ruch do USB HID
        self.send_mouse_movement(int(dx), int(dy))

    def send_mouse_movement(self, x, y):
        """Wyślij ruch myszy przez USB HID"""
        self.mouse_report[0] = self.buttons  # przyciski
        self.mouse_report[1] = x & 0xFF  # ruch X
        self.mouse_report[2] = y & 0xFF  # ruch Y
        self.mouse_report[3] = 0  # scroll

        try:
            self.mouse.send_report(self.mouse_report)
            self.led.value = not self.led.value  # Sygnalizacja ruchu
        except Exception as e:
            print("Błąd wysyłania ruchu:", e)

    def click(self, button=1):
        """Wykonaj kliknięcie"""
        # Ustaw bit przycisku
        self.buttons |= button
        self.send_mouse_movement(0, 0)
        time.sleep(0.1)

        # Zwolnij przycisk
        self.buttons &= ~button
        self.send_mouse_movement(0, 0)

    def start_movement_updates(self):
        """Rozpocznij aktualizacje pozycji"""
        self.update_timer.init(
            freq=int(1 / self.update_interval),
            mode=Timer.PERIODIC,
            callback=self.update_position
        )


class MouseServer:
    def __init__(self, mouse):
        self.mouse = mouse
        self.server_socket = None

    def start(self, port=80):
        """Uruchom serwer HTTP"""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('0.0.0.0', port))
        self.server_socket.listen(1)

        print(f"Serwer uruchomiony na porcie {port}")

        while True:
            try:
                conn, addr = self.server_socket.accept()
                request = conn.recv(1024).decode()

                if request:
                    self.handle_request(conn, request)

                conn.close()

            except Exception as e:
                print("Błąd serwera:", e)

    def handle_request(self, conn, request):
        """Obsługa żądań HTTP"""
        try:
            # Parsuj żądanie
            method = request.split()[0]
            path = request.split()[1]

            if method == "POST" and "/mouse/" in path:
                # Znajdź dane JSON
                content_pos = request.find('\r\n\r\n')
                if content_pos > 0:
                    data = json.loads(request[content_pos:])

                    # Obsłuż różne komendy
                    if "move" in path:
                        self.mouse.move_to(
                            data.get("x", 0),
                            data.get("y", 0),
                            data.get("speed", 5)
                        )
                    elif "click" in path:
                        self.mouse.click(data.get("button", 1))
                    elif "vector" in path:
                        self.mouse.set_vector(
                            data.get("x", 0),
                            data.get("y", 0),
                            data.get("speed", 5)
                        )

                    response = "OK"
                else:
                    response = "Bad Request"
            else:
                # Zwróć prostą stronę kontrolną
                response = self.get_control_page()

            # Wyślij odpowiedź
            conn.send('HTTP/1.1 200 OK\r\n')
            conn.send('Content-Type: text/html\r\n')
            conn.send('Connection: close\r\n\r\n')
            conn.send(response.encode())

        except Exception as e:
            print("Błąd obsługi żądania:", e)
            conn.send('HTTP/1.1 500 Internal Server Error\r\n\r\n')

    def get_control_page(self):
        """Generuj stronę kontrolną"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Mouse Control</title>
            <style>
                body { font-family: Arial; margin: 20px; }
                #mousepad { 
                    width: 400px; 
                    height: 400px; 
                    border: 2px solid #333;
                    position: relative;
                }
                .button {
                    padding: 10px;
                    margin: 5px;
                    background: #007bff;
                    color: white;
                    border: none;
                    cursor: pointer;
                }
            </style>
        </head>
        <body>
            <h1>Mouse Control</h1>
            <div id="mousepad"></div>
            <button class="button" onclick="click(1)">Left Click</button>
            <button class="button" onclick="click(2)">Right Click</button>

            <script>
                const pad = document.getElementById('mousepad');
                let isDrawing = false;
                let lastX = 0;
                let lastY = 0;

                pad.addEventListener('mousedown', startVector);
                pad.addEventListener('mousemove', updateVector);
                pad.addEventListener('mouseup', stopVector);

                function startVector(e) {
                    isDrawing = true;
                    [lastX, lastY] = [e.offsetX, e.offsetY];
                }

                function updateVector(e) {
                    if (!isDrawing) return;

                    const dx = e.offsetX - lastX;
                    const dy = e.offsetY - lastY;
                    const speed = Math.sqrt(dx*dx + dy*dy) / 10;

                    fetch('/mouse/vector', {
                        method: 'POST',
                        body: JSON.stringify({
                            x: dx,
                            y: dy,
                            speed: speed
                        })
                    });

                    [lastX, lastY] = [e.offsetX, e.offsetY];
                }

                function stopVector() {
                    isDrawing = false;
                }

                function click(button) {
                    fetch('/mouse/click', {
                        method: 'POST',
                        body: JSON.stringify({button: button})
                    });
                }
            </script>
        </body>
        </html>
        """


# Inicjalizacja i uruchomienie
mouse = VectorMouse()
mouse.setup_wifi_ap()
mouse.start_movement_updates()

# Uruchom serwer w osobnym wątku
server = MouseServer(mouse)
_thread.start_new_thread(server.start, ())

print("System gotowy!")
