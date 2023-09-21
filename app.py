import streamlit as st
import docx
import PyPDF2
from pptx import Presentation
import re

# File extraction functions with caching
@st.cache(allow_output_mutation=True, suppress_st_warning=True)
def extract_text_from_txt(file):
    try:
        return file.getvalue().decode('utf-8')
    except Exception as e:
        st.error(f"Error processing text file. Error: {e}")
        return None

@st.cache(allow_output_mutation=True, suppress_st_warning=True)
def extract_text_from_docx(file):
    try:
        doc = docx.Document(file)
        return ' '.join([para.text for para in doc.paragraphs])
    except Exception as e:
        st.error(f"Error processing docx file. Error: {e}")
        return None

@st.cache(allow_output_mutation=True, suppress_st_warning=True)
def extract_text_from_pdf(file):
    try:
        pdf_reader = PyPDF2.PdfFileReader(file)
        text = ""
        for page_num in range(pdf_reader.numPages):
            text += pdf_reader.getPage(page_num).extractText()
        return text
    except Exception as e:
        st.error(f"Error processing pdf file. Error: {e}")
        return None

@st.cache(allow_output_mutation=True, suppress_st_warning=True)
def extract_text_from_ppt(file):
    try:
        prs = Presentation(file)
        text = ""
        for slide in prs.slides:
            for shape in slide.shapes:
                if hasattr(shape, "text"):
                    text += shape.text
        return text
    except Exception as e:
        st.error(f"Error processing ppt file. Error: {e}")
        return None

@st.cache(allow_output_mutation=True, suppress_st_warning=True)
def extract_text(file):
    try:
        if file.type == "text/plain":
            return extract_text_from_txt(file)
        elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            return extract_text_from_docx(file)
        elif file.type == "application/pdf":
            return extract_text_from_pdf(file)
        elif file.type == "application/vnd.openxmlformats-officedocument.presentationml.presentation":
            return extract_text_from_ppt(file)
        else:
            return None
    except Exception as e:
        st.error(f"Error processing {file.name}. Error: {e}")
        return None

st.title("Transcript Analysis Tool")

uploaded_files = st.file_uploader(
    "Choose transcript files (.txt, .docx, .pdf, .ppt)",
    type=["txt", "docx", "pdf", "ppt"],
    accept_multiple_files=True,
)
guiding_questions = st.text_area("Enter the guiding questions or keywords (separated by commas)")

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
