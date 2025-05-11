import streamlit as st
from movie_recommender.utils.env import load_env

# Load environment variables first
load_env()

from movie_recommender.ui.app import main

if __name__ == "__main__":
    main() 