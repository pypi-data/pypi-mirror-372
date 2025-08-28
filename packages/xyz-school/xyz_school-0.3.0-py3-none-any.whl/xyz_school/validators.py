# -*- coding:utf-8 -*-
from __future__ import unicode_literals,print_function
__author__ = 'denishuang'
from xyz_util.validators import *


class StudentNumberValidator(RegexValidator):
    message = "学号格式不对"
    regex = "^\w{6,32}$"


valid_student_number = StudentNumberValidator()


class GradeValidator(RegexValidator):
    message = "年级格式不对"
    regex = "^(\d{2}|\d{4})级$"


valid_grade = GradeValidator()

class SessionValidator(RegexValidator):
    message = "届别格式不对"
    regex = "^(\d{2}|\d{4})"


valid_session = SessionValidator()



class StudentNumberField(BaseField):
    name = "学号"
    default_synonyms = ["学生编号"]
    default_validators = [valid_student_number]
    default_formaters = [format_not_float, format_banjiao]
    no_duplicate = True


field_student_number = StudentNumberField()

class WorkerNumberValidator(RegexValidator):
    message = "工号格式不对"
    regex = "^\w{4,12}$"


valid_worker_number = WorkerNumberValidator()


class WorkerNumberField(BaseField):
    name = "工号"
    default_validators = [valid_worker_number]
    default_formaters = [format_not_float, format_banjiao]
    ignore_invalid = True
    no_duplicate = True


field_worker_number = WorkerNumberField()


class CollegeField(BaseField):
    name = "院系"
    default_synonyms = ["学院", "教研室", "系别", "系部"]


field_college = CollegeField()


class MajorField(BaseField):
    name = "专业"
    default_synonyms = ["专业方向"]
    default_formaters = [format_banjiao]


field_major = MajorField()

def format_grade(v):
    if not v:
        return None
    if isinstance(v, int) or not v.endswith("级"):
        return "%s级" % v
    return v

class GradeField(BaseField):
    name = "年级"
    default_validators = [valid_grade]
    default_formaters = [format_not_float,   format_banjiao, format_str_without_space, format_grade]

field_grade = GradeField()


class SessionField(BaseField):
    name = "届别"
    default_synonyms = ["届"]
    default_validators = [valid_session]
    default_formaters = [format_not_float,  format_banjiao, format_str_without_space, format_grade]

field_session = SessionField()

class ClassField(BaseField):
    name = "班级"
    default_synonyms = ["班"]
    default_formaters = [format_not_float, text_type, format_banjiao, format_str_without_space]

field_class = ClassField()

# class SessionField(BaseField):
#     name = "届别"
#     default_synonyms = ["届"]
#     default_formaters = [format_not_float, text_type, format_banjiao, format_str_without_space]
#
# field_session = SessionField()


class InstructorField(BaseField):
    name = "辅导员"
    default_synonyms = ["辅导老师"]

field_instructor = InstructorField()


class IsInstructorField(BaseField):
    name = "辅导员"
    default_synonyms = ["辅导老师"]

field_is_instructor = IsInstructorField()


class CounsellorField(BaseField):
    name = "实习指导老师"
    default_synonyms = ["指导老师"]

field_counsellor = CounsellorField()


class IsCounsellorField(BaseField):
    name = "实习指导老师"
    default_synonyms = ["指导老师"]

field_is_counsellor = IsCounsellorField()

class DepartmentField(BaseField):
    name = "部门"
    default_synonyms = ["所在部门"]

field_department = DepartmentField()
