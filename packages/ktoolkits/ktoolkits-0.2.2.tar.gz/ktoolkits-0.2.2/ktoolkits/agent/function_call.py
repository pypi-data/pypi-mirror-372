import json
import sys
from ktoolkits.client.base_api import BaseApi
from ktoolkits.client.base_api import GetMixin
from typing import Union,Dict,List,Optional,Any

class FunctionCall(BaseApi):

    @classmethod
    def create_tool(cls,tool_name: str, api_key: str = None, agent_uuid: str=None) -> Optional[Dict[str, Any]]:

        api_reponse = GetMixin.get(path="tool", api_key=api_key, params={"tool_name":tool_name})

        if api_reponse.status_code != 200:
            return None
        else:
            result = {}
            result["tool_name"] = api_reponse.output.get("tool_name")
            result["tool_args"] = cls._get_args_name(api_reponse.output.get("input_parameters"))
            result["tool_func"] = cls._create_function(tool_name,result["tool_args"],agent_uuid)
            result["tool_desc"] = api_reponse.output.get("description")
            return result
    
    @classmethod
    def _get_args_name(cls, input_parameters: str)-> List[str]:
        argsJson = json.loads(input_parameters)
        args_list =[]
        for item in argsJson:
            args_name = item.get("name")
            args_list.append(args_name)
        return args_list
    @classmethod
    def _create_function(cls, tool_name: str, tool_args: List[str], agent_uuid: Optional[str] = None):

        func_name = f"k_function_{tool_name}"

        args_names = tool_args

        args_types = []
        for _ in args_names:
            args_types.append(str)

        input_param = ""
        input_param += "{"

        for item in args_names:
            #todo: two params
            input_param += f"'{item}':{item},"

        input_param = input_param[:-1]
        input_param += "}"

        #args_types = [Union[str,Dict[str,str]],str]

        body = f"""
        import ktoolkits as ktool
        a = ktool.Runner.call(
                tool_name='{tool_name}',
                tool_input={input_param},
                agent_uuid='{agent_uuid}',
            )

        output = a.output

        tool_uuid = output.get('task_id')
        tool_output = output.get('task_output')

        if '{agent_uuid}' != None:
            try:
                a = ktool.Agent.create_agent_tool(
                    agent_uuid='{agent_uuid}',
                    tool_uuid= tool_uuid,
                )
            except Exception as e:
                pass

        if output:
            return tool_output
        else:
            return a.message
        """
        return_type = "str"

        return cls._create_dynamic_function(func_name,args_names,args_types,body,return_type)

    @classmethod
    def _create_dynamic_function(cls,func_name,args_names,arg_types,body, return_type):
        def get_type_annotation(type_):
            if hasattr(type_, '__origin__') and type_.__origin__ is Union:
                # 处理 Union 类型
                return f"Union[{', '.join(get_type_annotation(t) for t in type_.__args__)}]"
            elif isinstance(type_, type):
                return type_.__name__
            else:
                return str(type_)
        # 构建参数列表，包括类型注解
        params_with_annotations = ', '.join(f"{args_name}: {get_type_annotation(arg_type)}" for args_name, arg_type in zip(args_names, arg_types))
        # 构建函数定义字符串
        func_def = f"def {func_name}({params_with_annotations}) -> {get_type_annotation(return_type)}:\n{body}"
        # 创建一个新的命名空间
        namespace = {}
        # 将 typing 模块添加到命名空间
        import typing
        namespace['typing'] = typing
        exec(func_def, globals(), namespace)
        
        # 从命名空间获取新定义的函数
        new_func = namespace[func_name]
        
        return new_func