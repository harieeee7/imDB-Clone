import streamlit as st
import pandas as pd
from fuzzywuzzy import process
import matplotlib.pyplot as plt
import base64

# --- Custom CSS for beautiful background and semi-transparent containers ---
def set_custom_styles(image_file):
    with open(image_file, "rb") as f:
        data = f.read()
    b64 = base64.b64encode(data).decode()

    custom_css = f"""
    <style>
    .stApp {{
        background-image: url("data:image/avif;base64,{b64}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        color: white;
    }}

    .main-container {{
        background-color: rgba(0, 0, 0, 0.6);
        padding: 2rem;
        border-radius: 10px;
    }}

    h1, h2, h3, h4, h5, h6 {{
        color: #FFD700;
    }}

    .stTextInput > div > div > input {{
        background-color: rgba(255, 255, 255, 0.8);
        color: black;
    }}

    .stButton button {{
        background-color: #FFD700;
        color: black;
    }}

    .stTable {{
        background-color: rgba(255, 255, 255, 0.9);
        color: black;
    }}
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

set_custom_styles("back.avif")

# --- Load data ---
df = pd.read_csv("imdb_top_1000.csv")
df.columns = df.columns.str.strip()

# --- Main container for content ---
st.markdown('<div class="main-container">', unsafe_allow_html=True)

st.title("🎬 IMDB Top 1000 Movie Finder")

st.markdown("""
Welcome to your stylish IMDB Explorer!  
Search for any movie, view full details with a beautiful poster, discover related films, and visualize rating vs gross — all on a clean, modern layout.
""")

# --- Search box ---
st.header("🔍 Search for a Movie")
movie_name = st.text_input("Type a movie name and press Enter:")

if movie_name:
    # Fuzzy match
    choices = df['Series_Title'].tolist()
    best_match, score = process.extractOne(movie_name, choices)

    st.success(f"✅ **Best match:** `{best_match}` (Confidence: {score}%)")

    movie = df[df['Series_Title'] == best_match]

    if not movie.empty:
        left_col, right_col = st.columns(2)

        with left_col:
            st.subheader("🖼️ Poster & Highlights")
            st.image(movie['Poster_Link'].values[0], width=300)

            title = movie['Series_Title'].values[0]
            rating = movie['IMDB_Rating'].values[0]
            director = movie['Director'].values[0]
            stars = [movie['Star1'].values[0], movie['Star2'].values[0],
                     movie['Star3'].values[0], movie['Star4'].values[0]]
            overview = movie['Overview'].values[0]

            st.markdown(f"**Title:** {title}")
            st.markdown(f"**IMDB Rating:** {rating}")
            st.markdown(f"**Director:** {director}")
            st.markdown(f"**Stars:** {', '.join(stars)}")
            st.markdown(f"**Overview:** {overview}")

        with right_col:
            st.subheader("🔗 Related Movies")
            genre = movie['Genre'].values[0]
            related = df[(df['Genre'] == genre) | (df['Director'] == director)]
            related = related[related['Series_Title'] != best_match]

            if not related.empty:
                st.table(related[['Series_Title', 'Released_Year']].head(5))
            else:
                st.write("No related movies found.")

            st.subheader("📊 Rating vs Gross Revenue")
            related = related.copy()
            related['Gross'] = related['Gross'].replace('[\$,]', '', regex=True)
            related['Gross'] = pd.to_numeric(related['Gross'], errors='coerce')

            fig, ax = plt.subplots()
            ax.scatter(related['IMDB_Rating'], related['Gross'], alpha=0.7, color="#FFD700")
            ax.set_xlabel("IMDB Rating")
            ax.set_ylabel("Gross Revenue ($)")
            ax.set_title(f"IMDB Rating vs Gross for movies like '{title}'")
            ax.grid(True)
            st.pyplot(fig)

        # Download
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
            "📥 Download Movie Details",
            data=details,
            file_name="movie_details.txt",
            mime="text/plain"
        )

    else:
        st.error("Movie not found!")

# Close main container
st.markdown('</div>', unsafe_allow_html=True)
