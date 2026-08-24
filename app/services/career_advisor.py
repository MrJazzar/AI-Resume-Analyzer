from app.rag.pipeline import RAGPipeline


class CareerAdvisor:
    def __init__(self):
        self.rag = RAGPipeline()

    def get_resume_skills(self, analysis):
        technical_skills = analysis.technical_skills or ""

        if isinstance(technical_skills, str):
            return [
                skill.strip()
                for skill in technical_skills.split(",")
                if skill.strip()
            ]

        return technical_skills

    def find_missing_skills(
        self,
        current_skills: list[str],
        target_career: str,
    ):
        result = self.rag.ask(
            f"""
            For the career path "{target_career}", identify the important
            technical skills required for this career.

            Current skills:
            {", ".join(current_skills)}

            Return JSON:
            {{
                "required_skills": [],
                "missing_skills": []
            }}
            """
        )

        return result

    def get_learning_path(
        self,
        current_skills: list[str],
        target_career: str,
    ):
        return self.rag.ask(
            f"""
            Create a learning path for someone who wants to become
            a "{target_career}".

            Current skills:
            {", ".join(current_skills)}

            Focus on the missing skills and organize them in learning order.

            Return JSON:
            {{
                "learning_path": [],
                "resources": []
            }}
            """
        )

    def get_career_advice(
        self,
        current_skills: list[str],
        target_career: str,
    ):
        return self.rag.ask(
            f"""
            Give personalized career advice for someone targeting
            "{target_career}".

            Current skills:
            {", ".join(current_skills)}

            Include:
            - missing skills
            - what to learn first
            - recommended projects
            - useful certifications
            - resume improvements

            Return JSON:
            {{
                "career": "",
                "missing_skills": [],
                "learning_path": [],
                "projects": [],
                "certifications": [],
                "resume_improvements": []
            }}
            """
        )