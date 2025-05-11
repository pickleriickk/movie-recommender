import streamlit as st
from movie_recommender.database.loader import MovieDataLoader

def main():
    st.title("🎬 Movie Data Loader")
    
    # File uploader
    uploaded_file = st.file_uploader("Choose a movies CSV file", type="csv")
    
    if uploaded_file is not None:
        # Save the uploaded file temporarily
        with open("temp_movies.csv", "wb") as f:
            f.write(uploaded_file.getvalue())
        
        # Load movies into Neo4j
        loader = MovieDataLoader()
        loader.load_movies("temp_movies.csv")
        
        # Clean up
        import os
        os.remove("temp_movies.csv")

if __name__ == "__main__":
    main() 