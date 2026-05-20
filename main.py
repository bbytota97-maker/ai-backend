from fastapi import FastAPI
from dotenv import load_dotenv

load_dotenv()

from dedalus_labs import AsyncDedalus, DedalusRunner

app = FastAPI()

client = AsyncDedalus()
runner = DedalusRunner(client)

@app.get("/")
def home():
    return {"status": "online"}

@app.get("/run")
async def run(query: str):
    result = await runner.run(
        input=query,
        model="openai/gpt-5-nano",
        mcp_servers=["windsor/brave-search-mcp"]
    )

    return {"output": result.final_output}