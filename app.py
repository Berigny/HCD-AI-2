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

# Function to extract insights from text
def extract_insights(text, guiding_questions):
    try:
        # Trim the text if it's too long
        if len(text) > 4000:
            trimmed_text = text[:4000]  # This is a naive trim
            st.warning("The text has been truncated for analysis.")
        else:
            trimmed_text = text

        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": f"Summarize the following text and identify customer segments, pain points, and opportunities: {trimmed_text}"
            },
            {"role": "user", "content": f"Guiding questions: {guiding_questions}"}
        ]
        insights = query_openai(api_key, messages)  # updated line
        return insights
    except Exception as e:
        st.error(f"OpenAI API error: {e}")

# Streamlit app UI
st.title("Transcript Analysis Tool")

api_key = st.text_input("API Key", type="password", help=None)  # Removed on-focus help text

guiding_questions = st.text_area("Enter any guiding questions for the analysis:")

uploaded_files = st.file_uploader(
    "Choose transcript files (.txt, .docx, .pdf, .ppt)",
    type=["txt", "docx", "pdf", "ppt"],
    accept_multiple_files=True,
)

# Button to initiate the analysis
if st.button("Submit") and uploaded_files:
    with st.spinner("Processing..."):
        # Concatenate all text from uploaded documents
        consolidated_text = " ".join([extract_text(file) for file in uploaded_files])

        # Get analysis result
        analysis_result = extract_insights(consolidated_text, guiding_questions)

        st.write(f"Debug: {analysis_result}")  # add this line to see what's in analysis_result

        # Assume the analysis result is formatted with newline separation for each section
        sections = analysis_result.split('\n')
        summary, customer_segments, pain_points, opportunities, insights = sections[:5]

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
