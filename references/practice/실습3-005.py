import os
from typing import List
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

# API KEY 설정 (실행 환경에 맞게 설정해주세요)
# os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"

# --- 1. Pydantic 모델 정의 ---
# 추출하고 싶은 데이터의 구조를 Pydantic 클래스로 명확하게 정의합니다.
# 각 필드에 대한 설명(description)은 LLM이 어떤 정보를 추출해야 하는지 이해하는 데 도움을 줍니다.
class Resume(BaseModel):
    """Extracts key information from a resume text."""
    name: str = Field(description="Candidate's full name")
    contact_email: str = Field(description="Candidate's email address")
    total_experience_years: int = Field(description="Total years of professional experience, calculated as an integer")
    skills: List[str] = Field(description="List of key technical or professional skills mentioned")

# --- 2. 모델 및 프롬프트 정의 ---
try:
    # Pydantic 모델의 스키마를 보고 JSON을 생성하는 능력이 좋은 모델을 사용하는 것이 좋습니다.
    llm = ChatOpenAI(model="gpt-4o")
except Exception as e:
    print(f"모델 초기화 중 오류가 발생했습니다: {e}")
    print("OPENAI_API_KEY 환경변수가 올바르게 설정되었는지 확인하세요.")
    # 실행 흐름을 보여주기 위해 더미 모델로 대체합니다.
    from langchain_core.runnables import RunnableLambda
    llm = RunnableLambda(lambda x: "This is a dummy response. Pydantic parsing will likely fail.")

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert at extracting information from unstructured text and formatting it into a structured JSON object. Your output must strictly conform to the provided JSON schema."),
    ("human", "Please extract the required information from the following text:\n\n{resume_text}")
])


# --- 3. 구조화된 출력 체인 생성 (Structured Output Chain) ---
# .with_structured_output() 메서드에 Pydantic 모델을 전달하는 것이 핵심입니다.
# 이 메서드는 LLM의 출력이 Resume 모델의 스키마를 따르도록 강제합니다.
structured_chain = prompt | llm.with_structured_output(Resume)


# --- 4. 실행 및 검증 ---
# 자유 형식의 이력서 텍스트 데이터
unstructured_resume_text = """
김철수 (Cheol-su Kim)
- 연락처: chulsu.kim@example.com
- 소개: 안녕하세요. 저는 2020년에 입사하여 지금까지 약 5년 간 성장해온 백엔드 개발자입니다.
주요 기술 스택은 Python과 Java이며, AWS를 이용한 클라우드 인프라 운영 경험도 풍부합니다.
최근에는 머신러닝 기술을 서비스에 접목하는 프로젝트에 큰 관심을 두고 있습니다.
"""

# 체인을 실행하면, LLM의 JSON 출력이 자동으로 Resume 객체로 파싱됩니다.
result_object = structured_chain.invoke({"resume_text": unstructured_resume_text})


# --- 5. 결과 확인 ---
print("--- Extracted Information (as Pydantic Object) ---")
print(result_object)
print("\n--- Accessing Data ---")
print(f"Name: {result_object.name}")
print(f"Email: {result_object.contact_email}")
print(f"Experience: {result_object.total_experience_years} years")
print(f"First Skill: {result_object.skills[0]}")