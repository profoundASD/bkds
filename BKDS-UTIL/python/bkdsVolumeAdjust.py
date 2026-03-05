import sys
from PyQt5.QtCore import Qt, QTimer, QPoint
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QSlider
from PyQt5.QtGui import QGuiApplication
import subprocess
import re


def get_default_sink():
    result = subprocess.run(['pactl', 'info'], capture_output=True, text=True, check=True)
    for line in result.stdout.split('\n'):
        if 'Default Sink:' in line:
            return line.split(':', 1)[1].strip()
    return None


class VolumeControl(QWidget):
    def __init__(self, duration, initial_volume):
        super().__init__()

        self.initial_duration = duration
        self.remaining_time = duration
        self.half_time = duration / 2
        self.is_updating = False  # Flag to prevent recursive updates

        self.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint)
        self.setWindowTitle("Adjust Volume")

        # Initialize UI and volume
        self.init_ui()
        self.volume_slider.blockSignals(True)
        self.volume_slider.setValue(initial_volume)
        self.volume_slider.blockSignals(False)
        self.set_volume(initial_volume)

        # Timer for polling system volume
        self.volume_check_timer = QTimer(self)
        self.volume_check_timer.timeout.connect(self.update_volume_from_system)

        # Start the volume check after a delay to ensure proper initialization
        QTimer.singleShot(500, self.volume_check_timer.start)

        # Countdown timer
        self.countdown_timer = QTimer(self)
        self.countdown_timer.timeout.connect(self.update_countdown)
        self.countdown_timer.start(1000)

    def update_volume_from_system(self):
        if self.is_updating:  # Prevent recursive updates
            return

        default_sink = get_default_sink()
        if not default_sink:
            print("Default sink not found.")
            return

        # Check if system is muted
        mute_output = subprocess.run(['pactl', 'get-sink-mute', default_sink], capture_output=True, text=True)
        is_muted = 'yes' in mute_output.stdout.strip().lower()

        if is_muted:
            self.is_updating = True
            self.volume_slider.blockSignals(True)
            self.volume_slider.setValue(0)
            self.label.setText("Muted")
            self.volume_slider.blockSignals(False)
            self.is_updating = False
        else:
            volume_output = subprocess.run(['pactl', 'get-sink-volume', default_sink], capture_output=True, text=True)
            match = re.search(r'Volume:.*?(\d+)%', volume_output.stdout)
            if match:
                current_system_volume = int(match.group(1))
            else:
                current_system_volume = self.volume_slider.value()

            # Update slider only if it differs from system volume
            if current_system_volume != self.volume_slider.value():
                self.is_updating = True
                self.volume_slider.blockSignals(True)
                self.volume_slider.setValue(current_system_volume)
                self.label.setText(f"{current_system_volume}%")
                self.volume_slider.blockSignals(False)
                self.is_updating = False
                self.reset_timer()

    def set_volume(self, volume):
        if self.is_updating:  # Prevent recursive updates
            return

        self.label.setText(f"{volume}%")
        self.label.setStyleSheet("background-color: #c8c8c8; color: #303030; font: 70pt 'Ubuntu Mono Bold';"
                                 "width: 80px; height: 30px; border-radius: 15px;")
        default_sink = get_default_sink()
        if default_sink:
            subprocess.run(['pactl', 'set-sink-volume', default_sink, f"{volume}%"])
        else:
            print("Default sink not found. Cannot set volume.")

    def init_ui(self):
        screen_geometry = QGuiApplication.primaryScreen().availableGeometry()
        self.setFixedSize(500, 300)
        self.move(screen_geometry.center() - self.rect().center())

        target_y = int(screen_geometry.bottom() * 0.65)
        target_point = QPoint(self.x(), target_y)
        self.move(target_point)

        layout = QVBoxLayout()
        self.label = QLabel()
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)

        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setMinimum(0)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setTickPosition(QSlider.TicksBelow)
        self.volume_slider.setTickInterval(10)
        self.volume_slider.setSingleStep(1)

        layout.addWidget(self.volume_slider)
        self.setLayout(layout)

        self.volume_slider.valueChanged.connect(self.set_volume)

    def update_countdown(self):
        self.remaining_time -= 1
        if self.remaining_time <= 0:
            self.close()

    def reset_timer(self):
        self.remaining_time = min(self.remaining_time + self.half_time, self.initial_duration)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    duration = 8
    initial_volume = 50

    if len(sys.argv) > 1:
        try:
            duration = int(sys.argv[1])
        except ValueError:
            pass

    if len(sys.argv) > 2:
        try:
            initial_volume = int(sys.argv[2])
        except ValueError:
            pass

    control = VolumeControl(duration, initial_volume)
    control.show()
    sys.exit(app.exec_())
