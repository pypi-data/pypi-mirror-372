from ultragpt import UltraGPT
from pydantic import BaseModel
from typing import List
import dotenv
import os

# Load environment variables
dotenv.load_dotenv()

class ToolAnalysisSchema(BaseModel):
    tools: List[str]

if __name__ == "__main__":

    api_key = os.getenv("OPENAI_API_KEY")
    ultragpt = UltraGPT(
        api_key=api_key,
        verbose=True
    )

    memory, total_tokens, dict = ultragpt.chat([
        {
            "role": "system",
            "content": "You are a helpful assistant that can perform calculations and answer questions about numbers."
        },
        {
            "role": "user",
            "content": "If I have 8 balls and I give person A 2 balls, and person B 4 balls, how many balls do I have left?"
        }],
        schema=ToolAnalysisSchema
        )

    print("Memory:", memory)
    print("Total tokens used:", total_tokens)
