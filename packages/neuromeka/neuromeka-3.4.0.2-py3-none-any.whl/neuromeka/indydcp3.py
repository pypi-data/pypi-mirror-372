import sys
if sys.version_info >= (3, 9):
    from neuromeka.proto import *
else:
    from neuromeka.proto_step import *

from neuromeka.common import *
from neuromeka.enums import *

import time
from typing import Optional, List

import grpc
from google.protobuf import json_format
from google.protobuf.json_format import ParseDict

CONTROL_SOCKET_PORT = [20001, 30001]
DEVICE_SOCKET_PORT = [20002, 30002]
CONFIG_SOCKET_PORT = [20003, 30003]
RTDE_SOCKET_PORT = [20004, 30004]
BOOT_SOCKET_PORT = [20010, 30010]
CRI_SOCKET_PORT = [20181, 30181]

class IndyDCP3:
    def __init__(self, robot_ip='127.0.0.1', index=0):
        if index not in [0, 1]:
            raise ValueError("Index must be 0 or 1")

        self.boot_channel = grpc.insecure_channel('{}:{}'.format(robot_ip, BOOT_SOCKET_PORT[index]))
        self.control_channel = grpc.insecure_channel('{}:{}'.format(robot_ip, CONTROL_SOCKET_PORT[index]))
        self.device_channel = grpc.insecure_channel('{}:{}'.format(robot_ip, DEVICE_SOCKET_PORT[index]))
        self.config_channel = grpc.insecure_channel('{}:{}'.format(robot_ip, CONFIG_SOCKET_PORT[index]))
        self.rtde_channel = grpc.insecure_channel('{}:{}'.format(robot_ip, RTDE_SOCKET_PORT[index]))
        self.cri_channel = grpc.insecure_channel('{}:{}'.format(robot_ip, CRI_SOCKET_PORT[index]))

        self.boot = BootStub(self.boot_channel)
        self.control = ControlStub(self.control_channel)
        self.device = DeviceStub(self.device_channel)
        self.config = ConfigStub(self.config_channel)
        self.rtde = RTDataExchangeStub(self.rtde_channel)
        self.cri = CRIStub(self.cri_channel)

        self._joint_waypoint = []
        self._task_waypoint = []

    def __del__(self):
        if self.boot_channel is not None:
            self.boot_channel.close()
        if self.control_channel is not None:
            self.control_channel.close()
        if self.device_channel is not None:
            self.device_channel.close()
        if self.config_channel is not None:
            self.config_channel.close()
        if self.rtde_channel is not None:
            self.rtde_channel.close()
        if self.cri_channel is not None:
            self.cri_channel.close()

    def __to_digital_request_list__(self, digital_signal_list) -> list:
        request_list = []
        if digital_signal_list is not None:
            for signal in digital_signal_list:
                request_list.append(device_msgs.DigitalSignal(address=signal['address'], state=signal['state']))
        return request_list

    def __to_analog_request_list__(self, analog_signal_list) -> list:
        request_list = []
        if analog_signal_list is not None:
            for signal in analog_signal_list:
                if isinstance(signal, (tuple, list)) and len(signal) == 2:
                    address, voltage = signal
                    request_list.append(device_msgs.AnalogSignal(address=address, voltage=voltage))
                elif isinstance(signal, dict):
                    request_list.append(device_msgs.AnalogSignal(address=signal['address'], voltage=signal['voltage']))
                else:
                    request_list.append(signal)
        return request_list

    def __to_endtool_signal_list__(self, endtool_signal_list) -> list:
        request_list = []
        if endtool_signal_list is not None:
            for sig in endtool_signal_list:
                if isinstance(sig, device_msgs.EndtoolSignal):
                    request_list.append(sig)
                elif isinstance(sig, (tuple, list)) and len(sig) == 2:
                    port, states = sig
                    request_list.append(device_msgs.EndtoolSignal(port=str(port), states=list(states)))
                elif isinstance(sig, dict):
                    request_list.append(device_msgs.EndtoolSignal(port=sig['port'], states=list(sig['states'])))
                else:
                    request_list.append(device_msgs.EndtoolSignal(port=sig.port, states=list(sig.states)))
        return request_list

    ############################
    # IndyDCP3 API protocols
    ############################
    def get_robot_data(self):
        """
        Control Data:
            running_hours   -> uint32
            running_mins   -> uint32
            running_secs  -> uint32
            op_state  -> OpState
            sim_mode  -> bool
            q  -> float[6]
            qdot  -> float[6]
            p  -> float[6]
            pdot  -> float[6]
            ref_frame  -> float[6]
            tool_frame  -> float[6]
            response  -> Response
        """
        response = self.rtde.GetControlData(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_control_data(self):
        return self.get_robot_data()

    def get_control_state(self):
        """
        Control Data:
            q  -> float[]
            qdot  -> float[]
            qddot  -> float[]
            qdes  -> float[]
            qdotdes  -> float[]
            qddotdes  -> float[]
            p  -> float[]
            pdot  -> float[]
            pddot  -> float[]
            pdes  -> float[]
            pdotdes  -> float[]
            pddotdes  -> float[]
            tau  -> float[]
            tau_act  -> float[]
            tau_ext  -> float[]
            tau_jts  -> float[]
        """
        response = self.rtde.GetControlState(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_motion_data(self):
        """
        Motion Data:
            traj_state   -> TrajState
            traj_progress   -> int32
            is_in_motion  -> bool
            is_target_reached  -> bool
            is_pausing  -> bool
            is_stopping  -> bool
            has_motion  -> bool
            speed_ratio  -> int32
            motion_id  -> int32
            remain_distance  -> float
            motion_queue_size  -> uint32
            cur_traj_progress  -> int32
        """
        response = self.rtde.GetMotionData(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_servo_data(self):
        """
        Servo Data:
            status_codes   -> string[]
            temperatures   -> float[]
            voltages  -> float[]
            currents  -> float[]
            servo_actives  -> bool[]
            brake_actives  -> bool[]
        """
        response = self.rtde.GetServoData(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_collision_model_state(self):
        response = self.rtde.GetCollisionModelState(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_reserved_data(self):
        response = self.rtde.GetReservedData(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_violation_data(self):
        """
        Violation Data:
            violation_code   -> uint64
            j_index   -> uint32
            i_args  -> int32[]
            f_args  -> float[]
            violation_str  -> string
        """
        response = self.rtde.GetViolationData(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_violation_message_queue(self):
        """
        Violation Data:
            violation_queue   -> ViolationData[]
        """
        response = self.rtde.GetViolationMessageQueue(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def commit_violation(self, violation: dict):
        req = device_msgs.ViolationRequest()
        ParseDict(violation, req)
        response = self.device.CommitViolation(req)
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_rt_task_times(self):
        response = self.device.GetRTTaskTimes(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_program_data(self):
        """
        Program Data:
            program_state   -> ProgramState
            cmd_id   -> int32
            sub_cmd_id  -> int32
            running_hours  -> int32
            running_mins  -> int32
            running_secs  -> int32
            program_name  -> string
            program_alarm  -> string
            program_annotation  -> string
            speed_ratio -> int32
        """
        response = self.rtde.GetProgramData(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_stop_state(self):
        """
        Program Data:
            category   -> StopCategory
        """
        response = self.rtde.GetStopState(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_boot_status(self):
        response = self.boot.GetBootStatus(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    ############################
    # IO board and Endtool port interfaces
    ############################
    def get_di(self):
        """
        address = uint32
        state = DigitalState
        """
        response = self.device.GetDI(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_do(self):
        """
        signals = index
        address = uint32
        state = DigitalState
        """
        response = self.device.GetDO(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def set_do(self, do_signal_list: list):
        """
        do_list = [(int_addr1, True/False), (int_addr1, True/False), ...]
        """
        # Normalize inputs: [(addr, state)] or [{'address':..,'state':..}] -> DigitalSignal
        norm_list = []
        for item in (do_signal_list or []):
            if isinstance(item, (tuple, list)) and len(item) == 2:
                addr, state = item
                norm_list.append({'address': addr, 'state': state})
            else:
                norm_list.append(item)
        response = self.device.SetDO(device_msgs.DigitalList(
            signals=self.__to_digital_request_list__(norm_list),
        ))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_ai(self) -> list:
        """
        address = uint32
        voltage = int32
        """
        response = self.device.GetAI(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_ao(self) -> list:
        """
        address = uint32
        voltage = int32
        """
        response = self.device.GetAO(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def set_ao(self, ao_signal_list: list):
        response = self.device.SetAO(device_msgs.AnalogList(
            signals=self.__to_analog_request_list__(ao_signal_list),
        ))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_endtool_di(self) -> list:
        """
        state = EndtoolState
        port = char value [A,B,C]
        """
        response = self.device.GetEndDI(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_endtool_do(self) -> list:
        """
        state = EndtoolState
        port = char value [A,B,C]
        """
        response = self.device.GetEndDO(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def set_endtool_do(self, end_do_signal_list: list):
        response = self.device.SetEndDO(device_msgs.EndtoolSignalList(
            signals=self.__to_endtool_signal_list__(end_do_signal_list),
        ))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_endtool_ai(self) -> list:
        """
        address = uint32
        voltage = int32
        """
        response = self.device.GetEndAI(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_endtool_ao(self) -> list:
        """
        address = uint32
        voltage = int32
        """
        response = self.device.GetEndAO(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def set_endtool_ao(self, end_ao_signal_list: list):
        response = self.device.SetEndAO(device_msgs.AnalogList(
            signals=self.__to_analog_request_list__(end_ao_signal_list),
        ))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_endtool_rs485_rx(self) -> dict:
        response = self.device.GetEndRS485Rx(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_endtool_rs485_tx(self) -> dict:
        response = self.device.GetEndRS485Tx(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def set_endtool_rs485_rx(self, word1: int, word2: int):
        response = self.device.SetEndRS485Rx(common_msgs.EndtoolRS485Rx(
            word1=word1, word2=word2
        ))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def set_endtool_led_dim(self, led_dim):
        response = self.device.SetEndLedDim(device_msgs.EndLedDim(led_dim=led_dim))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)
    
    def execute_tool(self, name: str):
        response = self.device.ExecuteTool(common_msgs.Name(name=name))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_el5001(self):
        # Not defined in proto_ori Device; 
        return {"error": "Unsupported RPC on Device: GetEL5001 (not in proto_ori)"}

    def get_el5101(self):
        # Not defined in proto_ori Device;
        return {"error": "Unsupported RPC on Device: GetEL5101 (not in proto_ori)"}

    def get_brake_control_style(self):
        response = self.device.GetBrakeControlStyle(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_device_info(self):
        """
        Device Info:
            num_joints   -> uint32
            robot_serial   -> string
            io_board_fw_ver  -> string
            core_board_fw_vers  -> string[6]
            endtool_board_fw_ver  -> string
            endtool_port_type  -> EndToolPortType
            teleop_loaded -> bool
            calibrated -> bool
        """
        response = self.device.GetDeviceInfo(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_conveyor(self):
        response = self.device.GetConveyor(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def set_conveyor_name(self, name: str):
        response = self.device.SetConveyorName(common_msgs.Name(name=name))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def set_conveyor_by_name(self, name: str):
        response = self.device.SetConveyorByName(common_msgs.Name(name=name))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def set_conveyor_encoder(self, encoder_type, channel1: int, channel2: int, sample_num: int,
                           mm_per_tick: float, vel_const_mmps: float, reversed: bool):
        response = self.device.SetConveyorEncoder(
            device_msgs.Encoder(type=encoder_type,
                                channel1=channel1, channel2=channel2, sample_num=sample_num,
                                mm_per_tick=mm_per_tick, vel_const_mmps=vel_const_mmps,
                                reversed=reversed)
        )
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def set_conveyor_trigger(self, trigger_type, channel: int, detect_rise: bool):
        response = self.device.SetConveyorTrigger(
            device_msgs.Trigger(type=trigger_type, channel=channel, detect_rise=detect_rise)
        )
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def set_conveyor_offset(self, offset_mm):
        response = self.device.SetConveyorOffset(common_msgs.Float(value=offset_mm))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def set_conveyor_locked_joint(self, index: int):
        response = self.device.SetConveyorLockedJoint(common_msgs.Int(value=index))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def set_conveyor_tool_link(self, index: int):
        response = self.device.SetConveyorToolLink(common_msgs.Int(value=index))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def set_conveyor_starting_pose(self, jpos, tpos):
        response = self.device.SetConveyorStartingPose(
            common_msgs.PosePair(q=jpos, p=tpos)
        )
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def set_conveyor_terminal_pose(self, jpos, tpos):
        response = self.device.SetConveyorTerminalPose(
            common_msgs.PosePair(q=jpos, p=tpos)
        )
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_conveyor_state(self):
        response = self.device.GetConveyorState(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def set_sander_command(self, sander_type, ip: str, speed: float, state: bool):
        response = self.device.SetSanderCommand(
            device_msgs.SanderCommand(type=sander_type, ip=ip, speed=speed, state=state))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_sander_command(self):
        """
        SanderCommand:
            type   -> SanderType
            ip   -> string
            speed  -> float
            state  -> bool
        """
        response = self.device.GetSanderCommand(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def add_photoneo_calib_point(self, vision_name, px, py, pz):
        response = self.device.AddPhotoneoCalibPoint(
            device_msgs.AddPhotoneoCalibPointReq(vision_name=vision_name, px=px, py=py, pz=pz))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_photoneo_detection(self, vision_server, object, frame_type):
        response = self.device.GetPhotoneoDetection(
            device_msgs.VisionRequest(vision_server=vision_server, object=object, frame_type=frame_type))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_photoneo_retrieval(self, vision_server, object, frame_type):
        response = self.device.GetPhotoneoRetrieval(
            device_msgs.VisionRequest(vision_server=vision_server, object=object, frame_type=frame_type))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_ft_sensor_data(self):
        """
        FT Sensor Data:
        """
        response = self.device.GetFTSensorData(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_load_factors(self):
        """
        Device Info:
            num_joints   -> uint32
            robot_serial   -> string
            io_board_fw_ver  -> string
            core_board_fw_vers  -> string[6]
            endtool_board_fw_ver  -> string
            endtool_port_type  -> EndToolPortType
            response  -> {code: int64, msg: string}
        """
        response = self.device.GetLoadFactors(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def set_auto_mode(self, on: bool):
        response = self.device.SetAutoMode(device_msgs.SetAutoModeReq(on=on))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def check_auto_mode(self):
        response = self.device.CheckAutoMode(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def check_reduced_mode(self):
        response = self.device.CheckReducedMode(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_safety_function_state(self):
        response = self.device.GetSafetyFunctionState(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def request_safety_function(self, id, state):
        response = self.device.RequestSafetyFunction(
            device_msgs.SafetyFunctionState(id = id, state = state))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_safety_control_data(self):
        response = self.device.GetSafetyControlData(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_gripper_data(self) -> list:
        response = self.device.GetGripperData(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def set_gripper_command(self, command, gripper_type, pvt_data):
        response = self.device.SetGripperCommand(device_msgs.GripperCommand(gripper_command=command,
                                                                            gripper_type=gripper_type,
                                                                            gripper_pvt_data=pvt_data))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def set_brakes(self, brake_state_list: list):
        """
        brake_state_list -> bool[6]
        """
        motor_list = []
        motor_idx = 0
        for brake_state in brake_state_list:
            motor_list.append(device_msgs.Motor(index=motor_idx, enable=brake_state))
            motor_idx += 1

        response = self.device.SetBrakes(device_msgs.MotorList(
            motors=list(motor_list)
        ))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)
    def set_servo_all(self, enable=True):
        """
        enable -> bool
        """
        response = self.device.SetServoAll(common_msgs.State(enable=enable))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def set_servo(self, index, enable=True):
        """
        index -> int
        enable -> bool
        """
        response = self.device.SetServo(device_msgs.Servo(index=index, enable=enable))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)
        
    ############################
    # CRI Funtions (CRI)
    ############################
    def activate_cri(self, on: bool) -> dict:
        response = self.cri.ActiveCRIVel(common_msgs.State(enable=on))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def is_cri_active(self) -> dict:
        response = self.cri.IsSFDLogin(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def login_cri_server(self, email: str, token: str) -> dict:
        response = self.cri.LoginSFD(cri_msgs.SFDAccount(email=email, token=token))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def is_cri_login(self) -> dict:
        response = self.cri.IsSFDLogin(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def set_cri_target(self, pn: str, fn: str, rn: str) -> dict:
        response = self.cri.SelectSFDTarget(cri_msgs.SFDTarget(pn=pn, fn=fn, rn=rn))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def set_cri_option(self, on: bool) -> dict:
        response = self.cri.ActiveCRIVel(common_msgs.State(enable=on))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_cri_proj_list(self) -> dict:
        response = self.cri.GetSFDProjList(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_cri(self) -> dict:
        response = self.cri.GetCRI(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    ############################
    # Motion Control (Move commands)
    ############################
    def stop_motion(self, stop_category=StopCategory.CAT2) -> dict:
        """
         stop motion element:
            stop_category -> StopCategory
                CAT0  = 0
                CAT1  = 1
                CAT2  = 2
        """
        response = self.control.StopMotion(common_msgs.StopCat(category=stop_category))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def movej(self, jtarget,
              blending_type=BlendingType.NONE,
              base_type=JointBaseType.ABSOLUTE,
              blending_radius=0.0,
              vel_ratio=Limits.JogVelRatioDefault,
              acc_ratio=Limits.JogAccRatioDefault,
              post_condition=PostCondition(),
              teaching_mode=False) -> dict:
        """
         Joint Move:
            blending_type -> BlendingType.Type
                NONE
                OVERRIDE
                DUPLICATE
            base_type -> JointBaseType
                ABSOLUTE
                RELATIVE
            vel_ratio (0-100) -> int
            acc_ratio (0-100) -> int
            post_condition -> PostCondition
            teaching_mode -> bool

        """
        if teaching_mode and base_type!=JointBaseType.ABSOLUTE:
            if self.get_robot_data()['op_state'] == 6:
                print("Robot is moving. Cannot execute movej with teaching_mode=True and base_type!=ABSOLUTE.")
                return {"error": "Robot is in motion, command aborted."}
            
        jtarget = control_msgs.TargetJ(j_start=[], j_target=list(jtarget), base_type=base_type)
        blending = control_msgs.BlendingType(type=blending_type, blending_radius=blending_radius)
        post_cond = control_msgs.MotionCondition()
        if post_condition is not None:
            post_cond = control_msgs.MotionCondition(
                type_cond=post_condition.condition_type,
                type_react=post_condition.reaction_type,
                const_cond=post_condition.const_cond,
                io_cond=control_msgs.IOCondition(
                    di=self.__to_digital_request_list__(
                        [{'address': di[0], 'state': di[1]} for di in post_condition.digital_inputs]),
                    # di=self.__to_digital_request_list__(post_condition.digital_inputs),
                    # end_di=self.__to_digital_request_list__(post_condition['enddi_condition']),
                ),
            )

        response = self.control.MoveJ(control_msgs.MoveJReq(
            target=jtarget,
            blending=blending,
            vel_ratio=vel_ratio, acc_ratio=acc_ratio,
            post_condition=post_cond,
            teaching_mode=teaching_mode
        ))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def movej_time(self, jtarget,
                   blending_type=BlendingType.NONE,
                   base_type=JointBaseType.ABSOLUTE,
                   blending_radius=0.0,
                   move_time=5.0,
                   post_condition=PostCondition()) -> dict:
        """
        jtarget = [deg, deg, deg, deg, deg, deg]
        move_time = seconds
        """
        jtarget = control_msgs.TargetJ(j_start=[], j_target=list(jtarget), base_type=base_type)
        blending = control_msgs.BlendingType(type=blending_type, blending_radius=blending_radius)
        post_cond = control_msgs.MotionCondition()
        if post_condition is not None:
            post_cond = control_msgs.MotionCondition(
                type_cond=post_condition.condition_type,
                type_react=post_condition.reaction_type,
                const_cond=post_condition.const_cond,
                io_cond=control_msgs.IOCondition(
                    di=self.__to_digital_request_list__(
                        [{'address': di[0], 'state': di[1]} for di in post_condition.digital_inputs]),
                    # di=self.__to_digital_request_list__(post_condition.digital_inputs),
                    # end_di=self.__to_digital_request_list__(post_condition['enddi_condition']),
                ),
            )

        response = self.control.MoveJT(control_msgs.MoveJTReq(
            target=jtarget,
            blending=blending,
            time=move_time,
            post_condition=post_cond
        ))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)
    
    def movel(self, ttarget,
              blending_type=BlendingType.NONE,
              base_type=TaskBaseType.ABSOLUTE,
              blending_radius=0.0,
              vel_ratio=Limits.JogVelRatioDefault,
              acc_ratio=Limits.JogAccRatioDefault,
              post_condition=PostCondition(),
              teaching_mode=False,
              bypass_singular=False) -> dict:
        """
        tstart = [mm, mm, mm, deg, deg, deg]
        ttarget = [mm, mm, mm, deg, deg, deg]

            base_tye -> TaskBaseType
                ABSOLUTE
                RELATIVE
                TCP
        """
        if teaching_mode and base_type!=TaskBaseType.ABSOLUTE:
            if self.get_robot_data()['op_state'] == 6:
                print("Robot is moving. Cannot execute movel with teaching_mode=True and base_type!=ABSOLUTE.")
                return {"error": "Robot is in motion, command aborted."}
        
        ptarget = control_msgs.TargetP(t_start=[], t_target=list(ttarget), base_type=base_type)
        blending = control_msgs.BlendingType(type=blending_type, blending_radius=blending_radius)
        post_cond = control_msgs.MotionCondition()
        if post_condition is not None:
            post_cond = control_msgs.MotionCondition(
                type_cond=post_condition.condition_type,
                type_react=post_condition.reaction_type,
                const_cond=post_condition.const_cond,
                io_cond=control_msgs.IOCondition(
                    di=self.__to_digital_request_list__(
                        [{'address': di[0], 'state': di[1]} for di in post_condition.digital_inputs]),
                    # di=self.__to_digital_request_list__(post_condition.digital_inputs),
                    # end_di=self.__to_digital_request_list__(post_condition['enddi_condition']),
                ),
            )

        response = self.control.MoveL(control_msgs.MoveLReq(
            target=ptarget,
            blending=blending,
            vel_ratio=vel_ratio, acc_ratio=acc_ratio,
            post_condition=post_cond,
            teaching_mode=teaching_mode,
            bypass_singular=bypass_singular
        ))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def movel_time(self, ttarget,
                   blending_type=BlendingType.NONE,
                   base_type=TaskBaseType.ABSOLUTE,
                   blending_radius=0.0,
                   move_time=5.0,
                   post_condition=PostCondition()) -> dict:
        """
        tstart = [mm, mm, mm, deg, deg, deg]
        ttarget = [mm, mm, mm, deg, deg, deg]

            base_tye -> TaskBaseType
                ABSOLUTE
                RELATIVE
                TCP
        """
        ptarget = control_msgs.TargetP(t_start=[], t_target=list(ttarget), base_type=base_type)
        blending = control_msgs.BlendingType(type=blending_type, blending_radius=blending_radius)
        post_cond = control_msgs.MotionCondition()
        if post_condition is not None:
            post_cond = control_msgs.MotionCondition(
                type_cond=post_condition.condition_type,
                type_react=post_condition.reaction_type,
                const_cond=post_condition.const_cond,
                io_cond=control_msgs.IOCondition(
                    di=self.__to_digital_request_list__(
                        [{'address': di[0], 'state': di[1]} for di in post_condition.digital_inputs]),
                    # di=self.__to_digital_request_list__(post_condition.digital_inputs),
                    # end_di=self.__to_digital_request_list__(post_condition['enddi_condition']),
                ),
            )

        response = self.control.MoveLT(control_msgs.MoveLTReq(
            target=ptarget,
            blending=blending,
            time=move_time,
            post_condition=post_cond
        ))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def movelf(self, ttarget, enabledaxis, desforce,
               blending_type=BlendingType.NONE,
               base_type=TaskBaseType.ABSOLUTE,
               blending_radius=0.0,
               vel_ratio=Limits.JogVelRatioDefault,
               acc_ratio=Limits.JogAccRatioDefault,
               post_condition=PostCondition(),
               teaching_mode=False) -> dict:
        """
        tstart = [mm, mm, mm, deg, deg, deg]
        ttarget = [mm, mm, mm, deg, deg, deg]
         Recover from violation
        """
        ptarget = control_msgs.TargetP(t_start=[], t_target=list(ttarget), base_type=base_type)
        blending = control_msgs.BlendingType(type=blending_type, blending_radius=blending_radius)
        post_cond = control_msgs.MotionCondition()
        if post_condition is not None:
            post_cond = control_msgs.MotionCondition(
                type_cond=post_condition.condition_type,
                type_react=post_condition.reaction_type,
                const_cond=post_condition.const_cond,
                io_cond=control_msgs.IOCondition(
                    di=self.__to_digital_request_list__(
                        [{'address': di[0], 'state': di[1]} for di in post_condition.digital_inputs]),
                    # di=self.__to_digital_request_list__(post_condition.digital_inputs),
                    # end_di=self.__to_digital_request_list__(post_condition['enddi_condition']),
                ),
            )

        response = self.control.MoveLF(control_msgs.MoveLFReq(
            target=ptarget,
            blending=blending,
            vel_ratio=vel_ratio, acc_ratio=acc_ratio,
            des_force=desforce, enabled_force=enabledaxis,
            post_condition=post_cond,
            teaching_mode=teaching_mode
        ))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_transformed_ft_sensor_data(self):
        """
        ft_Fx -> float N
        ft_Fy -> float N
        ft_Fz -> float N
        ft_Tx -> float N*m
        ft_Ty -> float N*m
        ft_Tz -> float N*m
        """
        response = self.control.GetTransformedFTSensorData(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def movec(self, tpos0, tpos1,
              blending_type=BlendingType.NONE,
              base_type=TaskBaseType.ABSOLUTE,
              angle=0.0,
              setting_type=CircularSettingType.POINT_SET,
              move_type=control_msgs.CONSTANT,
              blending_radius=0.0,
              vel_ratio=Limits.JogVelRatioDefault,
              acc_ratio=Limits.JogAccRatioDefault,
              post_condition=PostCondition(),
              teaching_mode=False,
              bypass_singular=False) -> dict:
        """
        tstart = [mm, mm, mm, deg, deg, deg]
        ttarget = [mm, mm, mm, deg, deg, deg]
         Recover from violation
        """

        ctarget = control_msgs.TargetC(t_start=[], t_pos0=list(tpos0), t_pos1=list(tpos1),
                                       base_type=base_type)
        blending = control_msgs.BlendingType(type=blending_type, blending_radius=blending_radius)
        post_cond = control_msgs.MotionCondition()
        if post_condition is not None:
            post_cond = control_msgs.MotionCondition(
                type_cond=post_condition.condition_type,
                type_react=post_condition.reaction_type,
                const_cond=post_condition.const_cond,
                io_cond=control_msgs.IOCondition(
                    di=self.__to_digital_request_list__(
                        [{'address': di[0], 'state': di[1]} for di in post_condition.digital_inputs]),
                    # di=self.__to_digital_request_list__(post_condition.digital_inputs),
                    # end_di=self.__to_digital_request_list__(post_condition['enddi_condition']),
                ),
            )

        response = self.control.MoveC(control_msgs.MoveCReq(
            target=ctarget,
            blending=blending,
            angle=angle,
            setting_type=setting_type,
            move_type=move_type,
            vel_ratio=vel_ratio, acc_ratio=acc_ratio,
            post_condition=post_cond,
            teaching_mode=teaching_mode,
            bypass_singular=bypass_singular
        ))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def movec_time(self, tpos0, tpos1,
               blending_type=BlendingType.NONE,
               base_type=TaskBaseType.ABSOLUTE,
               angle=90.0,
               setting_type=CircularSettingType.POINT_SET,
               move_type=control_msgs.CONSTANT,
               blending_radius=0.0,
               move_time=5.0,
               post_condition=PostCondition()) -> dict:
        
        ctarget = control_msgs.TargetC(t_start=[], t_pos0=list(tpos0), t_pos1=list(tpos1),
                                       base_type=base_type)
        
        blending = control_msgs.BlendingType(type=blending_type, blending_radius=blending_radius)
        post_cond = control_msgs.MotionCondition()
        if post_condition is not None:
            post_cond = control_msgs.MotionCondition(
                type_cond=post_condition.condition_type,
                type_react=post_condition.reaction_type,
                const_cond=post_condition.const_cond,
                io_cond=control_msgs.IOCondition(
                    di=self.__to_digital_request_list__(
                        [{'address': di[0], 'state': di[1]} for di in post_condition.digital_inputs]),
                    # di=self.__to_digital_request_list__(post_condition.digital_inputs),
                    # end_di=self.__to_digital_request_list__(post_condition['enddi_condition']),
                ),
            )

        response = self.control.MoveCT(control_msgs.MoveCTReq(
            target=ctarget,
            blending=blending,
            angle=angle,
            setting_type=setting_type,
            move_type=move_type,
            time=move_time,
            post_condition=post_cond
        ))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def move_gcode(self, gcode_file,
                   is_smooth_mode=False,
                   smooth_radius=0.0,
                   vel_ratio=Limits.JogVelRatioDefault,
                   acc_ratio=Limits.JogAccRatioDefault) -> dict:
        
        gcode_req = control_msgs.MoveGcodeReq(gcode_file=gcode_file,
                                              is_smooth_mode=is_smooth_mode,
                                              smooth_radius=smooth_radius,
                                              vel_ratio=vel_ratio,
                                              acc_ratio=acc_ratio)
        
        response = self.control.MoveGcode(gcode_req)
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    ############################
    # Move Trajectory
    ############################

    ##
    # @brief move along joint trajectory
    # @remark all arguments are NxD arrays (N: number of points, D: DOF)
    # @param q_list joint values (unit: rads)
    # @param qdot_list joint velocities (unit: rads/s)
    # @param qddot_list joint accelerations (unit: rads/s^2)
    def move_joint_traj(self, q_list: List[List[float]], qdot_list: List[List[float]],
                        qddot_list: List[List[float]]) -> dict:
        traj_req = control_msgs.MoveJointTrajReq(q_list=list(map(lambda x: common_msgs.Vector(values=x), q_list)),
                                                 qdot_list=list(map(lambda x: common_msgs.Vector(values=x), qdot_list)),
                                                 qddot_list=list(
                                                     map(lambda x: common_msgs.Vector(values=x), qddot_list)))
        response = self.control.MoveJointTraj(traj_req)
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    ##
    # @brief move along joint trajectory
    # @remark all arguments are Nx6 arrays (N: number of points)
    # @param p_list task positions (xyzuvw), unit: m & rads
    # @param pdot_list task velocities (v, w), unit: m/s & rads/s
    # @param pddot_list task accelerations (v, w), unit: m/s^2 & rads/s^2
    def move_task_traj(self, p_list: List[List[float]], pdot_list: List[List[float]],
                       pddot_list: List[List[float]]) -> dict:
        traj_req = control_msgs.MoveTaskTrajReq(p_list=list(map(lambda x: common_msgs.Vector(values=x), p_list)),
                                                pdot_list=list(map(lambda x: common_msgs.Vector(values=x), pdot_list)),
                                                pddot_list=list(
                                                    map(lambda x: common_msgs.Vector(values=x), pddot_list)))
        response = self.control.MoveTaskTraj(traj_req)
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def move_conveyor(self,
                     post_condition=PostCondition(),
                     teaching_mode=False, bypass_singular=False,
                     acc_ratio=Limits.JogAccRatioDefault) -> dict:
        post_cond = control_msgs.MotionCondition()
        if post_condition is not None:
            post_cond = control_msgs.MotionCondition(
                type_cond=post_condition.condition_type,
                type_react=post_condition.reaction_type,
                const_cond=post_condition.const_cond,
                io_cond=control_msgs.IOCondition(
                    di=self.__to_digital_request_list__(
                        [{'address': di[0], 'state': di[1]} for di in post_condition.digital_inputs]),
                    # di=self.__to_digital_request_list__(post_condition.digital_inputs),
                    # end_di=self.__to_digital_request_list__(post_condition['enddi_condition']),
                ),
            )

        response = self.control.MoveConveyor(control_msgs.MoveConveyorReq(
            teaching_mode=teaching_mode,
            bypass_singular=bypass_singular,
            acc_ratio=acc_ratio,
            post_condition=post_cond
        ))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    ############################
    # Move Waypoints
    ############################
    
    def add_joint_waypoint(self, waypoint: list):
        self._joint_waypoint.append(waypoint)
        return True

    def get_joint_waypoint(self):
        return self._joint_waypoint
    
    def clear_joint_waypoint(self):
        self._joint_waypoint.clear()
        return True
    
    def move_joint_waypoint(self, move_time=None):
        for wp in self._joint_waypoint:
            if move_time is None:
                self.movej(jtarget = wp, blending_type=BlendingType.OVERRIDE)
            else:
                self.movej_time(jtarget = wp, blending_type=BlendingType.OVERRIDE, move_time=move_time)
            self.wait_progress(progress=100)
        return True

    def add_task_waypoint(self, waypoint: list):
        self._task_waypoint.append(waypoint)
        return True
    
    def get_task_waypoint(self):
        return self._task_waypoint
    
    def clear_task_waypoint(self):
        self._task_waypoint.clear()
        return True
    
    def move_task_waypoint(self, move_time=None):
        for wp in self._task_waypoint:
            if move_time is None:
                self.movel(ttarget = wp, blending_type=BlendingType.OVERRIDE)
            else:
                self.movel_time(ttarget = wp, blending_type=BlendingType.OVERRIDE, move_time=move_time)
            self.wait_progress(progress=100)
        return True

    ############################
    # Motion Control (Teaching mode)
    ############################
    def move_home(self):
        home_pos = self.get_home_pos()['jpos']
        self.movej(home_pos,
                   blending_type=BlendingType.NONE,
                   base_type=JointBaseType.ABSOLUTE,
                   blending_radius=0.0,
                   vel_ratio=Limits.JogVelRatioDefault,
                   acc_ratio=Limits.JogAccRatioDefault,
                   post_condition=PostCondition(),
                   teaching_mode=False)

    ############################
    # Motion Control (Teleoperation)
    ############################
    def get_teleop_device(self):
        response = self.control.GetTeleOpDevice(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_teleop_state(self):
        response = self.control.GetTeleOpState(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def connect_teleop_device(self, name: str, type: control_msgs.TeleOpDevice, ip: str, port: int):
        response = self.control.ConnectTeleOpDevice(
            control_msgs.TeleOpDevice(name=name,type=type,ip=ip,port=port)
        )
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def disconnect_teleop_device(self):
        response = self.control.DisConnectTeleOpDevice(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def read_teleop_input(self):
        response = self.control.ReadTeleOpInput(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)
    
    def start_teleop(self, method):
        """
        Start tele op
        method:
            TELE_TASK_ABSOLUTE = 0
            TELE_TASK_RELATIVE = 1
            TELE_JOINT_ABSOLUTE = 10
            TELE_JOINT_RELATIVE = 11
        """
        response = self.control.StartTeleOp(
            control_msgs.TeleOpState(mode=control_msgs.TeleMode.TELE_RAW, method=method))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def stop_teleop(self):
        """
        Stop tele op
        """
        response = self.control.StopTeleOp(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def set_play_rate(self, rate: float):
        response = self.control.SetPlayRate(control_msgs.TelePlayRate(rate=rate))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_play_rate(self):
        response = self.control.GetPlayRate(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_tele_file_list(self):
        response = self.control.GetTeleFileList(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def save_tele_motion(self, name: str):
        response = self.control.SaveTeleMotion(control_msgs.TeleFileReq(name=name))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def load_tele_motion(self, name: str):
        response = self.control.LoadTeleMotion(control_msgs.TeleFileReq(name=name))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def delete_tele_motion(self, name: str):
        response = self.control.DeleteTeleMotion(control_msgs.TeleFileReq(name=name))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def enable_tele_key(self, enable):
        response = self.control.EnableTeleKey(common_msgs.State(enable=enable))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def movetelej_abs(self, jpos, vel_ratio=1.0, acc_ratio=1.0):
        """
        Joint Teleoperation - Absolute
        jpos = [deg, deg, deg, deg, deg, deg]
        """
        response = self.control.MoveTeleJ(control_msgs.MoveTeleJReq(jpos=jpos, vel_ratio=vel_ratio, acc_ratio=acc_ratio,
                                                                    method=control_msgs.TELE_JOINT_ABSOLUTE))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def movetelej_rel(self, jpos, vel_ratio=1.0, acc_ratio=1.0):
        """
        Joint Teleoperation - Relative
        jpos = [deg, deg, deg, deg, deg, deg]
        """
        response = self.control.MoveTeleJ(control_msgs.MoveTeleJReq(jpos=jpos, vel_ratio=vel_ratio, acc_ratio=acc_ratio,
                                                                    method=control_msgs.TELE_JOINT_RELATIVE))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def movetelel_abs(self, tpos, vel_ratio=1.0, acc_ratio=1.0):
        """
        Task Teleoperation - Absolute
        jpos = [mm, mm, mm, deg, deg, deg]
        """
        response = self.control.MoveTeleL(control_msgs.MoveTeleLReq(tpos=tpos, vel_ratio=vel_ratio, acc_ratio=acc_ratio,
                                                                    method=control_msgs.TELE_TASK_ABSOLUTE))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def movetelel_rel(self, tpos, vel_ratio=1.0, acc_ratio=1.0):
        """
        Task Teleoperation - Relative
        jpos = [mm, mm, mm, deg, deg, deg]
        """
        response = self.control.MoveTeleL(control_msgs.MoveTeleLReq(tpos=tpos, vel_ratio=vel_ratio, acc_ratio=acc_ratio,
                                                                    method=control_msgs.TELE_TASK_RELATIVE))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)
    
    def move_axis(self, start_mm, target_mm, is_absolute=True, vel_ratio=5, acc_ratio=100, teaching_mode=False):
        """
        start_mm = [mm, mm, mm] -> pos
        target_mm = [mm, mm, mm] -> pos
        vel_mm : int -> vel_ratio
        acc_mm : int -> acc_ratio
        is_absolute : True if target is absolute -> base_type
        """
        # print("Linear Control ====================")
        # print("target_mm ", target_mm)
        # print("is_absolute ", is_absolute)
        # print("vel_ratio ", vel_ratio)
        # print("acc_ratio ", acc_ratio)
        # print("teaching_mode ", teaching_mode)

        # vel = Common.Limits.ExternalMotorSpeedMax * vel_ratio / 100
        vel = 250 * vel_ratio / 100 # 250 mm/s
        acc = vel * acc_ratio / 100
        response = self.control.MoveLinearAxis(control_msgs.MoveAxisReq(
            start_mm=start_mm,
            target_mm=target_mm,
            vel_percentage=vel_ratio,
            acc_percentage=acc_ratio,
            is_absolute=is_absolute,
            teaching_mode=teaching_mode
        ))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    ############################
    # Control - Additional
    ############################
    def inverse_kin(self, tpos, init_jpos) -> dict:
        """
        :param tpos:
        :param init_jpos:
        :return:
            'jpos': []
        """
        response = self.control.InverseKinematics(control_msgs.InverseKinematicsReq(
            tpos=list(tpos),
            init_jpos=list(init_jpos)
        ))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)
    def forward_kin(self, jpos) -> dict:
        """
        :param tpos:
        :param init_jpos:
        :return:
            'jpos': []
        """
        response = self.control.ForwardKinematics(control_msgs.ForwardKinematicsReq(
            jpos=list(jpos)
        ))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def set_direct_teaching(self, enable=True) -> dict:
        """
         enable = True | False
        """
        response = self.control.SetDirectTeaching(common_msgs.State(enable=enable))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def set_simulation_mode(self, enable=True) -> dict:
        """
         Set simulation mode = True | False
        """
        response = self.control.SetSimulationMode(common_msgs.State(enable=enable))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def recover(self) -> dict:
        """
         Recover from violation
        """
        response = self.control.Recover(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def set_manual_recovery(self, enable=True) -> dict:
        """
         Set manual recovery = True | False
        """
        response = self.control.SetManualRecovery(common_msgs.State(enable=enable))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def calculate_relative_pose(self, start_pos, end_pos,
                                base_type=TaskBaseType.ABSOLUTE):
        """
        Calculate relative pose
        """
        response = self.control.CalculateRelativePose(control_msgs.CalculateRelativePoseReq(
            start_pos=list(start_pos),
            end_pos=list(end_pos),
            base_type=base_type
        ))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def calculate_current_pose_rel(self, current_pos, relative_pos,
                                   base_type=TaskBaseType.ABSOLUTE):
        """
        Calculate current pos rel
        """
        response = self.control.CalculateCurrentPoseRel(control_msgs.CalculateCurrentPoseRelReq(
            current_pos=list(current_pos),
            relative_pos=list(relative_pos),
            base_type=base_type
        ))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    ############################
    # Program control
    ############################
    def play_program(self, prog_name: str = '', prog_idx: int = -1):
        """
         Play program
        """
        response = self.control.PlayProgram(control_msgs.Program(
            prog_name=prog_name,
            prog_idx=prog_idx
        ))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def pause_program(self):
        """
         Pause program
        """
        response = self.control.PauseProgram(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def resume_program(self):
        """
         Resume program
        """
        response = self.control.ResumeProgram(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def stop_program(self):
        """
         Stop program
        """
        response = self.control.StopProgram(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def set_tact_time(self, type: str, tact_time: float):
        """
        TactTime
            type -> str {not implemented yet}
            tact_time -> float {seconds}
        """
        response = self.control.SetTactTime(common_msgs.TactTime(
            type=type, tact_time=tact_time
        ))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_tact_time(self):
        """
        TactTime
            type -> str {not implemented yet}
            tact_time -> float {seconds}
        """
        response = self.control.GetTactTime(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def set_speed_ratio(self, speed_ratio: int):
        """
        Speed Ratio
            ratio -> uint32 {0 ~ 100}
        """
        response = self.config.SetSpeedRatio(config_msgs.Ratio(
            ratio=speed_ratio
        ))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    ############################
    # Compliance Mode
    ############################
    def set_compliance_mode(self, enable: bool, stiffness: 'Optional[List[int]]' = None):
        """
        Set Compliance Mode
            enable -> bool
            stiffness -> int32[] (per-axis stiffness levels)
        """
        response = self.control.SetComplianceMode(
            control_msgs.ComplianceMode(
                enable=enable,
                stiffness=stiffness or []
            )
        )
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_compliance_mode(self):
        """
        Get Compliance Mode
            enable -> bool
            stiffness -> int32[]
        """
        response = self.control.GetComplianceMode(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    ############################
    # Variables
    ############################

    # def get_modbus_variable(self):
    #     """
    #     Modbus Variables:
    #         [
    #             name -> string
    #             addr -> int32
    #             value -> int32
    #         ]
    #     """
    #     response = self.control.GetModbusVariable(common_msgs.Empty())
    #     return json_format.MessageToDict(response,
    #                                      including_default_value_fields=True,
    #                                      preserving_proto_field_name=True,
    #                                      use_integers_for_enums=True)['variables']
    
    def get_bool_variable(self):
        """
        Bool Variables:
            [
                addr -> int32
                value -> bool
            ]
        """
        response = self.control.GetBoolVariable(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_int_variable(self):
        """
        Integer Variables:
            [
                addr -> int32
                value -> int32
            ]
        """
        response = self.control.GetIntVariable(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_float_variable(self):
        """
        Float Variables:
            [
                addr -> int32
                value -> float
            ]
        """
        response = self.control.GetFloatVariable(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_jpos_variable(self):
        """
        JPos Variables:
            [
                addr -> int32
                jpos -> float[]
            ]
        """
        response = self.control.GetJPosVariable(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)['variables']

    def get_tpos_variable(self):
        """
        TPos Variables:
            [
                addr -> int32
                tpos -> float[]
            ]
        """
        response = self.control.GetTPosVariable(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    # def set_modbus_variable(self, modbus_variables: list):
    #     """
    #     Modbus Variables:
    #         [
    #             name -> string
    #             addr -> int32
    #             value -> int32
    #         ]
    #     """
    #     variable_list = []
    #     for modbus_var in modbus_variables:
    #         variable_list.append(control_msgs.ModbusVariable(name=modbus_var['name'], addr=modbus_var['addr'],
    #                                                          value=modbus_var['value'],
    #                                                          signal_type=modbus_var['signal_type']))
    #     response = self.control.SetModbusVariable(
    #         control_msgs.ModbusVars(variables=variable_list)
    #     )
    #     return json_format.MessageToDict(response,
    #                                      including_default_value_fields=True,
    #                                      preserving_proto_field_name=True,
    #                                      use_integers_for_enums=True)

    def set_bool_variable(self, bool_variables: list):
        """
        Bool Variables:
            [
                addr -> int32
                value -> bool
            ]
        """
        variable_list = []
        for bool_var in bool_variables:
            variable_list.append(control_msgs.BoolVariable(addr=bool_var['addr'], value=bool_var['value']))

        response = self.control.SetBoolVariable(
            control_msgs.BoolVars(variables=variable_list)
        )
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def set_int_variable(self, int_variables: list):
        """
        Integer Variables:
            [
                addr -> int32
                value -> int64
            ]
        """
        variable_list = []
        for int_var in int_variables:
            variable_list.append(control_msgs.IntVariable(addr=int_var['addr'], value=int_var['value']))

        response = self.control.SetIntVariable(
            control_msgs.IntVars(variables=variable_list)
        )
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def set_float_variable(self, float_variables: list):
        """
        Float Variables:
            [
                addr -> int32
                value -> float
            ]
        """
        variable_list = []
        for float_var in float_variables:
            variable_list.append(control_msgs.FloatVariable(addr=float_var['addr'], value=float_var['value']))

        response = self.control.SetFloatVariable(
            control_msgs.FloatVars(variables=variable_list)
        )
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def set_jpos_variable(self, jpos_variables: list):
        """
        JPos Variables:
            [
                addr -> int32
                jpos -> float[]
            ]
        """
        variable_list = []
        for jpos in jpos_variables:
            variable_list.append(control_msgs.JPosVariable(addr=jpos['addr'], jpos=jpos['jpos']))

        response = self.control.SetJPosVariable(
            control_msgs.JPosVars(variables=variable_list)
        )
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def set_tpos_variable(self, tpos_variables: list):
        """
        TPos Variables:
            [
                addr -> int32
                tpos -> float[]
            ]
        """
        variable_list = []
        for tpos in tpos_variables:
            variable_list.append(control_msgs.TPosVariable(addr=tpos['addr'], tpos=tpos['tpos']))

        response = self.control.SetTPosVariable(
            control_msgs.TPosVars(variables=variable_list)
        )
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    ############################
    # Plugin Variables
    ############################
    def set_plugin_bool_variable(self, name: str, value: bool):
        response = self.control.SetPluginBoolVariable(
            common_msgs.NamedBool(name=name, value=value)
        )
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_plugin_bool_variable(self, name: str):
        response = self.control.GetPluginBoolVariable(
            common_msgs.Name(name=name)
        )
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def set_plugin_int_variable(self, name: str, value: int):
        response = self.control.SetPluginIntVariable(
            common_msgs.NamedInt(name=name, value=value)
        )
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_plugin_int_variable(self, name: str):
        response = self.control.GetPluginIntVariable(
            common_msgs.Name(name=name)
        )
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def set_plugin_float_variable(self, name: str, value: float):
        response = self.control.SetPluginFloatVariable(
            common_msgs.NamedFloat(name=name, value=value)
        )
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_plugin_float_variable(self, name: str):
        response = self.control.GetPluginFloatVariable(
            common_msgs.Name(name=name)
        )
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def set_plugin_jpos_variable(self, name: str, jpos: List[float]):
        response = self.control.SetPluginJPosVariable(
            common_msgs.NamedJointPosition(name=name, jpos=jpos)
        )
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_plugin_jpos_variable(self, name: str):
        response = self.control.GetPluginJPosVariable(
            common_msgs.Name(name=name)
        )
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def set_plugin_tpos_variable(self, name: str, tpos: List[float]):
        response = self.control.SetPluginTPosVariable(
            common_msgs.NamedTaskPosition(name=name, tpos=tpos)
        )
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_plugin_tpos_variable(self, name: str):
        response = self.control.GetPluginTPosVariable(
            common_msgs.Name(name=name)
        )
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    ############################
    # Config
    ############################
    def get_pack_pos(self):
        """
        Joint Pack Position
            jpos -> double[]
        """
        response = self.config.GetPackPosition(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_path_config(self):
        response = self.config.GetPathConfig(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def set_locked_joint(self, index: int):
        response = self.config.SetLockedJoint(common_msgs.Int(value=index))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def set_tool_link(self, index: int):
        response = self.config.SetToolLink(common_msgs.Int(value=index))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_speed_ratio(self):
        response = self.config.GetSpeedRatio(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def set_tool_list(self, tool_list: dict):
        req = config_msgs.ToolList()
        ParseDict(tool_list, req)
        response = self.config.SetToolList(req)
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_tool_list(self):
        response = self.config.GetToolList(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_vision_server_list(self):
        response = self.config.GetVisionServerList(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def set_vision_server_list(self, vision_server_list: dict):
        req = config_msgs.VisionServerList()
        ParseDict(vision_server_list, req)
        response = self.config.SetVisionServerList(req)
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_modbus_server_list(self):
        response = self.config.GetModbusServerList(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def set_modbus_server_list(self, modbus_server_list: dict):
        req = config_msgs.ModbusServerList()
        ParseDict(modbus_server_list, req)
        response = self.config.SetModbusServerList(req)
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_conveyor_list(self):
        response = self.config.GetConveyorList(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def set_conveyor_list(self, conveyor_list: dict):
        req = config_msgs.ConveyorList()
        ParseDict(conveyor_list, req)
        response = self.config.SetConveyorList(req)
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def set_compliance_control_joint_gain(self, gains: dict):
        req = config_msgs.ComplianceGainSet()
        ParseDict(gains, req)
        response = self.config.SetComplianceControlJointGain(req)
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_compliance_control_joint_gain(self):
        response = self.config.GetComplianceControlJointGain(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_tool_frame_list(self):
        response = self.config.GetToolFrameList(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def set_tool_frame_list(self, tool_frame_list: dict):
        req = config_msgs.ToolFrameList()
        ParseDict(tool_frame_list, req)
        response = self.config.SetToolFrameList(req)
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_ref_frame_list(self):
        response = self.config.GetRefFrameList(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def set_ref_frame_list(self, ref_frame_list: dict):
        req = config_msgs.RefFrameList()
        ParseDict(ref_frame_list, req)
        response = self.config.SetRefFrameList(req)
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_custom_pos_list(self):
        response = self.config.GetCustomPosList(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def set_custom_pos_list(self, custom_pos_list: dict):
        req = config_msgs.CustomPosList()
        ParseDict(custom_pos_list, req)
        response = self.config.SetCustomPosList(req)
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def set_tool_shape_list(self, tool_shape_list: dict):
        req = config_msgs.ToolShapeList()
        ParseDict(tool_shape_list, req)
        response = self.config.SetToolShapeList(req)
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_tool_shape_list(self):
        response = self.config.GetToolShapeList(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def set_environment_list(self, environment_list: dict):
        req = config_msgs.EnvironmentList()
        ParseDict(environment_list, req)
        response = self.config.SetEnvironmentList(req)
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_environment_list(self):
        response = self.config.GetEnvironmentList(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_default_coll_sens_param(self):
        response = self.config.GetDefaultCollSensParam(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def set_sensorless_params(self, params: dict):
        req = config_msgs.SensorlessParams()
        ParseDict(params, req)
        response = self.config.SetSensorlessParams(req)
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_sensorless_params(self):
        response = self.config.GetSensorlessParams(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def set_on_start_program_config(self, config: dict):
        req = config_msgs.OnStartProgramConfig()
        ParseDict(config, req)
        response = self.config.SetOnStartProgramConfig(req)
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_on_start_program_config(self):
        response = self.config.GetOnStartProgramConfig(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def set_simple_coll_threshold(self):
        response = self.config.SetSimpleCollThreshold(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_collison_model_margin(self):
        response = self.config.GetCollisonModelMargin(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def set_collison_model_margin(self, collision_margin: float, recover_margin: float):
        response = self.config.SetCollisonModelMargin(
            config_msgs.CollisionModelMargin(collision_margin=collision_margin,
                                             recover_margin=recover_margin)
        )
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    ############################
    # Bus Events
    ############################
    def push_bus_event(self, event_id: int,
                       b_data: 'Optional[List[bool]]' = None,
                       i_data: 'Optional[List[int]]' = None,
                       f_data: 'Optional[List[float]]' = None,
                       text_data: 'Optional[str]' = None):
        evt = control_msgs.BusEvent(
            event_id=event_id,
            b_data=b_data or [],
            i_data=i_data or [],
            f_data=f_data or [],
            text_data=text_data or ""
        )
        response = self.control.PushBusEvent(evt)
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def catch_bus_event(self, event_id: int, timeout: float):
        req = control_msgs.CatchBusEventReq(event_id=event_id, timeout=timeout)
        response = self.control.CatchBusEvent(req)
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    ############################
    # Force Mode
    ############################
    def set_force_mode(self, force_mode: dict):
        """
        Set Force Mode using a dict matching control_msgs.ForceModeReq schema.
        Tip: Use get_force_mode() to see the shape and modify as needed.
        """
        msg = control_msgs.ForceModeReq()
        ParseDict(force_mode, msg)
        response = self.control.SetForceMode(msg)
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_force_mode(self):
        response = self.control.GetForceMode(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)
        
        
    def get_home_pos(self):
        """
        Joint Home Position
            jpos -> double[]
        """
        response = self.config.GetHomePosition(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def set_home_pos(self, home_jpos: list):
        """
        Joint Home Position
            jpos -> double[]
        """
        response = self.config.SetHomePosition(config_msgs.JointPos(
            jpos=home_jpos
        ))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_ref_frame(self):
        """
        Reference frame
            fpos -> float[6]
        """

        response = self.config.GetRefFrame(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def set_ref_frame(self, fpos: list):
        """
        Ref Frame
            fpos -> float[6]
        """
        response = self.config.SetRefFrame(config_msgs.Frame(
            fpos=list(fpos)
        ))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def set_ref_frame_planar(self, fpos0: list, fpos1: list, fpos2: list):
        """
        Ref Frame
            fpos -> float[6]
        """
        response = self.config.SetRefFramePlanar(config_msgs.PlanarFrame(
            fpos0=list(fpos0), fpos1=list(fpos1), fpos2=list(fpos2)
        ))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def set_tool_frame(self, fpos: list):
        """
        Tool Frame
            fpos -> float[6]
        """
        response = self.config.SetToolFrame(config_msgs.Frame(
            fpos=list(fpos)
        ))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_friction_comp(self):
        """
        Friction Compensation Set:
            joint_idx   -> uint32
            control_comp_enable   -> bool
            control_comp_levels   -> int32[6]
            teaching_comp_enable   -> bool
            teaching_comp_levels   -> int32[6]
        """
        response = self.config.GetFrictionComp(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def set_friction_comp(self, control_comp: bool, control_comp_levels: list,
                          dt_comp: bool, dt_comp_levels: list):
        """
        Friction Compensation Set:
            joint_idx   -> uint32
            control_comp_enable   -> bool
            control_comp_levels   -> int32[6]
            teaching_comp_enable   -> bool
            teaching_comp_levels   -> int32[6]
        """
        response = self.config.SetFrictionComp(config_msgs.FrictionCompSet(
            control_comp_enable=control_comp, control_comp_levels=list(control_comp_levels),
            teaching_comp_enable=dt_comp, teaching_comp_levels=list(dt_comp_levels)
        ))

        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def set_friction_comp_state(self, enable=False) -> dict:
        response = self.control.SetFrictionCompensation(common_msgs.State(enable=enable))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_friction_comp_state(self) -> dict:
        response = self.control.GetFrictionCompensationState(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def set_mount_pos(self, rot_y=0.0, rot_z=0.0):
        """
        Mounting Angles:
            rot_y   -> float
            rot_z   -> float
        """
        response = self.config.SetMountPos(config_msgs.MountingAngles(
            ry=rot_y, rz=rot_z
        ))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_mount_pos(self):
        """
        Mounting Angles:
            rot_y   -> float
            rot_z   -> float
        """
        response = self.config.GetMountPos(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_tool_property(self):
        """
        Tool Properties:
            mass   -> float
            center_of_mass   -> float[3]
            inertia   -> float[6]
        """
        response = self.config.GetToolProperty(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def set_tool_property(self, mass: float, center_of_mass: list, inertia: list):
        """
        Tool Properties:
            mass   -> float
            center_of_mass   -> float[3]
            inertia   -> float[6]
        """
        response = self.config.SetToolProperty(config_msgs.ToolProperties(
            mass=mass, center_of_mass=list(center_of_mass), inertia=list(inertia)
        ))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_coll_sens_level(self):
        """
        Collision Sensitivity Level:
            level -> uint32
        """
        response = self.config.GetCollSensLevel(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def set_coll_sens_level(self, level: int):
        """
        Collision Sensitivity Level:
            level -> uint32
        """
        response = self.config.SetCollSensLevel(config_msgs.CollisionSensLevel(
            level=level
        ))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_coll_sens_param(self):
        """
        Collision Params:
            j_torque_bases                  -> double[6]
            j_torque_tangents               -> double[6]
            t_torque_bases                  -> double[6]
            t_torque_tangents               -> double[6]
            error_bases                     -> double[6]
            error_tangents                  -> double[6]
            t_constvel_torque_bases         -> double[6]
            t_constvel_torque_tangents      -> double[6]
            t_conveyor_torque_bases         -> double[6]
            t_conveyor_torque_tangents      -> double[6]
        """
        response = self.config.GetCollSensParam(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def set_coll_sens_param(self, j_torque_bases, j_torque_tangents,
                            t_torque_bases, t_torque_tangents,
                            t_constvel_torque_bases, t_constvel_torque_tangents,
                            t_conveyor_torque_bases, t_conveyor_torque_tangents,
                            error_bases, error_tangents):
        """
        Collision Params:
            j_torque_bases                  -> double[6]
            j_torque_tangents               -> double[6]
            t_torque_bases                  -> double[6]
            t_torque_tangents               -> double[6]
            error_bases                     -> double[6]
            error_tangents                  -> double[6]
            t_constvel_torque_bases         -> double[6]
            t_constvel_torque_tangents      -> double[6]
            t_conveyor_torque_bases         -> double[6]
            t_conveyor_torque_tangents      -> double[6]
        """
        response = self.config.SetCollSensParam(config_msgs.CollisionThresholds(
            j_torque_bases=list(j_torque_bases), j_torque_tangents=list(j_torque_tangents),
            t_torque_bases=list(t_torque_bases), t_torque_tangents=list(t_torque_tangents),
            error_bases=list(error_bases), error_tangents=list(error_tangents),
            t_constvel_torque_bases=list(t_constvel_torque_bases),
            t_constvel_torque_tangents=list(t_constvel_torque_tangents),
            t_conveyor_torque_bases=list(t_conveyor_torque_bases),
            t_conveyor_torque_tangents=list(t_conveyor_torque_tangents)
        ))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_coll_policy(self):
        """
        Collision Policy:
            policy -> uint32
            sleep_time -> float
            gravity_time -> float
        """
        response = self.config.GetCollPolicy(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def set_coll_policy(self, policy=CollisionPolicyType.NONE,
                        sleep_time=0, gravity_time=0.1):
        """
        Collision Policies:
            policy -> uint32
            sleep_time -> float
            gravity_time -> float
        """
        CollisionPolicyType.NONE
        response = self.config.SetCollPolicy(config_msgs.CollisionPolicy(
            policy=policy, sleep_time=sleep_time, gravity_time=gravity_time
        ))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_safety_limits(self):
        """
        Safety Limits:
            power_limit             -> float
            power_limit_ratio       -> float
            tcp_force_limit         -> float
            tcp_force_limit_ratio   -> float
            tcp_speed_limit         -> float
            tcp_speed_limit_ratio   -> float
            joint_upper_limits   -> float[]
            joint_lower_limits   -> float[]
        """
        response = self.config.GetSafetyLimits(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def set_safety_limits(self, power_limit: float, power_limit_ratio: float,
                          tcp_force_limit: float, tcp_force_limit_ratio: float,
                          tcp_speed_limit: float, tcp_speed_limit_ratio: float):
        """
        Safety Limits:
            power_limit             -> float
            power_limit_ratio       -> float
            tcp_force_limit         -> float
            tcp_force_limit_ratio   -> float
            tcp_speed_limit         -> float
            tcp_speed_limit_ratio   -> float
        """
        response = self.config.SetSafetyLimits(config_msgs.SafetyLimits(
            power_limit=power_limit, power_limit_ratio=power_limit_ratio,
            tcp_force_limit=tcp_force_limit, tcp_force_limit_ratio=tcp_force_limit_ratio,
            tcp_speed_limit=tcp_speed_limit, tcp_speed_limit_ratio=tcp_speed_limit_ratio
        ))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    ############################
    # IndySDK related
    ############################
    def activate_sdk(self, license_key, expire_date):
        """
        license_key: license key issued by Neuromeka
        expire_date: expire date for the license, format YYYY-MM-DD
        SDKLicenseResp:
            activated -> bool, True if activated
            response (code, msg)
                - 0, 'Activated'                -> SDK Activated
                - 1, 'Invalid'                  -> Wrong key or expire date
                - 2, 'No Internet Connection'   -> Need Internet for License Verification
                - 3, 'Expired'                  -> License Expired
                - 4, 'HW_FAILURE'               -> Failed acquire HW ID to verify license
        """
        response = self.control.ActivateIndySDK(
            control_msgs.SDKLicenseInfo(license_key=license_key, expire_date=expire_date))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def set_custom_control_mode(self, mode):
        """
        mode:
        - False (0): IndyFramework's default controller is used
        - True (1): IndySDK's component is used
        """
        response = self.control.SetCustomControlMode(common_msgs.IntMode(mode=mode))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_custom_control_mode(self):
        """

        """
        response = self.control.GetCustomControlMode(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_custom_control_gain(self):
        """
        Custom Control Gain
            gain0   -> float[6]
            gain1   -> float[6]
            gain2   -> float[6]
            gain3   -> float[6]
            gain4   -> float[6]
            gain5   -> float[6]
            gain6   -> float[6]
            gain7   -> float[6]
            gain8   -> float[6]
            gain9   -> float[6]
        """
        response = self.config.GetCustomControlGain(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)
    
    def set_custom_control_gain(self, gain0=None, gain1=None, gain2=None, gain3=None, gain4=None, 
                                gain5=None, gain6=None, gain7=None, gain8=None, gain9=None):
        """
        Set custom control gains with up to 10 gain arrays.
        Args:
            gain0, gain1, ..., gain9: Up to 10 lists of gain values. Each gain should be a list of floats.
                                    If a gain is None, it will be replaced with a default list [0, 0, 0, 0, 0, 0].
        """
        # Replace None with a list of six 0s
        gains = [gain if gain is not None else [0] * 6 for gain in [gain0, gain1, gain2, gain3, gain4, gain5, gain6, gain7, gain8, gain9]]

        response = self.config.SetCustomControlGain(config_msgs.CustomGainSet(
            gain0=gains[0], gain1=gains[1], gain2=gains[2], gain3=gains[3],
            gain4=gains[4], gain5=gains[5], gain6=gains[6], gain7=gains[7],
            gain8=gains[8], gain9=gains[9]
        ))

        return json_format.MessageToDict(response,
                                        including_default_value_fields=True,
                                        preserving_proto_field_name=True,
                                        use_integers_for_enums=True)

    def set_joint_control_gain(self, kp: list, kv: list, kl2: list):
        """
        Joint Control Gains:
            kp   -> float[6]
            kv   -> float[6]
            kl2  -> float[6]
        """
        response = self.config.SetJointControlGain(config_msgs.JointGainSet(
            kp=list(kp), kv=list(kv), kl2=list(kl2)
        ))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_joint_control_gain(self):
        """
        Joint Control Gains:
            kp   -> float[6]
            kv   -> float[6]
            kl2  -> float[6]
        """
        response = self.config.GetJointControlGain(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def set_task_control_gain(self, kp, kv, kl2):
        """
        Task Control Gains:
            kp   -> float[6]
            kv   -> float[6]
            kl2  -> float[6]
        """
        response = self.config.SetTaskControlGain(config_msgs.TaskGainSet(
            kp=list(kp), kv=list(kv), kl2=list(kl2)
        ))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_task_control_gain(self):
        """
        Task Control Gains:
            kp   -> float[6]
            kv   -> float[6]
            kl2  -> float[6]
        """
        response = self.config.GetTaskControlGain(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def set_impedance_control_gain(self, mass, damping, stiffness, kl2):
        """
        Impedance Control Gains:
            mass   -> float[6]
            damping   -> float[6]
            stiffness   -> float[6]
            kl2  -> float[6]
        """
        response = self.config.SetImpedanceControlGain(config_msgs.ImpedanceGainSet(
            mass=list(mass), damping=list(damping), stiffness=list(stiffness), kl2=list(kl2)
        ))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_impedance_control_gain(self):
        """
        Impedance Control Gains:
            mass   -> float[6]
            damping   -> float[6]
            stiffness   -> float[6]
            kl2  -> float[6]
        """
        response = self.config.GetImpedanceControlGain(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def set_force_control_gain(self, kp, kv, kl2, mass, damping, stiffness, kpf, kif):
        """
        Impedance Control Gains:
            mass   -> float[6]
            damping   -> float[6]
            stiffness   -> float[6]
            kl2  -> float[6]
        """
        response = self.config.SetForceControlGain(config_msgs.ForceGainSet(
            kp=list(kp), kv=list(kv), kl2=list(kl2), mass=list(mass), damping=list(damping), stiffness=list(stiffness),
            kpf=list(kpf), kif=list(kif)
        ))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_force_control_gain(self):
        """
        Impedance Control Gains:
            mass   -> float[6]
            damping   -> float[6]
            stiffness   -> float[6]
            kl2  -> float[6]
        """
        response = self.config.GetForceControlGain(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    ############################
    # Utility functions
    ############################
    def start_log(self):
        """
        Start realtime data logging
        """
        int_vars_to_set = [{"addr": 300, "value": 1}]
        self.set_int_variable(int_vars_to_set)

    def end_log(self):
        """
        Finish realtime data logging and save the realtime data in STEP
        saved path:
            /home/user/release/IndyDeployments/RTlog/RTLog.csv
        """
        int_vars_to_set = [{"addr": 300, "value": 2}]
        self.set_int_variable(int_vars_to_set)

    def wait_for_operation_state(self, wait_op_state=None):
        if wait_op_state is not None:
            while self.get_robot_data()['op_state'] != wait_op_state:
                time.sleep(0.01)
                
    def wait_for_motion_state(self, wait_motion_state=None): 
        motion_list = ["is_in_motion", "is_target_reached", "is_pausing", "is_stopping", "has_motion"]
        if wait_motion_state is not None and wait_motion_state in motion_list:
            while self.get_motion_data()[wait_motion_state] is False:
                time.sleep(0.01)

    ############################
    def wait_io(self, 
                di_signal_list, 
                do_signal_list, 
                end_di_signal_list, 
                end_do_signal_list, 
                conjunction=0):
        response = self.control.WaitIO(control_msgs.WaitIOReq(
            di_list=self.__to_digital_request_list__(di_signal_list),
            do_list=self.__to_digital_request_list__(do_signal_list),
            end_di_list=self.__to_digital_request_list__(end_di_signal_list),
            end_do_list=self.__to_digital_request_list__(end_do_signal_list),
            conjunction=conjunction
        ))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)
    
    
    def wait_time(self, time: float):
        """
         Wait time [s]
        """
        response = self.control.WaitTime(control_msgs.WaitTimeReq(
            time=time
        ))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def wait_progress(self, progress: int):
        """
         Wait progress [s]
        """
        response = self.control.WaitProgress(control_msgs.WaitProgressReq(
            progress=progress
        ))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def wait_traj(self, traj_condition):
        """
         Wait trajectory
        """
        response = self.control.WaitTraj(control_msgs.WaitTrajReq(
            traj_condition=traj_condition
        ))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def wait_radius(self, radius: int):
        """
         Wait radius [mm]
        """
        response = self.control.WaitRadius(control_msgs.WaitRadiusReq(
            radius=radius
        ))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)
    

    ############################
    def set_do_config_list(self, do_config_list: dict):
        """
        DO Configuration List
            {
                'do_configs': [
                    {
                        'state_code': 2,
                        'state_name': "name",
                        'onSignals': [{'address': 1, 'state': 1}, {'address': 2, 'state': 0}],
                        'offSignals': [{'address': 1, 'state': 1}, {'address': 2, 'state': 0}]
                    }
                ]
            }
        """
        do_list_request = config_msgs.DOConfigList()
        json_format.ParseDict(do_config_list, do_list_request)

        response = self.config.SetDOConfigList(do_list_request)

        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_do_config_list(self):
        """
        DO Configuration List
            {
                'do_configs': [
                    {
                        'state_code': 2,
                        'state_name': "name",
                        'onSignals': [{'address': 1, 'state': 1}, {'address': 2, 'state': 0}],
                        'offSignals': [{'address': 1, 'state': 1}, {'address': 2, 'state': 0}]
                    }
                ]
            }
        """
        response = self.config.GetDOConfigList(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def move_recover_joint(self, jtarget,
                           base_type=JointBaseType.ABSOLUTE) -> dict:
        """
         Move recover joint
         jtarget = [deg, deg, deg, deg, deg, deg]
        """
        response = self.control.MoveRecoverJoint(
            control_msgs.TargetJ(j_target=list(jtarget), base_type=base_type)
        )
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_control_info(self):
        response = self.control.GetControlInfo(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def check_aproach_retract_valid(self, tpos, init_jpos, pre_tpos, post_tpos):
        """
        Check aproach retract valid
        """
        response = self.control.CheckAproachRetractValid(control_msgs.CheckAproachRetractValidReq(
            tpos=list(tpos),
            init_jpos=list(init_jpos),
            pre_tpos=list(pre_tpos),
            post_tpos=list(post_tpos)
        ))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_pallet_point_list(self, tpos, jpos, pre_tpos, post_tpos, pallet_pattern, width, height):
        """
        Get pallet point list
        """
        response = self.control.GetPalletPointList(control_msgs.GetPalletPointListReq(
            tpos=list(tpos),
            jpos=list(jpos),
            pre_tpos=list(pre_tpos),
            post_tpos=list(post_tpos),
            pallet_pattern=pallet_pattern,
            width=width,
            height=height
        ))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    # def play_program_line(self, prog_name: str = '', prog_idx: int = -1):
    #     response = self.control.PlayProgramLine(control_msgs.Program(
    #         prog_name=prog_name,
    #         prog_idx=prog_idx
    #     ))
    #     return json_format.MessageToDict(response,
    #                                      including_default_value_fields=True,
    #                                      preserving_proto_field_name=True,
    #                                      use_integers_for_enums=True)

    def play_tuning_program(self, prog_name: str = '', prog_idx: int = -1,
                            tuning_space=common_msgs.TUNE_ALL, precision=common_msgs.HIGH_PRECISION,
                            vel_level_max=9):
        """
        Play tuning program
        """
        tuning_prog_dict = dict(
            program=dict(
                prog_name=prog_name,
                prog_idx=prog_idx),
            tuning_space=tuning_space,
            precision=precision,
            vel_level_max=vel_level_max
        )
        tuning_req = control_msgs.TuningProgram()

        # json_format.ParseDict(tuning_prog_dict, tuning_req)
        ParseDict(tuning_prog_dict, tuning_req)
        response = self.control.PlayTuningProgram(tuning_req)
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def set_di_config_list(self, di_config_list: dict):
        """
        DI Configuration List
            {
                'di_configs': [
                    {
                        'function_code': 2,
                        'function_name': "name",
                        'triggerSignals': [{'address': 1, 'state': 1}, {'address': 2, 'state': 0}]
                        'successSignals': [{'address': 1, 'state': 1}, {'address': 2, 'state': 0}]
                        'failureSignals': [{'address': 1, 'state': 1}, {'address': 2, 'state': 0}]
                    }
                ]
            }
        """
        di_list_request = config_msgs.DIConfigList()
        # json_format.ParseDict(di_config_list, di_list_request)
        ParseDict(di_config_list, di_list_request)
        response = self.config.SetDIConfigList(di_list_request)

        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_di_config_list(self):
        """
        DI Configuration List
            {
                'di_configs': [
                    {
                        'function_code': 2,
                        'function_name': "name",
                        'triggerSignals': [{'address': 1, 'state': 1}, {'address': 2, 'state': 0}],
                        'successSignals': [{'address': 1, 'state': 1}, {'address': 2, 'state': 0}],
                        'failureSignals': [{'address': 1, 'state': 1}, {'address': 2, 'state': 0}]
                    }
                ]
            }
        """
        response = self.config.GetDIConfigList(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def set_ft_sensor_config(self,
                          dev_type, com_type, ip_address,
                               ft_frame_translation_offset_x=0.0,
                               ft_frame_translation_offset_y=0.0,
                               ft_frame_translation_offset_z=0.0,
                               ft_frame_rotation_offset_r=0.0,
                               ft_frame_rotation_offset_p=0.0,
                               ft_frame_rotation_offset_y=0.0):
        response = self.config.SetFTSensorConfig(config_msgs.FTSensorDevice(
            dev_type=dev_type, com_type=com_type,ip_address=ip_address,
            ft_frame_translation_offset_x=ft_frame_translation_offset_x,
            ft_frame_translation_offset_y=ft_frame_translation_offset_y,
            ft_frame_translation_offset_z=ft_frame_translation_offset_z,
            ft_frame_rotation_offset_r=ft_frame_rotation_offset_r,
            ft_frame_rotation_offset_p=ft_frame_rotation_offset_p,
            ft_frame_rotation_offset_y=ft_frame_rotation_offset_y))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_ft_sensor_config(self):
        response = self.config.GetFTSensorConfig(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def set_auto_servo_off(self, enable: bool, time: float):
        """
        Auto Servo-Off Config
            enable -> bool
            time -> float
        """
        response = self.config.SetAutoServoOff(config_msgs.AutoServoOffConfig(
            enable=enable, time=time
        ))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_auto_servo_off(self):
        """
        Auto Servo-Off Config
            enable -> bool
            time -> float
        """
        response = self.config.GetAutoServoOff(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def set_safety_stop_config(self, jpos_limit_stop_cat=StopCategory.CAT0,
                               jvel_limit_stop_cat=StopCategory.CAT0,
                               jtau_limit_stop_cat=StopCategory.CAT0,
                               tvel_limit_stop_cat=StopCategory.CAT0,
                               tforce_limit_stop_cat=StopCategory.CAT0,
                               power_limit_stop_cat=StopCategory.CAT0,
                               safegd_stop_cat=None,
                               safegd_type=None):
        """
        Safety Stop Category:
            jpos_limit_stop_cat = IMMEDIATE_BRAKE(0) | SMOOTH_BRAKE(1) | SMOOTH_ONLY(2)
            jvel_limit_stop_cat = IMMEDIATE_BRAKE(0) | SMOOTH_BRAKE(1) | SMOOTH_ONLY(2)
            jtau_limit_stop_cat = IMMEDIATE_BRAKE(0) | SMOOTH_BRAKE(1) | SMOOTH_ONLY(2)
            tvel_limit_stop_cat = IMMEDIATE_BRAKE(0) | SMOOTH_BRAKE(1) | SMOOTH_ONLY(2)
            tforce_limit_stop_cat = IMMEDIATE_BRAKE(0) | SMOOTH_BRAKE(1) | SMOOTH_ONLY(2)
            power_limit_stop_cat = IMMEDIATE_BRAKE(0) | SMOOTH_BRAKE(1) | SMOOTH_ONLY(2)
        Optional:
            safegd_stop_cat -> list[StopCategory]
            safegd_type -> list[SafeGdType]
        """
        response = self.config.SetSafetyStopConfig(config_msgs.SafetyStopConfig(
            joint_position_limit_stop_cat=jpos_limit_stop_cat,
            joint_speed_limit_stop_cat=jvel_limit_stop_cat,
            joint_torque_limit_stop_cat=jtau_limit_stop_cat,
            tcp_speed_limit_stop_cat=tvel_limit_stop_cat,
            tcp_force_limit_stop_cat=tforce_limit_stop_cat,
            power_limit_stop_cat=power_limit_stop_cat,
            safegd_stop_cat=(safegd_stop_cat or []),
            safegd_type=(safegd_type or [])
        ))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_safety_stop_config(self):
        """
        Safety Stop Category:
            joint_position_limit_stop_cat = IMMEDIATE_BRAKE(0) | SMOOTH_BRAKE(1) | SMOOTH_ONLY(2)
            joint_speed_limit_stop_cat = IMMEDIATE_BRAKE(0) | SMOOTH_BRAKE(1) | SMOOTH_ONLY(2)
            joint_torque_limit_stop_cat = IMMEDIATE_BRAKE(0) | SMOOTH_BRAKE(1) | SMOOTH_ONLY(2)
            tcp_speed_limit_stop_cat = IMMEDIATE_BRAKE(0) | SMOOTH_BRAKE(1) | SMOOTH_ONLY(2)
            tcp_force_limit_stop_cat = IMMEDIATE_BRAKE(0) | SMOOTH_BRAKE(1) | SMOOTH_ONLY(2)
            power_limit_stop_cat = IMMEDIATE_BRAKE(0) | SMOOTH_BRAKE(1) | SMOOTH_ONLY(2)
        """
        response = self.config.GetSafetyStopConfig(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_reduced_ratio(self):
        response = self.config.GetReducedRatio(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_reduced_speed(self):
        response = self.config.GetReducedSpeed(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def set_reduced_speed(self, speed):
        response = self.config.SetReducedSpeed(config_msgs.SetReducedSpeedReq(speed=speed))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def set_teleop_params(self, smooth_factor, cutoff_freq, error_gain):
        response = self.config.SetTeleOpParams(
            config_msgs.TeleOpParams(smooth_factor=smooth_factor,
                                     cutoff_freq=cutoff_freq,
                                     error_gain=error_gain))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_teleop_params(self):
        """
        IO Data:
            smooth_factor   -> float
            cutoff_freq   -> float
            error_gain  -> float
        """
        response = self.config.GetTeleOpParams(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_kinematics_params(self):
        response = self.config.GetKinematicsParams(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def get_io_data(self):
        """
        IO Data:
            di   -> DigitalSignal[]
            do   -> DigitalSignal[]
            ai  -> AnalogSignal[]
            ao  -> AnalogSignal[]
            end_di  -> EndtoolSignal[]
            end_do  -> EndtoolSignal[]
            end_ai  -> AnalogSignal[]
            end_ao  -> AnalogSignal[]
            response  -> Response
        """
        response = self.rtde.GetIOData(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def ping_from_conty(self):
        response = self.control.PingFromConty(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                    including_default_value_fields=True,
                                    preserving_proto_field_name=True,
                                    use_integers_for_enums=True)

    def load_reference_frame(self):
        response = self.config.GetRefFrameList(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                    including_default_value_fields=True,
                                    preserving_proto_field_name=True,
                                    use_integers_for_enums=True)
        
    def save_reference_frame(self, frames, default_name):
        """
        frames = [
            {
                'name': 'frame1',
                'tpos': [0.0, 0.0, 0.0, 0.0, 0.0],
                'jpos0': [0.0, 0.0, 0.0, 0.0, 0.0]
            },
            {
                'name': 'frame2',
                'tpos': [0.0, 0.0, 0.0, 0.0, 0.0],
                'jpos1': [0.0, 0.0, 0.0, 0.0, 0.0]
            }
        ]
        default_name = "default_frame"
        """
        request = config_msgs.RefFrameList(
            ref_frames=[
                common_msgs.NamedReferencePosition(
                    name=frame['name'],
                    tpos=frame.get('tpos', []),
                    tpos0=frame.get('tpos0', []),
                    tpos1=frame.get('tpos1', []),
                    tpos2=frame.get('tpos2', []),
                    jpos0=frame.get('jpos0', []),
                    jpos1=frame.get('jpos1', []),
                    jpos2=frame.get('jpos2', [])
                ) for frame in frames
            ],
            default_name=default_name
        )

        response = self.config.SetRefFrameList(request)
        return json_format.MessageToDict(response,
                                    including_default_value_fields=True,
                                    preserving_proto_field_name=True,
                                    use_integers_for_enums=True)

    def get_ft_zero(self):
        response = self.control.FTZero(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)
        
    def get_inference_data(self):
        response = self.control.GetControlInferenceData(common_msgs.Empty())
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def set_inference_data(self, infdata0, infdata1, infdata2, infdata3, infdata4, infdata5):

        response = self.control.SetControlInferenceData(control_msgs.ControlInferenceDataSet(
            infdata0=infdata0,
            infdata1=infdata1,
            infdata2=infdata2,
            infdata3=infdata3,
            infdata4=infdata4,
            infdata5=infdata5
        ))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)

    def set_inference_data(self, *args):        

        infdata = [[0.0] * 6 for _ in range(6)]

        for i, value in enumerate(args):
            if i < 6:
                if isinstance(value, list) and len(value) == 6:
                    infdata[i] = value
                else:
                    print(f"Debug 2: Argument {i} ignored - Expected a list of size 6 but got {value}.")
            else:
                print(f"Debug 2: Argument {i} = {value} ignored (index exceeds 5).")

        response = self.control.SetControlInferenceData(control_msgs.ControlInferenceDataSet(
            infdata0=infdata[0],
            infdata1=infdata[1],
            infdata2=infdata[2],
            infdata3=infdata[3],
            infdata4=infdata[4],
            infdata5=infdata[5]
        ))
        return json_format.MessageToDict(response,
                                         including_default_value_fields=True,
                                         preserving_proto_field_name=True,
                                         use_integers_for_enums=True)
        