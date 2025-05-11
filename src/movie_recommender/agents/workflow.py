from langgraph.graph import StateGraph
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
import os

from ..models.state import AgentState
from ..database.neo4j_client import Neo4jClient

class MovieRecommendationAgent:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
            
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0,
            api_key=api_key
        )
        self.db_client = Neo4jClient()
        self.workflow = self._create_workflow()

    def _extract_genres(self, state: AgentState) -> AgentState:
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a movie genre extraction expert. 
            Extract ALL relevant movie genres from the user's input.
            Return ONLY the genre names as a comma-separated list, nothing else.
            Common genres include: Action, Adventure, Animation, Comedy, Crime, Documentary, 
            Drama, Fantasy, Horror, Mystery, Romance, Sci-Fi, Thriller.
            Example: If user says "I like comedy and crime movies", return "Comedy, Crime".
            Example: If user says "I enjoy sci-fi and action films", return "Sci-Fi, Action"."""),
            MessagesPlaceholder(variable_name="messages"),
        ])
        
        chain = prompt | self.llm | StrOutputParser()
        genres_str = chain.invoke({"messages": state["messages"]})
        
        genres = [genre.strip() for genre in genres_str.split(",")]
        return {**state, "extracted_genres": genres}

    def _get_recommendations(self, state: AgentState) -> AgentState:
        recommendations = self.db_client.get_movie_recommendations(state["extracted_genres"])
        return {**state, "recommendations": recommendations}

    def _generate_explanation(self, state: AgentState) -> AgentState:
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a movie recommendation expert. 
            Generate a brief, friendly explanation of why these movies were recommended.
            Consider the user's original input and the genres that were extracted.
            Mention that the recommendations are randomly selected from movies that match ALL the specified genres."""),
            ("human", f"User input: {state['user_input']}\nGenres: {', '.join(state['extracted_genres'])}\nMovies: {', '.join(state['recommendations'])}"),
        ])
        
        chain = prompt | self.llm | StrOutputParser()
        explanation = chain.invoke({})
        
        return {**state, "explanation": explanation}

    def _create_workflow(self):
        workflow = StateGraph(AgentState)

        # Add nodes
        workflow.add_node("extract_genres", self._extract_genres)
        workflow.add_node("get_recommendations", self._get_recommendations)
        workflow.add_node("generate_explanation", self._generate_explanation)

        # Add edges
        workflow.add_edge("extract_genres", "get_recommendations")
        workflow.add_edge("get_recommendations", "generate_explanation")
        workflow.set_entry_point("extract_genres")
        workflow.set_finish_point("generate_explanation")

        return workflow.compile()

    def get_recommendations(self, user_input: str) -> AgentState:
        initial_state = {
            "messages": [HumanMessage(content=user_input)],
            "user_input": user_input,
            "extracted_genres": [],
            "recommendations": [],
            "explanation": ""
        }
        return self.workflow.invoke(initial_state) 