
import sys  
import threading
import socket
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QDateTime
from PyQt5.QtGui import QPainter, QPen, QColor, QFont, QPixmap, QRadialGradient, QBrush
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QMessageBox
 
MAX_SPEED = 220
MAX_RPM = 8000
MAX_FUEL = 100
 
class InstrumentCluster(QWidget):
    update_values_signal = pyqtSignal(int, int, int)
 
    def __init__(self):
        super().__init__()
        self.setFixedSize(1800, 600)
        self.setWindowTitle("Modern Instrument Cluster")
        self.speed = 0
        self.rpm = 0
        self.fuel_level = 0
        self.car_position_level = 0
        self.level_positions = [170, 150, 130, 110]
        self.max_level = len(self.level_positions) - 1
        self.car_status = "OFF"
 
        self.car_label = QLabel(self)
        self.jaguar_label = QLabel(self)
        self.load_car_pixmap()
        self.load_jaguar_pixmap()
 
        self.road_y_position = 0
        self.dash_offset = 0
        self.digital_font_family = "Amasis MT Pro Black"
        self.digital_font_size = 24
 
        self.update_values_signal.connect(self.update_values)
 
        # Start socket thread to listen for server data
        threading.Thread(target=self.socket_listener, daemon=True).start()
 
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_positions)
        self.timer.start(100)
 
        # Update positions initially to ensure images are displayed
        self.update_car_position()
        self.update_jaguar_position()
       
 
    def socket_listener(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(('localhost', 8080))
        server_socket.listen(1)
        print("Server is listening on port 8080...")
        client_socket, client_address = server_socket.accept()
        print(f"Client connected: {client_address}")
 
        while True:
            data = client_socket.recv(1024).decode()
            if data:
                print(f"Received: {data}")  # Print the received data
                try:
                    address_hex, data_hex = data.split()
                    address = int(address_hex, 16)
                    data = int(data_hex, 16)
 
                    if address == 0x00:  # Car Status
                        self.car_status = "ON" if data == 0x01 else "OFF"
                        print(f"Car status set to: {self.car_status}")
                        if self.car_status == "OFF":
                            self.speed = 0
                            self.rpm = 0
                            self.update()
                       
                    elif address == 0x01:  # Speed
                        if 0 <= data <= MAX_SPEED:
                            self.speed = data
                            print(f"Speed set to: {self.speed}")
                        else:
                            print("Invalid speed received.")
 
                    elif address == 0x02:  # RPM
                        if 0 <= data <= MAX_RPM:
                            self.rpm = data
                            print(f"RPM set to: {self.rpm}")
                        else:
                            print("Invalid RPM received.")
 
                    elif address == 0x03:  # Fuel
                        if 0 <= data <= MAX_FUEL:
                            self.fuel_level = data
                            print(f"Fuel set to: {self.fuel_level}")
                        else:
                            print("Invalid Fuel received.")
 
                    self.update_values_signal.emit(self.speed, self.rpm, self.fuel_level)
                   
 
                except ValueError:
                    print("Invalid data received from client:", data)
 
 
    # Other methods (load_car_pixmap, update_car_position, paintEvent, etc.) remain unchanged        
 
    def load_car_pixmap(self):
        try:
            self.car_pixmap = QPixmap("car_image.png").scaled(1000, 250, Qt.KeepAspectRatio)
            if not self.car_pixmap.isNull():
                self.car_label.setPixmap(self.car_pixmap)
            else:
                raise Exception("Image is null")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error loading image: {e}")
            self.car_pixmap = QPixmap()
        pass
 
    def load_jaguar_pixmap(self):
        try:
            self.jaguar_pixmap = QPixmap("jaguar_image.png").scaled(250, 125, Qt.KeepAspectRatio)
            if not self.jaguar_pixmap.isNull():
                self.jaguar_label.setPixmap(self.jaguar_pixmap)
            else:
                raise Exception("Image is null")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error loading image: {e}")
            self.jaguar_pixmap = QPixmap()
        pass
 
    def update_car_position(self):
        # Always keep the car at the bottom of the cluster
        new_position_y = self.level_positions[self.car_position_level]
        self.car_label.move(740, new_position_y)
        pass
 
    def update_jaguar_position(self):
        # Position the Jaguar in the middle of the cluster
        jaguar_x = (self.width() - self.jaguar_label.width()-75) // 2
        jaguar_y = 30  # Adjust as needed for vertical positioning
        self.jaguar_label.move(jaguar_x, jaguar_y)
        pass
 
    def update_positions(self):
        if self.car_status == "ON" and self.speed > 0:
            self.road_y_position = (self.road_y_position + int(self.speed * 0.2)) % self.height()
            self.update()
        self.update_car_position()  # Ensure the car position is updated
 
 
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        self.draw_background(painter)
        self.draw_road(painter)
        self.draw_speedometer(painter, 500, 375, 220)
        self.draw_rpm_meter(painter, 1300, 375, 220)
        self.draw_digital_speed(painter)
 
        if self.car_status == "OFF":
            # Darken the cluster when the car is OFF
            painter.setBrush(QColor(0, 0, 0, 225))  # Semi-transparent black
            painter.drawRect(0, 0, self.width(), self.height())
 
    def draw_background(self, painter):
        gradient = QRadialGradient(self.width() / 2, self.height() / 2, 600)
        gradient.setColorAt(0, QColor(0, 0, 150))
        gradient.setColorAt(1, QColor(0, 0, 50))
        painter.setBrush(QBrush(gradient))
        painter.drawRect(0, 0, self.width(), self.height())
 
    def draw_road(self, painter):
        road_top_y = 150
        road_bottom_y = self.height() - 150
        road_left_x = int(self.width() / 2 - 80)
        road_right_x = int(self.width() / 2 + 80)
 
        painter.setPen(QPen(QColor(255, 255, 255), 5))
        painter.drawLine(road_left_x, road_top_y, road_left_x, road_bottom_y)
        painter.drawLine(road_right_x, road_top_y, road_right_x, road_bottom_y)
 
        dash_length = 3
        spacing = 20
        lane_x = int(self.width() / 2)
 
        for y in range(road_top_y + self.dash_offset, road_bottom_y, spacing):
            painter.drawLine(lane_x, y, lane_x, y + dash_length)
 
        if self.speed > 0:
            self.dash_offset = (self.dash_offset + 5) % spacing
 
    def draw_speedometer(self, painter, x, y, radius):
        painter.setPen(QPen(QColor(0, 150, 255), 10))
        painter.drawArc(x - radius, y - radius, 2 * radius, 2 * radius, -30 * 16, 240 * 16)
 
        painter.setPen(QPen(Qt.white, 3))
        painter.setFont(QFont("Arial", 10))
 
        for i in range(0, MAX_SPEED + 1, 10):
            angle = (i / MAX_SPEED) * 240 - 120
            painter.save()
            painter.translate(x, y)
            painter.rotate(angle)
            if i % 20 == 0:
                painter.drawLine(0, -radius + 20, 0, -radius + 40)
                painter.drawText(-15, -radius + 60, str(i))
            else:
                painter.drawLine(0, -radius + 30, 0, -radius + 40)
            painter.restore()
 
        self.draw_center_speed(painter, x, y, self.speed, "km/h")
        self.draw_dynamic_needle(painter, x, y, radius - 30, self.speed, max_value=MAX_SPEED)
 
        self.draw_small_gauge(painter, int(x - 250), int(y - 90), int(radius // 1.5))  # Small gauge
 
    def draw_small_gauge(self, painter, x, y, radius):
        painter.setPen(QPen(QColor(0, 150, 255), 8))
        painter.drawArc(int(x - radius), int(y - radius), int(2 * radius), int(2 * radius), 38 * 16, 245 * 16)  # Inclined semicircle
 
    # Draw the current date and time
        current_time = QDateTime.currentDateTime()
        date_text = current_time.toString("dddd")  # Full day of the week
        month_year_text = current_time.toString("MMMM yyyy")  # Full month and year
        time_text = current_time.toString("h:mm AP")  # 12-hour format with AM/PM
 
        # Example temperature (you can replace this with actual temperature data)
        temperature = 21  # In Celsius
        temperature_text = f"{temperature} °C"
   
        painter.setPen(Qt.white)
        painter.setFont(QFont("Amasis MT Pro Black", 13, QFont.Bold))  # Make the font bold
 
    # Calculate text widths
        date_width = painter.fontMetrics().width(date_text)
        month_year_width = painter.fontMetrics().width(month_year_text)
        time_width = painter.fontMetrics().width(time_text)
        temperature_width = painter.fontMetrics().width(temperature_text)
 
    # Draw date and time centered in the gauge
        line_spacing=5
        painter.drawText(int(x - date_width / 2-25), int(y + radius / 4-100), date_text)  # Day on the first line
        painter.drawText(int(x - month_year_width / 2-25), int(y + radius / 4 - 80+line_spacing), month_year_text)# Month and year on the second line
        painter.drawText(int(x - time_width / 2-35), int(y + radius / 4 - 60+(line_spacing+20)), time_text)  # Time on the third line
 
        painter.setFont(QFont("Amasis MT Pro Black", 23, QFont.Bold))  # Larger font for temperature
        temperature_width = painter.fontMetrics().width(temperature_text)
        painter.drawText(int(x - temperature_width / 2-50), int(y + radius / 4 + 1.5 * (line_spacing + 20)), temperature_text)  # Temperature on the fourth line
 
    def draw_rpm_meter(self, painter, x, y, radius):
        painter.setPen(QPen(QColor(0, 150, 255), 10))
        painter.drawArc(x - radius, y - radius, 2 * radius, 2 * radius, -30 * 16, 240 * 16)
 
        painter.setPen(QPen(Qt.white, 3))
        painter.setFont(QFont("Arial", 12))
 
        for i in range(0, MAX_RPM + 1, 500):
            angle = (i / MAX_RPM) * 240 - 120
            painter.save()
            painter.translate(x, y)
            painter.rotate(angle)
            if i % 1000 == 0:
                painter.drawLine(0, -radius + 20, 0, -radius + 40)
                painter.drawText(-15, -radius + 70, f"{i // 1000}k")
            else:
                painter.drawLine(0, -radius + 30, 0, -radius + 40)
            painter.restore()
 
        self.draw_center_speed(painter, x, y, self.rpm, "RPM")
        self.draw_dynamic_needle(painter, x, y, radius - 30, self.rpm, max_value=MAX_RPM)
 
        self.draw_rpm_small_gauge(painter, int(x + 250), int(y - 90), int(radius // 1.5))  # Small gauge for RPM
 
    def draw_rpm_small_gauge(self, painter, x, y, radius):
        painter.setPen(QPen(QColor(255, 0, 0), 8))
        painter.drawArc(int(x - radius), int(y - radius), int(2 * radius), int(2 * radius), 258 * 16, 245 * 16)  # Inclined semicircle
 
        painter.setPen(QPen(Qt.white, 3))
        painter.setFont(QFont("Amasis MT Pro Black", 12))
        # Draw the fuel indicator
        fuel_angle = (self.fuel_level / 100) * 245  # Map fuel level to angle
        painter.setPen(QPen(QColor(0, 150, 255), 8))  # Color for fuel indicator (gold)
        painter.drawArc(int(x - radius), int(y - radius), int(2 * radius), int(2 * radius), 258 * 16, int(fuel_angle * 16))
 
        painter.setPen(Qt.white)
        painter.setFont(QFont(self.digital_font_family, 8, QFont.Bold | QFont.StyleItalic))
        painter.setPen(QPen(QColor(255, 255, 255), 2))
        painter.drawArc(x - 100, y - 87, 180, 180, 258 * 16, 245 * 16)
 
        # Adjusted tick lengths
        tick_length_major = radius * 0.15  # Major ticks (for every 50 units)
        tick_length_minor = radius * 0.1    # Minor ticks (for every 10 units)
 
        # Draw major ticks and labels
        for i in range(0, MAX_FUEL + 1, 50):
            angle = (i / MAX_FUEL) * 210 - 35
            painter.save()
            painter.translate(x, y)
            painter.rotate(angle)
            # Ensure the tick length is converted to int
            painter.drawLine(0, int(-radius + 20), 0, int(-radius + 20 + tick_length_major))
            if i % 100 == 0:
                painter.drawText(-15, int(-radius + 70), f"{i // 100}")
            painter.restore()
 
        # Draw minor ticks
        for i in range(0, MAX_FUEL + 1, 10):
            if i % 50 != 0:  # Skip the major ticks
                angle = (i / MAX_FUEL) * 210 - 35
                painter.save()
                painter.translate(x, y)
                painter.rotate(angle)
                # Ensure the tick length is converted to int
                painter.drawLine(0, int(-radius + 20), 0, int(-radius + 20 + tick_length_minor))
                painter.restore()
 
        # Draw the needle
        needle_angle = (self.fuel_level / MAX_FUEL) * 210 - 35  # Adjusted to match ticks
        painter.save()
        painter.translate(x, y)
        painter.rotate(needle_angle)
 
        # Set needle color based on fuel level
        if self.fuel_level < 20:
            painter.setPen(QPen(QColor(255, 0, 0), 2))  # Red for low fuel
        else:
            painter.setPen(QPen(QColor(255, 255, 255), 2))  # White for normal fuel
 
        painter.drawLine(0, 0, 0, -radius + 30)  # Needle length
        painter.restore()
       
        # Optionally, you could draw a label for the fuel level
        painter.setPen(QPen(Qt.white, 150))
        painter.setFont(QFont(self.digital_font_family, 12, QFont.Bold | QFont.StyleItalic))
        painter.drawText(int(x - 20), int(y + 10), f"{self.fuel_level}%")  # Display fuel level percentage
 
    def draw_dynamic_needle(self, painter, x, y, radius, value, max_value):
        needle_angle = (value / max_value) * 240 - 120
        color = QColor(255, 255, 255) if value < max_value * 0.6 else QColor(255, 100, 100)
 
        painter.setPen(QPen(Qt.black, 2))
        painter.save()
        painter.translate(x, y)
        painter.rotate(needle_angle)
        painter.drawLine(0, 0, 0, -radius)  # Draw the needle line for the border
        painter.restore()
 
        painter.setPen(QPen(color, 3))
        painter.save()
        painter.translate(x, y)
        painter.rotate(needle_angle)
        painter.drawLine(0, 0, 0, -radius + 15)  # Offset needle to ensure it doesn't overlap with the center arc
        painter.restore()
 
    def draw_center_speed(self, painter, x, y, value, unit):
        painter.setPen(Qt.white)
        painter.setFont(QFont(self.digital_font_family, 40, QFont.Bold | QFont.StyleItalic))
        painter.setPen(QPen(QColor(255, 255, 255), 2))
        painter.drawArc(x - 120, y - 120, 240, 240, -30 * 16, 240 * 16)
 
        speed_text = str(value)
        speed_width = painter.fontMetrics().width(speed_text)
        painter.drawText(int(x - speed_width / 2), int(y + 20), speed_text)
 
        painter.setPen(QColor(255, 255, 255))
        painter.setFont(QFont(self.digital_font_family, 12, QFont.Bold | QFont.StyleItalic))
        unit_width = painter.fontMetrics().width(unit)
        painter.drawText(int(x - unit_width / 2), int(y + 50), unit)
 
    def draw_digital_speed(self, painter):
        digital_speed_position_y = self.height() - 60
        painter.setPen(Qt.white)
        painter.setFont(QFont(self.digital_font_family, 50, QFont.Bold | QFont.StyleItalic))
        speed_text = str(self.speed)
        speed_width = painter.fontMetrics().width(speed_text)
        painter.drawText(int((self.width() - speed_width) / 2), int(digital_speed_position_y), speed_text)
 
        painter.setPen(QColor(255, 255, 255))
        painter.setFont(QFont(self.digital_font_family, 10, QFont.Bold | QFont.StyleItalic))
        kmph_text = "kmph"
        kmph_width = painter.fontMetrics().width(kmph_text)
        painter.drawText(int((self.width() - kmph_width) / 2), int(digital_speed_position_y + 30), kmph_text)
 
    def update_values(self, new_speed, new_rpm, fuel_level):
        self.speed = new_speed
        self.rpm = new_rpm
        self.fuel_level = fuel_level
        self.update()
 
    def get_initial_input(self):
        while True:
            try:
                if self.car_status == "OFF":
                    car_status = input("Enter car status (ON/OFF): ").strip().upper()
                    if car_status in ["ON", "OFF"]:
                        self.car_status = car_status
                        if self.car_status == "ON":
                            print("Car status set to ON. Enter speed and RPM values:")
                    else:
                        print("Please enter 'ON' or 'OFF'.")
                    continue
 
                new_speed = int(input("Enter new speed (0-220): "))
                new_rpm = int(input("Enter new RPM (0-8000): "))
 
                if 0 <= new_speed <= MAX_SPEED and 0 <= new_rpm <= MAX_RPM:
                    self.update_values_signal.emit(new_speed, new_rpm)
                else:
                    print(f"Please enter values within the limits: Speed (0-{MAX_SPEED}), RPM (0-{MAX_RPM})")
            except ValueError:
                print("Invalid input. Please enter integer values.")
 
def main():
    app = QApplication(sys.argv)
    cluster = InstrumentCluster()
    cluster.show()
    sys.exit(app.exec_())
 
if __name__ == "__main__":
    main()
 