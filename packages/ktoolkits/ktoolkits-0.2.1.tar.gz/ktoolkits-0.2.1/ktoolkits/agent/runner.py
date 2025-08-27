#coding=utf-8
import os
import sys
import time
import random
import requests
import threading
from tqdm import tqdm
from ktoolkits.agent.async_runner import AsyncRunner
from ktoolkits.client.base_api import BaseApi
from ktoolkits.api_entities.ktool_response import RunnerResponse
from ktoolkits.common.constants import KToolAPICode
from ktoolkits.common.utils import calculate_md5

from typing import Union,Dict


class ProgressThread(threading.Thread):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._stop_event = threading.Event()
        #最长执行时间5分钟,500*0.6
        self._max_total = 3000
        self.tool_name = None

    def set_tool_name(self,tool_name):
        self.tool_name = tool_name

    def terminate(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()
    
    def run(self):
        progress_bar = tqdm(total=self._max_total, desc=f"{self.tool_name}工具正在执行", position=0, leave=True)
        while not self.stopped():
            try:
                self.work(progress_bar)
            except Exception as e:
                print(e)
                break
            finally:
                progress_bar.close()

    def work(self, progress_bar):
        for i in range(self._max_total):
            if self.stopped():
                progress_bar.update(self._max_total)
                progress_bar.close()
                return
            progress_bar.update(6)
            time.sleep(random.uniform(0.1, 0.6))

class Runner(BaseApi):
    task = 'tool-runner'
    """
    API for ktoolkits Runner.
    """
    @classmethod
    def call(
        cls,
        tool_name: str,
        tool_input: Union[str,Dict],
        file_location: str = 'local_file',#['local_file','remote_file']
        **kwargs
    ) -> RunnerResponse:
        """Call tool runner service.

        Args:
            tool_name (str): The name of requested tool, such as nmap
            tool_input (str): The input for requested tool, such as: scan_target,root_domain etc

        Returns:
            RunnerResponse.
        """

        """
        @本地文件: /path/to/file.txt
        @远程文件: https://path/file.txt
        """
        file_info = []

        if isinstance(tool_input,Dict):
            for key, value in tool_input.items():
                if value:
                    #提取文件信息
                    if file_location == 'remote_file':
                        if value.startswith('http://') or value.startswith('https://'):
                            file_name = calculate_md5(value)
                            content = requests.get(value).content
                            file_item = {'file_path':'/', 'file_name': file_name, 'file_content': content}
                            file_info.append(file_item)
                    elif file_location == 'local_file': 
                        if os.path.exists(value):
                            file_name = os.path.basename(value)
                            content = open(value, 'r').read()
                            file_item = {'file_path':'/', 'file_name': file_name, 'file_content': content}
                            file_info.append(file_item)

                            tool_input[key] = "".join(['/', file_name])
                    else:
                        pass

        # 启动进度条线程执行耗时操作
        if len(file_info)>0:
            task_response = AsyncRunner.async_call(tool_name=tool_name, tool_input=tool_input, tool_input_file=file_info, **kwargs)
        else:
            task_response = AsyncRunner.async_call(tool_name=tool_name, tool_input=tool_input, **kwargs)

        try:

            if task_response.status_code != 200 or task_response.code == KToolAPICode.FAILURE:
                #print(task_response.message)
                return task_response
            
            worker = ProgressThread()
            worker.set_tool_name(tool_name)
            worker.start()

            response = AsyncRunner.wait(task_response)
            
            worker.terminate()
            worker.join()   

            is_stream = kwargs.get('stream', False)
            if is_stream:
                return (RunnerResponse.from_api_response(rsp)
                        for rsp in response)
            else:
                return RunnerResponse.from_api_response(response)
        except KeyboardInterrupt:
            # 当用户按下 Ctrl+C 时，会执行这里的代码
            worker.terminate()
            worker.join()
            print(f"\n{tool_name}工具已停止运行...")
            return task_response

