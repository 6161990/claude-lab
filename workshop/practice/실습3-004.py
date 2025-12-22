import os
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

# API KEY 설정 (실행 환경에 맞게 설정해주세요)
# os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"

# 1. 모델 및 파서 정의
try:
    model = ChatOpenAI(model="gpt-4o")
except Exception as e:
    print(f"모델 초기화 중 오류가 발생했습니다: {e}")
    print("OPENAI_API_KEY 환경변수가 올바르게 설정되었는지 확인하세요.")
    # 실행 흐름을 보여주기 위해 더미 모델로 대체합니다.
    from langchain_core.runnables import RunnableLambda
    model = RunnableLambda(lambda x: "This is a dummy response from a fake model.")

parser = StrOutputParser()

# 2. 프롬프트 템플릿 정의
translate_prompt = ChatPromptTemplate.from_template("Translate the following English text to Korean: {text}")
summarize_prompt = ChatPromptTemplate.from_template("Summarize the following text in 3 key bullet points in Korean:\n\n{korean_text}")

# 3. 체인 구성 (LCEL)
# TODO: 번역 체인과 요약 체인을 '|' 연산자로 연결하여 최종 체인을 완성하세요.

# 첫 번째 체인: 영문 텍스트를 입력받아 한글로 번역합니다.
# 입력: {"text": "..."} -> 출력: "번역된 한글 문자열"
translate_chain = translate_prompt | model | parser

# 최종 체인: 번역 체인의 출력을 다음 체인의 입력으로 연결합니다.
# translate_chain의 출력(한글 문자열)을
# summarize_prompt가 요구하는 입력 형식인 {"korean_text": "..."} 딕셔너리에 매핑해줍니다.
final_chain = {"korean_text": translate_chain} | summarize_prompt | model | parser


# 4. 실행
english_text = "LangChain Expression Language (LCEL) is a declarative way to compose chains, making it easy to build complex applications by combining modular components."
result = final_chain.invoke({"text": english_text})
print(result)