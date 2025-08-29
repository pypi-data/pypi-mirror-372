from __future__ import annotations

import typing as t
from dataclasses import dataclass, field

import numpy as np
from datasets import Dataset
from langchain.callbacks.manager import CallbackManager, trace_as_chain_group
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate

from bisheng_ragas.metrics._answer_similarity import AnswerSimilarity
from bisheng_ragas.metrics.base import EvaluationMode, MetricWithLLM
from bisheng_ragas.utils import json_loader

if t.TYPE_CHECKING:
    from langchain.callbacks.base import Callbacks

CORRECTNESS_PROMPT = HumanMessagePromptTemplate.from_template(
    """
Extract following from given question and ground truth

Question:What powers the sun and what is its primary function?
Answer: The sun is powered by nuclear fission, similar to nuclear reactors on Earth, and its primary function is to provide light to the solar system.
Ground truth: The sun is actually powered by nuclear fusion, not fission. In its core, hydrogen atoms fuse to form helium, releasing a tremendous amount of energy. This energy is what lights up the sun and provides heat and light, essential for life on Earth. The sun's light also plays a critical role in Earth's climate system and helps to drive the weather and ocean currents.
Extracted statements:
[
{{
  "statements that are present in both the answer and the ground truth": ["The sun's primary function is to provide light"],
  "statements present in the answer but not found in the ground truth": ["The sun is powered by nuclear fission", "similar to nuclear reactors on Earth"],
  "relevant statements found in the ground truth but omitted in the answer": ["The sun is powered by nuclear fusion, not fission", "In its core, hydrogen atoms fuse to form helium, releasing a tremendous amount of energy", "This energy provides heat and light, essential for life on Earth", "The sun's light plays a critical role in Earth's climate system", "The sun helps to drive the weather and ocean currents"]
}}
]

Question: What is the boiling point of water?
Answer: The boiling point of water is 100 degrees Celsius at sea level.
Ground truth: The boiling point of water is 100 degrees Celsius (212 degrees Fahrenheit) at sea level, but it can change with altitude.
Extracted statements:
[
  {{
    "statements that are present in both the answer and the ground truth": ["The boiling point of water is 100 degrees Celsius at sea level"],
    "statements present in the answer but not found in the ground truth": [],
    "relevant statements found in the ground truth but omitted in the answer": ["The boiling point can change with altitude", "The boiling point of water is 212 degrees Fahrenheit at sea level"]
  }}
]

Question: 公司2021年的研发费用占营业收入的比例是多少？
Answer: 根据提供的信息，公司2021年的研发费用占营业收入的比例为15.86%。
Ground truth: 根据公司招股书披露数据，公司2021年的研发费用占营业收入的比例为15.86%。
Extracted statements:
[
  {{
    "statements that are present in both the answer and the ground truth": ["公司2021年的研发费用占营业收入的比例为15.86%"],
    "statements present in the answer but not found in the ground truth": [],
    "relevant statements found in the ground truth but omitted in the answer": []
  }}
]

Question: 达梦2021年的息税折旧摊销前利润是多少？
Answer: 达梦2021年的息税折旧摊销前利润为49,189.87万元。
Ground truth: 根据达梦数据库招股书披露数据，达梦2021年的息税折旧摊销前利润为49,189.85万元。
Extracted statements:
[
  {{
    "statements that are present in both the answer and the ground truth": [],
    "statements present in the answer but not found in the ground truth": ["达梦2021年的息税折旧摊销前利润为49,189.87万元"],
    "relevant statements found in the ground truth but omitted in the answer": ["根据达梦数据库招股书披露数据，达梦2021年的息税折旧摊销前利润为49,189.85万元"]
  }}
]

Question: 达梦2022年的应收账款周转率是多少？
Answer: 根据提供的信息，无法得知达梦2022年的应收账款周转率。
Ground truth: 很抱歉，达梦尚未披露2022年报数据。
Extracted statements:
[
  {{
    "statements that are present in both the answer and the ground truth": ["无法得知达梦2022年的应收账款周转率"],
    "statements present in the answer but not found in the ground truth": [],
    "relevant statements found in the ground truth but omitted in the answer": [],
  }}
]


Question:{question}
Answer: {answer}
Ground truth: {ground_truth}
Extracted statements:"""  # noqa: E501
)


@dataclass
class AnswerCorrectnessBisheng(MetricWithLLM):
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

    name: tuple = (
        "statements_gt_only",
        "statements_num_gt_only",
        "statements_answer_only",
        "statements_num_answer_only",
        "statements_overlap",
        "statements_num_overlap",
        "answer_f1",
        "answer_precision",
        "answer_recall",
    )
    evaluation_mode: EvaluationMode = EvaluationMode.qga  # type: ignore[reportIncompatibleMethodOverride]
    batch_size: int = 15
    human_prompt: str = ""

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
        prompts = []

        prompt_template = HumanMessagePromptTemplate.from_template(self.human_prompt) if self.human_prompt else CORRECTNESS_PROMPT
        cb = CallbackManager.configure(inheritable_callbacks=callbacks)
        with trace_as_chain_group(callback_group_name, callback_manager=cb) as batch_group:
            for q, a, g in zip(question, answer, ground_truths):
                human_prompt = prompt_template.format(question=q, ground_truth=g[0], answer=a)
                prompts.append(ChatPromptTemplate.from_messages([human_prompt]))

        result = self.llm.generate(prompts, callbacks=batch_group)
        outputs = result.generations
        key_map = {
            "TP": "statements that are present in both the answer and the ground truth",
            "FP": "statements present in the answer but not found in the ground truth",
            "FN": "relevant statements found in the ground truth but omitted in the answer",  # noqa: E501
        }

        f1_score = []
        precision_score = []
        recall_score = []
        statements_gt_only = []
        statements_answer_only = []
        statements_overlap = []
        statements_num_gt_only = []
        statements_num_answer_only = []
        statements_num_overlap = []
        for prediction in outputs:
            prediction = json_loader.safe_load(prediction[0].text, self.llm)
            prediction = prediction if isinstance(prediction, list) else []
            if prediction:
                prediction = [item.get(key_map[k], '') for item in prediction for k in key_map.keys()]
                statements_gt_only.append(str(prediction[2]))
                statements_answer_only.append(str(prediction[1]))
                statements_overlap.append(str(prediction[0]))
                tp, fp, fn = [len(item) if isinstance(item, list) else np.nan for item in prediction]
                statements_num_gt_only.append(fn)
                statements_num_answer_only.append(fp)
                statements_num_overlap.append(tp)
                score = tp / (tp + 0.5 * (fp + fn))
                precision_score.append(tp / (tp + fp) if (tp + fp)!=0 else np.nan)
                recall_score.append(tp / (tp + fn) if (tp + fn)!=0 else np.nan)
            else:
                statements_gt_only.append('')
                statements_answer_only.append('')
                statements_overlap.append('')
                statements_num_gt_only.append(np.nan)
                statements_num_answer_only.append(np.nan)
                statements_num_overlap.append(np.nan)
                score = np.nan
                precision_score.append(np.nan)
                recall_score.append(np.nan)

            f1_score.append(score)

        return list(
            zip(
                statements_gt_only,
                statements_num_gt_only,
                statements_answer_only,
                statements_num_answer_only,
                statements_overlap,
                statements_num_overlap,
                f1_score,
                precision_score,
                recall_score,
            )
        )


answer_correctness_bisheng = AnswerCorrectnessBisheng()
