import streamlit as st
from ..agents.workflow import MovieRecommendationAgent

def main():
    st.title("🎬 Movie Recommendation System")
    st.write("Tell us what kind of movies you like, and we'll recommend some great films!")

    # Initialize the agent
    agent = MovieRecommendationAgent()

    # User input
    user_input = st.text_input(
        "What kind of movies do you enjoy?",
        placeholder="e.g., I like sci-fi and action movies or I enjoy comedy and crime films"
    )

    if st.button("Get Recommendations"):
        if user_input:
            # Get recommendations
            final_state = agent.get_recommendations(user_input)

            # Display results
            st.subheader("🎯 Recommended Movies")
            if final_state["recommendations"]:
                for i, movie in enumerate(final_state["recommendations"], 1):
                    st.write(f"{i}. {movie}")
                
                st.subheader("💡 Why these movies?")
                st.write(final_state["explanation"])
            else:
                st.warning("No movies found for those genres. Try different preferences!")
        else:
            st.warning("Please enter your movie preferences first!")

if __name__ == "__main__":
    main() 