import streamlit as st
import docx
import PyPDF2
from pptx import Presentation
import openai

# Define function to handle OpenAI API calls
def query_openai(api_key, messages):
    openai.api_key = api_key
    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
    return response.choices[0].message["content"]

# Text extraction functions for different file types
def extract_text_from_txt(file):
    return file.getvalue().decode('utf-8')

def extract_text_from_docx(file):
    doc = docx.Document(file)
    return ' '.join([para.text for para in doc.paragraphs])

def extract_text_from_pdf(file):
    pdf_reader = PyPDF2.PdfFileReader(file)
    text = ""
    for page_num in range(pdf_reader.numPages):
        text += pdf_reader.getPage(page_num).extractText()
    return text

def extract_text_from_ppt(file):
    prs = Presentation(file)
    text = ""
    for slide in prs.slides:
        for shape in slide.shapes:
            if hasattr(shape, "text"):
                text += shape.text
    return text

# Function to extract text based on file type
def extract_text(uploaded_file):
    if uploaded_file.type == "text/plain":
        return extract_text_from_txt(uploaded_file)
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        return extract_text_from_docx(uploaded_file)
    elif uploaded_file.type == "application/pdf":
        return extract_text_from_pdf(uploaded_file)
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.presentationml.presentation":
        return extract_text_from_ppt(uploaded_file)
    else:
        st.error(f"File type not supported: {uploaded_file.type}")

# Streamlit app UI
st.title("Transcript Analysis Tool")

api_key = st.text_input("API Key", type="password")

uploaded_files = st.file_uploader(
    "Choose transcript files (.txt, .docx, .pdf, .ppt)",
    type=["txt", "docx", "pdf", "ppt"],
    accept_multiple_files=True,
)

guiding_questions = st.text_area("Guiding Questions", "What guiding questions or themes are you interested in?")

def analyze_text(text, questions):
    # Incorporate guiding questions into the analysis request
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": f"Perform a thematic analysis on the following text: {text}. Guiding questions: {questions}"}
    ]
    analysis = query_openai(api_key, messages)
    return analysis

# Button to initiate the analysis
if st.button("Submit") and uploaded_files:
    with st.spinner("Processing..."):
        # Concatenate all text from uploaded documents
        consolidated_text = " ".join([extract_text(file) for file in uploaded_files])

        # Get analysis result
        analysis_result = analyze_text(consolidated_text, guiding_questions)
        
        # Assume the analysis result is formatted with newline separation for each section
        summary, customer_segments, pain_points, opportunities, insights = analysis_result.split('\n')

        # Display each section of the analysis result in separate accordions
        with st.expander("Summary"):
            st.write(summary)

        with st.expander("Customer Segments"):
            st.write(customer_segments)

        with st.expander("Pain Points"):
            st.write(pain_points)

        with st.expander("Opportunities"):
            st.write(opportunities)

        with st.expander("Insights"):
            st.write(insights)
