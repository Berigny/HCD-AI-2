# Grouping all imports at the top
import streamlit as st
import docx
import PyPDF2
from pptx import Presentation
import re

# sfdsf
st.title("Transcript Analysis Tool")

uploaded_files = st.file_uploader(
    "Choose transcript files (.txt, .docx, .pdf, .ppt)",
    type=["txt", "docx", "pdf", "ppt"],
    accept_multiple_files=True,
)
guiding_questions = st.text_area("Enter the guiding questions or keywords (separated by commas)")

# ... [keep your functions here without any change] ...

# Dictionary to store text content for each uploaded file
file_contents = {}

if uploaded_files:
    st.write("Uploaded files:")
    for uploaded_file in uploaded_files:
        try:
            # Extract and store text once
            text_content = extract_text(uploaded_file)
            file_contents[uploaded_file.name] = text_content

            # Display a preview of the content (first 500 characters)
            st.write(f"Contents of {uploaded_file.name}: {text_content[:500]}...")

        except Exception as e:
            st.error(f"An error occurred processing {uploaded_file.name}: {str(e)}")

if guiding_questions:
    keywords = [keyword.strip() for keyword in guiding_questions.split(",")]
    
    for keyword in keywords:
        for file_name, text_content in file_contents.items():
            # Simple keyword matching for demonstration
            matches = re.findall(keyword, text_content, re.IGNORECASE)
            if matches:
                st.write(f"Found {len(matches)} instances of '{keyword}' in {file_name}.")


