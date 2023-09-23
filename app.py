import streamlit as st
import docx
import PyPDF2
from pptx import Presentation
import openai
from docx import Document
from collections import defaultdict

# OpenAI API Call
def query_openai(api_key, messages):
    openai.api_key = api_key
    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
    return response.choices[0].message["content"]

# Text Extraction Functions
# ... (retain the previous text extraction functions)

# Analysis Function
def analyze_text(api_key, text):
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": f"Provide a thematic analysis of the following text: {text}"}
    ]
    analysis_result = query_openai(api_key, messages)
    return analysis_result  # Assume the analysis_result is structured as required

# Exporting Findings
def export_findings(analysis_result):
    doc = Document()
    doc.add_heading('Consolidated Findings', 0)
    for key, value in analysis_result.items():
        doc.add_heading(key, level=1)
        doc.add_paragraph(value)

    doc_path = 'findings.docx'
    doc.save(doc_path)
    return doc_path

# Streamlit Interface
st.title("Transcript Analysis Tool")

api_key = st.text_input("API Key", type="password")

uploaded_files = st.file_uploader(
    "Choose transcript files (.txt, .docx, .pdf, .ppt)",
    type=["txt", "docx", "pdf", "ppt"],
    accept_multiple_files=True,
)

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
