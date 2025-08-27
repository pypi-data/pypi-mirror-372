import sys
from ktoolkits.io.console import IOStream
from ktoolkits.formatting_utils import colored
from ktoolkits.client.base_api import BaseApi
from typing import Dict,Union, Generator, Optional, Callable, Any

from ktoolkits.common.constants import KTOOL_AGENT_LIST

class Chat(BaseApi):

    @classmethod
    def role(cls,
               role,
               **kwargs) -> str:
        
        response =  super().role(role)

        return response.output
    
    @classmethod
    def create_agent(cls,
                     agent_name: str,
                     api_key: str = None,
                     **kwargs):
        response = super().create_agent(agent_name,api_key,**kwargs)
        agent_uuid = super()._get_task_id(response)
        return agent_uuid
    
    @classmethod
    def create_agent_tool(cls, 
                          agent_uuid: str = None, 
                          tool_uuid: str = None, 
                          api_key: str = None, 
                          **kwargs) -> str:
        
        return super().create_agent_tool(agent_uuid, tool_uuid, api_key, **kwargs)
    
    @classmethod
    def chat_to(cls,
              message: str,
              recipient: str = "渗透测试专家",
              **kwargs) -> Union[dict, Generator]:
        """
        :param message: 任务内容
        :param recipient: AI智能体名称
        :param stream: 流式模式
        :return:
        """
        if recipient not in KTOOL_AGENT_LIST:
            sys.exit(f"请输入正确的智能体名称，当前支持的智能体仅有:" + " ".join(KTOOL_AGENT_LIST))

        response = super().chat(message, recipient)
        #is_stream = kwargs.get('stream', True)

        result = []

        for item in response:
            cls._print_received_message(item)
            result.append(item)

        return result


    @classmethod
    def instantiate(
        cls,
        template: Optional[Union[str, Callable[[Dict[str, Any]], str]]],
        context: Optional[Dict[str, Any]] = None,
        allow_format_str_template: Optional[bool] = False,
    ) -> Optional[str]:
        if not context or template is None:
            return template  # type: ignore [return-value]
        if isinstance(template, str):
            return template.format(**context) if allow_format_str_template else template
        return template(context)

    @classmethod
    def _print_received_message(cls, message: Union[Dict, str],chat_header: bool = True):
        iostream = IOStream.get_default()
        # print the message received
        sender    = message.get("sender")
        recipient = message.get("recipient") 
        if "message" in message:
            messageObj = message["message"]
        else:
            messageObj = message

        if chat_header:
            iostream.print(colored(sender, "yellow"), "(to", f"{recipient}):\n", flush=True)
        
        if isinstance(messageObj,dict) and messageObj.get("tool_responses"):  # Handle tool multi-call responses
            for tool_response in messageObj["tool_responses"]:
                cls._print_received_message(tool_response,chat_header=False)
            if messageObj.get("role") == "tool":
                return  # If role is tool, then content is just a concatenation of all tool_responses

        if isinstance(messageObj,dict) and messageObj.get("role") in ["function", "tool"]:
            if messageObj["role"] == "function":
                id_key = "name"
            else:
                id_key = "tool_call_id"
            id = messageObj.get(id_key, "No id found")
            func_print = f"***** Response from calling {messageObj['role']} ({id}) *****"
            iostream.print(colored(func_print, "green"), flush=True)
            iostream.print(messageObj["content"], flush=True)
            iostream.print(colored("*" * len(func_print), "green"), flush=True)
        else:
            if isinstance(messageObj, str):
                iostream.print(messageObj, flush=True)
            if "function_call" in messageObj and messageObj["function_call"]:
                function_call = dict(messageObj["function_call"])
                func_print = (
                    f"***** Suggested function call: {function_call.get('name', '(No function name found)')} *****"
                )
                iostream.print(colored(func_print, "green"), flush=True)
                iostream.print(
                    "Arguments: \n",
                    function_call.get("arguments", "(No arguments found)"),
                    flush=True,
                    sep="",
                )
                iostream.print(colored("*" * len(func_print), "green"), flush=True)
            if "tool_calls" in messageObj and messageObj["tool_calls"]:
                for tool_call in messageObj["tool_calls"]:
                    id = tool_call.get("id", "No tool call id found")
                    function_call = dict(tool_call.get("function", {}))
                    func_print = f"***** Suggested tool call ({id}): {function_call.get('name', '(No function name found)')} *****"
                    iostream.print(colored(func_print, "green"), flush=True)
                    iostream.print(
                        "Arguments: \n",
                        function_call.get("arguments", "(No arguments found)"),
                        flush=True,
                        sep="",
                    )
                    iostream.print(colored("*" * len(func_print), "green"), flush=True)

        iostream.print("\n", "-" * 80, flush=True, sep="")




