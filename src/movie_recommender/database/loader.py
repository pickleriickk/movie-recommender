import pandas as pd
from neo4j import GraphDatabase
import os
from typing import List, Dict
import streamlit as st

class MovieDataLoader:
    def __init__(self):
        self.uri = os.getenv("NEO4J_URI")
        self.user = os.getenv("NEO4J_USER")
        self.password = os.getenv("NEO4J_PASSWORD")
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

    def load_movies(self, movies_file: str):
        """Load movies from CSV file into Neo4j"""
        driver = self.connect()
        if not driver:
            return

        try:
            # Read the movies CSV file
            df = pd.read_csv(movies_file)
            
            with driver.session() as session:
                # Clear existing data
                session.run("MATCH (n) DETACH DELETE n")
                
                # Create constraints
                session.run("CREATE CONSTRAINT movie_id IF NOT EXISTS FOR (m:Movie) REQUIRE m.id IS UNIQUE")
                session.run("CREATE CONSTRAINT genre_name IF NOT EXISTS FOR (g:Genre) REQUIRE g.name IS UNIQUE")
                
                # Load movies and genres
                for _, row in df.iterrows():
                    # Create movie node
                    session.run(
                        """
                        CREATE (m:Movie {id: $id, title: $title})
                        """,
                        id=row['movieId'],
                        title=row['title']
                    )
                    
                    # Create genre nodes and relationships
                    genres = row['genres'].split('|')
                    for genre in genres:
                        if genre != '(no genres listed)':
                            session.run(
                                """
                                MERGE (g:Genre {name: $genre})
                                WITH g
                                MATCH (m:Movie {id: $id})
                                MERGE (m)-[:HAS_GENRE]->(g)
                                """,
                                genre=genre,
                                id=row['movieId']
                            )
                
                st.success("Successfully loaded movies into Neo4j!")
        except Exception as e:
            st.error(f"Error loading movies: {str(e)}")
        finally:
            self.close() 