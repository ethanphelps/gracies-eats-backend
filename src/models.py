from pydantic import BaseModel
from typing import Optional


class Ingredient(BaseModel):
    name: str
    quantity: float # maybe a str that gets parsed, like amount-unit ?


class InstructionStep(BaseModel):
    description: str
    prePrep: bool


# for validating user creation and updating
class User(BaseModel):
    email: str
    firstName: str
    lastName: str


# for validating recipe creation and updating
class Recipe(BaseModel):
    id: Optional[str]
    name: str
    description: str = ""
    prepTime: str = "" # could create an hr-min format and parse it after retrieving from DB
    cookTime: str = ""
    serves: int
    ingredients: list[Ingredient]
    instructions: list[InstructionStep]