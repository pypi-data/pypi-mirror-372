import sys
if sys.version_info >= (3, 9):
    from neuromeka.proto import *
else:
    from neuromeka.proto_step import *
    
from neuromeka.common import *
from neuromeka.enums import *

import grpc
import time

ETHERCAT_PORT = 20000


class EtherCAT:
    def __init__(self, ip_addr):
        # initialize RPC
        ecat_channel = grpc.insecure_channel("{}:{}".format(ip_addr, ETHERCAT_PORT))
        ecat_stub = EtherCATStub(ecat_channel)

        self.__ethercat_stub = ecat_stub

    
    ###### EtherCAT Communication Task gRPC protocol
    # @Utils.exception_handler
    def get_master_status(self):
        """
        Master status
            status -> int
        """
        status = self.__ethercat_stub.GetMasterStatus(common_msgs.Empty()).status
        if status == 1:
            return "INIT"
        elif status == 2:
            return "PRE-OP"
        elif status == 4:
            return "SAFE-OP"
        elif status == 8:
            return "OP"
        else:
            return "None"

    @Utils.exception_handler
    def get_slave_status(self):
        """
        Slave status

        """
        status = (self.__ethercat_stub.GetSlaveStatus(common_msgs.Empty()).status)
        slave_status = []
        for stat in status:
            if stat == 1:
                slave_status.append("INIT")
            elif stat == 2:
                slave_status.append("PRE-OP")
            elif stat == 4:
                slave_status.append("SAFE-OP")
            elif stat == 8:
                slave_status.append("OP")
            else:
                slave_status.append("None")
        return slave_status

    @Utils.exception_handler
    def get_txdomain_status(self):
        """
        PDO Tx Domain status
        """
        status = self.__ethercat_stub.GetTxDomainStatus(common_msgs.Empty()).status
        if status == 0:
            return "ZERO"
        elif status == 1:
            return "INCOMPLETE"
        elif status == 2:
            return "COMPLETE"
        else:
            return "None"

    @Utils.exception_handler
    def get_rxdomain_status(self):
        """
        PDO Rx Domain status
        """
        status = self.__ethercat_stub.GetRxDomainStatus(common_msgs.Empty()).status
        if status == 0:
            return "ZERO"
        elif status == 1:
            return "INCOMPLETE"
        elif status == 2:
            return "COMPLETE"
        else:
            return "None"

    @Utils.exception_handler
    def is_system_ready(self) -> list:
        """
        System ready state
        """
        return list(self.__ethercat_stub.IsSystemReady(common_msgs.Empty()).ready)

    @Utils.exception_handler
    def is_servo_on(self) -> list:
        """
        Servo on state
        """
        return list(self.__ethercat_stub.IsServoOn(common_msgs.Empty()).servo)

    @Utils.exception_handler
    def get_slave_type_num(self):
        """
        Servo on state
        """
        return self.__ethercat_stub.GetSlaveTypeNum(common_msgs.Empty())

    @Utils.exception_handler
    def reset_overflow_count(self):
        """
        Reset and save overflow count
        """
        return self.__ethercat_stub.ResetOverflowCount(common_msgs.Empty())

    @Utils.exception_handler
    def set_servo(self, servo_idx, on):
        """
        Servo on state
        """
        if on:
            self.__ethercat_stub.SetServoOn(ethercat_msgs.ServoIndex(servoIndex=servo_idx))
        else:
            self.__ethercat_stub.SetServoOff(ethercat_msgs.ServoIndex(servoIndex=servo_idx))

    @Utils.exception_handler
    def get_servo_tx(self, servo_idx):
        """
        Get Servo driver's Tx PDO values
        """
        res = self.__ethercat_stub.GetServoTx(ethercat_msgs.ServoIndex(servoIndex=servo_idx))
        return [EtherCATStatus.status2string(res.statusWord),
                EtherCATStatus.modeop2string(res.modeOpDisp), res.actualPosition, res.actualVelocity, res.actualTorque]

    @Utils.exception_handler
    def get_servo_tx_raw(self, servo_idx):
        """
        Get Servo driver's Tx PDO values
        """
        return self.__ethercat_stub.GetServoTx(ethercat_msgs.ServoIndex(servoIndex=servo_idx))

    @Utils.exception_handler
    def get_servo_tx_keba(self, servo_idx):
        """
        Get Servo (Keba) driver's Tx PDO values
        """
        res = self.__ethercat_stub.GetServoTxKeba(ethercat_msgs.ServoIndex(servoIndex=servo_idx))
        res1 = [EtherCATStatus.status2string(res.statusWord), res.actualPosition, res.actualVelocity]
        res2 = [EtherCATStatus.status2string(res.statusWord2), res.actualPosition2, res.actualVelocity2]
        res3 = [EtherCATStatus.status2string(res.statusWord3), res.actualPosition3, res.actualVelocity3]
        return [res1, res2, res3]

    @Utils.exception_handler
    def get_servo_rx_keba(self, servo_idx):
        """
        Get Servo (Keba) driver's Rx PDO values
        """
        res = self.__ethercat_stub.GetServoRxKeba(ethercat_msgs.ServoIndex(servoIndex=servo_idx))
        res1 = [res.controlWord, res.targetPosition, res.targetTorque]
        res2 = [res.controlWord2, res.targetPosition2, res.targetTorque2]
        res3 = [res.controlWord3, res.targetPosition3, res.targetTorque3]
        return [res1, res2, res3]

    @Utils.exception_handler
    def get_servo_rx(self, servo_idx):
        """
        Get Servo driver's Rx PDO values
        """
        res = self.__ethercat_stub.GetServoRx(ethercat_msgs.ServoIndex(servoIndex=servo_idx))
        return [res.controlWord, res.modeOp, res.targetPosition, res.targetVelocity, res.targetTorque]

    @Utils.exception_handler
    def set_servo_rx(self, servo_idx, control_word, mode_op, target_pos, target_vel, target_tor):
        """
        Set Servo driver's Rx PDO values
        """
        print(servo_idx, control_word, mode_op, target_pos, target_vel, target_tor)
        servo_rx = ethercat_msgs.ServoRx(controlWord=control_word, modeOp=mode_op, targetPosition=target_pos, targetVelocity=target_vel, targetTorque=target_tor)
        return self.__ethercat_stub.SetServoRx(ethercat_msgs.ServoRxIndex(servoIndex=servo_idx, rx=servo_rx))

    @Utils.exception_handler
    def set_servo_rx_keba(self, servo_idx, rx1, rx2, rx3):
        """
        Set Servo (Keba) driver's Rx PDO values
        """
        control_word = rx1[0]
        control_word2 = rx2[0]
        control_word3 = rx3[0]

        target_pos = rx1[1]
        target_pos2 = rx2[1]
        target_pos3 = rx3[1]

        target_tor = rx1[2]
        target_tor2 = rx2[2]
        target_tor3 = rx3[2]
        servo_rx = ethercat_msgs.ServoRxKeba(controlWord=control_word, controlWord2=control_word2, controlWord3=control_word3,
                               targetPosition=target_pos, targetPosition2=target_pos2, targetPosition3=target_pos3,
                               targetTorque=target_tor, targetTorque2=target_tor2, targetTorque3=target_tor3)
        return self.__ethercat_stub.SetServoRx(ethercat_msgs.ServoRxIndexKeba(servoIndex=servo_idx, rx=servo_rx))

    @Utils.exception_handler
    def get_servo_temperature(self, servo_idx):
        """
        Get Servo SDO temperatures
        """
        return self.__ethercat_stub.GetServoTemperature(ethercat_msgs.ServoIndex(servoIndex=servo_idx)).temperature

    @Utils.exception_handler
    def get_servo_errorcode(self, servo_idx):
        """
        Get Servo SDO error code
        """
        return self.__ethercat_stub.GetServoErrorCode(ethercat_msgs.ServoIndex(servoIndex=servo_idx)).errorCode

    @Utils.exception_handler
    def reset_servo(self, servo_idx):
        """
        Reset servo error
        """
        return self.__ethercat_stub.ResetServo(ethercat_msgs.ServoIndex(servoIndex=servo_idx))

    @Utils.exception_handler
    def set_brake(self, ecat_idx, onoff):
        """
        Manual brake by SDO
        """
        return self.__ethercat_stub.SetCOREManualBrake(ethercat_msgs.ServoBrake(ecatIndex=ecat_idx, onoff=onoff))

    @Utils.exception_handler
    def set_endtool_rx(self, endtool_rx):
        """
        Set endtool Rx data
        """
        eqc = endtool_rx["eqc"]
        gripper = endtool_rx["gripper"]
        ft_param = endtool_rx["ft_param"]
        led_mode = endtool_rx["led_mode"]
        led_g = endtool_rx["led_g"]
        led_r = endtool_rx["led_r"]
        led_b = endtool_rx["led_b"]
        return self.__ethercat_stub.SetEndtoolRx(ethercat_msgs.EndtoolRx(eqc=eqc, gripper=gripper, ft_param=ft_param, led_mode=led_mode, led_g=led_g, led_r=led_r, led_b=led_b))

    @Utils.exception_handler
    def get_endtool_rx(self):
        """
        Get endtool Rx data
        """
        endtool_rx = {}
        data = self.__ethercat_stub.GetEndtoolRx(common_msgs.Empty())
        endtool_rx["eqc"] = data.eqc
        endtool_rx["gripper"] = data.gripper
        endtool_rx["ft_param"] = data.ft_param
        endtool_rx["led_mode"] = data.led_mode
        endtool_rx["led_g"] = data.led_g
        endtool_rx["led_r"] = data.led_r
        endtool_rx["led_b"] = data.led_b
        return endtool_rx

    @Utils.exception_handler
    def set_endtool_rs485_rx(self, word1, word2):
        return self.__ethercat_stub.SetEndtoolRS485Rx(common_msgs.EndtoolRS485Rx(word1=word1, word2=word2))

    @Utils.exception_handler
    def get_endtool_rs485_rx(self):
        return self.__ethercat_stub.GetEndtoolRS485Rx(common_msgs.Empty())

    @Utils.exception_handler
    def get_endtool_rs485_tx(self):
        return self.__ethercat_stub.GetEndtoolRS485Tx(common_msgs.Empty())

    @Utils.exception_handler
    def set_endtool_srkey_rx(self, srkey_endtool_rx):
        """
        Set endtool SRKey Rx data
        """
        dout = srkey_endtool_rx["dout"]
        tool_Id = srkey_endtool_rx["tool_Id"]
        set_Tool = srkey_endtool_rx["set_Tool"]
        tool_Closing_Force = srkey_endtool_rx["tool_Closing_Force"]
        tool_Opening_Force = srkey_endtool_rx["tool_Opening_Force"]
        tool_Force_Location = srkey_endtool_rx["tool_Force_Location"]
        return self.__ethercat_stub.SetSRKeyEndtoolRx(ethercat_msgs.SRKeyEndtoolRx(dout = dout, tool_Id = tool_Id, set_Tool = set_Tool, tool_Closing_Force = tool_Closing_Force, tool_Opening_Force = tool_Opening_Force, tool_Force_Location = tool_Force_Location))

    @Utils.exception_handler
    def get_endtool_srkey_rx(self):
        """
        Get endtool SRKey Rx data
        """
        endtool_srkey_rx = {}
        data = self.__ethercat_stub.GetSRKeyEndtoolRx(common_msgs.Empty())
        endtool_srkey_rx["dout"] = data.dout
        endtool_srkey_rx["tool_Id"] = data.tool_Id
        endtool_srkey_rx["set_Tool"] = data.set_Tool
        endtool_srkey_rx["tool_Closing_Force"] = data.tool_Closing_Force
        endtool_srkey_rx["tool_Opening_Force"] = data.tool_Opening_Force
        endtool_srkey_rx["tool_Force_Location"] = data.tool_Force_Location
        return endtool_srkey_rx

    @Utils.exception_handler
    def get_endtool_srkey_tx(self):
        """
        Get endtool SRKey Tx data
        """
        endtool_srkey_tx = {}
        data = self.__ethercat_stub.GetSRKeyEndtoolTx(common_msgs.Empty())
        endtool_srkey_tx["din"] = data.din
        endtool_srkey_tx["tool_Status"] = data.tool_Status
        endtool_srkey_tx["tool_Location"] = data.tool_Location
        endtool_srkey_tx["analog0"] = data.analog0
        endtool_srkey_tx["analog1"] = data.analog1
        endtool_srkey_tx["version"] = data.version
        return endtool_srkey_tx

    @Utils.exception_handler
    def set_endtool_led_dim(self, led_dim):
        return self.__ethercat_stub.SetEndtoolLedDim(ethercat_msgs.LedDim(led_dim=led_dim))

    @Utils.exception_handler
    def get_endtool_tx(self):
        """
        Get endtool Tx data
        """
        endtool_tx = {}
        data = self.__ethercat_stub.GetEndtoolTx(common_msgs.Empty())
        endtool_tx["status"] = data.status
        endtool_tx["button"] = data.button
        endtool_tx["ft_sensor"] = data.ft_sensor
        endtool_tx["ft_state"] = data.ft_state
        endtool_tx["ft_error"] = data.ft_error
        return endtool_tx

    @Utils.exception_handler
    def get_ioboard_tx(self):
        """
        Get ioboard Tx data
        """
        ioboard_tx = {}
        data = self.__ethercat_stub.GetIOBoardTx(common_msgs.Empty())
        ioboard_tx["di5v"] = data.di5v
        ioboard_tx["di24v1"] = data.di24v1
        ioboard_tx["di24v2"] = data.di24v2
        ioboard_tx["ai1"] = data.ai1
        ioboard_tx["ai2"] = data.ai2
        return ioboard_tx

    @Utils.exception_handler
    def get_ioboard_rx(self):
        """
        Get ioboard Rx data
        """
        ioboard_rx = {}
        data = self.__ethercat_stub.GetIOBoardRx(common_msgs.Empty())
        ioboard_rx["do5v"] = data.do5v
        ioboard_rx["do24v1"] = data.do24v1
        ioboard_rx["do24v2"] = data.do24v2
        ioboard_rx["ao1"] = data.ao1
        ioboard_rx["ao2"] = data.ao2
        ioboard_rx["ft_param"] = data.ft_param
        return ioboard_rx

    @Utils.exception_handler
    def set_ioboard_rx(self, ioboard_rx):
        """
        Set ioboard Rx data
        """
        do5v = ioboard_rx["do5v"]
        do24v1 = ioboard_rx["do24v1"]
        do24v2 = ioboard_rx["do24v2"]
        ao1 = ioboard_rx["ao1"]
        ao2 = ioboard_rx["ao2"]
        ft_param = ioboard_rx["ft_param"]
        return self.__ethercat_stub.SetIOBoardRx(
            ethercat_msgs.EndtoolRx(do5v=do5v, do24v1=do24v1, do24v2=do24v2, ao1=ao1, ao2=ao2, ft_param=ft_param))


    @Utils.exception_handler
    def get_di(self, dio_index):
        """
        Get DIO Tx data
        """
        return self.__ethercat_stub.GetDI(ethercat_msgs.DIOIndex(dioIndex=dio_index)).di_list

    @Utils.exception_handler
    def get_do(self, dio_index):
        """
        Set ioboard Rx data
        """
        return self.__ethercat_stub.GetDO(ethercat_msgs.DIOIndex(dioIndex=dio_index)).do_list

    @Utils.exception_handler
    def set_do(self, dio_index, dio):
        """
        Set ioboard Rx data
        """
        return self.__ethercat_stub.SetDO(ethercat_msgs.DIODigitalOutput(dioIndex=dio_index, do_list=dio))


    @Utils.exception_handler
    def set_maxTorque(self, slave_idx, value):
        """
        Set Maximum Torque [ecat idx, torq]
        """
        return self.__ethercat_stub.SetMaxTorqueSDO(ethercat_msgs.ServoParam(slaveIdx=slave_idx, val=value))

    @Utils.exception_handler
    def set_profileVel(self, slave_idx, value):
        """
        Set Profile Velocity [ecat idx, vel]
        """
        return self.__ethercat_stub.SetProfileVelSDO(ethercat_msgs.ServoParam(slaveIdx=slave_idx, val=value))

    @Utils.exception_handler
    def set_profileAcc(self, slave_idx, value):
        """
        Set Profile Acceleration [ecat idx, acc]
        """
        return self.__ethercat_stub.SetProfileAccSDO(ethercat_msgs.ServoParam(slaveIdx=slave_idx, val=value))

    @Utils.exception_handler
    def set_profileDec(self, slave_idx, value):
        """
        Set Profile Deceleration [ecat idx, dec]
        """
        return self.__ethercat_stub.SetProfileDecSDO(ethercat_msgs.ServoParam(slaveIdx=slave_idx, val=value))

    @Utils.exception_handler
    def get_maxTorque(self, slave_idx):
        """
        Get Maximum Torque [ecat idx]
        """
        return self.__ethercat_stub.GetMaxTorqueSDO(ethercat_msgs.EcatIndex(ecatIndex=slave_idx)).val

    @Utils.exception_handler
    def get_profileVel(self, slave_idx):
        """
        Get Profile Velocity [ecat idx]
        """
        return self.__ethercat_stub.GetProfileVelSDO(ethercat_msgs.EcatIndex(ecatIndex=slave_idx)).val

    @Utils.exception_handler
    def get_profileAcc(self, slave_idx):
        """
        Get Profile Acceleration [ecat idx]
        """
        return self.__ethercat_stub.GetProfileAccSDO(ethercat_msgs.EcatIndex(ecatIndex=slave_idx)).val

    @Utils.exception_handler
    def get_profileDec(self, slave_idx):
        """
        Get Profile Deceleration [ecat idx]
        """
        return self.__ethercat_stub.GetProfileDecSDO(ethercat_msgs.EcatIndex(ecatIndex=slave_idx)).val


    def get_robot_zero_count(self, servo_idx):
        """
        Get robot zero count
        """
        return self.__ethercat_stub.GetRobotZeroCount(ethercat_msgs.ServoIndex(servoIndex=servo_idx))

    @Utils.exception_handler
    def set_robot_zero_as_current(self, servo_idx):
        """
        Set robot zero as current
        """
        return self.__ethercat_stub.SetRobotZeroAsCurrent(ethercat_msgs.ServoIndex(servoIndex=servo_idx))


    ## Conty Linear Ext Servo
    @Utils.exception_handler
    def get_axis_data(self,servo_idx):
        """
        Axis Data:
          repeated bool active = 1;
          repeated float pos_mm = 2;
          repeated float vel_mm = 3;

          repeated float despos_mm = 4;
          repeated float desvel_mm = 5;
          repeated float desacc_mm = 6;

          uint32 num_axes = 10;
          OpState op_state = 11;
          TrajState traj_state = 12;
        """
        """
        # enum OpState {
            SYSTEM_OFF = 0;
            SYSTEM_ON = 1;
            VIOLATE = 2;
            RECOVER_HARD = 3;
            RECOVER_SOFT = 4;
            IDLE = 5;
            MOVING = 6;
            }
        # enum TrajState {
            TRAJ_NONE = 0;
            TRAJ_INIT = 1;
            TRAJ_CALC = 2;
            TRAJ_STBY = 3;
            TRAJ_ACC = 4;
            TRAJ_CRZ = 5;
            TRAJ_DEC = 6;
            TRAJ_CANC = 7;
            TRAJ_FIN = 8;
            TRAJ_ERR = 9;
            }
        """
        num_axes = 1 # num_axes ##TO CONFIG
        servo_tx = self.get_servo_tx(servo_idx)  ##TO CONFIG
        servo_rx = self.get_servo_rx(servo_idx)

        #active
        if servo_tx[0] == 'OPERATION_ENABLED':
            active = [True]
        else:
            active = [False]

        convert = 1/7200 # 1rev per 0.5cm  , 1rev per 360000feed ##TO CONFIG

        pos_cnt = servo_tx[2] # actualPos
        pos_mm = [pos_cnt * convert]

        vel_cnt = servo_tx[3] # actualVel
        vel_mm = [vel_cnt * convert]

        despos_cnt = servo_rx[2]
        despos_mm = despos_cnt * convert

        desvel_mm = 0.0 # ethertoolslave -p0 upload -t uint32 0x6081 0  (profiled velocity)
        desacc_mm = 0.0 # ethertoolslave -p0 upload -t uint32 0x6083 0  (profiled velocity)
        # ethertoolslave -p0 upload -t uint32 0x6084 0  (profiled velocity)

        if self.is_servo_on()[servo_idx]:
            op_state = 1 # SYSTEM_ON
            if self.is_system_ready()[servo_idx]:
                op_state = 5 # IDLE
            elif self.is_system_ready()[servo_idx] & servo_rx[2] != 0:
                op_state = 6 # MOVING
        else:
            op_state = 0 # SYSTEM_OFF

        traj_state: TrajState = TrajState.TRAJ_NONE


        # print(f"num_axes = {type(num_axes)}")
        # print(f"active = {type(active)}")
        # print(f"pos_mm = {type(pos_mm)}")
        # print(f"vel_mm = {type(vel_mm)}")
        # print(f"despos_mm = {type(despos_mm)}")
        # print(f"desvel_mm = {type(desvel_mm)}")
        # print(f"desacc_mm = {type(desacc_mm)}")

        # print(f"op_state = {type(op_state)}")
        # print(f"traj_state = {type(traj_state)}")

        axis_data_dict = {
            "active" : active,
            "pos_mm" : pos_mm,
            "vel_mm" : vel_mm,
            "despos_mm" : despos_mm,
            "desvel_mm" : desvel_mm,
            "desacc_mm" : desacc_mm,
            "num_axes" : num_axes,
            "op_state" : op_state,
            "traj_state" : traj_state
        }

        # print('Linear Axis Data: ' + str(axis_data_dict))
        return axis_data_dict

    @Utils.exception_handler
    def move_axis(self,
                  servo_idx,
                  start_mm,
                  target_mm,
                  is_absolute=True,
                  vel_ratio=50,
                  acc_ratio=100,
                  teaching_mode=True):
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
        # print("teaching_mode ", teaching_mode)

        vel = Limits.ExternalMotorSpeedMax * vel_ratio / 100
        acc = vel * acc_ratio / 100

        # servo_tx = self.get_servo_tx(EXT_SERVO_IDX)
        # servo_rx = self.get_servo_rx(EXT_SERVO_IDX)
        convert = 1/7200
        sync_mode=False
        if teaching_mode:
            # curr_pos = servo_tx[2]
            tar_pos_cnt = int(target_mm / convert)

            if sync_mode:
                self.set_servo_rx(servo_idx, 0x1f, 0x01, tar_pos_cnt, 0, 0)
            else:
                self.set_servo_rx(servo_idx, 0x3f,0x01, tar_pos_cnt, 0, 0)
                time.sleep(0.01)
                self.set_servo_rx(servo_idx, 0x2f, 0x01, tar_pos_cnt, 0, 0)

        linear_target = {
            "start_mm" : [float(start_mm)],
            "target_mm" : [float(target_mm)],
            "is_absolute" : is_absolute,
            "vel_ratio" : float(vel_ratio),
            "acc_ratio" : float(acc_ratio),
            "teaching_mode" : [teaching_mode]
        }
        # print(f"linear target : {str(linear_target)}")

        return linear_target


    @Utils.exception_handler
    def stop_motion(self, servo_idx):
        print("StopMotion Frome Ethercat_client")
        self.set_servo_rx(servo_idx, 15, 10, 0, 0, 0)
