import streamlit as st
import docx
import PyPDF2
from pptx import Presentation
import openai
from collections import defaultdict

# OpenAI API Call
def query_openai(api_key, messages):
    openai.api_key = api_key
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.7,
        max_tokens=150
    )
    return response.choices[0].message["content"]

# Segment size for chunking text for analysis
SEGMENT_SIZE = 3500  

# Function to extract insights from text
@st.cache(allow_output_mutation=True)
def extract_insights(api_key, text):
    insights = ""
    segments = text.split('. ')
    i = 0
    while i < len(segments):
        segment = segments[i]
        while len(segment) < SEGMENT_SIZE and i < len(segments) - 1:
            i += 1
            segment += ". " + segments[i]
        try:
            messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"Provide insights on the following transcript segment: {segment}"}
            ]
            insight_segment = query_openai(api_key, messages)
            insights += insight_segment.strip() + " "
        except Exception as e:
            st.error(f"OpenAI API error: {e}")
        i += 1
    return insights.strip()

@st.cache(allow_output_mutation=True)
def generate_summary(api_key, insight):
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": f"Summarize the following insights: {insight}"}
    ]
    summary = query_openai(api_key, messages)
    return summary

def process_uploaded_files(uploaded_files):
    file_contents = {}
    for uploaded_file in uploaded_files:
        file_name = uploaded_file.name
        if file_name.endswith('.txt'):
            text_content = uploaded_file.read().decode()
        elif file_name.endswith('.docx'):
            doc = docx.Document(uploaded_file)
            text_content = " ".join([paragraph.text for paragraph in doc.paragraphs])
        elif file_name.endswith('.pdf'):
            pdf_reader = PyPDF2.PdfFileReader(uploaded_file)
            text_content = " ".join([page.extractText() for page in pdf_reader.pages])
        elif file_name.endswith('.ppt'):
            ppt = Presentation(uploaded_file)
            text_content = " ".join([shape.text for slide in ppt.slides for shape in slide.shapes if hasattr(shape, "text")])
        else:
            st.error(f"Unsupported file type: {file_name}")
            continue
        file_contents[file_name] = text_content
    return file_contents

# Streamlit UI
st.title("Transcript Analysis Tool")

api_key = st.text_input("API Key", type="password", help=None)

guiding_questions = st.text_area("Enter any guiding questions for the analysis:")

uploaded_files = st.file_uploader(
    "Choose transcript files (.txt, .docx, .pdf, .ppt)",
    type=["txt", "docx", "pdf", "ppt"],
    accept_multiple_files=True,
)

if st.button("Submit", key='submit') and guiding_questions and uploaded_files:
    st.session_state['file_contents'] = process_uploaded_files(uploaded_files)
    with st.spinner("Processing..."):
        with st.expander("Consolidated Insights & Summaries"):
            for file_name, text_content in st.session_state['file_contents'].items():
                insights = extract_insights(api_key, text_content)
                st.write(f"Insights from {file_name}:")
                st.write(insights)
        st.session_state['processing_complete'] = True

        with st.expander("Summary"):
            summary = generate_summary(api_key, insights)
            st.write(summary)

        # For other sections like Customer Segments, Pain Points, and Opportunities,
        # you may need to define the functions to extract or generate these data.
