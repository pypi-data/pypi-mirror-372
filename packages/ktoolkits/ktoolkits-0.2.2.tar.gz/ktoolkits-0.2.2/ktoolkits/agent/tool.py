#coding=utf-8
import sys

from http import HTTPStatus

from ktoolkits.client.toolbox_api import ToolboxApi

from ktoolkits.agent.sandbox import Sandbox
from ktoolkits.api_entities.ktool_response import KToolAPIResponse
from ktoolkits.models.sandbox import SandboxInfo,SandboxInstance

from typing import Optional

class Tool(ToolboxApi):

    @classmethod
    def create_sandbox(cls,
                    name: str = "",
                    image: str="registry.cn-hangzhou.aliyuncs.com/kservice/kigo-kali",
                    version: str="0.1",
                    **kwargs) -> Optional[Sandbox]:
        
        try:

            if name =="":
                raise Exception("Sandbox Name Required")

            api_response = ToolboxApi._create_sandbox(name=name,
                                                      image=image,
                                                      version=version,
                                                      **kwargs)

            sandbox_id = ToolboxApi._get_sandbox_id(api_response)

            if sandbox_id is None:
                raise Exception(f"Create Sandbox Error: {name}")

            sandbox = cls.get_current_sandbox()

            return sandbox

        except Exception as e:
            print(str(e))
            raise e


    @classmethod
    def get_current_sandbox(cls,**kwargs):
        
        api_response = ToolboxApi._get_sandbox(**kwargs)

        try:
            if isinstance(api_response, KToolAPIResponse) and api_response.status_code == HTTPStatus.OK:
                    
                output = api_response.output

                sandbox_id =None
                
                if 'sandbox_id' in output:
                    sandbox_id = output['sandbox_id']
                    if sandbox_id is None:
                        raise Exception(f"No Available Sandbox")
                
                if 'image' in output:
                    image = output['image']
                else:
                    image = ""

                if 'webapp_addr' in output:
                    webapp_addr = output['webapp_addr']
                else:
                    webapp_addr = ""

                if 'mcpapp_addr' in output:
                    mcpapp_addr = output['mcpapp_addr']
                else:
                    mcpapp_addr = ""
                

                if 'webapp_pass' in output:
                    webapp_pass = output['webapp_pass']
                else:
                    webapp_pass = ""
                
                if 'auto_stop_interval' in output:
                    auto_stop_interval = output['auto_stop_interval']
                else:
                    #default: 5min
                    auto_stop_interval = 5

                sandbox_info = SandboxInfo()

                sandbox_info.id = sandbox_id
                sandbox_info.image = image
                sandbox_info.webapp_addr = webapp_addr
                sandbox_info.mcpapp_addr = mcpapp_addr
                sandbox_info.webapp_pass = webapp_pass
                sandbox_info.auto_stop_interval = auto_stop_interval

                sandbox_inst = SandboxInstance()

                sandbox_inst.info = sandbox_info

                sandbox = Sandbox(sandbox_id, sandbox_inst, ToolboxApi)

                return sandbox
            
            else:
                raise Exception(api_response.message)
        
        except Exception as e:
            print(str(e))
            raise e

    @classmethod
    def get_current_sandbox_by_name(cls,
                        name: str,
                        **kwargs) -> Optional[Sandbox]:
        
        api_response = ToolboxApi._get_sandbox_by_name(name=name,
                                                       **kwargs)
        
        print(api_response)
        
        try:
            if isinstance(api_response, KToolAPIResponse) and api_response.status_code == HTTPStatus.OK:
                    
                output = api_response.output
                print(api_response)
                if 'sandbox_id' in output:
                    sandbox_id = output['sandbox_id']
                    if sandbox_id is None:
                        raise Exception(f"Current Sandbox {name} is not found")
                
                if 'image' in output:
                    image = output['image']
                else:
                    image = ""

                if 'webapp_addr' in output:
                    webapp_addr = output['webapp_addr']
                else:
                    webapp_addr = ""
                

                if 'webapp_pass' in output:
                    webapp_pass = output['webapp_pass']
                else:
                    webapp_pass = ""
                
                if 'auto_stop_interval' in output:
                    auto_stop_interval = output['auto_stop_interval']
                else:
                    #default: 5min
                    auto_stop_interval = 5

                sandbox_info = SandboxInfo()

                sandbox_info.id = sandbox_id
                sandbox_info.image = image
                sandbox_info.webapp_addr = webapp_addr
                sandbox_info.webapp_pass = webapp_pass
                sandbox_info.auto_stop_interval = auto_stop_interval

                sandbox_inst = SandboxInstance()

                sandbox_inst.info = sandbox_info

                sandbox = Sandbox(sandbox_id, sandbox_inst, ToolboxApi)

                return sandbox
        
        except Exception as e:
            print(str(e))
            raise e