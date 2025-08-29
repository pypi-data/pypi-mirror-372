from __future__ import annotations
import typing as t
from dataclasses import dataclass
from datasets import Dataset
from langchain.callbacks.manager import CallbackManager, trace_as_chain_group
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from bisheng_ragas.metrics.base import EvaluationMode, MetricWithLLM
from bisheng_ragas.utils import json_loader
import json
import time
if t.TYPE_CHECKING:
    from langchain.callbacks.base import Callbacks


# Tips: in Step2, you need to understand the type of Question, if the Question need an exact answer like a number or , the answer must have the same statement with the extracted statements of ground-truth
CORRECTNESS_PROMPT_SPLIT = HumanMessagePromptTemplate.from_template(
    """
Extract the key statements of ground-truth. You will get a Question and Ground truth, you have to extract the key statements of ground-truth.
Here are some examples:

Example1:
Question:What powers the sun and what is its primary function?
Ground truth: The sun is actually powered by nuclear fusion, not fission. In its core, hydrogen atoms fuse to form helium, releasing a tremendous amount of energy. This energy is what lights up the sun and provides heat and light, essential for life on Earth. The sun's light also plays a critical role in Earth's climate system and helps to drive the weather and ocean currents.
Extracted ground-truth statements: ["The sun is powered by nuclear fusion, not fission", "In its core, hydrogen atoms fuse to form helium, releasing a tremendous amount of energy", "This energy provides heat and light, essential for life on Earth", "The sun's light plays a critical role in Earth's climate system", "The sun helps to drive the weather and ocean currents"]

Example2:
Question: What is the boiling point of water?
Ground truth: The boiling point of water is 100 degrees Celsius (212 degrees Fahrenheit) at sea level, but it can change with altitude.
Extracted ground-truth statements: ["The boiling point of water is 100 degrees Celsius at sea level", "The boiling point can change with altitude", "The boiling point of water is 212 degrees Fahrenheit at sea level"]

Example3:
Question: 公司2021年的研发费用占营业收入的比例是多少？
Ground truth: 根据公司招股书披露数据，公司2021年的研发费用占营业收入的比例为15.86%。
Extracted ground-truth statements: ["公司2021年的研发费用占营业收入的比例为15.86%"]

Example4:
Question: 达梦2021年的息税折旧摊销前利润是多少？
Ground truth: 根据达梦数据库招股书披露数据，达梦2021年的息税折旧摊销前利润为49,189.85万元。
Extracted ground-truth statements: ["达梦2021年的息税折旧摊销前利润为49,189.85万元"]

Example5:
Question: 达梦2022年的应收账款周转率是多少？
Ground truth: 很抱歉，达梦尚未披露2022年报数据。
Extracted ground-truth statements: ["无法得知达梦2022年的应收账款周转率"]

Example6:
Question: 达梦2022年的应收账款周转率是多少？
Ground truth: 根据提供的文本，没有明确提到达梦2022年的应收账款周转率，具体情况需要进一步了解公司的财务报表和其他相关信息才能确定。
Extracted ground-truth statements: ["没有明确提到达梦2022年的应收账款周转率"]

Example7:
Question: 太原智慧城市原则是什么？
Ground truth: 太原智慧城市建设的原则包括：1. 坚持以人为本、全民共享：以提升惠民便企服务水平为目标，将人民群众的获得感和幸福感作为建设成效的出发点和落脚点，确保全民共享数字化发展红利。2. 坚持统筹谋划、系统推进：加强智慧太原"一盘棋"部署，强化设施、数据、系统、应用统建共用和资金、技术人员等资源统筹配置，集中优势资源建好智慧太原"四梁八柱"。突出技术创新与制度改革双轨并行，不断完善智慧太原建设、管理、运营的制度规范和标准体系，健全开放合作共赢的发展环境。3. 坚持多元合作、共建共治：发挥政府在总体规划、政策扶持、标准规范、监督考核等方面的作用，以及市场在扩大数字能力有效供给中的决定性作用，探索政企合作合营发展模式，吸引各类市场主体参与智慧太原建设，提升长效可持续发展活力。4. 坚持制度护航、安全发展：坚持安全保障工作与智慧城市建设同步规划、同步建设、同步使用，增强网络与信息安全管理水平，走自主可控、安全高效的技术路线，建设全要素、多层次的安全防护体系。不断探索行业监管机制，保障数据资源安全有序流动与合规开发利用。
Extracted ground-truth statements: ["1. 坚持以人为本、全民共享：以提升惠民便企服务水平为目标，将人民群众的获得感和幸福感作为建设成效的出发点和落脚点，确保全民共享数字化发展红利。", "2. 坚持统筹谋划、系统推进：加强智慧太原"一盘棋"部署，强化设施、数据、系统、应用统建共用和资金、技术人员等资源统筹配置，集中优势资源建好智慧太原"四梁八柱"。突出技术创新与制度改革双轨并行，不断完善智慧太原建设、管理、运营的制度规范和标准体系，健全开放合作共赢的发展环境。", "3. 坚持多元合作、共建共治：发挥政府在总体规划、政策扶持、标准规范、监督考核等方面的作用，以及市场在扩大数字能力有效供给中的决定性作用，探索政企合作合营发展模式，吸引各类市场主体参与智慧太原建设，提升长效可持续发展活力。", "4. 坚持制度护航、安全发展：坚持安全保障工作与智慧城市建设同步规划、同步建设、同步使用，增强网络与信息安全管理水平，走自主可控、安全高效的技术路线，建设全要素、多层次的安全防护体系。不断探索行业监管机制，保障数据资源安全有序流动与合规开发利用。"]

Example8:
Question: 错例分析包括哪些步骤？
Ground truth: 错例分析包括以下步骤：1、观察⽐对错误字段的标注值、预估值、预估值后处理前结果，对每⼀个错误字段做好标签统计.• 如果标注值与图中字段真实内容不⼀致，则为标注错误，在该字段下⽅添加错误标签“标注错误”• 如果标注值正确，观察该字段预估值在原图中显⽰的红框是否错位，如果与标注值的绿框有少量偏移，切到下⽅⽂字，则为检测错误• 如果预估值的框没有错位，则为识别错误• 观察预估值后处理前结果，若后处理前结果正确，但预估值错误，则为后处理错误• 结构化错误：预估值明显与图中字段真实内容不对应其他错误情况，⽀持⾃定义添加标签2、对不同错误类别进⾏单独优化• 对标注错误的字段，进⼊评测集标注⻚⾯，点击“筛选标注错误”，修正错误的标注结果• 对后处理错误的字段，修改后处理脚本，重新评估• 对识别错误的字段，尝试更换识别模型，重新评估• 对检测错误的字段，若该类错误数量占⽐较多，对准确率影响⽐较严重，可以尝试使⽤后处理参数sprint功能，重新切⽚检测，或专⻔finetune训练⼀个检测模型• 对结构化错误，进⼊模型任务管理模块针对智能结构化模型优化训练。
Extracted ground-truth statements: ["错例分析包括以下步骤：1、观察⽐对错误字段的标注值、预估值、预估值后处理前结果，对每⼀个错误字段做好标签统计", "如果标注值与图中字段真实内容不⼀致，则为标注错误，在该字段下⽅添加错误标签“标注错误”", "如果标注值正确，观察该字段预估值在原图中显⽰的红框是否错位，如果与标注值的绿框有少量偏移，切到下⽅⽂字，则为检测错误", "如果预估值的框没有错位，则为识别错误", "观察预估值后处理前结果，若后处理前结果正确，但预估值错误，则为后处理错误", "结构化错误：预估值明显与图中字段真实内容不对应其他错误情况，⽀持⾃定义添加标签", "2、对不同错误类别进⾏单独优化", "对标注错误的字段，进⼊评测集标注⻚⾯，点击“筛选标注错误”，修正错误的标注结果", "对后处理错误的字段，修改后处理脚本，重新评估", "对识别错误的字段，尝试更换识别模型，重新评估", "对检测错误的字段，若该类错误数量占⽐较多，对准确率影响⽐较严重，可以尝试使⽤后处理参数sprint功能，重新切⽚检测，或专⻔finetune训练⼀个检测模型", "对结构化错误，进⼊模型任务管理模块针对智能结构化模型优化训练。"]

Example9:
Question: 什么是大疆机场？
Ground truth: 大疆机场是一款全自动无人值守作业平台，由大疆创新设计和制造。它的机身设计高度一体化，集成了超广角监控相机、风速计、雨量计、通讯天线、RTK模块、UPS电源等设备。大疆机场具有强大的环境适应性，能够在恶劣气候条件下持续工作，内置防雷保护功能，并达到IP55防护等级，最长维护间隔可达6个月。它还配备了快充模块，内置空调系统可以为电池快速降温，最短充电时间约为25分钟。大疆机场的作业覆盖半径可达7公里，重量为105千克，占地面积不足1平方米，支持快速安装和配置。
Extracted ground-truth statements: ["大疆机场是一款全自动无人值守作业平台，由大疆创新设计和制造。", "大疆机场的机身设计高度一体化，集成了超广角监控相机、风速计、雨量计、通讯天线、RTK模块、UPS电源等设备。", "大疆机场具有强大的环境适应性，能够在恶劣气候条件下持续工作，内置防雷保护功能，并达到IP55防护等级，最长维护间隔可达6个月。", "大疆机场还配备了快充模块，内置空调系统可以为电池快速降温，最短充电时间约为25分钟。", "大疆机场的作业覆盖半径可达7公里，重量为105千克，占地面积不足1平方米，支持快速安装和配置。"]

Now, you have to extract the key statements of ground-truth, you must output the extracted statements follow the format above.
Question:{question}
Ground truth: {ground_truth}
Extracted ground-truth statements: """  # noqa: E501
)

# Now, you have to finish the following task, you must follow the steps above, but you must only return the content of Output!
CORRECTNESS_PROMPT_SCORE = HumanMessagePromptTemplate.from_template(
    """
Give the statements of Ground-truth contained in the answer. You will get a Question, a Ground truth and an answer, you have to compare the answers according to the statements of ground-truth, and judge whether each statement is contained in the answers.
Here are some examples:

Example1:
Question:What powers the sun and what is its primary function?
Answer: The sun is powered by nuclear fission, similar to nuclear reactors on Earth, and its primary function is to provide light to the solar system.
Ground truth: ["The sun is powered by nuclear fusion, not fission", "In its core, hydrogen atoms fuse to form helium, releasing a tremendous amount of energy", "This energy provides heat and light, essential for life on Earth", "The sun's light plays a critical role in Earth's climate system", "The sun helps to drive the weather and ocean currents"]
Extracted ground-truth statements: 
[
    {{
        "Statement": "The sun is powered by nuclear fusion, not fission",
        "Analyse": "Statement is contained in the answer because the description in the answer ('The sun is powered by nuclear fission, similar to nuclear reactors on Earth') is similar to the Statement. So, Statement is contained in the answer.",
        "Output": "include"
    }},
    {{
        "Statement": "In its core, hydrogen atoms fuse to form helium, releasing a tremendous amount of energy",
        "Analyse": "Statement is not contained in the answer because you cannot find the similar description in the answer. So, Statement is not contained in the answer.",
        "Output": "not include"
    }},
    {{
        "Statement": "This energy provides heat and light, essential for life on Earth",
        "Analyse": "Statement is not contained in the answer because you cannot find the similar description in the answer. So, Statement is not contained in the answer.",
        "Output": "not include"
    }},
    {{
        "Statement": "The sun's light plays a critical role in Earth's climate system",
        "Analyse": "Statement is not contained in the answer because you cannot find the similar description in the answer. So, Statement is not contained in the answer.",
        "Output": "not include"
    }},
    {{
        "Statement": "The sun helps to drive the weather and ocean currents",
        "Analyse": "Statement is not contained in the answer because you cannot find the similar description in the answer. So, Statement is not contained in the answer.",
        "Output": "not include"
    }}  
]

Example2:
Question: What is the boiling point of water?
Answer: The boiling point of water is 100 degrees Celsius at sea level.
Ground truth: ["The boiling point of water is 100 degrees Celsius at sea level", "The boiling point can change with altitude", "The boiling point of water is 212 degrees Fahrenheit at sea level"]
Extracted ground-truth statements: 
[
    {{
        "Statement": "The boiling point of water is 100 degrees Celsius at sea level",
        "Analyse": "Statement is contained in the answer because the description in the answer ('The boiling point of water is 100 degrees Celsius at sea level') is similar to the Statement. So, Statement is contained in the answer.",
        "Output": "include"
    }},
    {{
        "Statement": "The boiling point can change with altitude",
        "Analyse": "Statement is not contained in the answer because you cannot find the similar description in the answer. So, Statement is not contained in the answer.",
        "Output": "not include"
    }},
    {{
        "Statement": "The boiling point of water is 212 degrees Fahrenheit at sea level",
        "Analyse": "Statement is not contained in the answer because you cannot find the similar description in the answer. So, Statement is not contained in the answer.",
        "Output": "not include"
    }}  
]

Example3:
Question: 公司2021年的研发费用占营业收入的比例是多少？
Answer: 根据提供的信息，公司2021年的研发费用占营业收入的比例为15.86%。
Ground truth: ["公司2021年的研发费用占营业收入的比例为15.86%"]
Extracted ground-truth statements: 
[
    {{
        "Statement": "公司2021年的研发费用占营业收入的比例为15.86%",
        "Analyse": "Statement is contained in the answer because the description in the answer ('根据提供的信息，公司2021年的研发费用占营业收入的比例为15.86%') is similar to the Statement. So, Statement is contained in the answer.",
        "Output": "include"
    }}
]

Example4:
Question: 达梦2021年的息税折旧摊销前利润是多少？
Answer: 达梦2021年的息税折旧摊销前利润为49,189.87万元。
Ground truth: ["达梦2021年的息税折旧摊销前利润为49,189.85万元"]
Extracted ground-truth statements: 
[
    {{
        "Statement": "达梦2021年的息税折旧摊销前利润为49,189.85万元",
        "Analyse": "Statement is not contained in the answer because the number in the statement is different from the answer ('达梦2021年的息税折旧摊销前利润为49,189.87万元‘). So, Statement is not contained in the answer.",
        "Output": "not include"
    }}
]

Example5:
Question: 达梦2022年的应收账款周转率是多少？
Answer: 根据提供的信息，无法得知达梦2022年的应收账款周转率。
Ground truth: ["无法得知达梦2022年的应收账款周转率"]
Extracted ground-truth statements: 
[
    {{
        "Statement": "无法得知达梦2022年的应收账款周转率",
        "Analyse": "Statement is contained in the answer because the description in the answer ('根据提供的信息，无法得知达梦2022年的应收账款周转率') is similar to the Statement. So, Statement is contained in the answer.",
        "Output": "include"
    }}
]

Example6:
Question: 达梦2022年的应收账款周转率是多少？
Answer: 达梦2022年的应收账款周转率是100%。
Ground truth: ["没有明确提到达梦2022年的应收账款周转率"]
Extracted ground-truth statements: 
[
    {{
        "Statement": "没有明确提到达梦2022年的应收账款周转率",
        "Analyse": "Statement contradicts the meaning of the answer ('达梦2022年的应收账款周转率是100%'), because the statement means it does not give information but the answer gives an extract number. So, Statement is not contained in the answer.",
        "Output": "not include"
    }}
]

Example7:
Question: 太原智慧城市原则是什么？
Answer: 太原智慧城市建设的基本原则包括：1. 坚持以人为本、全民共享：以提升惠民便企服务水平为目标，确保全民共享数字化发展红利。2. 坚持统筹谋划、系统推进：加强智慧太原"一盘棋"部署，集中优势资源建好智慧太原"四梁八柱"，不断完善智慧太原建设、管理、运营的制度规范和标准体系。3. 坚持多元合作、共建共治：发挥政府和市场在智慧城市建设中的作用，探索政企合作合营发展模式，吸引各类市场主体参与。4. 坚持制度护航、安全发展：同步规划、同步建设、同步使用，增强网络与信息安全管理水平，走自主可控、安全高效的技术路线。
Ground truth: ["1. 坚持以人为本、全民共享：以提升惠民便企服务水平为目标，将人民群众的获得感和幸福感作为建设成效的出发点和落脚点，确保全民共享数字化发展红利。", "2. 坚持统筹谋划、系统推进：加强智慧太原"一盘棋"部署，强化设施、数据、系统、应用统建共用和资金、技术人员等资源统筹配置，集中优势资源建好智慧太原"四梁八柱"。突出技术创新与制度改革双轨并行，不断完善智慧太原建设、管理、运营的制度规范和标准体系，健全开放合作共赢的发展环境。", "3. 坚持多元合作、共建共治：发挥政府在总体规划、政策扶持、标准规范、监督考核等方面的作用，以及市场在扩大数字能力有效供给中的决定性作用，探索政企合作合营发展模式，吸引各类市场主体参与智慧太原建设，提升长效可持续发展活力。", "4. 坚持制度护航、安全发展：坚持安全保障工作与智慧城市建设同步规划、同步建设、同步使用，增强网络与信息安全管理水平，走自主可控、安全高效的技术路线，建设全要素、多层次的安全防护体系。不断探索行业监管机制，保障数据资源安全有序流动与合规开发利用。"]
Extracted ground-truth statements: 
[
    {{
        "Statement": "1. 坚持以人为本、全民共享：以提升惠民便企服务水平为目标，将人民群众的获得感和幸福感作为建设成效的出发点和落脚点，确保全民共享数字化发展红利。",
        "Analyse": "Statement is contained in the answer because the description in the answer ('1. 坚持以人为本、全民共享：以提升惠民便企服务水平为目标，确保全民共享数字化发展红利。') is similar to the Statement. So, Statement is contained in the answer.",
        "Output": "include"
    }},
    {{
        "Statement": "2. 坚持统筹谋划、系统推进：加强智慧太原"一盘棋"部署，强化设施、数据、系统、应用统建共用和资金、技术人员等资源统筹配置，集中优势资源建好智慧太原"四梁八柱"。突出技术创新与制度改革双轨并行，不断完善智慧太原建设、管理、运营的制度规范和标准体系，健全开放合作共赢的发展环境。",
        "Analyse": "Statement is contained in the answer because the description in the answer ('2. 坚持统筹谋划、系统推进：加强智慧太原"一盘棋"部署，集中优势资源建好智慧太原"四梁八柱"，不断完善智慧太原建设、管理、运营的制度规范和标准体系。') is similar to the Statement. So, Statement is contained in the answer.",
        "Output": "include"
    }},
    {{
        "Statement": "3. 坚持多元合作、共建共治：发挥政府在总体规划、政策扶持、标准规范、监督考核等方面的作用，以及市场在扩大数字能力有效供给中的决定性作用，探索政企合作合营发展模式，吸引各类市场主体参与智慧太原建设，提升长效可持续发展活力。",
        "Analyse": "Statement is contained in the answer because the description in the answer ('3. 坚持多元合作、共建共治：发挥政府和市场在智慧城市建设中的作用，探索政企合作合营发展模式，吸引各类市场主体参与。') is similar to the Statement. So, Statement is contained in the answer.",
        "Output": "include"
    }},
    {{
        "Statement": "4. 坚持制度护航、安全发展：坚持安全保障工作与智慧城市建设同步规划、同步建设、同步使用，增强网络与信息安全管理水平，走自主可控、安全高效的技术路线，建设全要素、多层次的安全防护体系。不断探索行业监管机制，保障数据资源安全有序流动与合规开发利用。",
        "Analyse": "Statement is contained in the answer because the description in the answer ('4. 坚持制度护航、安全发展：同步规划、同步建设、同步使用，增强网络与信息安全管理水平，走自主可控、安全高效的技术路线。') is similar to the Statement. So, Statement is contained in the answer.",
        "Output": "include"
    }}
]

Example8:
Question: 错例分析包括哪些步骤？
Answer: 错例分析包括以下步骤：1. 观察比对错误字段的标注值、预估值、预估值后处理前结果，对每一个错误字段做好标签统计：- 如果标注值与图中字段真实内容不一致，则为标注错误，在该字段下方添加错误标签“标注错误”。- 如果标注值正确，观察该字段预估值在原图中显示的红框是否错位，如果与标注值的绿框有少量偏移，切到下方文字，则为检测错误。- 结构化错误：预估值明显与图中字段真实内容不对应。- 其他错误情况，支持自定义添加标签。2. 对不同错误类别进行单独优化：- 对标注错误的字段，进入评测集标注页面，点击“筛选标注错误”，修正错误的标注结果。- 对后处理错误的字段，修改后处理脚本，重新评估。- 对识别错误的字段，尝试更换识别模型，重新评估。- 对检测错误的字段，若该类错误数量占比较多，对准确率影响比较严重，可以尝试使用后处理参数sprint功能，重新切片检测，或专门finetune训练一个检测模型。
Ground truth: ["错例分析包括以下步骤：1、观察⽐对错误字段的标注值、预估值、预估值后处理前结果，对每⼀个错误字段做好标签统计", "如果标注值与图中字段真实内容不⼀致，则为标注错误，在该字段下⽅添加错误标签“标注错误”", "如果标注值正确，观察该字段预估值在原图中显⽰的红框是否错位，如果与标注值的绿框有少量偏移，切到下⽅⽂字，则为检测错误", "如果预估值的框没有错位，则为识别错误", "观察预估值后处理前结果，若后处理前结果正确，但预估值错误，则为后处理错误", "结构化错误：预估值明显与图中字段真实内容不对应其他错误情况，⽀持⾃定义添加标签", "2、对不同错误类别进⾏单独优化", "对标注错误的字段，进⼊评测集标注⻚⾯，点击“筛选标注错误”，修正错误的标注结果", "对后处理错误的字段，修改后处理脚本，重新评估", "对识别错误的字段，尝试更换识别模型，重新评估", "对检测错误的字段，若该类错误数量占⽐较多，对准确率影响⽐较严重，可以尝试使⽤后处理参数sprint功能，重新切⽚检测，或专⻔finetune训练⼀个检测模型", "对结构化错误，进⼊模型任务管理模块针对智能结构化模型优化训练。"]
Extracted ground-truth statements: 
[
    {{
        "Statement": "错例分析包括以下步骤：1、观察⽐对错误字段的标注值、预估值、预估值后处理前结果，对每⼀个错误字段做好标签统计",
        "Analyse": "Statement is contained in the answer because the description in the answer ('错例分析包括以下步骤：1. 观察比对错误字段的标注值、预估值、预估值后处理前结果，对每一个错误字段做好标签统计') is similar to the Statement. So, Statement is contained in the answer.",
        "Output": "include"
    }},
    {{
        "Statement": "如果标注值与图中字段真实内容不⼀致，则为标注错误，在该字段下⽅添加错误标签“标注错误”",
        "Analyse": "Statement is contained in the answer because the description in the answer ('如果标注值与图中字段真实内容不一致，则为标注错误，在该字段下方添加错误标签“标注错误”。') is similar to the Statement. So, Statement is contained in the answer.",
        "Output": "include"
    }},
    {{
        "Statement": "如果标注值正确，观察该字段预估值在原图中显⽰的红框是否错位，如果与标注值的绿框有少量偏移，切到下⽅⽂字，则为检测错误",
        "Analyse": "Statement is contained in the answer because the description in the answer ('如果标注值正确，观察该字段预估值在原图中显示的红框是否错位，如果与标注值的绿框有少量偏移，切到下方文字，则为检测错误。') is similar to the Statement. So, Statement is contained in the answer.",
        "Output": "include"
    }},
    {{
        "Statement": "如果预估值的框没有错位，则为识别错误",
        "Analyse": "Statement is not contained in the answer because you cannot find the similar description in the answer. So, Statement is not contained in the answer.",
        "Output": "not include"
    }},
    {{
        "Statement": "观察预估值后处理前结果，若后处理前结果正确，但预估值错误，则为后处理错误",
        "Analyse": "Statement is not contained in the answer because you cannot find the similar description in the answer. So, Statement is not contained in the answer.",
        "Output": "not include"
    }},
    {{
        "Statement": "结构化错误：预估值明显与图中字段真实内容不对应其他错误情况，⽀持⾃定义添加标签",
        "Analyse": "Statement is contained in the answer because the description in the answer ('结构化错误：预估值明显与图中字段真实内容不对应。') is similar to the Statement. So, Statement is contained in the answer.",
        "Output": "include"
    }},
    {{
        "Statement": "2、对不同错误类别进⾏单独优化",
        "Analyse": "Statement is contained in the answer because the description in the answer ('2. 对不同错误类别进行单独优化') is similar to the Statement. So, Statement is contained in the answer.",
        "Output": "include"
    }},
    {{
        "Statement": "对标注错误的字段，进⼊评测集标注⻚⾯，点击“筛选标注错误”，修正错误的标注结果",
        "Analyse": "Statement is contained in the answer because the description in the answer ('对标注错误的字段，进入评测集标注页面，点击“筛选标注错误”，修正错误的标注结果。') is similar to the Statement. So, Statement is contained in the answer.",
        "Output": "include"
    }},
    {{
        "Statement": "对后处理错误的字段，修改后处理脚本，重新评估",
        "Analyse": "Statement is contained in the answer because the description in the answer ('对后处理错误的字段，修改后处理脚本，重新评估。') is similar to the Statement. So, Statement is contained in the answer.",
        "Output": "include"
    }},
    {{
        "Statement": "对识别错误的字段，尝试更换识别模型，重新评估",
        "Analyse": "Statement is contained in the answer because the description in the answer ('对识别错误的字段，尝试更换识别模型，重新评估。') is similar to the Statement. So, Statement is contained in the answer.",
        "Output": "include"
    }},
    {{
        "Statement": "对检测错误的字段，若该类错误数量占⽐较多，对准确率影响⽐较严重，可以尝试使⽤后处理参数sprint功能，重新切⽚检测，或专⻔finetune训练⼀个检测模型",
        "Analyse": "Statement is contained in the answer because the description in the answer ('对检测错误的字段，若该类错误数量占比较多，对准确率影响比较严重，可以尝试使用后处理参数sprint功能，重新切片检测，或专门finetune训练一个检测模型。') is similar to the Statement. So, Statement is contained in the answer.",
        "Output": "include"
    }},
        {{
        "Statement": "对结构化错误，进⼊模型任务管理模块针对智能结构化模型优化训练。",
        "Analyse": "Statement is not contained in the answer because you cannot find the similar description in the answer. So, Statement is not contained in the answer.",
        "Output": "not include"
    }}    
]

Example9:
Question: 什么是大疆机场？
Answer: 大疆机场位于中国深圳，是大疆创新科技有限公司专用的私人机场。这座机场不仅是大疆公司的总部所在地，也是其研发、生产和测试无人机产品的重要基地之一。机场拥有现代化的设施和设备，包括长跑道、航空维修厂、无人机试飞区等，为公司的研发和生产提供了便利条件。此外，大疆机场还经常举办无人机飞行比赛、技术研讨会等活动，吸引着来自世界各地的无人机爱好者和专业人士。作为全球领先的无人机企业之一，大疆机场象征着中国在航空科技领域的雄心与实力。
Ground truth: ["大疆机场是一款全自动无人值守作业平台，由大疆创新设计和制造。", "大疆机场的机身设计高度一体化，集成了超广角监控相机、风速计、雨量计、通讯天线、RTK模块、UPS电源等设备。", "大疆机场具有强大的环境适应性，能够在恶劣气候条件下持续工作，内置防雷保护功能，并达到IP55防护等级，最长维护间隔可达6个月。", "大疆机场还配备了快充模块，内置空调系统可以为电池快速降温，最短充电时间约为25分钟。", "大疆机场的作业覆盖半径可达7公里，重量为105千克，占地面积不足1平方米，支持快速安装和配置。"]
Extracted ground-truth statements: 
[
    {{
        "Statement": "大疆机场是一款全自动无人值守作业平台，由大疆创新设计和制造。",
        "Analyse": "Statement is not contained in the answer because you cannot find the similar description in the answer. So, Statement is not contained in the answer.",
        "Output": "not include"
    }},
    {{
        "Statement": "大疆机场的机身设计高度一体化，集成了超广角监控相机、风速计、雨量计、通讯天线、RTK模块、UPS电源等设备。",
        "Analyse": "Statement is not contained in the answer because you cannot find the similar description in the answer. So, Statement is not contained in the answer.",
        "Output": "not include"
    }},
    {{
        "Statement": "大疆机场具有强大的环境适应性，能够在恶劣气候条件下持续工作，内置防雷保护功能，并达到IP55防护等级，最长维护间隔可达6个月。",
        "Analyse": "Statement is not contained in the answer because you cannot find the similar description in the answer. So, Statement is not contained in the answer.",
        "Output": "not include"
    }},
    {{
        "Statement": "大疆机场还配备了快充模块，内置空调系统可以为电池快速降温，最短充电时间约为25分钟。",
        "Analyse": "Statement is not contained in the answer because you cannot find the similar description in the answer. So, Statement is not contained in the answer.",
        "Output": "not include"
    }},
    {{
        "Statement": "大疆机场的作业覆盖半径可达7公里，重量为105千克，占地面积不足1平方米，支持快速安装和配置。",
        "Analyse": "Statement is not contained in the answer because you cannot find the similar description in the answer. So, Statement is not contained in the answer.",
        "Output": "not include"
    }}    
]

You must output the result using the format above. Now, you have to extract the key statements of ground-truth, you must not change the statement in the ground-truth.
Question:{question}
Answer: {answer}
Ground truth: {ground_truth}
Extracted ground-truth statements: """  # noqa: E501
)

@dataclass
# class AnswerRecallBisheng(MetricWithLLM, isgtsplitdone):
class AnswerRecallBisheng(MetricWithLLM):
    
    """
    Measures answer correctness compared to ground truth as a combination of
    semantic similarity and factuality

    Attributes
    ----------
    name: string
        The name of the metrics
    batch_size: int
        batch size for evaluation
    """
    name: tuple = ("gt_split_point_out", "analyse","bisheng_recall")
    evaluation_mode: EvaluationMode = EvaluationMode.qga  # type: ignore[reportIncompatibleMethodOverride]
    batch_size: int = 6
    whether_gtsplit: bool = False

    def __post_init__(self: t.Self):
        pass

    def _score_batch(
        self: t.Self,
        dataset: Dataset,
        callbacks: t.Optional[Callbacks] = None,
        callback_group_name: str = "batch",
    ) -> list[float]:
        question, answer, ground_truths = (
            dataset["question"],
            dataset["answer"],
            dataset["ground_truths"],
        )
        gtsplit = []    
        analyse = []
        score = []
        if "gt_split_point" not in dataset.features or self.whether_gtsplit:
            prompts = []          
            starttime = time.time()
            print("start split")
            cb = CallbackManager.configure(inheritable_callbacks=callbacks)
            with trace_as_chain_group(
                callback_group_name, callback_manager=cb
            ) as batch_group:
                for q, a, g in zip(question, answer, ground_truths):
                    human_prompt = CORRECTNESS_PROMPT_SPLIT.format(
                        question=q, ground_truth=g[0]
                    )
                    prompts.append(ChatPromptTemplate.from_messages([human_prompt]))

            result = self.llm.generate(prompts, callbacks=batch_group)
            outputs = result.generations

            for prediction in outputs:
                alltext = prediction[0].text
                print(alltext)
                if alltext[-1] == '.':
                    alltext = alltext[:-1]
                gtsplitnum  = json.loads(alltext)
                if len(gtsplitnum) >= 20 :
                    alltext = json.dumps(gtsplitnum[:20])         
                gtsplit.append(alltext)
            endtime = time.time()
            print("the time for spliting:", endtime-starttime)
        else:
            gtsplit = dataset["gt_split_point"]
        starttime = time.time()
        promptstep2 = []
        cb = CallbackManager.configure(inheritable_callbacks=callbacks)
        with trace_as_chain_group(
            callback_group_name, callback_manager=cb
        ) as batch_group:
            for q, a, g, s in zip(question, answer, ground_truths, gtsplit):
                human_prompt = CORRECTNESS_PROMPT_SCORE.format(
                    question=q, ground_truth=s, answer=a
                )
                promptstep2.append(ChatPromptTemplate.from_messages([human_prompt]))

        result = self.llm.generate(promptstep2, callbacks=batch_group)
        outputs = result.generations

        for prediction in outputs:             
            alltext = prediction[0].text
            include_times = 0
            statement_times = 0
            notinclude_times = 0
            analyse.append(alltext)
            alljson = json_loader.safe_load(alltext,self.llm)
            for statementoutput in alljson:
                statement_times += 1
                includeornot = statementoutput['Output']
                if includeornot == 'include' or includeornot == 'partially include':  
                    include_times += 1
                if includeornot == 'not include':
                    notinclude_times += 1
            score_temp = include_times/statement_times        
            print("评分: ", score_temp, "include nums: ", include_times, "not include nums: ", notinclude_times, "allstatement nums: ", statement_times)
            score.append(score_temp)
        endtime = time.time()
        print("score time : ", endtime-starttime)

        return list(zip(gtsplit, analyse, score))


answer_recall_bisheng = AnswerRecallBisheng()
