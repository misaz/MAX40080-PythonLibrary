import smbus, crc

class MAX40080(object):

	def __init__(self, i2c_controller_no=1, i2c_address=0x21, shunt=0.010):
		self.bus =  smbus.SMBus(i2c_controller_no)
		self.i2c_addr = i2c_address
		self.shunt = shunt
		self.gain = 25

		# First value of tuple indicates measurements of Current.
		# Second value of tuple indicates measreument of Voltage.
		self.measure = (False, False)
		
		self.configure(measure_current=False, measure_voltage=False)

	def crc(self, data):
		crc_params = crc.Configuration(8, 0x07, 0x00, 0x00, False, False)
		return crc.CrcCalculator(crc_params, True).calculate_checksum(data)

	def wr16(self, reg_addr, data):
		buffer = [data & 0xFF, (data & 0xFF00) >> 8]
		buffer.append(self.crc([self.i2c_addr << 1, reg_addr] + buffer))
		self.bus.write_i2c_block_data(self.i2c_addr, reg_addr, buffer)
		
	def rd16(self, reg_addr):
		buffer = self.bus.read_i2c_block_data(self.i2c_addr, reg_addr, 3)
		if self.crc([self.i2c_addr << 1, reg_addr, (self.i2c_addr << 1) | 0x01] + buffer[0:2]) != buffer[2]:
			raise Exception("Bad CRC received.")

		return buffer[0] | (buffer[1] << 8);

	def rd32(self, reg_addr):
		buffer = self.bus.read_i2c_block_data(self.i2c_addr, reg_addr, 5)
		if self.crc([self.i2c_addr << 1, reg_addr, (self.i2c_addr << 1) | 0x01] + buffer[0:4]) != buffer[4]:
			raise Exception("Bad CRC received.")

		return buffer[0] | (buffer[1] << 8) | (buffer[2] << 16) | (buffer[3] << 24);

	def configure(self, sample_rate_khz=15, digital_filter=1, measure_current=True, measure_voltage=False):
		if measure_current == False and measure_voltage == False:
			self.mode = (False, False)
			self.wr16(0x00, 0x0060)
			return

		if measure_current == True and measure_voltage == True:
			if sample_rate_khz != 0.5:
				raise ValueError("Sample rate must be 0.5 when measurement of both current and voltage is selected.")

		sample_rates = [15, 18.75, 23.45, 30, 37.5, 47.1, 60, 93.5, 120, 150, 234.5, 375, 468.5, 750, 1000, 0.5]
		try:
			sample_rate_index = sample_rates.index(sample_rate_khz)
		except ValueError:
			valid_sample_rates = ", ".join(map(lambda it: str(it), sample_rates))
			raise ValueError("Unsupported sample rate. Supported sample rates are: " + valid_sample_rates)
		
		digital_filters = [1, 8, 16, 32, 64, 128]
		try:
			digital_filter_index = digital_filters.index(digital_filter)
		except ValueError:
			valid_digital_filters = ", ".join(map(lambda it: str(it), digital_filters))
			raise ValueError("Unsupported number of averaged samples (digital filter). Supported values are: " + valid_digital_filters)

		cfg_reg = 0x0023 | (sample_rate_index << 8) | (digital_filter_index << 12);
		self.wr16(0x00, cfg_reg)

		fifo_cfg_reg = 0x3400
		if measure_current == False and measure_voltage == True:
			fifo_cfg_reg |= 0x01
		elif measure_current == True and measure_voltage == True: 
			fifo_cfg_reg |= 0x02

		self.wr16(0x0A, fifo_cfg_reg | 0x8000)
		self.wr16(0x0A, fifo_cfg_reg)
		self.mode = (measure_current, measure_voltage)

		# first reading after reconfiguration seems to be sometimes invalid so we reads and discard them here
		if measure_current == True and measure_voltage == True:
			self.read_current_and_voltage()
		elif measure_current == True:
			self.read_current()
		elif measure_voltage == True:
			self.read_voltage()


	def read_raw_current(self):
		if not self.mode[0]:
			raise Exception("Cant read current because measuring current was disabled in last configure() call or configure() was not called yet.")
		
		attemps = 1000
		while attemps != 0:
			val = self.rd16(0x0C)
			if (val & 0x8000) == 0:
				attemps -= 1
				continue

			magnitude = val & 0xFFF
			if val & 0x1000:
				return -((magnitude ^ 0xFFF) + 1);
			else:
				return magnitude

		raise Exception("Timed out")


	def read_raw_voltage(self):
		if not self.mode[1]:
			raise Exception("Cant read voltage because measuring volatege was disabled in last configure() call or configure() was not called yet.")
			
		attemps = 1000
		while attemps != 0:
			val = self.rd16(0x0E)
			if (val & 0x8000) == 0:
				attemps -= 1
				continue
		
			return val & 0xFFF
		
		raise Exception("Timed out")

	def read_raw_current_and_voltage(self):
		if not self.mode[0]:
			raise Exception("Cant read current because measuring current was disabled by last configure() call or configure() was not called yet.")
		if not self.mode[1]:
			raise Exception("Cant read voltage because measuring volatege was disabled by last configure() call or configure() was not called yet.")
		
		attemps = 1000
		while attemps != 0:
			val = self.rd32(0x10)
			if (val & 0x80000000) == 0:
				attemps -= 1
				continue

			current = (val & 0xFFF)
			if val & 0x1000:
				current = -((current ^ 0xFFF) + 1);

			voltage = (val & 0xFFF0000) >> 16

			return (current, voltage)

		raise Exception("Timed out")

	def read_current(self):
		# 4096 is there becacause division by pow of two is simplier and results 
		# to better float numbers. Technicaly there should be 4095 instead.

		return self.read_raw_current() * 1.25 / 4096 / self.gain / self.shunt

	def read_voltage(self):
		# 4096 is there becacause division by pow of two is simplier and results 
		# to better float numbers. Technicaly there should be 4095 instead.

		return self.read_raw_voltage() * 37.5 / 4096

	def read_current_and_voltage(self):
		# 4096 is there becacause division by pow of two is simplier and results 
		# to better float numbers. Technicaly there should be 4095 instead.

		(raw_current, raw_voltage) = self.read_raw_current_and_voltage()
		current = raw_current * 1.25 / 4096 / self.gain / self.shunt
		voltage = raw_voltage * 37.5 / 4096

		return (current, voltage)
