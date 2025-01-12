import streamlit as st
import pandas as pd
import os

# List of areas for selection
areas = [
    "Ambegaon Budruk", "Aundh", "Baner", "Bavdhan Khurd", "Bavdhan Budruk", "Balewadi",
    "Shivajinagar", "Bibvewadi", "Bhugaon", "Bhukum", "Dhankawadi", "Dhanori", "Dhayari", 
    "Erandwane", "Fursungi", "Ghorpadi", "Hadapsar", "Hingne Khurd", "Karve Nagar", "Kalas", 
    "Katraj", "Khadki", "Kharadi", "Kondhwa", "Koregaon Park", "Kothrud", "Lohagaon", "Manjri", 
    "Markal", "Mohammed Wadi", "Mundhwa", "Nanded", "Parvati (Parvati Hill)", "Panmala", 
    "Pashan", "Pirangut", "Shivane", "Sus", "Undri", "Vishrantwadi", "Vitthalwadi", 
    "Vadgaon Khurd", "Vadgaon Budruk", "Vadgaon Sheri", "Wagholi", "Wanwadi", "Warje", "Yerwada"
]

# Title of the survey
st.title("Pune Municipal Feedback Survey")

# Introduction
st.write("Please fill out this survey. Your feedback will help improve public services.")

# Collect respondent details
st.header("Respondent Details")
name = st.text_input("Your Name:", help="Please enter your full name.")
age = st.number_input("Your Age:", min_value=18, max_value=120, step=1, help="You must be at least 18 years old to participate.")
area = st.selectbox("Select your area:", ["Select"] + areas, help="Choose your area from the dropdown.")

# Check for mandatory fields
if not name:
    st.warning("Please enter your name.")
if age < 18:
    st.warning("You must be at least 18 years old to participate.")
if area == "Select":
    st.warning("Please select your area.")

# File where responses are stored
file_name = "governance_feedback.csv"

# Directories for storing images and videos
image_dir = "uploaded_images"
video_dir = "uploaded_videos"

# Ensure directories exist
os.makedirs(image_dir, exist_ok=True)
os.makedirs(video_dir, exist_ok=True)

# Check if the CSV file exists and load existing data, if any
try:
    existing_data = pd.read_csv(file_name)
except FileNotFoundError:
    existing_data = pd.DataFrame(columns=[
        "Survey Number", "Name", "Age", "Area",
        "Healthcare Rating", "Healthcare Follow-Up",
        "Education Rating", "Education Follow-Up",
        "Water Supply Rating", "Water Supply Follow-Up",
        "Transportation Rating", "Transportation Follow-Up",
        "Garbage Collection Rating", "Garbage Collection Follow-Up",
        "Safety and Security Rating", "Safety and Security Follow-Up",
        "Image Feedback", "Video Feedback"
    ])

# Store responses
responses = {}

# If basic info is completed, allow users to fill out the ratings section
if name and age >= 18 and survey_number and survey_number.isalnum() and area != "Select":
    st.success("Thank you for providing your details. You can now proceed with the survey.")

    # Feedback sections
    st.header("Rate the Following Public Services")

    # Define sectors, initial questions, and follow-ups
    sectors = {
        "Healthcare": {
            "question": "Rate healthcare services (1-5):",
            "follow_up": ["Hospitals", "Doctors", "Medicines"]
        },
        "Education": {
            "question": "Rate education quality (1-5):",
            "follow_up": ["Schools", "Teachers", "Curriculum"]
        },
        "Water Supply": {
            "question": "Rate water supply services (1-5):",
            "follow_up": ["Cleanliness", "Availability", "Pressure"]
        },
        "Transportation": {
            "question": "Rate transportation facilities (1-5):",
            "follow_up": ["Roads", "Public Transport", "Traffic Management"]
        },
        "Garbage Collection": {
            "question": "Rate garbage collection services (1-5):",
            "follow_up": ["Frequency", "Quality", "Timeliness"]
        },
        "Safety and Security": {
            "question": "Rate safety and security in your area (1-5):",
            "follow_up": ["Police Presence", "Street Lighting", "Community Awareness"]
        },
    }

    # Iterate through sectors and get responses
    for sector, details in sectors.items():
        st.subheader(sector)

        # Initial rating question
        rating = st.slider(details["question"], 1, 5, key=f"rating_{sector}")
        responses[sector] = {"Rating": rating}

        # Show follow-up questions only if rating is ≤ 3
        if rating <= 3:
            st.write(f"Please provide specific feedback for {sector}:")
            follow_up_responses = {}
            for follow_up in details["follow_up"]:
                follow_up_rating = st.slider(
                    f"Rate {follow_up} in {sector} (1-5):",
                    1,
                    5,
                    key=f"{sector}_{follow_up}"
                )
                follow_up_responses[follow_up] = follow_up_rating
            responses[sector]["Follow_Up"] = follow_up_responses

            # Mandatory text feedback for low ratings
            feedback = st.text_area(f"Describe issues in {sector}:", key=f"feedback_{sector}")
            responses[sector]["Comments"] = feedback
        else:
            responses[sector]["Follow_Up"] = "No follow-up feedback required."
            responses[sector]["Comments"] = "No issues reported."

    # Media Uploads for Feedback (Image and Video)
    st.header("Upload Images or Videos for Feedback (Optional)")

    # Image Upload
    image = st.file_uploader("Upload an image related to the issue", type=["jpg", "jpeg", "png"])
    image_path = None
    if image:
        image_path = os.path.join(image_dir, image.name)
        with open(image_path, "wb") as f:
            f.write(image.read())
        st.image(image, caption="Uploaded Image", use_column_width=True)

    # Video Upload
    video = st.file_uploader("Upload a video related to the issue", type=["mp4", "mov", "avi"])
    video_path = None
    if video:
        video_path = os.path.join(video_dir, video.name)
        with open(video_path, "wb") as f:
            f.write(video.read())
        st.video(video)

    # Submission button
    if st.button("Submit"):
        # Prepare data for saving
        row_data = {
            "Survey Number": survey_number,
            "Name": name,
            "Age": age,
            "Area": area,
            "Image Feedback": image_path if image_path else "No Image Uploaded",
            "Video Feedback": video_path if video_path else "No Video Uploaded"
        }

        # Add ratings and follow-up data for each sector
        for sector, feedback in responses.items():
            row_data[f"{sector} Rating"] = feedback["Rating"]
            row_data[f"{sector} Follow-Up"] = feedback["Comments"]

            # Add sub-area ratings if applicable
            if isinstance(feedback["Follow_Up"], dict):
                for sub_area, sub_rating in feedback["Follow_Up"].items():
                    row_data[f"{sector} - {sub_area} Rating"] = sub_rating

        # Convert to DataFrame
        new_data = pd.DataFrame([row_data])

        # Save the updated data to CSV
        try:
            existing_df = pd.read_csv(file_name)
            updated_data = pd.concat([existing_df, new_data], ignore_index=True)
        except FileNotFoundError:
            updated_data = new_data

        updated_data.to_csv(file_name, index=False)
        st.success("Thank you for your feedback! Your response has been recorded.")
else:
    st.warning("Please complete your basic information (Name, Age, Survey Number, and Area) to proceed.")
    st.stop()
