from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from database import query
from openai import OpenAI
import logging

app = FastAPI()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

class recipeRequest(BaseModel):
    ingredients: str

@app.get("/")
async def home():
    return JSONResponse(content={"message": "Working Fine"})


@app.post("/generate")
async def get_ingredients(data: recipeRequest):
    ingredient = data.ingredients

    # Safe SELECT
    recipes = query("SELECT * FROM recipes WHERE ingredient = %s", (ingredient,))
    logger.info(f"Query result: {recipes}")
    if len(recipes) > 0: 
        steps_from_db = recipes[0][2].split("\n")
        return JSONResponse(content={"message": "Data from DB", "recipe": steps_from_db})
    else:
        try:
            gemini_key = "AIzaSyAdfD6yDtOF6vbmoxVvtHcuG4SVPTMx_fg"
            client = OpenAI(
                api_key=gemini_key,
                base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
            )

            response = client.chat.completions.create(
                model="gemini-2.5-flash",
                messages=[
                    {"role": "system", "content": "You are an expert recipe generator."},
                    {"role": "user", "content": f"Give me recipes using these ingredients: {ingredient}"}
                ]
            )

            result_text = response.choices[0].message.content
            steps = result_text.split("\n")

            if not steps:
                return {"message": "No ingredients found for this recipe"}


            steps_text = "\n".join(steps)
            query("INSERT INTO recipes (ingredient, steps) VALUES (%s, %s)", (ingredient, steps_text))
        
            return {"message": "Data fetched from Gemini API", "recipe": steps}

        except Exception as e:
            logger.error(str(e))
            return {"message": "Error fetching data", "error": str(e)}
