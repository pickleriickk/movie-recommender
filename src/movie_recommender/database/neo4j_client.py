from neo4j import GraphDatabase
import os
from typing import List, Optional
import streamlit as st

class Neo4jClient:
    def __init__(self):
        self.uri = os.getenv("NEO4J_URI")
        self.user = os.getenv("NEO4J_USER")
        self.password = os.getenv("NEO4J_PASSWORD")
        
        if not all([self.uri, self.user, self.password]):
            raise ValueError("Missing Neo4j credentials in environment variables")
            
        self._driver = None

    def connect(self):
        """Establish connection to Neo4j database"""
        try:
            self._driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
            return self._driver
        except Exception as e:
            st.error(f"Failed to connect to Neo4j: {str(e)}")
            return None

    def close(self):
        """Close the Neo4j connection"""
        if self._driver:
            self._driver.close()

    def get_movie_recommendations(self, genres: List[str]) -> List[str]:
        """Query Neo4j for movie recommendations based on multiple genres"""
        driver = self.connect()
        if not driver:
            return []
        
        try:
            with driver.session() as session:
                query = """
                MATCH (m:Movie)-[:HAS_GENRE]->(g:Genre)
                WHERE g.name IN $genres
                WITH m, collect(g.name) as movieGenres
                WHERE all(genre in $genres WHERE genre in movieGenres)
                WITH m
                ORDER BY rand()
                RETURN m.title as title
                LIMIT 5
                """
                result = session.run(query, genres=genres)
                return [record["title"] for record in result]
        except Exception as e:
            st.error(f"Error querying Neo4j: {str(e)}")
            return []
        finally:
            self.close() 