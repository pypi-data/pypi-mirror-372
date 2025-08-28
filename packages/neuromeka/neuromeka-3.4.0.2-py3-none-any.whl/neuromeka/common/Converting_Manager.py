import json
import os
from pathlib import Path
import netifaces as ni

round_num = 3

tool_data_get = {}
program_tool_data = []
Convert_Modbus = True
Convert_Tool = True

class RobotProgramConverter:
    def __init__(self, input_data, dof):
        self.input_data = input_data
        self.float_val_num = 0
        self.bool_val_num = 0
        self.int_val_num = 0
        self.B_variaable = False
        self.operators = {0: "==", 1: "!=", 2: ">", 3: ">=", 4: "<", 5: "<="}
        self.init_data = input_data
        self.assignment_com  = 3
        self.set_DIO         = 4
        self.set_STOP        = 1
        self.loop_com        = 20
        self.loopBreak_com   = 21
        self.wait_com        = 22
        self.waitfor_com     = 23
        self.if_com          = 24
        self.elif_com        = 25
        self.else_com        = 26
        self.waitfor_di_com  = 28
        self.if_DI           = 29
        self.elif_DI         = 30
        self.set_tool        = 40
        self.home_com        = 100
        self.joint_absoulte  = 102
        self.task_absoulte   = 103
        self.joint_relative  = 104
        self.task_relative   = 105
        self.group           = 200
        self.pick            = 201
        self.place           = 202
        self.robot_dof       = dof

    def get_joint_A_motion(self, name, data,enable):
        for move in data["moveList"]:
            if move["name"] == name:
                move_vel = move["boundary"]["velLevel"]
                move_acc = move["boundary"]["accLevel"]
                shif_value = move["refFrame"]["tref"]
                move_data = {
                    "cmd": "MoveJ",
                    "name": name,
                    "wait_finish": True,
                    "base_type": "ABSOLUTE",
                    "interpolator_type": "VELOCITY",
                    "vel_ratio": move_vel*10,
                    "acc_ratio": move_acc*10,
                    "coll_sens_level": 3,
                    "blending": {"type": "NONE"},
                    "shift": [0]*self.robot_dof,
                    "shift_base": "RELATIVE",
                    "offsets": [[0]*self.robot_dof]*len(move["wpList"]),
                    "waypoint_time": [2, 2],
                    "waypoint_active": [],
                    "waypoints": [],
                    "active":enable
                }

                for waypoint in move["wpList"]:
                    try:
                        move_data["waypoint_active"].append(enable)
                        round_position = [round(position, round_num) for position in data["wpList"][waypoint["id"]]["q"]]
                        move_data["waypoints"].append(round_position)
                    except Exception as e:
                        print(e)
                return move_data

    def get_task_A_motion(self,name, data, enable):
        for move in data["moveList"]:
            if move["name"] == name:
                move_vel = move["boundary"]["velLevel"]
                move_acc = move["boundary"]["accLevel"]
                shif_value =[x * 1000 if i<3 else x for i,x in enumerate(move["refFrame"]["tref"])]
                move_data = {
                    "cmd": "MoveL",
                    "name": name,
                    "wait_finish": True,
                    "base_type": "ABSOLUTE",
                    "interpolator_type": "VELOCITY",
                    "vel_ratio": move_vel*10,
                    "acc_ratio": move_acc*10,
                    "coll_sens_level": 3,
                    "blending": {"type": "NONE"},
                    "shift": shif_value,
                    "shift_base": "RELATIVE",
                    "offsets": [[0]*self.robot_dof]*len(move["wpList"]),
                    "waypoint_time": [2, 2],
                    "waypoint_active": [],
                    "waypoints": [],
                    "waypoints_joint": [],
                    "active":enable
                }

                for waypoint in move["wpList"]:
                    try:
                        move_data["waypoint_active"].append(enable)
                        converting_point = [x * 1000 if i<3 else x for i,x in enumerate(data["wpList"][waypoint["id"]]["p"])]
                        round_position = [round(position, round_num) for position in converting_point]
                        round_joint_pos = [round(position, round_num) for position in data["wpList"][waypoint["id"]]["q"]]
                        move_data["waypoints"].append(round_position)
                        move_data["waypoints_joint"].append(round_joint_pos)
                    except Exception as e:
                        print(e)
                return move_data

    def get_joint_R_motion(self,name, data, enable):
        for move in data["moveList"]:
            if move["name"] == name:
                move_vel = move["boundary"]["velLevel"]
                move_acc = move["boundary"]["accLevel"]
                move_data = {
                    "cmd": "MoveJ",
                    "name": name,
                    "wait_finish": True,
                    "base_type": "RELATIVE",
                    "interpolator_type": "VELOCITY",
                    "vel_ratio": move_vel*10,
                    "acc_ratio": move_acc*10,
                    "coll_sens_level": 3,
                    "blending": {"type": "NONE"},
                    "shift": [0]*self.robot_dof,
                    "shift_base": "RELATIVE",
                    "offsets": [[0]*self.robot_dof]*len(move["wpList"]),
                    "waypoint_time": [2, 2],
                    "waypoint_active": [],
                    "waypoints": [],
                    "waypoints_origin": [],
                    "active":enable
                }

                for waypoint in move["wpList"]:
                    try:
                        move_data["waypoint_active"].append(enable)
                        round_position = [round(position, round_num) for position in data["wpList"][waypoint["id"]]["q"]]
                        round_origin = [round(position, round_num) for position in move["wpListOrigin"][0]["startPose"]["q"]]
                        move_data["waypoints"].append(round_position)
                        move_data["waypoints_origin"].append(round_origin)
                    except Exception as e:
                        print(e)
                return move_data

    def get_task_R_motion(self,name, data, enable):
        for move in data["moveList"]:
            if move["name"] == name:
                move_vel = move["boundary"]["velLevel"]
                move_acc = move["boundary"]["accLevel"]
                move_data = {
                    "cmd": "MoveL",
                    "name": name,
                    "wait_finish": True,
                    "base_type": "RELATIVE",
                    "interpolator_type": "VELOCITY",
                    "vel_ratio": move_vel*10,
                    "acc_ratio": move_acc*10,
                    "coll_sens_level": 3,
                    "blending": {"type": "NONE"},
                    "shift": [0,0,0,0,0,0],
                    "shift_base": "RELATIVE",
                    "offsets": [[0,0,0,0,0,0]]*len(move["wpList"]),
                    "waypoint_time": [2, 2],
                    "waypoint_active": [],
                    "waypoints": [],
                    "waypoints_origin": [],
                    "waypoints_joint": [],
                    "active":enable
                }

                for waypoint in move["wpList"]:
                    try:
                        converting_point = [x * 1000 if i<3 else x for i,x in enumerate(data["wpList"][waypoint["id"]]["p"])]
                        move_data["waypoints"].append(converting_point)
                        move_data["waypoint_active"].append(enable)
                        converting_origin = [x * 1000 if i<3 else x for i,x in enumerate(move["wpListOrigin"][0]["startPose"]["p"])]
                        move_data["waypoints_origin"].append(converting_origin)
                        move_data["waypoints_joint"].append(move["wpListOrigin"][0]["startPose"]["q"])
                        move_data["waypoints_joint"].append(move["wpListOrigin"][0]["endPose"]["q"])
                    except Exception as e:
                        print(e)
                return move_data

    def home_motion(self,data):
        move_data = {
            "cmd":"MoveHome",
            "vel_ratio":25,
            "acc_ratio":100,
            "active":data['enable']
        }
        return move_data

    def set_variable(self,data):
        set_data = []
        for i in range (len(data["varList"])):
            cur_name = data["varList"][i]["name"]
            if cur_name[0] == 'M':
                cur_name +='_WRITE'
            cur_value = data["varList"][i]["value"]
            set_data.append(str(cur_name)+" := "+str(cur_value))
        move_data = {
            "cmd":"SetVar",
            "active":data['enable'],
            "fold":False,
            "expression":set_data
        }
        return move_data

    def wait_command(self,data):
        cur_time = data["time"]
        move_data = {
            "cmd":"Sleep",
            "condition":{
                "type":"TIME",
                "time":cur_time
            },
            "async_sleep":False,
            "active":data['enable']
        }
        return move_data

    def loop_command(self,data):
        cur_count = data["count"]
        cur_id = data["id"]
        move_data = {
            "cmd":"Loop",
            "count":cur_count,
            "active":data['enable'],
            "fold":False,
            "children":[],
            "id":cur_id
        }
        return move_data

    def loop_break_command(self,data):
        move_data = {
            "cmd":"Break",
            "active":data['enable']
        }
        return move_data

    def wait_for_command(self,data):
        right_value = data["cond"]["right"]["value"]
        left_value = data["cond"]["left"]["value"]
        if left_value[0] == 'M':
            left_value +='_READ'
        op_value = data["cond"]["op"]
        expression = str(left_value)+self.operators[op_value]+str(right_value)
        move_data = {
            "cmd":"Sleep",
            "condition":{
                "type":"EXPRESSION",
                "expression":expression
            },
            "async_sleep":False,
            "active":data['enable']
        }
        return move_data

    def wait_for_di_command(self,data):
        condition = data["diList"]
        expresion = "("
        start = 0
        for cond in condition:
            ONOFF = "True"
            if start != 0:
                expresion+=(" and ")
            if cond["value"] == 0:
                ONOFF = "False"
            expresion+=("dinBoard["+str(cond["idx"])+"] == "+ ONOFF)
            start +=1
        expresion+=" )"
        ID = data["id"]

        move_data = {
            "cmd":"Sleep",
            "condition": {
                "type":"EXPRESSION",
                "expression":expresion,
            },
            "async_sleep":False,
            "active":data['enable']
        }
        return move_data

    def pick_place_command(self,data):
        work_type = "PICK"
        if data["type"] == 202:
            work_type = "PLACE"

        target_vel = data["target"]["boundary"]["velLevel"]
        target_acc = data["target"]["boundary"]["accLevel"]

        approach_vel = data["approach"]["boundary"]["velLevel"]
        approach_type = data["approach"]["direction"]
        approach_distance = data["approach"]["distance"]*1000

        retract_vel = data["approach"]["boundary"]["velLevel"]
        retract_type = data["retract"]["direction"]
        retract_distance = data["retract"]["distance"]*1000

        converting_point = [x * 1000 if i<3 else x for i,x in enumerate(data["target"]["point"]["p"])]
        target_pos_j = data["target"]["point"]["q"]
        move_data = {
            "cmd":"PickPlace",
            "work_type":work_type,
            "payload":0,
            "payload_set_tcp":False,
            "tar_pos":converting_point,
            "waypoints_joint":target_pos_j,
            "approach_pos":[0]*self.robot_dof,
            "retract_pos":[0]*self.robot_dof,
            "async_sleep":False,
            "vel_level":target_vel,
            "acc_level":target_acc,
            "vision_target":"None",
            "coll_sens_level":3,
            "approach_vel_level":approach_vel,
            "retract_vel_level":retract_vel,
            "approach_condition":{
                "type":"Constant",
                "value":True
            },
            "approach_check_cycle":0,
            "approach_wait_time":0,
            "retract_condition":{
                "type":"Constant",
                "value":True
            },
            "retract_check_cycle":0,
            "retract_wait_time":0,
            "active":data['enable'],
            "fold":False
        }
        move_data["approach_pos"][2]
        if approach_type <=1:
            if approach_type%2==1:
                move_data["approach_pos"][2] = -approach_distance
            else:
                move_data["approach_pos"][2] = approach_distance
        elif approach_type <=3:
            if approach_type%2==1:
                move_data["approach_pos"][0] = -approach_distance
            else:
                move_data["approach_pos"][0] = approach_distance
        elif approach_type <=5:
            if approach_type%2==1:
                move_data["approach_pos"][1] = -approach_distance
            else:
                move_data["approach_pos"][1] = approach_distance

        if retract_type <=1:
            if retract_type%2==1:
                move_data["retract_pos"][2] = -retract_distance
            else:
                move_data["retract_pos"][2] = retract_distance
        elif retract_type <=3:
            if retract_type%2==1:
                move_data["retract_pos"][0] = -retract_distance
            else:
                move_data["retract_pos"][0] = retract_distance
        elif retract_type <=5:
            if retract_type%2==1:
                move_data["retract_pos"][1] = -retract_distance
            else:
                move_data["retract_pos"][1] = retract_distance

        return move_data

    def if_command(self,data):
        right_value = data["cond"]["right"]["value"]
        left_value = data["cond"]["left"]["value"]
        if left_value[0] == 'M':
            left_value +='_READ'
        op_value = data["cond"]["op"]
        expression = str(left_value)+self.operators[op_value]+str(right_value)
        id = data["id"]
        move_data = {
            "cmd":"If",
            "condition":{
                "type":"Expression",
                "expression":expression
            },
            "active":data['enable'],
            "fold":False,
            "children":[],
            "id": id
        }
        return move_data

    def elif_command(self,data):
        right_value = data["cond"]["right"]["value"]
        left_value = data["cond"]["left"]["value"]
        if left_value[0] == 'M':
            left_value +='_READ'
        op_value = data["cond"]["op"]
        expression = str(left_value)+self.operators[op_value]+str(right_value)
        id = data["id"]
        move_data = {
            "cmd":"ElseIf",
            "condition":{
                "type":"Expression",
                "expression":expression
            },
            "active":data['enable'],
            "fold":False,
            "children":[],
            "id": id
        }
        return move_data

    def else_command(self,data):
        id = data["id"]
        move_data = {
            "cmd":"Else",
            "active":data['enable'],
            "fold":False,
            "children":[],
            "id": id
        }
        return move_data

    def if_dio_command(self,data):
        condition = data["diList"]
        expresion = "("
        start = 0
        for cond in condition:
            ONOFF = "True"
            if start != 0:
                expresion+=(" and ")
            if cond["value"] == 0:
                ONOFF = "False"
            expresion+=("dinBoard["+str(cond["idx"])+"] == "+ONOFF)
            start +=1
        expresion+=" )"
        ID = data["id"]
        move_data = {
            "cmd":"If",
            "condition": {
                "type":"Expression",
                "expression":expresion,
            },
            "active":data['enable'],
            "fold":False,
            "children":[],
            "id":ID
        }
        return move_data

    def elif_dio_command(self,data):
        condition = data["diList"]
        expresion = "("
        start = 0
        for cond in condition:
            ONOFF = "True"
            if start != 0:
                expresion+=(" and ")
            if cond["value"] == 0:
                ONOFF = "False"
            expresion+=("dinBoard["+str(cond["idx"])+"] == "+ ONOFF)
            start +=1
        expresion+=" )"
        ID = data["id"]
        move_data = {
            "cmd":"ElseIf",
            "condition": {
                "type":"Expression",
                "expression":expresion,
            },
            "active":data['enable'],
            "fold":False,
            "children":[],
            "id":ID
        }
        return move_data

    def group_command(self,data):
        name = data["groupName"]
        id = data["id"]
        move_data = {
            "cmd":"Group",
            "name": name,
            "active":data['enable'],
            "fold":False,
            "children":[],
            "id": id
        }
        return move_data

    def add_child_to_program(self,program_data, target_id, new_child):
        for item in program_data:
            if 'id' in item and item['id'] == target_id:
                item.setdefault('children', []).append(new_child)
            elif 'children' in item and item['children']:
                # Recursively check in the children
                updated_children = self.add_child_to_program(item['children'], target_id, new_child)
                if updated_children is not None:
                    item['children'] = updated_children
                    program_data
        return program_data

    def set_DIO_command(self,data) :
        do_list = data["doList"]
        converted_do_list = [{"address": item["idx"], "state": item["value"]} for item in do_list]
        move_data = {
            "cmd":"SetSignals",
            "do_signals":converted_do_list
        }
        return move_data
    def set_STOP_command(self,data) :
        move_data = {
            "cmd":"QuitProgram",
            "active":data['enable']
        }
        return move_data

    def set_Tool(self,data):
        try:            
            tool_num = str(data["toolCmd"]["toolId"])+"_"+str(data["toolCmd"]["cmdId"])
            tool_name = tool_data_get[tool_num]
        except:
            tool_name = "0_0"

        if tool_num in modbus_tool_ID:
            for dictionary in modbus_tool:
                if 'ID' in dictionary and dictionary['ID'] == tool_num:
                    break

            set_data = []
            for send_modbus in dictionary['value']:
                cur_name = send_modbus['name']
                cur_name +='_WRITE'
                cur_value = send_modbus["value"]
                set_data.append(str(cur_name)+" := "+str(cur_value))
            tool_data = {
                "cmd":"SetVar",
                "active":data['enable'],
                "fold":False,
                "expression":set_data
            }
        else:
            tool_data = {
                "cmd":"SetTool",
                "tool_name":tool_name,
                "active":data['enable']
            }
        return tool_data



    def convert_motion(self,robot_ip_address):
        input_data = self.init_data
        float_val_num = 0
        bool_val_num = 0
        int_val_num = 0
        B_variaable = False
        robot_ip = robot_ip_address
        output_data = {
            "Program": [
                {"cmd": "CollisionConfig", "policy": "PAUSE", "duration": 0},
                {"cmd": "VisionConfig"},
                {"cmd": "VariableConfig",
                 "local_list": [],
                 "modbus_list": [
                     {
                         "server_name":"my_robot_local",
                         "server_ip":"127.0.0.1",
                         "server_port":502,
                         "variable_list":[]
                     },
                     {
                         "server_name":"my_robot_ip",
                         "server_ip":robot_ip,
                         "server_port":502,
                         "variable_list":[]
                     }
                 ]
                 }
            ]
        }
        for val in input_data["program"][0]["toolInfo"]:
            program_tool_data.append(val)


        for val in input_data["program"][1]["varList"]: # 변수등록
            if val["name"][0] == 'B' and val["type"] == 5:
                B_variaable = True
                output_data["Program"][2]["local_list"].append(["INT",val["name"],int(''.join(filter(str.isdigit, val["name"]))),"LOCAL"])
            if val["name"][0] == 'M' and val["type"] == 5:
                output_data["Program"][2]["modbus_list"][1]["variable_list"].append(["WRITE_REGISTER",val["name"]+"_WRITE",int(''.join(filter(str.isdigit, val["name"]))),"LOCAL"])
                output_data["Program"][2]["modbus_list"][0]["variable_list"].append(["READ_REGISTER",val["name"]+"_READ",int(''.join(filter(str.isdigit, val["name"]))),"LOCAL"])
            if val["type"] == 2:  #float 변수
                output_data["Program"][2]["local_list"].append(["FLOAT",val["name"],float_val_num,"LOCAL"])
                float_val_num+=1
            if val["type"] == 3:  #boolean 변수
                output_data["Program"][2]["local_list"].append(["BOOL",val["name"],bool_val_num,"LOCAL"])
                bool_val_num+=1

        for val in input_data["program"][1]["varList"]: # 변수등록
            if B_variaable == False and val["type"] == 1:
                output_data["Program"][2]["local_list"].append(["INT",val["name"],int_val_num,"LOCAL"])
                int_val_num +=1

        for cur_program in input_data["program"]:
            if cur_program["type"] == 999:
                continue
            elif cur_program["type"] == 2:
                continue

            elif cur_program["type"] == self.assignment_com:
                return_data = self.set_variable(cur_program)

            elif cur_program["type"] == self.set_DIO:
                return_data = self.set_DIO_command(cur_program)

            elif cur_program["type"] == self.set_STOP:
                return_data = self.set_STOP_command(cur_program)

            elif cur_program["type"] == self.if_DI:
                return_data = self.if_dio_command(cur_program)
            elif cur_program["type"] == self.elif_DI:
                return_data = self.elif_dio_command(cur_program)
            elif cur_program["type"] == self.set_tool:
                return_data = self.set_Tool(cur_program)
            elif cur_program["type"] == self.waitfor_di_com:
                return_data = self.wait_for_di_command(cur_program)

            elif cur_program["type"] == self.loop_com:
                return_data = self.loop_command(cur_program)

            elif cur_program["type"] == self.loopBreak_com:
                return_data = self.loop_break_command(cur_program)

            elif cur_program["type"] == self.wait_com:
                return_data = self.wait_command(cur_program)
            elif cur_program["type"] == self.waitfor_com:
                return_data = self.wait_for_command(cur_program)
            elif cur_program["type"] == self.if_com:
                return_data = self.if_command(cur_program)

            elif cur_program["type"] == self.elif_com:
                return_data = self.elif_command(cur_program)
            elif cur_program["type"] == self.else_com:
                return_data = self.else_command(cur_program)

            elif cur_program["type"] == self.home_com:
                return_data = self.home_motion(cur_program)
            elif cur_program["type"] == self.joint_absoulte:
                name = cur_program["name"]
                return_data = self.get_joint_A_motion(name,input_data,cur_program['enable'])
            elif cur_program["type"] == self.task_absoulte:
                name = cur_program["name"]
                return_data = self.get_task_A_motion(name,input_data,cur_program['enable'])
            elif cur_program["type"] == self.joint_relative:
                name = cur_program["name"]
                return_data = self.get_joint_R_motion(name,input_data,cur_program['enable'])
            elif cur_program["type"] == self.task_relative:
                name = cur_program["name"]
                return_data = self.get_task_R_motion(name,input_data,cur_program['enable'])
            elif cur_program["type"] == self.group:
                return_data = self.group_command(cur_program)
            elif cur_program["type"] == self.pick:
                return_data = self.pick_place_command(cur_program)
            elif cur_program["type"] == self.place:
                return_data = self.pick_place_command(cur_program)

            else:
                return_data = [0,0,0,0]
            if cur_program["pId"] != 0:
                return_d =self.add_child_to_program(output_data["Program"],cur_program["pId"],return_data)
                output_data["Program"] = return_d
                continue
            else:
                output_data["Program"].append(return_data)
        return json.dumps(output_data, ensure_ascii=False)


if __name__ == "__main__":    
    current_working_directory = os.getcwd()+"/"

    files = [f for f in os.listdir('.') if os.path.isfile(f) and f.endswith('.json')]
    if not files:
        print("No JSON files found in the directory.")
    for i, file in enumerate(files):
        print(f"{i + 1}: {file}")
    file_index = int(input("Choose a file by entering its number: ")) - 1
    input_name = files[file_index]
    parts = input_name.split('.')
    if len(parts) < 3:
        print("File name format is incorrect.")
    before_robot_name = parts[-2]
    if before_robot_name in ["7","12","7v2","12v2"]:
        robot_dof = 6
    if before_robot_name in["rp2","rp2v2"]:
        if before_robot_name.startswith("rp"):
            before_robot_name  = before_robot_name.replace("rp", "RP", 1)
        robot_dof = 7
    robot_name = "indy"+before_robot_name    
    try:
        robot_ip = ni.ifaddresses('eth1')[ni.AF_INET][0]['addr']
    except:
        robot_ip = input("Enter the Robot IP Address: ")
    converting_name = input("Enter the output file name (without extension): ")    

    if Convert_Modbus:
        ipadress = robot_ip
        inputlocal = {'name': 'my_robot_local', 'ip': '127.0.0.1', 'port': 502}
        inputip = {'name': 'my_robot_ip', 'ip':ipadress, 'port': 502}
        try:
            with open("/home/user/release/IndyConfigurations/Cobot/Params/Modbus.json","r") as file:
                modbusdata = json.load(file)
            modbus_local = False
            modbus_ip = False

            for i in modbusdata['modbus_servers']:
                if i['name'] == 'my_robot_local':
                    modbus_local = True
                if i['name'] == 'my_robot_ip':
                    modbus_ip = True
                    if i['ip'] != ipadress:
                        i['ip']=ipadress
            if modbus_local == False:
                modbusdata['modbus_servers'].append(inputlocal)
            if modbus_ip == False:
                modbusdata['modbus_servers'].append(inputip)
            write_data = json.dumps(modbusdata)

            with open("/home/user/release/IndyConfigurations/Cobot/Params/Modbus.json", "w") as output_file:
                output_file.write(write_data)
        except:
            send_data = {"modbus_servers": []}
            send_data['modbus_servers'].append(inputlocal)
            send_data['modbus_servers'].append(inputip)
            write_data = json.dumps(send_data)
            with open("/home/user/release/IndyConfigurations/Cobot/Params/Modbus.json", "w") as output_file:
                output_file.write(write_data)

    if Convert_Tool:    
        with open(current_working_directory+input_name, "r") as file:
            input_data = json.load(file)

        for val in input_data["program"][0]["toolInfo"]:
            program_tool_data.append(val)
        convert_tool_data = {
            "tools": []
        }

        tool_idx = 0
        tool_subidx = 0


        modbus_tool=[]
        modbus_tool_ID=[]
        for tool_data in program_tool_data:
            for tool in tool_data['toolCommand']:
                append_data = {}
                tool_name = tool_data["name"] + "_" + tool["name"]
                tool_data_get[str(tool_idx)+"_"+str(tool_subidx)] = tool_name
                append_data["name"] = tool_name
                append_data["execute_time"] = tool["postwait"]
                append_data["do_signals"] = []
                append_data["enddo_signals"] = []
                append_data["ao_signals"] = []
                append_data["endao_signals"] = []
                append_data["expression"] = []

                if tool['commType'] == 4:
                    modbus_tool.append({"ID":str(tool_idx)+"_"+str(tool_subidx),"value": tool['varList']})
                    modbus_tool_ID.append(str(tool_idx)+"_"+str(tool_subidx))
                else:
                    if tool['commType'] == 1:
                        for do in tool["doMap"]:
                            append_data["do_signals"].append({"address": do["idx"], "state": do["value"]})

                    if tool['commType'] == 6:
                        tool_state = 2*(tool["endToolDO"]["toolType"]+1)*(tool["endToolDO"]["value"]-0.5)
                        append_data["enddo_signals"].append({"port":"C","states":[int(tool_state)]})
                    
                    convert_tool_data["tools"].append(append_data)
                    tool_subidx +=1
            tool_idx +=1
            tool_subidx = 0


        write_data = json.dumps(convert_tool_data)
        with open("/home/user/release/IndyConfigurations/Cobot/Configs/ToolList.json", "w") as output_file:
            output_file.write(write_data)


    with open(current_working_directory+input_name, "r") as file:
        input_data = json.load(file)

    converter = RobotProgramConverter(input_data, robot_dof)
    converted_program = converter.convert_motion(robot_ip)

    with open("/home/user/release/IndyDeployment/ProgramScripts/"+converting_name+"."+robot_name+".json", "w") as output_file:
        output_file.write(converted_program)


    print("converting_finish")