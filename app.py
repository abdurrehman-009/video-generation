
import base64
import streamlit as st
from google import genai

st.set_page_config(
    page_title="ToonGenius AI - Video Generator",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 ToonGenius AI")
st.subheader("Turn your imagination into animated videos")
st.write(
    "Describe your scene in detail and generate a short AI video."
)

# Get Gemini API key from Streamlit Secrets
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    api_key = ""

if not api_key:
    st.error(
        "Gemini API key not found. Add GEMINI_API_KEY "
        "in Streamlit Secrets before generating videos."
    )
    st.info(
        'Add this in Streamlit Cloud → App settings → Secrets:\n\n'
        'GEMINI_API_KEY = "your_actual_api_key"'
    )
    st.stop()

with st.form("video_generation_form"):
    prompt = st.text_area(
        "Describe your video scene",
        placeholder=(
            "Example: A cute little fox wearing a blue jacket "
            "runs through a magical forest. Glowing butterflies "
            "fly around it, colorful flowers move in the wind, "
            "cinematic 3D cartoon animation, smooth camera movement, "
            "beautiful lighting, cheerful mood."
        ),
        height=180,
        max_chars=5000
    )

    col1, col2 = st.columns(2)

    with col1:
        style = st.selectbox(
            "Animation style",
            [
                "3D Cartoon",
                "Anime",
                "2D Cartoon",
                "Pixar-like 3D animation",
                "Clay Animation",
                "Fantasy Animation",
                "Cinematic Animation"
            ]
        )

    with col2:
        aspect_ratio = st.selectbox(
            "Video format",
            ["9:16 - Vertical (Shorts/Reels)",
             "16:9 - Landscape (YouTube)"]
        )

    generate = st.form_submit_button(
        "✨ Generate Video",
        use_container_width=True
    )

if generate:
    if not prompt.strip():
        st.warning("Please enter a scene description first.")
        st.stop()

    final_prompt = f"""
Create a high-quality animated video.

Scene description:
{prompt.strip()}

Visual style: {style}.
Make the movement smooth and natural.
Keep the main characters visually consistent.
Use detailed backgrounds, cinematic lighting, and clear composition.
Follow the scene description closely.
"""

    ratio = "9:16" if aspect_ratio.startswith("9:16") else "16:9"

    try:
        with st.spinner(
            "Creating your video... This may take some time."
        ):
            client = genai.Client(api_key=api_key)

            interaction = client.interactions.create(
                model="gemini-omni-1.1-flash",
                input=final_prompt,
                response_format={
                    "type": "video",
                    "aspect_ratio": ratio,
                    "resolution": "720p"
                }
            )

        video_data = getattr(interaction, "output_video", None)

        if video_data is None or not getattr(video_data, "data", None):
            st.error(
                "The model did not return a video. "
                "Check your API access and try again."
            )
            st.stop()

        video_bytes = base64.b64decode(video_data.data)

        st.success("Your video is ready!")
        st.video(video_bytes)

        st.download_button(
            label="⬇️ Download MP4 Video",
            data=video_bytes,
            file_name="toongenius_video.mp4",
            mime="video/mp4",
            use_container_width=True
        )

    except Exception as e:
        st.error("Video generation failed.")
        st.write(
            "Check that your API key is valid, the model is "
            "available to your account, and your API quota allows "
            "video generation."
        )
        st.caption(f"Technical details: {str(e)[:700]}")
