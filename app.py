import streamlit as st
import pytesseract
from PIL import Image
import openai
import os

# Set your OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# App title
st.set_page_config(page_title="HealthEase OCR+AI", layout="wide")
st.title("🩺 HealthEase - OCR + AI Medical Report Helper")

# Sections
menu = ["Patient - Upload & Summarize", "Doctor - Prescribe & Comment"]
choice = st.sidebar.selectbox("Select Mode", menu)

# Fake storage for demo (in real app, use database)
if "patient_data" not in st.session_state:
    st.session_state.patient_data = {}

# ------------------- PATIENT MODE -------------------
if choice == "Patient - Upload & Summarize":
    st.header("📄 Upload Your Medical Report")
    uploaded_file = st.file_uploader("Upload image or PDF", type=["png", "jpg", "jpeg"])

    if uploaded_file is not None:
        # Display uploaded image
        img = Image.open(uploaded_file)
        st.image(img, caption="Uploaded Report", use_container_width=True)

        # Extract text via OCR
        with st.spinner("Extracting text with OCR..."):
            extracted_text = pytesseract.image_to_string(img)

        st.subheader("📝 Extracted Text")
        st.text_area("Raw OCR Output", extracted_text, height=200)

        # AI Summarization
        if st.button("Summarize & Translate"):
            with st.spinner("Using AI to summarize and translate..."):
                prompt = f"Summarize the following medical report in simple language and translate into Hindi:\n\n{extracted_text}"
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.5
                )
                summary = response.choices[0].message["content"]

            st.subheader("🤖 AI Summary + Hindi Translation")
            st.write(summary)

        # Save for doctor
        patient_name = st.text_input("Enter your name for record:")
        if st.button("Save for Doctor"):
            if patient_name.strip():
                st.session_state.patient_data[patient_name] = {
                    "report_text": extracted_text,
                    "doctor_notes": ""
                }
                st.success("Report saved for your doctor.")
            else:
                st.warning("Please enter your name.")

# ------------------- DOCTOR MODE -------------------
elif choice == "Doctor - Prescribe & Comment":
    st.header("🩺 Doctor Dashboard")
    patient_list = list(st.session_state.patient_data.keys())

    if patient_list:
        selected_patient = st.selectbox("Select Patient", patient_list)
        patient_info = st.session_state.patient_data[selected_patient]

        st.subheader(f"📄 Patient Report - {selected_patient}")
        st.text_area("Report Text", patient_info["report_text"], height=150)

        prescription = st.text_area("💊 Write Prescription")
        comment = st.text_area("💬 Write Comments")

        if st.button("Save Notes"):
            st.session_state.patient_data[selected_patient]["doctor_notes"] = {
                "prescription": prescription,
                "comment": comment
            }
            st.success("Notes saved successfully!")

        # Show saved notes
        if patient_info.get("doctor_notes"):
            st.subheader("📌 Saved Doctor Notes")
            st.write(f"**Prescription:** {patient_info['doctor_notes']['prescription']}")
            st.write(f"**Comments:** {patient_info['doctor_notes']['comment']}")
    else:
        st.info("No patient data available yet.")
