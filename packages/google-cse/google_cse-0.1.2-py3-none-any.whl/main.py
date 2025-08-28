from dotenv import load_dotenv
load_dotenv()

import os
from google_cse import GoogleCSE


client = GoogleCSE(
    api_key=os.getenv("GOOGLE_API_KEY"),
    search_engine_id=os.getenv("GOOGLE_CSE_ENGINE_ID")
)

res = client.raw_search("OpenAI", num_results=5)

web_res = client.web_search("OpenAI", num_results=5)

image_res = client.image_search("OpenAI", num_results=5)

print()
