from typing import List, TypedDict, Annotated, Sequence
from langchain_core.messages import HumanMessage, AIMessage
from pydantic import BaseModel, Field

class AgentState(TypedDict):
    messages: Annotated[Sequence[HumanMessage | AIMessage], "The messages in the conversation"]
    user_input: str
    extracted_genres: List[str]
    recommendations: List[str]
    explanation: str

class GenreInput(BaseModel):
    genres: List[str] = Field(description="List of movie genres to search for") 