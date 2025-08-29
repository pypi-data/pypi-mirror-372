from dataclasses import dataclass
from os.path import exists
from typing import Any
import yaml


@dataclass
class UserInfoJson:
    email: str


@dataclass
class QuizInfo:
    min_supported_app_version: str = ""


@dataclass
class VariableJson:
    param_name: str
    param_type: str
    param_value: str


@dataclass
class TestCaseJson:
    inputs: list[VariableJson]
    expected: VariableJson


@dataclass
class QuestionJson:
    id: int
    title: str
    text: str
    code_template: str
    code: str
    test_cases: list[TestCaseJson]
    is_passed: str


@dataclass
class PythonQuizJson:
    id: str
    title: str
    questions: list[QuestionJson]


@dataclass
class JsonLoadResult:
    user_info: UserInfoJson
    quizes: list[PythonQuizJson]
    quiz_info: QuizInfo


def get_quiz_json(file_path: str) -> JsonLoadResult:
    if not exists(file_path):
        raise FileExistsError(f"<{file_path}> not found")
    load_result = JsonLoadResult(
        quiz_info=QuizInfo(),
        user_info=UserInfoJson(email=""),
        quizes=[]
    )
    with open(file_path, encoding='UTF-8') as f:
        yaml_data = yaml.safe_load(f)
        load_result.user_info.email = yaml_data["user_info"]["email"]
        load_result.quiz_info.min_supported_app_version = yaml_data[
            "quiz_info"]["min_supported_app_version"]
        # map quizes
        yaml_quizes: dict[str, dict[str, Any]] = yaml_data["quizes"]
        last_question_id = 0
        for quiz_id, quiz_content in yaml_quizes.items():
            quiz_obj = PythonQuizJson(
                id=quiz_id,
                title=quiz_content["title"],
                questions=[]
            )
            # map questions
            question_dict: dict[str, Any] = quiz_content["questions"]
            for q_title, q_content in question_dict.items():
                quiz_obj.questions.append(
                    QuestionJson(
                        id=last_question_id,
                        title=q_title,
                        text=q_content["text"],
                        code_template=q_content["code_template"],
                        code=q_content["code"],
                        test_cases=_get_test_cases(
                            q_content
                        ),
                        is_passed=q_content.get("is_passed", "")
                    )
                )
                last_question_id += 1
            load_result.quizes.append(quiz_obj)
    return load_result


def _get_test_cases(question_content: dict[str, Any]) -> list[TestCaseJson]:
    def parse_param_value(param_name: str, param_val: str) -> VariableJson:
        func_descr_params = question_content["params"]
        if param_name not in func_descr_params:
            raise ValueError(
                f"No param type for {param_name} parameter"
            )
        ptype = func_descr_params[param_name]
        return VariableJson(
            param_name=param_name,
            param_type=ptype,
            param_value=param_val)

    def parse_param(case_yaml: dict[str, str]) -> TestCaseJson:
        exp = VariableJson(
            param_name="expected",
            param_type=question_content["params"]["return"],
            param_value=case_yaml["expected"]
        )
        inputs = [parse_param_value(p_name, p_val)
                  for p_name, p_val
                  in case_yaml.items() if p_name != "expected"]

        return TestCaseJson(
            inputs=inputs,
            expected=exp
        )

    return [
        parse_param(case_yaml) for case_yaml in question_content["test_cases"]
    ]
