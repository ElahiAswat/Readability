import streamlit as st
import tempfile
import os
import requests
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
import io

def download_pdf_from_url(url):
    response = requests.get(url)
    response.raise_for_status()
    return io.BytesIO(response.content)

def process_pdf(input_path, output_path, background_color):
    reader = PdfReader(input_path)
    writer = PdfWriter()
    
    for page in reader.pages:
        width = float(page.mediabox.width)
        height = float(page.mediabox.height)
        
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=(width, height))
        can.setFillColor(HexColor(f"#{background_color}"))
        can.rect(0, 0, width, height, fill=1)
        can.save()
        packet.seek(0)
        
        background = PdfReader(packet).pages[0]
        new_page = background
        new_page.merge_page(page)
        writer.add_page(new_page)
        
        if page.annotations:
            writer.pages[-1].annotations = page.annotations
    
    with open(output_path, 'wb') as output_file:
        writer.write(output_file)
    
    with open(output_path, 'rb') as output_file:
        pdf_bytes = output_file.read()
    return pdf_bytes

def main():
    # Page config must be the first Streamlit command
    st.set_page_config(page_icon="icon.png")
    
    # Then other Streamlit commands can follow
    st.markdown('<link rel="icon" type="image/png" href="icon.png">', unsafe_allow_html=True)
    st.title("Readability")
    st.write("Make your PDFs more readable with custom background colors")

    # Rest of your code remains the same...
    # Initialize session state for color selection
    if 'selected_color' not in st.session_state:
        st.session_state.selected_color = "#F7F1E4"  # Default color
    if 'pdf_processed' not in st.session_state:
        st.session_state.pdf_processed = False
    if 'pdf_data' not in st.session_state:
        st.session_state.pdf_data = None
    if 'output_filename' not in st.session_state:
        st.session_state.output_filename = None

    # Input method selection
    input_method = st.radio("Choose input method:", ["Upload PDF", "PDF URL"])

    if input_method == "Upload PDF":
        uploaded_files = st.file_uploader("Choose PDF files", type=['pdf'], accept_multiple_files=True)
        files_to_process = uploaded_files if uploaded_files else []
    else:
        pdf_url = st.text_input("Enter PDF URL")
        files_to_process = [pdf_url] if pdf_url else []

    # Color picker section
    st.subheader("Choose Background Color")
    
    # Display color palette image
    st.image("color_picker.png")
    
    # Dropdown for color selection
    color_options = {
        "2 - Classic Yellow": "#F7F1E4",
        "1 - Medium Grey": "#BFBAB7",
        "3 - Soft Cream": "#FDFAF1",
        "4 - Warm Sand": "#F5E6D3",
        "5 - Cool Mint": "#F1F7ED",
        "6 - Gentle Blue": "#F0F5FA",
        "7 - Blush Pink": "#FFF0F0"
    }
    
    selected_option = st.selectbox("Select color number", options=list(color_options.keys()))
    st.session_state.selected_color = color_options[selected_option]

    # Custom color picker with updated title
    st.subheader("Custom Color")
    custom_color = st.color_picker("Pick a custom color:", st.session_state.selected_color)
    st.session_state.selected_color = custom_color

    final_color = st.session_state.selected_color.lstrip('#')

    if files_to_process:
        if st.button("Process PDFs"):
            with tempfile.TemporaryDirectory() as temp_dir:
                for file_input in files_to_process:
                    try:
                        if input_method == "Upload PDF":
                            temp_input = os.path.join(temp_dir, file_input.name)
                            with open(temp_input, "wb") as f:
                                f.write(file_input.getvalue())
                            output_filename = f"readbetter_{file_input.name}"
                        else:
                            pdf_content = download_pdf_from_url(file_input)
                            temp_input = os.path.join(temp_dir, "downloaded.pdf")
                            with open(temp_input, "wb") as f:
                                f.write(pdf_content.getvalue())
                            output_filename = f"readbetter_document.pdf"

                        output_path = os.path.join(temp_dir, output_filename)
                        pdf_bytes = process_pdf(temp_input, output_path, final_color)
                        st.session_state.pdf_data = pdf_bytes
                        st.session_state.output_filename = output_filename
                        st.session_state.pdf_processed = True

                    except Exception as e:
                        st.error(f"Error processing PDF: {str(e)}")
    
    if st.session_state.pdf_processed:
        st.success(f"Successfully processed PDF")
        st.download_button(
            label=f"Download {st.session_state.output_filename}",
            data=st.session_state.pdf_data,
            file_name=st.session_state.output_filename,
            mime="application/pdf"
        )
        
        # Add Preview button and iframe
        if st.button("Preview PDF"):
            # Create a base64 version of the PDF for display
            import base64
            base64_pdf = base64.b64encode(st.session_state.pdf_data).decode('utf-8')
            pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800px" type="application/pdf"></iframe>'
            st.markdown(pdf_display, unsafe_allow_html=True)
if __name__ == "__main__":
    main()
