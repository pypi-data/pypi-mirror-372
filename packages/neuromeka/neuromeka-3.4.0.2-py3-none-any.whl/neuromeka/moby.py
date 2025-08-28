import sys
if sys.version_info >= (3, 9):
    from neuromeka.proto import *
else:
    from neuromeka.proto_step import *
    
from neuromeka.common import *

import grpc, time

MOBY_PORT = 20200


class MobyClient:
    def __init__(self, ip_addr):
        moby_channel = grpc.insecure_channel("{}:{}".format(ip_addr, MOBY_PORT))
        moby_stub = MobyStub(moby_channel)

        self.__moby_stub = moby_stub

    @Utils.exception_handler
    def get_moby_state(self):
        """
        Get Moby State
        -State
        -is_ready
        -is_enable
        -is_moving
        -is_violation
        """
        state_dict = {
            0: "SYSTEM_OFF",
            1: "SYSTEM_ON",
            2: "VIOLATE",
            4: "RECOVER_SOFT",
            6: "IDLE",
            7: "MOVING",
            16: "TELE_OP",
        }
        state = self.__moby_stub.GetMobyState(common_msgs.Empty())
        moby_state = state_dict.get(state.status, "(UNKNOWN STATE CODE)")
        b_ready = state.is_ready
        b_enable = state.is_enable
        b_moving = state.is_moving
        b_violation = state.is_violation

        return {'state': moby_state, 'is_ready': b_ready,
                'is_enable': b_enable, 'is_moving': b_moving, 'is_violation': b_violation}

    @Utils.exception_handler
    def get_moby_error_state(self):
        """
        Get Moby Error State
        """
        error_dict = {
            0x00: "NONE",
            0x01: "SW_MASTER_NOT_OP",
            0x02: "SW_SLAVES_NOT_OP",
            0x04: "SW_SERVO_NOT_ON",
            0x08: "SW_SERVO_NOT_READY",
            0x10: "SW_ENCODER_ABNORMAL",
            0x20: "SW_BUMPER_DETECT",
            0x100: "HW_CONNECTION_LOST",
        }

        err = self.__moby_stub.GetMobyErrorState(common_msgs.Empty())

        return [error_dict.get(err.errorState, "(UNKNOWN ERROR CODE)"),
                err.errorIndex1, err.errorIndex2, err.errorIndex3]

    @Utils.exception_handler
    def recover(self):
        return self.__moby_stub.Recover(common_msgs.Empty())

    @Utils.exception_handler
    def get_moby_pose(self):
        """
        Get Moby pose (m): [Px, Py, Pw]
        """
        pose = self.__moby_stub.GetMobyPose(common_msgs.Empty())
        return [pose.px, pose.py, pose.pw]

    @Utils.exception_handler
    def get_moby_vel(self):
        """
        Get Moby velocity (m/s): [Vx, Vy, Vw]
        """
        vel = self.__moby_stub.GetMobyVel(common_msgs.Empty())
        return [vel.vx, vel.vy, vel.vw]

    @Utils.exception_handler
    def reset_moby_pose(self):
        """
        Reset Moby pose
        """
        return self.__moby_stub.ResetMobyPose(common_msgs.Empty())

    @Utils.exception_handler
    def get_rotation_angle(self):
        """
        Get rotation angle (deg): [fl, fr, bl, br]
        """
        val = self.__moby_stub.GetRotationAngleDeg(common_msgs.Empty())
        return {'fl': val.fl, 'fr': val.fr, 'bl': val.bl, 'br': val.br}

    @Utils.exception_handler
    def get_drive_speed(self):
        """
        Get drive speed (m/s): [fl, fr, bl, br]
        """
        val = self.__moby_stub.GetDriveSpeed(common_msgs.Empty())
        return {'fl': val.fl, 'fr': val.fr, 'bl': val.bl, 'br': val.br}

    @Utils.exception_handler
    def get_target_vel(self):
        """
        Get Moby's target velocity
        """
        target = self.__moby_stub.GetTargetVel(common_msgs.Empty())
        return [target.vx, target.vy, target.vw]

    @Utils.exception_handler
    def get_zero(self):
        """
        Get rotation's zero position (encoder count)
                                    [fl, fr, bl, br]
        """
        val = self.__moby_stub.GetRotationZeroCount(common_msgs.Empty())
        return {'fl': val.fl, 'fr': val.fr, 'bl': val.bl, 'br': val.br}

    @Utils.exception_handler
    def get_gyro_data(self):
        """
        Get Gyro sensor data (yaw, yaw rate)
        """
        return self.__moby_stub.GetGyroData(common_msgs.Empty()).val

    @Utils.exception_handler
    def get_imu_data(self):
        """
        Get Full IMU sensor data
        """
        data = self.__moby_stub.GetGyroFullData(common_msgs.Empty())
        angle = [data.angleX, data.angleY, data.angleZ]
        vel = [data.angleVelX, data.angleVelY, data.angleVelZ]
        acc = [data.linAccX, data.linAccY, data.linAccZ]
        return angle, vel, acc

    @Utils.exception_handler
    def reset_gyro(self):
        """
        Reset gyro sensor
        """
        return self.__moby_stub.ResetGyroSensor(common_msgs.Empty())

    @Utils.exception_handler
    def use_gyro_for_odom(self, use_gyro):
        """
        Use gyro sensor for odometry calculation
        """
        return self.__moby_stub.UseGyroForOdom(moby_msgs.BoolVal(val=use_gyro))

    @Utils.exception_handler
    def get_us_data(self):
        """
        Get US sensor data
        """
        value = self.__moby_stub.GetUSSensorData(common_msgs.Empty())
        return {'front_left1': value.us_front_left1, 'front_left2': value.us_front_left2,
                'front_left3': value.us_front_left3, 'front_ground': value.us_front_ground,
                'front_right1': value.us_front_right1, 'front_right2': value.us_front_right2,
                'front_right3': value.us_front_right3, 'front_right4': value.us_front_right4,
                'back_right1': value.us_back_right1, 'back_right2': value.us_back_right2,
                'back_right3': value.us_back_right3, 'back_ground': value.us_back_ground,
                'back_left1': value.us_back_left1, 'back_left2': value.us_back_left2, 'back_left3': value.us_back_left3,
                'back_left4': value.us_back_left4}

    @Utils.exception_handler
    def get_bms(self):
        """
        Get BMS data
        GreenPyzzle : 
            'BMS status-1', 'BMS status-2',
            'Pack voltage-1', 'Pack voltage-2',
            'Battery Voltage-1', 'Battery Voltage-2',
            'Pack current1-1', 'Pack current1-2', 'Pack current2-1', 'Pack current2-2',
            'Temperature-1', 'Temperature-2', 'Temperature-3', 'Temperature-4'
        CTNS : 
            'Pack voltage-1', 'Pack current1-1
            'Is Charge', 'Is Cell OverVoltage',
            'Is Cell UnderVoltage', 'Is OverCurrent Charge',
            'Is OverCurrent Discharge', 'Is Short Circuit',
            'Is OverTemperature', 'Is Pack OverVoltage',
            'SOC', 'SOH', 'Time for Charge', 'time for Discharge'
            'Remain Capacity Ah', 'Remain Capacity Wh'
            'Temperature-(1~3)', 'Cell Voltage-(1~13)'
        """
        value = self.__moby_stub.GetBMSData(common_msgs.Empty())
        return {'BMS status-1': value.bms_status[0] / 10, 'BMS status-2': value.bms_status[1] / 10,
                'Pack voltage-1': value.pack_volt[0] / 100, 'Pack voltage-2': value.pack_volt[1] / 100,
                'Battery Voltage-1': value.battery_volt[0] / 100, 'Battery Voltage-2': value.battery_volt[1] / 100,
                'Pack current1-1': value.pack_current1[0] / 100, 'Pack current1-2': value.pack_current1[1] / 100,
                'Pack current2-1': value.pack_current2[0] / 100, 'Pack current2-2': value.pack_current2[1] / 100,
                'Is Charge': value.isCharge, 'Is Cell OverVoltage': value.isCellOverVolt,
                'Is Cell UnderVoltage': value.isCellUnderVolt, 'Is OverCurrent Charge': value.isOverCurCharge,
                'Is OverCurrent Discharge': value.isOverCurDischrg, 'Is Short Circuit': value.isShortCircuit,
                'Is OverTemperature': value.isOverTemperature, 'Is Pack OverVoltage': value.isPackOverVolt,
                'SOC': value.SOC * 0.1, 'SOH': value.SOH, 'Time for Charge': value.time_charge,
                'time for Discharge': value.time_dcharge, 'Remain Capacity Ah': value.rem_capAh / 100,
                'Remain Capacity Wh': value.rem_capWh, 'Temperature-1': value.bms_temperature[0] * 0.1,
                'Temperature-2': value.bms_temperature[1] * 0.1, 'Temperature-3': value.bms_temperature[2] * 0.1,
                'Temperature-4': value.bms_temperature[3] * 0.1, 'Cell Voltage-1': value.cell_volt[0] * 0.001,
                'Cell Voltage-2': value.cell_volt[1] * 0.001, 'Cell Voltage-3': value.cell_volt[2] * 0.001,
                'Cell Voltage-4': value.cell_volt[3] * 0.001, 'Cell Voltage-5': value.cell_volt[4] * 0.001,
                'Cell Voltage-6': value.cell_volt[5] * 0.001, 'Cell Voltage-7': value.cell_volt[6] * 0.001,
                'Cell Voltage-8': value.cell_volt[7] * 0.001, 'Cell Voltage-9': value.cell_volt[8] * 0.001,
                'Cell Voltage-10': value.cell_volt[9] * 0.001, 'Cell Voltage-11': value.cell_volt[10] * 0.001,
                'Cell Voltage-12': value.cell_volt[11] * 0.001, 'Cell Voltage-13': value.cell_volt[12] * 0.001}

    @Utils.exception_handler
    def set_target_vel(self, vx, vy, vw):
        """
        Drive control
        """
        return self.__moby_stub.SetStepControl(moby_msgs.TargetVel(vx=vx, vy=vy, vw=vw))

    @Utils.exception_handler
    def stop_motion(self):
        """
        Stop Moby motion
        """
        return self.__moby_stub.StopMotion(common_msgs.Empty())

    @Utils.exception_handler
    def go_straight(self):
        """
        Go straight (zero rotation)
        """
        return self.__moby_stub.SetRotationAngleDeg(moby_msgs.SwerveDoubles(fl=0, fr=0, bl=0, br=0))

    @Utils.exception_handler
    def move_rotation_deg(self, fl, fr, bl, br):
        """
        Rotation control (target angle degree)
        """
        return self.__moby_stub.SetRotationAngleDeg(moby_msgs.SwerveDoubles(fr=fr, br=br, bl=bl, fl=fl))

    @Utils.exception_handler
    def move_driving_mps(self, fl, fr, bl, br):
        """
        Driving control (target speed m/s)
        """
        return self.__moby_stub.DriveWheel(moby_msgs.SwerveDoubles(fr=fr, br=br, bl=bl, fl=fl))

    ############################
    # Set Moby parameters
    ############################

    @Utils.exception_handler
    def set_zero_as_current(self):
        """
        Set current roation position as zero
        """
        return self.__moby_stub.SetZeroPosAsCurrentPos(common_msgs.Empty())

    @Utils.exception_handler
    def set_rotation_vel_acc(self, vel, acc):
        """
        Set rotation maximum velocity, acceleration
        """
        return self.__moby_stub.SetRotationVelAcc(moby_msgs.DoubleVals(val=[vel, acc]))

    @Utils.exception_handler
    def set_rotation_interpolator(self, val):
        """
        Set rotation interpolator
        0: Ramp interpolator
        1: Streaming interpolator
        2: Velocity interpolator
        3: Trapezoidal interpolator
        """
        return self.__moby_stub.SetRotationInterpolator(moby_msgs.IntVal(val=val))

    @Utils.exception_handler
    def set_drive_acc_dec(self, acc, dec):
        """
        Set drive acc dec
        """
        return self.__moby_stub.SetDriveAccDec(moby_msgs.DoubleVals(val=[acc, dec]))

    @Utils.exception_handler
    def set_drive_interpolator_on_off(self, on):
        """
        Set drive interpolator On Off
        """
        return self.__moby_stub.SetDriveInterpolatorOnOff(moby_msgs.BoolVal(val=on))

    @Utils.exception_handler
    def set_rotation_controller_type(self, val):
        """
        Set rotation controller type
        0: HINFPID_CONTROLLER,
        1: SIMPLEPID_POS_CONTROLLER,
        2: SIMPLEPID_VEL_CONTROLLER
        """
        return self.__moby_stub.SetRotationControllerType(moby_msgs.IntVal(val=val))

    @Utils.exception_handler
    def set_rotation_gain(self, index, k, kv, kp):
        """
        Set Rotation Control Gain
        """
        return self.__moby_stub.SetControlParam(moby_msgs.RotationGain(idx=index, k=k, kv=kv, kp=kp))

    @Utils.exception_handler
    def get_rotation_gain(self, index):
        """
        Get Rotation Control Gain (k, kv, kp)
        """
        val = self.__moby_stub.GetControlParam(moby_msgs.IntVal(val=index))
        return {'k': val.k, 'kv': val.kv, 'kp': val.kp}

    @Utils.exception_handler
    def set_kinematics_forced(self, activate, angle):
        """
        Set Kinematics Forced( activate: allow infinite steering, angle: steering error limit to allow wheel driving )
        """
        self.__moby_stub.SetForceKinematics(moby_msgs.ForcedKinematicsData(activate=activate, angle=angle))

    @Utils.exception_handler
    def get_kinematics_forced(self):
        """
        Get Kinematics Forced( on=true, off=false )
        """
        val = self.__moby_stub.GetForceKinematics(common_msgs.Empty())
        return val

    ############################
    # Moby-Agri related commands
    ############################

    @Utils.exception_handler
    def turn_light(self, on):
        return self.__moby_stub.TurnLightOnOff(moby_msgs.BoolVal(val=on))

    @Utils.exception_handler
    def turn_buzzer(self, on):
        return self.__moby_stub.TurnBuzzOnOff(moby_msgs.BoolVal(val=on))

    @Utils.exception_handler
    def pause_bumper(self, on):
        return self.__moby_stub.PauseBumper(moby_msgs.BoolVal(val=on))

    @Utils.exception_handler
    def set_extra_do(self, val):
        return self.__moby_stub.SetExtraDO(moby_msgs.BoolVals(val=val))

    ############################
    # Moby Data logging
    ############################

    @Utils.exception_handler
    def start_rt_logging(self):
        """
        Start RT logging
        """
        return self.__moby_stub.StartRTLogging(common_msgs.Empty())

    @Utils.exception_handler
    def end_rt_logging(self):
        """
        End RT logging
        """
        return self.__moby_stub.EndRTLogging(common_msgs.Empty())
