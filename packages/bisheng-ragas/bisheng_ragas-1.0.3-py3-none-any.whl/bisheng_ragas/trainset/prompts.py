from langchain.prompts import HumanMessagePromptTemplate

SEED_QUESTION = HumanMessagePromptTemplate.from_template(
    """\
您的任务是遵循以下规则从给定的上下文中提出一个问题，规则如下：

    1. 即使在没有给定上下文的情况下，问题也应该对人类有意义。
    2. 应该可以从给定上下文中完全回答问题。
    3. 问题应该来自包含重要信息的上下文部分。它也可以来自表格、段落、或者代码等。
    4. 回答问题时不应包含任何链接。
    5. 问题的难度应该是中等的。
    6. 问题必须是合理的，并且必须能被人理解和回答。
    7. 不要在问题中使用“提供的上下文”等短语。
    8. 避免使用可以分解成多个问题的“和”字样来构建问题。
    9. 问题不应该包含超过10个单词，尽可能使用缩写。
    10. 如果上下文是中文，那么问题也应该是中文的。

Examples:
context:武汉达梦数据库股份有限公司 招股说明书 （申报稿） 1-1-226 表中作出恰当列报。 2、研发费用 2021年度、 2020年度、 2019 年度，达梦数据 研发费用金额分别 为11,786.99 万元、 9,660.26 万元、 6,255.86万元， 各年度研发费用占营 业收入的比例分别为 15.86 % 、 21.46 %、20.74 %。 由于研发投入金额及其占当期 营业收入的比例是 达梦数据 的关键 指标之一，可能存在因为核算不准 确而导致的错报风险。因此， 中天 运会计师 将研发费用的归集和核算 确定为关键审计事项。 针对研发费用的真实性与准确性，会计师执行的 重要审计程序主要包括： （1）了解与研发费用相关的关键内部控制，评价 这些控制的设计，确定其是否得到执行，并对相关内 部控制的运行有效性进行测试； （2）获取研发项目立项、审批资料，抽查重要研 发项目的过程文档，判断研发项目的真实性； （3）获取研发费用按项目、性质分类明细表，分
question:达梦2021年的研发费用占营业收入的比例是多少？

context:武汉达梦数据库股份有限公司 招股说明书 （申报稿） 1-1-329 （2）存货周转率 公司与同行业可比公司存货周转率对比情况如下： 公司简称 2021年度 2020年度 2019年度 中望软件 6.93 5.62 10.66 星环科技 3.38 3.21 2.24 金山办公 212.60 175.46 162.91 平均值 74.30 61.43 58.60 本公司 1.13 0.57 0.87 数据来源：可比公司招股说明书、定期报告。 报告期各期， 公司存货周转率显著低于同行业可比公司存货周转率平均水平， 主要是因为公司将未验收的数据及行业解决方案项目所发生的累 计成本均作为 存货核算。报告期各期末，公司存在 “湖北省司法行政数据中心项目 ”、“政法云 大数据中心基础设施服务及大数据中心软件采购 项目”等金额较大且实施周期较 长的数据及行业解决方案项目，导致年末存货金额较大。
question:达梦2021年的存货周转率相较于前一年有何变化？

-------------------
context:{context}
question:
"""  # noqa: E501
)


REASONING_QUESTION = HumanMessagePromptTemplate.from_template(
    """\
You are a prompt rewriter. You will be provided with a question and a long context.Your task to is to complicate the given question to improve the difficulty of answering. 
You should do complicate the question by rewriting question into a multi-hop reasoning question based on the provided context. The question should require the reader to make multiple logical connections or inferences using the information available in given context. 
Here are some strategies to create multi-hop questions:

   - Bridge related entities: Identify information that relates specific entities and frame question that can be answered only by analysing information of both entities.
   
   - Use Pronouns: identify (he, she, it, they) that refer to same entity or concepts in the context, and ask questions that would require the reader to figure out what pronouns refer to.

   - Refer to Specific Details: Mention specific details or facts from different parts of the context including tables, code, etc and ask how they are related.

   - Pose Hypothetical Scenarios: Present a hypothetical situation or scenario that requires combining different elements from the context to arrive at an answer.

Rules to follow when rewriting question:
1. Ensure that the rewritten question can be answered entirely from the information present in the contexts.
2. Do not frame questions that contains more than 15 words. Use abbreviation wherever possible.
3. Make sure the question is clear and unambiguous. 
4. phrases like 'based on the provided context','according to the context',etc are not allowed to appear in the question.

question: {question}
CONTEXTS:
{context}

Multi-hop Reasoning Question:
"""  # noqa: E501
)

MULTICONTEXT_QUESTION = HumanMessagePromptTemplate.from_template(
    """\
You are a prompt rewriter. You will be provided with a question and two set of contexts namely context1 and context2. 
Your task is to complicate the given question in a way that answering it requires information derived from both context1 and context2. 
Follow the rules given below while rewriting the question.
    1. The rewritten question should not be very long. Use abbreviation wherever possible.
    2. The rewritten question must be reasonable and must be understood and responded by humans.
    3. The rewritten question must be fully answerable from information present in context1 and context2. 
    4. Read and understand both contexts and rewrite the question so that answering requires insight from both context1 and context2.
    5. phrases like 'based on the provided context','according to the context?',etc are not allowed to appear in the question.

question:\n{question}
context1:\n{context1}
context2:\n{context2}
"""  # noqa: E501
)


CONDITIONAL_QUESTION = HumanMessagePromptTemplate.from_template(
    """\
Rewrite the provided question to increase its complexity by introducing a conditional element.
The goal is to make the question more intricate by incorporating a scenario or condition that affects the context of the question.
Follow the rules given below while rewriting the question.
    1. The rewritten question should not be longer than 25 words. Use abbreviation wherever possible.
    2. The rewritten question must be reasonable and must be understood and responded by humans.
    3. The rewritten question must be fully answerable from information present context.
    4. phrases like 'provided context','according to the context?',etc are not allowed to appear in the question.
for example,
question: What are the general principles for designing prompts in LLMs?
Rewritten Question:how to apply prompt designing principles to improve LLMs performance in reasoning tasks

question:{question}
context:\n{context}
Rewritten Question
"""  # noqa: E501
)


COMPRESS_QUESTION = HumanMessagePromptTemplate.from_template(
    """\
Rewrite the following question to make it more indirect and shorter while retaining the essence of the original question. The goal is to create a question that conveys the same meaning but in a less direct manner.
The rewritten question should shorter so use abbreviation wherever possible.
Original Question:
{question}

Indirectly Rewritten Question:
"""  # noqa: E501
)


CONVERSATION_QUESTION = HumanMessagePromptTemplate.from_template(
    """\
Reformat the provided question into two separate questions as if it were to be part of a conversation. Each question should focus on a specific aspect or subtopic related to the original question.
question: What are the advantages and disadvantages of remote work?
Reformatted Questions for Conversation: What are the benefits of remote work?\nOn the flip side, what challenges are encountered when working remotely?
question:{question}

Reformatted Questions for Conversation:
"""  # noqa: E501
)


SCORE_CONTEXT = HumanMessagePromptTemplate.from_template(
    """Evaluate the provided context and assign a numerical score between 0 and 10 based on the following criteria:
1. Award a high score to context that thoroughly delves into and explains concepts.
2. Assign a lower score to context that contains excessive references, acknowledgments, external links, personal information, or other non-essential elements.
Output the score only.
Context:
{context}
Score:
"""  # noqa: E501
)

FILTER_QUESTION = HumanMessagePromptTemplate.from_template(
    """\
Determine if the given question can be clearly understood even when presented without any additional context. Specify reason and verdict is a valid json format.

question: What is the discovery about space?
{{
    "reason":"The question is too vague and does not specify which discovery about space it is referring to."
    "verdit":"No"
}}

question: What caused the Great Depression?
{{
    "reason":"The question is specific and refers to a well-known historical economic event, making it clear and answerable.",
    "verdict":"Yes"
}}

question: What is the keyword that best describes the paper's focus in natural language understanding tasks?
{{
    "reason": "The question mentions a 'paper' in it without referring it's name which makes it unclear without it",
    "verdict": "No"
}}

question: Who wrote 'Romeo and Juliet'?
{{
    "reason": "The question is clear and refers to a specific work by name therefore it is clear",
    "verdict": "Yes"
}}

question: What did the study mention?
{{
    "reason": "The question is vague and does not specify which study it is referring to",
    "verdict": "No"
}}

question: What is the focus of the REPLUG paper?
{{
    "reason": "The question refers to a specific work by it's name hence can be understood", 
    "verdict": "Yes"
}}

question:{question}
"""  # noqa: E501
)


ANSWER_FORMULATE = HumanMessagePromptTemplate.from_template(
    """\
Answer the question using the information from the given context. 

context:{context}

question:{question}
answer:
"""  # noqa: E501
)

CONTEXT_FORMULATE = HumanMessagePromptTemplate.from_template(
    """Please extract relevant sentences from the provided context that can potentially help answer the following question. While extracting candidate sentences you're not allowed to make any changes to sentences from given context.

question:{question}
context:\n{context}
candidate sentences:\n
"""  # noqa: E501
)
