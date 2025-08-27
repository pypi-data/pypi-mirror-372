KToolkits

## 介绍

KToolkits是一款面向AI智能体应用开发的开源工具库，它融合了后端即服务和AI智能体的理念，使开发者可以快速搭建和定制AI智能体应用；即使你是非技术专业人员，也能参与到AI智能体的定义和运营过程中。


## 功能

### 一、工具箱

```
import ktoolkits

ktoolkits.api_key="XXXX"

#当工具有多个参数时，可以使用参数字典为输入tool_input={"scan_target":"www.baidu.com"}
output = ktoolkits.Runner.call(
	tool_name="nmap",
	tool_input="www.baidu.com",
)
```

### 更多

+ https://apifox.com/apidoc/shared-2b306df6-5d22-423f-83ba-ed07415b13d5/doc-5681852