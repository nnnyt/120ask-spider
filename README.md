# 120ask-spider
Web信息处理与应用 开放实验  
宁雨亭 PB17111577   
爬取[快速问医生](https://www.120ask.com) - [检查库](https://tag.120ask.com/jiancha/)   



## Usage

```
$ python3 spider.py
```



## 数据

数据格式：
```json
[
    {
        类型: "检查",
        网址: "http://xxx..."
        名称: "xx",
        简介: "xxx",
        属性: {
        	专科分类: "",
        	检查分类: "",
        	...
    	},
    	正常值: "",
    	临床意义: "",
    	注意事项: "",
    	检查过程: "",
    	不适宜人群: "",
    	不良反应与风险: "",
    	相关疾病: [
    		{名称: "aaa", 网址: ""},
    		{名称: "bbb", 网址: ""},
    		...
		]
    }
]
```
运行后默认存储在当前文件夹`data.json`文件中，可在调用`write_json()`函数时通过参数`data_dir`指定目标输出目录



## 代码设计

####  get_logger()
创建日志，将日志输出到moniter

#### write_json(data, data_dir=DEFAULT_DATADIR, encoding='utf-8', indent=2)
将数据以`json`格式输出到文件`data.json`   
*para*:   
`data`: 数据，list格式   
`data_dir`: 数据输出目标文件夹，默认为DEFAULT_DATADIR为代码所在文件夹   
`encoding`: 编码，默认utf-8   
`indent`: json格式锁进，默认为2   

#### spider()
爬虫入口   
调用`get_jiancha(url)`分别得到每一个网页的信息，将信息存储在一个list中，返回这个list。   
若`get_jiancha(url)`执行出错，则说明这个`url`对应的网页`404 Not Found`。   
*return*: 所有数据，`list(dictionary)`类型 

#### get_jiancha(url)
对一个页面的信息进行爬取   
通过调用`get_intro()`, `get_attr()`, `get_normal()`, `get_clinical()`, `get_related_disease()`这几个函数得到一个检查的信息，若调用的函数出错，则表示该检查无此类信息。   
将一个检查的所有信息保存在一个字典里返回。   
*para*:   
`url`: 所爬网页网址   
*return*: 单个检查的所有数据，`dictionary`类型   

#### get_intro(bs)
获得一个检查的介绍部分信息（名称、简介）   
*para*:   
`bs`: BeautifulSoup解析后的内容   
*return*: 名称，简介，均为`string`类型

#### get_attr(bs)
获得一个检查的属性（专科分类、检查分类……）   
*para*:   
`bs`: BeautifulSoup解析后的内容   
*return*: 属性的所有内容，`dictionary`类型   

#### get_normal(bs)
获得一个检查的正常值   
注意不是所有检查都有正常值域，没有的话`get_normal`函数返回异常，在`get_jiancha`中处理   
*para*:   
`bs`: BeautifulSoup解析后的内容   
*return*: 正常值，`string`类型   

#### get_clinical(bs)
获得一个检查的临床信息（临床意义、注意事项、检查过程、不适宜人群、不良反应与风险）  
不是所有检查的临床信息都齐全，只返回有的信息，没有的域不保留，在get_jiancha中返回日志报告什么信息没有。如果没有临床信息，则`get_clinical`函数返回异常，在`get_jiancha`中处理   
*para*:   
`bs`: BeautifulSoup解析后的内容   
*return*: 临床信息的所有内容，`dictionary`类型   

#### get_related_disease(bs)
获得一个检查的相关疾病信息   
对每一个相关疾病，建立一个`dictionary`，内容为名称和网址。所有相关疾病组成一个`list`。注意不是所有检查都有相关疾病，如果没有则`get_related_disease`函数返回异常，在`get_jiancha`中处理   
*para*:
`bs`: BeautifulSoup解析后的内容   
*return*: 相关疾病，`list(dictionary)`类型


