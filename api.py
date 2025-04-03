from livekit.agents import llm
import enum
from typing import Annotated
import logging
from db_driver import StudentDatabase

logger = logging.getLogger("user-data")
logger.setLevel(logging.INFO)

DB = StudentDatabase()

class StudentDeatils(enum.Enum):
    Student_id = "student_id"
    Name = "name"
    Language = "language"
    Skill_Level = "skill_level"  # e.g., Beginner, Intermediate, Advanced
    Strengths = "strengths"
    Weaknesses = "weaknesses"

class TutorFnc(llm.FunctionContext):
    def __init__(self):
        super().__init__()

        self._student_details = {
            StudentDeatils.Student_id: "",
            StudentDeatils.Name: "",
            StudentDeatils.Language: "",
            StudentDeatils.Skill_Level: "",
            StudentDeatils.Strengths: "",
            StudentDeatils.Weaknesses: "",
        }
    
    def get_student_str(self):
        student_str = ""
        for key, value in self._student_details.items():
            student_str += f"{key}: {value}\n"

        return student_str

    @llm.ai_callable(description="get details on current student")
    def get_student_details(self):
        logger.info("get student details")
        return f"The student details are: {self.get_student_details()}"

    @llm.ai_callable(description="lookup a student by their ID")
    def lookup_car(self, student_id: Annotated[str, llm.TypeInfo(description="The student id of the student to lookup")]):
        logger.info("lookup student - student_id: %s", student_id)

        result = DB.get_student_by_id(student_id)
        if result is None:
            return "Student not found"
        
        self._student_details = {
            StudentDeatils.Student_id: result.student_id,
            StudentDeatils.Name: result.name,
            StudentDeatils.Language: result.language,
            StudentDeatils.Skill_Level: result.skill_level,
            StudentDeatils.Strengths: result.strengths,
            StudentDeatils.Weaknesses: result.weaknesses,
        }

        return f"The student details are: {self.get_student_str()}"
    
    @llm.ai_callable(description="Add a new student")
    def add_car(
        self, 
        student_id: Annotated[str, llm.TypeInfo(description="The student id of the student")],
        name: Annotated[str, llm.TypeInfo(description="The name of the student")],
        language: Annotated[str, llm.TypeInfo(description="The language of the student")],
        skill_level: Annotated[str, llm.TypeInfo(description="The skill level of the student")],
        strengths: Annotated[str, llm.TypeInfo(description="The strengths of the student")],
        weaknesses: Annotated[str, llm.TypeInfo(description="The weaknesses of the student")],
    ):
        logger.info("add student - student id: %s, name: %s, language: %s, skill level: %s, strengths: %s, weaknesses: %s", student_id, name, language, skill_level, strengths, weaknesses)
        result = DB.add_student(student_id, name, language, skill_level, strengths, weaknesses)
        if result is None:
            return "Failed to create car"
        
        self._student_details = {
            StudentDeatils.Student_id: result.student_id,
            StudentDeatils.Name: result.name,
            StudentDeatils.Language: result.language,
            StudentDeatils.Skill_Level: result.skill_level,
            StudentDeatils.Strengths: result.strengths,
            StudentDeatils.Weaknesses: result.weaknesses,
        }

        return "Student Added!"
    
    def has_student(self):
        return self._student_details[StudentDeatils.Student_id] != ""
