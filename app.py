import streamlit as st
import docx
import PyPDF2
from pptx import Presentation
import os
import openai
from docx import Document
from collections import defaultdict

# Text Extraction Functions
def extract_text_from_txt(file):
    try:
        return file.getvalue().decode('utf-8')
    except Exception as e:
        st.error(f"Error processing text file. Error: {e}")
        return None

def extract_text_from_docx(file):
    try:
        doc = docx.Document(file)
        return ' '.join([para.text for para in doc.paragraphs])
    except Exception as e:
        st.error(f"Error processing docx file. Error: {e}")
        return None

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

def extract_text(uploaded_file):
    try:
        if uploaded_file.type == "text/plain":
            return extract_text_from_txt(uploaded_file)
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            return extract_text_from_docx(uploaded_file)
        elif uploaded_file.type == "application/pdf":
            return extract_text_from_pdf(uploaded_file)
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.presentationml.presentation":
            return extract_text_from_ppt(uploaded_file)
        else:
            return None
    except Exception as e:
        st.error(f"Error processing {uploaded_file.name}. Error: {e}")
        return None

# ...rest of your code...

# Streamlit Interface
st.title("Transcript Analysis Tool")

api_key = st.text_input("API Key", type="password")

uploaded_files = st.file_uploader(
    "Choose transcript files (.txt, .docx, .pdf, .ppt)",
    type=["txt", "docx", "pdf", "ppt"],
    accept_multiple_files=True,
)

consolidated_text = " ".join([extract_text(file) for file in uploaded_files])

if st.button("Submit", key='submit') and uploaded_files:
    with st.spinner("Processing..."):
        # Concatenate all text from uploaded documents
        consolidated_text = " ".join([extract_text(file) for file in uploaded_files])
        # Analyze the consolidated text
        analysis_result = analyze_text(api_key, consolidated_text)
        
        # Assume the analysis_result is a dictionary with separate keys for each section
        with st.expander("Summary"):
            st.write(analysis_result['summary'])

        with st.expander("Customer Segments"):
            st.write(analysis_result['customer_segments'])

        with st.expander("Pain Points"):
            st.write(analysis_result['pain_points'])

        with st.expander("Opportunities"):
            st.write(analysis_result['opportunities'])

        with st.expander("Insights"):
            st.write(analysis_result['insights'])
        
        st.session_state['analysis_complete'] = True

if 'analysis_complete' in st.session_state and st.button("Export Findings"):
    doc_path = export_findings(analysis_result)
    with open(doc_path, "rb") as file:
        st.download_button(
            label="Download Findings",
            data=file.read(),
            file_name='findings.docx',
            mime='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
