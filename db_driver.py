import sqlite3
from typing import Optional, List
from dataclasses import dataclass
from contextlib import contextmanager

@dataclass
class Student:
    student_id: int
    name: str
    language: str
    skill_level: str  # e.g., Beginner, Intermediate, Advanced
    strengths: str
    weaknesses: str

class StudentDatabase:
    def __init__(self, db_path: str = "language_students.sqlite"):
        self.db_path = db_path
        self._init_db()

    @contextmanager
    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enables dict-like row access
        try:
            yield conn
        finally:
            conn.close()

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS students (
                    student_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    language TEXT NOT NULL,
                    skill_level TEXT NOT NULL CHECK(skill_level IN ('Beginner', 'Intermediate', 'Advanced')),
                    strengths TEXT,
                    weaknesses TEXT
                )
            """)
            conn.commit()

    def add_student(self, name: str, language: str, skill_level: str, strengths: str, weaknesses: str) -> Student:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO students (name, language, skill_level, strengths, weaknesses) VALUES (?, ?, ?, ?, ?)",
                (name, language, skill_level, strengths, weaknesses)
            )
            conn.commit()
            student_id = cursor.lastrowid
            return Student(student_id, name, language, skill_level, strengths, weaknesses)

    def get_student_by_id(self, student_id: int) -> Optional[Student]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM students WHERE student_id = ?", (student_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return Student(student_id=row["student_id"], name=row["name"], language=row["language"],
                           skill_level=row["skill_level"], strengths=row["strengths"], weaknesses=row["weaknesses"])

    def get_all_students(self) -> List[Student]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM students")
            rows = cursor.fetchall()
            return [Student(student_id=row["student_id"], name=row["name"], language=row["language"],
                            skill_level=row["skill_level"], strengths=row["strengths"], weaknesses=row["weaknesses"])
                    for row in rows]

    def update_student(self, student_id: int, skill_level: Optional[str] = None, strengths: Optional[str] = None, weaknesses: Optional[str] = None) -> bool:
        if not any([skill_level, strengths, weaknesses]):
            return False  # No updates provided

        updates = []
        values = []

        if skill_level:
            updates.append("skill_level = ?")
            values.append(skill_level)
        if strengths:
            updates.append("strengths = ?")
            values.append(strengths)
        if weaknesses:
            updates.append("weaknesses = ?")
            values.append(weaknesses)

        values.append(student_id)

        query = f"UPDATE students SET {', '.join(updates)} WHERE student_id = ?"

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, values)
            conn.commit()
            return cursor.rowcount > 0  # Returns True if a row was updated

    def delete_student(self, student_id: int) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM students WHERE student_id = ?", (student_id,))
            conn.commit()
            return cursor.rowcount > 0  # Returns True if a row was deleted
