import serial
from .uservo import *
import time
import copy

class StopOptions:

	mode={
		"unlocked" : 0x10,
		"locked" : 0x11,
		"damping" : 0x12
		}
	# def __init__(self, str_mode:str):
	# 	return self.mode(str_mode)
	@classmethod
	def str2int(cls, str_mode:str)-> int:
		return cls.mode[str_mode]



class Monitor_data:
	id :int
	current_position :float
	power:int
	voltage :int
	current:int
	temperature :float
	status:int
	def __init__(self, id:int, current_position:float, power:int, voltage:int, current:int, temperature:float, status:int):
		self.id = id
		self.current_position = current_position
		self.power = power
		self.voltage = voltage
		self.current = current
		self.temperature = temperature
		self.status = status
	def __str__(self):
		return f"Motor {self.id}:\n\tCurrent Position: {self.current_position}\n\tPower: {self.power}\n\tVoltage: {self.voltage}\n\tCurrent: {self.current}\n\tTemperature: {self.temperature}\n\tStatus: {self.status}"
		


class SyncPositionControlOptions:
	id:int
	target_position:float
	motion_time:int
	power:int
	t_acc:int
	t_dec:int
	def __init__(self, id:int, target_position:float, motion_time:int, power:int, t_acc:int, t_dec:int):
		self.id = id
		self.target_position = target_position
		self.motion_time = motion_time
		self.power = power

		self.t_acc = t_acc
		self.t_dec = t_dec

	def __str__(self):
		return f"Motor {self.id}:\n\tTarget Position: {self.target_position}\n\tMotion Time: {self.motion_time}\n\tPower: {self.power}\n\tt_acc: {self.t_acc}\n\tt_dec: {self.t_dec}"





class PortHandler(UartServoManager):

	@property
	def is_open(self):
		if self.uart == None:
			return False
		return self.uart.is_open
	
	def __init__(self, port_name:str, baudrate:int):
		# self.min_position_limit = [-1024*360.0 for i in range(255)]
		# self.max_position_limit = [1024*360.0 for i in range(255)]
		self.port_name = port_name
		self.baudrate = baudrate
		self.uart = None
		self.write={
			# "Min_Position_Limit":self.SetMinPositionLimit,
			# "Max_Position_Limit":self.SetMaxPositionLimit,
			"Stop_On_Control_Mode":self.StopOnControlMode,
		}

		self.read={
			"Present_Position":self.ReadCurrentPosition_EX,
			# "Min_Position_Limit":self.ReadMinPositionLimit,
			# "Max_Position_Limit":self.ReadMaxPositionLimit,

		}
		self.sync_read={
			"Monitor":self.SyncServoSonitor,
		}
		self.sync_write={
			"Goal_Position":self.SyncPositionControl_EX
		}


	def openPort(self):
		self.uart = serial.Serial(port=self.port_name, baudrate=self.baudrate,parity=serial.PARITY_NONE, stopbits=1,bytesize=8,timeout=0)
		super().__init__(self.uart)

	def closePort(self):
		self.uart.close()
		self.uart = None
	
	def clearPort(self):
		self.uart.flush()

	# def ReadMinPositionLimit(self,id:int):
	# 	return self.min_position_limit[id]
	
	# def ReadMaxPositionLimit(self,id:int):
	# 	return self.max_position_limit[id]


	# def SetMinPositionLimit(self,id:int,limit:float):
	# 	self.min_position_limit[id] = limit
	
	# def SetMaxPositionLimit(self,id:int,limit:float):
	# 	self.max_position_limit[id] = limit

	def PositionControl(self,id:int,target_position:float,motion_time:int,power:int=0):
		if self.is_open == False:
			raise Exception("Please connect the device first")
		target_position = target_position * 360.0
		if target_position < self.min_position_limit[id]:
			target_position = self.min_position_limit[id]
		elif target_position > self.max_position_limit[id]:
			target_position = self.max_position_limit[id]
		return self.set_servo_angle(servo_id = id,is_mturn = False,angle=target_position,interval = motion_time,power = power)
	
	def PositionControl_TimeBased(self,data:SyncPositionControlOptions):
		if self.is_open == False:
			raise Exception("Please connect the device first")
		return self.set_servo_angle(servo_id = data.id,is_mturn = False,angle=data.target_position,interval = data.motion_time,power = data.power,t_acc=data.t_acc,t_dec=data.t_dec)

	def PositionControl_SpeedBased(self,id:int,target_position:float,motion_speed:int,accel_time:int,decel_time:int,power:int=0):
		return self.set_servo_angle(servo_id = id,is_mturn = False,angle=target_position,voltage = motion_speed,power = power,t_acc=accel_time,t_dec=decel_time)

	def PositionControl_EX(self,id:int,target_position:float,motion_time:int,power:int=0):
		return self.set_servo_angle(servo_id = id,is_mturn = False,angle=target_position,interval = motion_time,power = power)
	
	def PositionControl_TimeBased_EX(self,id:int,target_position:float,motion_time:int,accel_time:int,decel_time:int,power:int=0):		
		return self.set_servo_angle(servo_id = id,is_mturn = False,angle=target_position,interval = motion_time,power = power,t_acc=accel_time,t_dec=decel_time)

	def PositionControl_SpeedBased_EX(self,id:int,target_position:float,motion_speed:int,accel_time:int,decel_time:int,power:int=0):
		return self.set_servo_angle(servo_id = id,is_mturn = False,angle=target_position,voltage = motion_speed,power = power,t_acc=accel_time,t_dec=decel_time)

	def ReadCurrentPosition(self,id:int):
		return self.query_servo_angle(servo_id=id)
	
	def ReadCurrentPosition_EX(self,id:int):
		return self.query_servo_mturn_angle(servo_id=id)

	def ResetLoop(self,id:int):
		return self.reset_multi_turn_angle(servo_id=id)

	def DampingControl(self,id:int,power:int):
		return self.set_damping(servo_id=id,power=power)
		
	def StopOnControlMode(self,id:int,mode:str,power:int):
		return self.stop_on_control_mode(servo_id=id,method=StopOptions.str2int(mode),power=int(power))



	############
	def SyncServoSonitor(self, motors:dict[str,id])-> dict[str, Monitor_data]:
		if self.is_open == False:
			raise Exception("Please connect the device first")
		ids = [motors[id] for id in motors]
		self.send_sync_servo_monitor(servo_ids=ids)

		monitor_datas:dict[str, Monitor_data] = {}
		for motor in motors:
			id = motors[motor]
			data = Monitor_data(id,
								self.servos[id].angle_monitor, 
								self.servos[id].power, 
								self.servos[id].voltage, 
								self.servos[id].current, 
								self.servos[id].temp, 
								self.servos[id].status)
			monitor_datas[motor] = data
		time.sleep(0.01)
		return monitor_datas


	def SyncPositionControl_EX(self,motors:dict[str,SyncPositionControlOptions])->None:
		ids = [motors[id].id for id in motors]
		targets = [motors[id].target_position for id in motors]
		motion_times = [motors[id].motion_time for id in motors]
		powers = [motors[id].power for id in motors]
		t_accs = [motors[id].t_acc for id in motors]
		t_decs = [motors[id].t_dec for id in motors]

		command_data_list = [struct.pack("<BlLHHH", ids[i], targets[i], motion_times[i], t_accs[i], t_decs[i] , powers[i])for i in ids]
		
		
		self.send_sync_multiturnanglebyinterval(self.CODE_SET_SERVO_ANGLE_MTURN_BY_INTERVAL,
													   		len(ids), 
															command_data_list)

	