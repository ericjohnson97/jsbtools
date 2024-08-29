import struct
from typing import List, Tuple

# Constants
FG_MAX_ENGINES = 4
FG_MAX_WHEELS = 3
FG_MAX_TANKS = 4

class FGNetFDM:
    def __init__(self, byte_data: bytes):
        self.parse_byte_array(byte_data)

    def parse_byte_array(self, byte_data: bytes):
        offset = 0

        def read(fmt: str):
            nonlocal offset
            size = struct.calcsize(fmt)
            if offset + size > len(byte_data):
                raise ValueError("Not enough data to unpack")
            result = struct.unpack_from(fmt, byte_data, offset)
            offset += size
            return result if len(result) > 1 else result[0]

        # JSB uses big-endian format
        endian_prefix = '>'

        self.version = read(endian_prefix + 'I')
        self.padding = read(endian_prefix + 'I')
        self.longitude = read(endian_prefix + 'd')
        self.latitude = read(endian_prefix + 'd')
        self.altitude = read(endian_prefix + 'd')
        self.agl = read(endian_prefix + 'f')
        self.phi = read(endian_prefix + 'f')
        self.theta = read(endian_prefix + 'f')
        self.psi = read(endian_prefix + 'f')
        self.alpha = read(endian_prefix + 'f')
        self.beta = read(endian_prefix + 'f')

        self.phidot = read(endian_prefix + 'f')
        self.thetadot = read(endian_prefix + 'f')
        self.psidot = read(endian_prefix + 'f')
        self.vcas = read(endian_prefix + 'f')
        self.climb_rate = read(endian_prefix + 'f')
        self.v_north = read(endian_prefix + 'f')
        self.v_east = read(endian_prefix + 'f')
        self.v_down = read(endian_prefix + 'f')
        self.v_body_u = read(endian_prefix + 'f')
        self.v_body_v = read(endian_prefix + 'f')
        self.v_body_w = read(endian_prefix + 'f')

        self.A_X_pilot = read(endian_prefix + 'f')
        self.A_Y_pilot = read(endian_prefix + 'f')
        self.A_Z_pilot = read(endian_prefix + 'f')

        self.stall_warning = read(endian_prefix + 'f')
        self.slip_deg = read(endian_prefix + 'f')

        self.num_engines = read(endian_prefix + 'I')
        
        self.eng_state = [read(endian_prefix + 'I') for _ in range(self.num_engines)]
        self.rpm = [read(endian_prefix + 'f') for _ in range(self.num_engines)]
        self.fuel_flow = [read(endian_prefix + 'f') for _ in range(self.num_engines)]
        self.fuel_px = [read(endian_prefix + 'f') for _ in range(self.num_engines)]
        self.egt = [read(endian_prefix + 'f') for _ in range(self.num_engines)]
        self.cht = [read(endian_prefix + 'f') for _ in range(self.num_engines)]
        self.mp_osi = [read(endian_prefix + 'f') for _ in range(self.num_engines)]
        self.tit = [read(endian_prefix + 'f') for _ in range(self.num_engines)]
        self.oil_temp = [read(endian_prefix + 'f') for _ in range(self.num_engines)]
        self.oil_px = [read(endian_prefix + 'f') for _ in range(self.num_engines)]

        # Consumables
        self.num_tanks = read(endian_prefix + 'I')
        if self.num_tanks > FG_MAX_TANKS:
            raise ValueError("num_tanks exceeds maximum allowed tanks")
        
        self.fuel_quantity = [read(endian_prefix + 'f') for _ in range(self.num_tanks)]
        self.tank_selected = [read(endian_prefix + 'I') for _ in range(self.num_tanks)]
        self.capacity_m3 = [read(endian_prefix + 'd') for _ in range(self.num_tanks)]
        self.unusable_m3 = [read(endian_prefix + 'd') for _ in range(self.num_tanks)]
        self.density_kgpm3 = [read(endian_prefix + 'd') for _ in range(self.num_tanks)]
        self.level_m3 = [read(endian_prefix + 'd') for _ in range(self.num_tanks)]

        # Gear status
        self.num_wheels = read(endian_prefix + 'I')
        if self.num_wheels > FG_MAX_WHEELS:
            raise ValueError("num_wheels exceeds maximum allowed wheels")
        
        self.wow = [read(endian_prefix + 'I') for _ in range(self.num_wheels)]
        self.gear_pos = [read(endian_prefix + 'f') for _ in range(self.num_wheels)]
        self.gear_steer = [read(endian_prefix + 'f') for _ in range(self.num_wheels)]
        self.gear_compression = [read(endian_prefix + 'f') for _ in range(self.num_wheels)]

        # Environment
        self.cur_time = read(endian_prefix + 'I')
        self.warp = read(endian_prefix + 'i')
        self.visibility = read(endian_prefix + 'f')

        # Control surface positions (normalized values)
        self.elevator = read(endian_prefix + 'f')
        self.elevator_trim_tab = read(endian_prefix + 'f')
        self.left_flap = read(endian_prefix + 'f')
        self.right_flap = read(endian_prefix + 'f')
        self.left_aileron = read(endian_prefix + 'f')
        self.right_aileron = read(endian_prefix + 'f')
        self.rudder = read(endian_prefix + 'f')
        self.nose_wheel = read(endian_prefix + 'f')
        self.speedbrake = read(endian_prefix + 'f')
        self.spoilers = read(endian_prefix + 'f')

    # untested
    def to_byte_array(self) -> bytes:
        # Combine all elements into a byte array
        result = struct.pack('IIdddffffffffffffff', 
            self.version, self.padding, self.longitude, self.latitude, self.altitude,
            self.agl, self.phi, self.theta, self.psi, self.alpha, self.beta,
            self.phidot, self.thetadot, self.psidot, self.vcas, self.climb_rate,
            self.v_north, self.v_east, self.v_down, self.v_body_u, self.v_body_v, self.v_body_w,
            self.A_X_pilot, self.A_Y_pilot, self.A_Z_pilot,
            self.stall_warning, self.slip_deg,
            self.num_engines)

        # Add variable-length arrays
        result += struct.pack(f'{self.num_engines}I', *self.eng_state)
        result += struct.pack(f'{self.num_engines}f', *self.rpm)
        result += struct.pack(f'{self.num_engines}f', *self.fuel_flow)
        result += struct.pack(f'{self.num_engines}f', *self.fuel_px)
        result += struct.pack(f'{self.num_engines}f', *self.egt)
        result += struct.pack(f'{self.num_engines}f', *self.cht)
        result += struct.pack(f'{self.num_engines}f', *self.mp_osi)
        result += struct.pack(f'{self.num_engines}f', *self.tit)
        result += struct.pack(f'{self.num_engines}f', *self.oil_temp)
        result += struct.pack(f'{self.num_engines}f', *self.oil_px)

        result += struct.pack('I', self.num_tanks)
        result += struct.pack(f'{self.num_tanks}f', *self.fuel_quantity)
        result += struct.pack(f'{self.num_tanks}I', *self.tank_selected)
        result += struct.pack(f'{self.num_tanks}d', *self.capacity_m3)
        result += struct.pack(f'{self.num_tanks}d', *self.unusable_m3)
        result += struct.pack(f'{self.num_tanks}d', *self.density_kgpm3)
        result += struct.pack(f'{self.num_tanks}d', *self.level_m3)

        result += struct.pack('I', self.num_wheels)
        result += struct.pack(f'{self.num_wheels}I', *self.wow)
        result += struct.pack(f'{self.num_wheels}f', *self.gear_pos)
        result += struct.pack(f'{self.num_wheels}f', *self.gear_steer)
        result += struct.pack(f'{self.num_wheels}f', *self.gear_compression)

        result += struct.pack('If', self.cur_time, self.visibility)

        result += struct.pack('f' * 10,
            self.elevator, self.elevator_trim_tab, self.left_flap, self.right_flap, self.left_aileron,
            self.right_aileron, self.rudder, self.nose_wheel, self.speedbrake, self.spoilers)

        return result
