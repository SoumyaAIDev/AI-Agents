import streamlit as st
import os
import tempfile
from dotenv import load_dotenv

load_dotenv()

from ingest import ingest_pdf, chunk_documents
from index import build_vector_store
from extract import extract_lease_info, LeaseSummary
from qa import answer_question
from utils import get_logger

logger = get_logger(__name__)

# Must be the first Streamlit command
st.set_page_config(page_title="Lease Analyzer", page_icon="📄", layout="wide")

def main():
    st.title("📄 Lease Analyzer")
    st.markdown("Upload a single Commercial Lease PDF to extract material terms and chat with the document.")

    # Sidebar for API Key if not in env
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        api_key = st.sidebar.text_input("Enter OpenRouter API Key", type="password")
        if api_key:
            os.environ["OPENROUTER_API_KEY"] = api_key
        else:
            st.sidebar.warning("Please enter your OpenRouter API Key to proceed.")
            st.stop()

    # File upload
    uploaded_file = st.file_uploader("Upload Lease PDF", type=["pdf"])

    if uploaded_file is not None:
        # Initialize session state variables
        if "docs" not in st.session_state:
            with st.spinner("Processing PDF..."):
                try:
                    # Save to temp file
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                        tmp.write(uploaded_file.getvalue())
                        tmp_path = tmp.name
                    
                    # Ingest and chunk
                    docs = ingest_pdf(tmp_path)
                    
                    if not docs:
                        st.error("No text could be extracted from this PDF. Please verify the document is not an image-only scan.")
                        os.unlink(tmp_path)
                        return
                        
                    chunks = chunk_documents(docs)
                    
                    # Store in session state
                    st.session_state["docs"] = docs
                    st.session_state["chunks"] = chunks
                    
                    # Build index
                    st.session_state["vector_store"] = build_vector_store(chunks)
                    
                    # Extract Summary
                    st.session_state["lease_summary"] = extract_lease_info(docs)
                    
                    st.success("PDF successfully processed and analyzed!")
                    os.unlink(tmp_path)  # cleanup
                except Exception as e:
                    st.error(f"Error processing file: {e}")
                    logger.error(f"Error processing file: {e}")
                    return

        # Tabs setup
        tab1, tab2 = st.tabs(["Lease Summary", "Q&A Chat"])

        with tab1:
            st.header("Structured Lease Summary")
            summary = st.session_state.get("lease_summary")
            if summary:
                # Display summary in an organized way
                for field_name, field_data in summary.model_dump().items():
                    with st.expander(f"{field_name.replace('_', ' ').title()}: {field_data['value'] or 'Not Found'} (Confidence: {field_data['confidence']:.2f})", expanded=True):
                        st.write(f"**Field Type**: {field_data['field_type']}")
                        
                        if field_data['value'] is None:
                            st.write(f"**Reason Not Found**: {field_data.get('not_found_reason', 'N/A')}")
                        
                        if field_data['citations']:
                            st.write("**Citations:**")
                            for cite in field_data['citations']:
                                st.markdown(f"- **Page {cite.get('page_number', '?')}** ({cite.get('location_hint', '')}): _{cite.get('supporting_snippet', '')}_")

        with tab2:
            st.header("Chat with the Lease")
            
            if "messages" not in st.session_state:
                st.session_state.messages = []

            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

            if prompt := st.chat_input("Ask a question about the lease..."):
                st.session_state.messages.append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)

                with st.chat_message("assistant"):
                    with st.spinner("Thinking..."):
                        try:
                            response = answer_question(prompt, st.session_state["vector_store"])
                            
                            # Build answer string with citations
                            answer_text = response.answer
                            if response.citations:
                                answer_text += "\n\n**Sources:**\n"
                                for c in response.citations:
                                    answer_text += f"- **{c.page_number}** ({c.location_hint}): _{c.supporting_snippet}_\n"
                            
                            st.markdown(answer_text)
                            st.session_state.messages.append({"role": "assistant", "content": answer_text})
                        except Exception as e:
                            st.error(f"Error generating answer: {e}")
                            logger.error(f"QA Error: {e}")

if __name__ == "__main__":
    main()
