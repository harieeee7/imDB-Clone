import streamlit as st
import pandas as pd
from fuzzywuzzy import process
import matplotlib.pyplot as plt

# Load dataset
df = pd.read_csv("imdb_top_1000.csv")
df.columns = df.columns.str.strip()

st.title("🎬 IMDB Movie Finder")

# Input box for movie name
movie_name = st.text_input("Enter a movie name:")

if movie_name:
    # Fuzzy matching
    choices = df['Series_Title'].tolist()
    best_match, score = process.extractOne(movie_name, choices)

    st.write(f"✅ **Best match:** `{best_match}` (Confidence: {score}%)")

    # Filter matched movie
    movie = df[df['Series_Title'] == best_match]

    if not movie.empty:
        # Split layout
        left_col, right_col = st.columns(2)

        # === LEFT: Poster & Highlights ===
        with left_col:
            st.subheader("🖼️ Poster")
            st.image(movie['Poster_Link'].values[0], width=300)

            st.subheader("✨ Key Highlights")
            title = movie['Series_Title'].values[0]
            rating = movie['IMDB_Rating'].values[0]
            director = movie['Director'].values[0]
            stars = [movie['Star1'].values[0], movie['Star2'].values[0],
                     movie['Star3'].values[0], movie['Star4'].values[0]]
            overview = movie['Overview'].values[0]

            st.write(f"**Title:** {title}")
            st.write(f"**IMDB Rating:** {rating}")
            st.write(f"**Director:** {director}")
            st.write(f"**Stars:** {', '.join(stars)}")
            st.write(f"**Overview:** {overview}")

        # === RIGHT: Plot & Related ===
        with right_col:
            # Related movies
            st.subheader("🔗 Related Movies")
            genre = movie['Genre'].values[0]
            related = df[(df['Genre'] == genre) | (df['Director'] == director)]
            related = related[related['Series_Title'] != best_match]

            if not related.empty:
                st.table(related[['Series_Title', 'Released_Year']].head(5))
            else:
                st.write("No related movies found.")

            # Plot: IMDB Rating vs Gross Revenue
            st.subheader("📊 Rating vs Gross Revenue")

            related = related.copy()
            related['Gross'] = related['Gross'].replace('[\$,]', '', regex=True)
            related['Gross'] = pd.to_numeric(related['Gross'], errors='coerce')

            fig, ax = plt.subplots()
            ax.scatter(related['IMDB_Rating'], related['Gross'], alpha=0.7)
            ax.set_xlabel("IMDB Rating")
            ax.set_ylabel("Gross Revenue ($)")
            ax.set_title(f"IMDB Rating vs Gross for movies like '{title}'")
            ax.grid(True)
            st.pyplot(fig)

        # === Download Button ===
        details = f"""=== Movie Details ===
{movie.to_string(index=False)}

=== Key Highlights ===
Title: {title}
IMDB Rating: {rating}
Director: {director}
Stars: {', '.join(stars)}
Overview: {overview}

=== Related Movies ===
"""
        if not related.empty:
            for i, row in related.head(5).iterrows():
                details += f"- {row['Series_Title']} ({row['Released_Year']})\n"
        else:
            details += "No related movies found.\n"

        st.download_button(
            "📥 Download Details",
            data=details,
            file_name="movie_details.txt",
            mime="text/plain"
        )

    else:
        st.error("Movie not found!")
