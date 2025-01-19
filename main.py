import streamlit as st
import openai
import os
from PIL import Image
from dotenv import load_dotenv
from reference_script import reference_script

# Load environment variables
load_dotenv()

# Set the OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    st.error("OpenAI API key not found. Please set it in the .env file.")

def execute_script(script, output_path):
    """Executes the provided script and renders the scene."""
    try:
        # Use exec to run the Blender script
        exec(script, globals())
        st.success("Script executed successfully.")
        return output_path
    except Exception as e:
        st.error(f"An error occurred while executing the script: {e}")
        return None

def generate_and_execute_script(prompt, asset_paths, reference_script, output_path):
    """Generates and executes a Blender script based on user input."""
    try:
        # Initialize the OpenAI client
        client = openai.OpenAI(api_key=openai.api_key)
        # Query the LLM
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": """
                You are an interior design visualizer agent that accepts the user input
                as text and assets and then creates a Blender script that visualizes
                what the user wants to see.

                The user provides:
                - A text description of their design.
                - One or more image assets (textures).

                Guidelines:
                - Modify the reference script based on the user's request.
                - Use the provided assets dynamically to create materials for the scene.
                - Ensure the room is well-lit (use create_interior_light function).
                - The camera should be positioned to view the scene from one corner.
                """},
                {"role": "user", "content": f"""
                Modify the reference script: {reference_script}, according to the
                user's wishes here: {prompt}. Use these assets: {asset_paths}.
                The light and background ALL should be white.
                The room must be very lit.
                The view of the render should be the from the farthest corner from the 
                origin of the room looking at the opposite corner.
                Return ONLY script itself. No ```python.
                Remember, I strictly ask you to not change the fundamental
                approaches in the reference script. However, you can:
                - Adjust plane dimensions to satisfy the user's wishes.
                - Update the camera location and angle to make all walls visible.
                - Modify light settings to suit an interior scene.
                - Use BLENDER_EEVEE_NEXT engine.
                - Set interior light energy to max 30. everywhere. 
                """}
            ]
        )

        # Extract the content
        generated_script = response.choices[0].message.content
        st.code(generated_script, language="python")

        # Execute the script
        result_path = execute_script(generated_script, output_path)
        return result_path
    except Exception as e:
        st.error(f"An error occurred while generating or executing the script: {e}")
        return None

# Streamlit App
st.title("Interior Design Visualizer")
st.write("Describe your interior design idea and upload one or more textures to visualize it.")

# User input: Text prompt
user_prompt = st.text_area("Enter your design description:", placeholder="E.g., Design a cozy living room with a wooden floor and painted walls.")

# User input: Multiple file upload for assets
uploaded_files = st.file_uploader(
    "Upload one or more textures (e.g., floor, wall):",
    type=["png", "jpg", "jpeg"],
    accept_multiple_files=True
)

# Save uploaded files temporarily
asset_paths = []
if uploaded_files:
    os.makedirs("uploaded_assets", exist_ok=True)
    for uploaded_file in uploaded_files:
        file_path = f"uploaded_assets/{uploaded_file.name}"
        with open(file_path, "wb") as f:
            f.write(uploaded_file.read())
        asset_paths.append(file_path)

if st.button("Generate Design"):
    if user_prompt.strip() and asset_paths:
        st.write("Processing your request...")

        # Path to save the rendered output
        output_path = "output/rendered_scene.png"
        os.makedirs("output", exist_ok=True)

        # Generate and execute the script
        result_path = generate_and_execute_script(user_prompt, asset_paths, reference_script, output_path)

        # Display the rendered image if it exists
        if result_path and os.path.exists(result_path):
            st.image(Image.open(result_path), caption="Rendered Scene", use_column_width=True)
    else:
        st.error("Please provide a design description and upload at least one asset.")
