import streamlit as st
import pandas as pd
from fuzzywuzzy import process
import matplotlib.pyplot as plt
import base64
from fpdf import FPDF

# --- Custom CSS with cinematic font, smooth fade-in & new background ---
def set_custom_style(image_file):
    with open(image_file, "rb") as f:
        img = f.read()
    b64 = base64.b64encode(img).decode()

    custom_css = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&display=swap');

    .stApp {{
        background-image: url("data:image/jpg;base64,{b64}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        font-family: 'Playfair Display', serif;
        color: white;
    }}

    .main-container {{
        background: rgba(0, 0, 0, 0.75);
        padding: 2rem;
        border-radius: 12px;
        margin-top: 2rem;
        font-weight: bold;
        animation: fadeIn 2s ease-in-out;
    }}

    @keyframes fadeIn {{
        0% {{ opacity: 0; }}
        100% {{ opacity: 1; }}
    }}

    h1, h2, h3 {{
        color: #FFD700;
        font-weight: bold;
    }}

    .stTextInput input {{
        background: rgba(255, 255, 255, 0.95);
        color: black;
        font-weight: bold;
    }}

    .stButton button {{
        background-color: #FFD700;
        color: black;
        font-weight: bold;
        border: none;
    }}

    .stTable {{
        background: rgba(255, 255, 255, 0.95);
        color: black;
        font-weight: bold;
        border-radius: 8px;
    }}
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

# Apply style with new cinematic font and fade-in
set_custom_style("backk.jpg")

# --- Load dataset ---
df = pd.read_csv("imdb_top_1000.csv")
df.columns = df.columns.str.strip()

# --- Main container with fade-in ---
st.markdown('<div class="main-container">', unsafe_allow_html=True)

st.title("🎬 IMDB Top 1000 Movie Finder")
st.markdown("""
Search for your favorite movies, get detailed highlights, explore related films, and analyze rating vs gross — all with a cinematic experience.
""")

# --- Movie input ---
st.header("🔍 Search for a Movie")
movie_name = st.text_input("Type a movie name and press Enter:")

if movie_name:
    choices = df['Series_Title'].tolist()
    best_match, score = process.extractOne(movie_name, choices)

    st.success(f"✅ Best match: `{best_match}` (Confidence: {score}%)")

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

        # --- PDF download ---
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, f"Movie Details\n\nTitle: {title}\nIMDB Rating: {rating}\nDirector: {director}\nStars: {', '.join(stars)}\n\nOverview:\n{overview}\n\nRelated Movies:\n")

        if not related.empty:
            for i, row in related.head(5).iterrows():
                pdf.multi_cell(0, 10, f"- {row['Series_Title']} ({row['Released_Year']})")
        else:
            pdf.multi_cell(0, 10, "No related movies found.")

        pdf_file = f"{title.replace(' ', '_')}_details.pdf"
        pdf.output(pdf_file)

        with open(pdf_file, "rb") as f:
            st.download_button(
                label="📥 Download Movie Details (PDF)",
                data=f,
                file_name=pdf_file,
                mime="application/pdf"
            )

    else:
        st.error("Movie not found!")

st.markdown('</div>', unsafe_allow_html=True)
