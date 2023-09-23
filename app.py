import streamlit as st
import docx
import PyPDF2
from pptx import Presentation
import openai

# Define constants
SEGMENT_SIZE = 1000  # Define this constant as per your requirements

# Define function to handle OpenAI API calls
def query_openai(api_key, messages):
    openai.api_key = api_key
    response = openai.ChatCompletion.create(model="gpt-4", messages=messages)
    return response.choices[0].message["content"]

# ... (rest of the text extraction functions here)

# Function to extract insights from text
def extract_insights(api_key, text):
    insights = ""
    segments = text.split('. ')  # Split by sentences
    
    # Function to handle OpenAI API calls
    def query_openai(segment):
        # Truncate the segment if it's too long
        MAX_CHAR_LIMIT = 4000  # Set based on OpenAI's max tokens limit
        truncated_segment = segment[:MAX_CHAR_LIMIT]
        if len(segment) > MAX_CHAR_LIMIT:
            st.warning(f"A segment was truncated from {len(segment)} to {len(truncated_segment)} characters.")
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Provide insights on the following transcript segment: {truncated_segment}"}
        ]
        return query_openai(api_key, messages)
    
    # Join sentences until they approach the segment size
    i = 0
    while i < len(segments):
        segment = segments[i]
        while len(segment) < SEGMENT_SIZE and i < len(segments) - 1:
            i += 1
            segment += ". " + segments[i]
        
        try:
            insight_segment = query_openai(segment)
            insights += insight_segment.strip() + " "
        except Exception as e:
            st.error(f"OpenAI API error: {e}")
        
        i += 1
    
    return insights.strip()

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
        analysis_result = extract_insights(api_key, consolidated_text)

        st.write(f"Debug: {analysis_result}")  # add this line to see what's in analysis_result

        # Assume the analysis result is formatted with newline separation for each section
        sections = analysis_result.split('\n')
        
        # Updated unpacking line
        summary, customer_segments, pain_points, opportunities, insights = (sections + [None]*5)[:5]

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
