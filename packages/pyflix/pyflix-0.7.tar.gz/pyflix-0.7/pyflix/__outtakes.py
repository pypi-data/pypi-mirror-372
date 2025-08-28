def ping(self) -> bool:
    self.mav.ping_send(int(time.time() * 1e6), 0, 0, 0)

def set_wifi(self, ssid: str, password: str, mode: Literal['ap', 'client']='ap') -> bool:
    if mode != 'ap':
        raise NotImplementedError('Only AP mode is supported')
    self.mav.wifi_config_ap_send(bytes(ssid, 'utf-8'), bytes(password, 'utf-8'))

def on_print(self, callback: Callable):  # TODO: Callable[[int], str] possible
    pass

def on_connected(self, callback: Callable[[], None]):
    pass

def on_disconnected(self, callback: Callable[[], None]):
    pass

def state(self) -> dict:
    # Send status command to obtain the full internal state
    # > state
    # landed: 1
    # gyroBias: 0 0 0
    # ...
    pass
    # https://chatgpt.com/c/6872a832-5430-800e-8984-3f55a623d783

def take_off(self, alt: float, speed: float=0.5):
    # send set_position_target
    raise NotImplementedError

    def _set_attitude(self, roll: float, pitch: float, yaw: float, thrust: float):
        pass

    def get_telemetry(self):
        return {'connected': True,
                'motors': [0, 0, 0, 0],
                'pitch': 0, #?
                'attitude': [0, 0, 0],
            # TODO:
        }
    

# TODO: GCS bridge (TCP)


# TODO: By default: autodiscovery
# Listen to Flix itself (if not busy) and to QGC Forwarding
# https://docs.qgroundcontrol.com/Stable_V4.3/en/qgc-user-guide/settings_view/mavlink.html


    """Flix quadcopter control library.

    Attributes:
        connected (bool): True if connected to the drone.
        mode (str): Current flight mode.
        armed (bool): True if the drone is armed.
    """

# from pymavlink.mavutil import mavlink


    def update_parameters(self):
        self.connection.param_fetch_all()


    @property
    def parameters(self) -> dict:
        return {}

def quaternion_to_euler(q: Sequence[float]) -> List[float]:
    """Convert quaternion to euler angles (roll, pitch, yaw)"""
    if len(q) != 4:
        raise ValueError('Quaternion must have 4 values')
    w, x, y, z = q
    roll = math.atan2(2 * (y * w - x * z), 1 - 2 * (y**2 + z**2))
    pitch = math.asin(2 * (x * y + w * z))
    yaw = math.atan2(2 * (x * w - y * z), 1 - 2 * (x**2 + y**2))
    return [roll, pitch, yaw]


# TODO: obtaining ESP32 images using ENCAPSULATED_DATA
# flix.get_camera_image()
# flix.on_camera_image()
# flix.get_camera_info()
# flix.set_camera_settings()


# TODO: close socket on __del__

# TODO: don't override telemetry state data, if timestamp decreases


def download_log(self) -> dict:
    return {} # TODO:

# TODO: pyflix, flixpy, flixuav, flixlink, flixconn
# https://chatgpt.com/c/687cb782-2e18-800e-afaa-4ef60876153a

# TODO: test print event

# TODO: setup.py

# TODO:
# events:
# connected.true
# armed.true
# mode.MANUAL

# TODO: on SERIAL_CONTROL print like
# Flix 0: Text

if os.environ.get('DRONEKIT'):
    import dronekit  # TODO: remove

# TODO: use tuples for properties?

# TODO: print_cli

    def __del__(self):
        # TODO:
        print('Close connection')
        self.connection.close()

def set_attitude(self, attitude: List[float], thrust: float):
    # if len(attitude) is 4 then quaternion, if 3 then euler angles
    # TODO: send 3 times (redundancy) for to guarantee delivery on unreliable connection
    # duplicate sending for reliability
    raise NotImplementedError('Automatic flight is not implemented yet')


# set motors
# https://mavlink.io/en/messages/common.html#SET_ACTUATOR_CONTROL_TARGET ❓

    @staticmethod
    def _parse_serial_control(msg: mavlink.MAVLink_serial_control_message) -> str:
        return bytes(msg.data)[:msg.count].decode('utf-8') # check
