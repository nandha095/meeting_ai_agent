from dotenv import load_dotenv
load_dotenv()

from app.services.llm_extractor import llm_extract_intent_and_time

if __name__ == "__main__":
    text = "Next Friday evening around 8 PM IST should be fine."

    result = llm_extract_intent_and_time(text)

    print("\n===== LLM RESULT =====")
    print(result)
