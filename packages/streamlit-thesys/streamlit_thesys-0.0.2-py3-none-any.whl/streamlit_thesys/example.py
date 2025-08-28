import streamlit as st
from streamlit_thesys import visualize, render_response
from streamlit_thesys.demo_data import DEFAULT_USER_MESSAGE, DEMO_DATA_OPTIONS
from openai import OpenAI
from typing import Any
import os
import json
import pandas as pd

st.subheader("Thesys + Streamlit")

# You need to get your API key from https://console.thesys.dev
# For demo purposes, you can add your API key here or use environment variables
API_KEY = st.secrets.get("THESYS_API_KEY", os.environ.get("THESYS_API_KEY", ""))

if not API_KEY or API_KEY == "your-api-key-here":
    st.info("Get your API key from: https://console.thesys.dev")

    # Add input field for API key in the UI
    user_api_key = st.text_input(
        "Enter your Thesys API Key:",
        type="password",
        help="Your API key will be used for this session only"
    )

    if user_api_key:
        API_KEY = user_api_key
        st.success("✅ API key provided! You can now use the component below.")
    else:
        st.info("👆 Please enter your API key above to continue")
        st.stop()

# Initialize the OpenAI client with Thesys base URL
client = OpenAI(
    api_key=API_KEY,
    base_url="https://api.thesys.dev/v1/embed"
)

# Add tabs for different functionalities
tab1, tab2 = st.tabs(["Visualize Data", "Chat"])

with tab1:
    st.subheader("Visualize Data")
    st.write("Upload your own data file to create visualizations with Thesys.")

    data_input: Any = None  # Initialize with None to allow proper type inference
    data_source = ""

    # Primary file upload section
    uploaded_file = st.file_uploader(
        "Choose a data file",
        type=['csv', 'xlsx', 'xls', 'json'],
        help="Upload CSV, Excel, or JSON files for visualization"
    )

    if uploaded_file is not None:
        try:
            # Process different file types with proper encoding handling
            if uploaded_file.name.endswith('.csv'):
                # Try multiple encodings for CSV files
                encodings_to_try = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'iso-8859-1']
                data_input = None

                for encoding in encodings_to_try:
                    try:
                        # Reset file pointer
                        uploaded_file.seek(0)
                        data_input = pd.read_csv(uploaded_file, encoding=encoding)
                        break
                    except (UnicodeDecodeError, UnicodeError):
                        continue

                if data_input is None:
                    raise ValueError("Could not decode the CSV file with any supported encoding")

                data_source = f"Uploaded CSV file: {uploaded_file.name}"
                st.success(f"✅ Successfully loaded {uploaded_file.name}")
                st.dataframe(data_input.head())

            elif uploaded_file.name.endswith(('.xlsx', '.xls')):
                # Excel files typically handle encoding better
                uploaded_file.seek(0)
                data_input = pd.read_excel(uploaded_file)
                data_source = f"Uploaded Excel file: {uploaded_file.name}"
                st.success(f"✅ Successfully loaded {uploaded_file.name}")
                st.dataframe(data_input.head())

            elif uploaded_file.name.endswith('.json'):
                # Handle JSON with proper encoding
                uploaded_file.seek(0)
                try:
                    # Try UTF-8 first (most common for JSON)
                    json_content = uploaded_file.read().decode('utf-8')
                    json_data = json.loads(json_content)
                except UnicodeDecodeError:
                    # Fallback to other encodings
                    uploaded_file.seek(0)
                    json_content = uploaded_file.read().decode('utf-8-sig')
                    json_data = json.loads(json_content)

                data_input = json_data
                data_source = f"Uploaded JSON file: {uploaded_file.name}"
                st.success(f"✅ Successfully loaded {uploaded_file.name}")
                st.json(data_input)

        except ValueError as e:
            st.error(f"❌ Encoding error: {str(e)}")
            st.info("💡 Try saving your file with UTF-8 encoding, or use Excel format (.xlsx) instead.")
            data_input = None
        except Exception as e:
            st.error(f"❌ Error reading file: {str(e)}")
            st.info("Please check your file format and try again.")
            data_input = None

    # Demo data option (only show if no file uploaded)
    if uploaded_file is None:
        demo_option = st.selectbox(
            "Or choose a demo dataset:",
            list(DEMO_DATA_OPTIONS.keys()),
            help="Select from various demo datasets to test visualization"
        )

        if st.button("Load Demo Data", key="load_demo"):
            # Store demo data in session state
            st.session_state.demo_data = DEMO_DATA_OPTIONS[demo_option]()
            st.session_state.demo_data_source = f"Demo dataset: {demo_option}"
            st.session_state.demo_data_name = demo_option

    # Check if demo data is loaded in session state
    if uploaded_file is None and hasattr(st.session_state, 'demo_data'):
        data_input = st.session_state.demo_data
        data_source = st.session_state.demo_data_source
        st.success(f"Loaded demo dataset: {st.session_state.demo_data_name}")
        st.dataframe(data_input.head())

        # Add button to clear demo data
        if st.button("Clear Demo Data", key="clear_demo"):
            del st.session_state.demo_data
            del st.session_state.demo_data_source
            del st.session_state.demo_data_name
            st.rerun()

    # Instructions and generate button
    if data_input is not None:
        st.markdown("---")
        st.markdown("### Visualization Instructions")
        instructions = st.text_area(
            "Instructions (optional):",
            value="",
            help="Provide specific instructions for how you want the data visualized. Leave empty for automatic visualization.",
            placeholder="e.g., 'Create a bar chart showing sales by month' or 'Generate a line graph with trend analysis'"
        )

        # Generate visualization button
        if st.button("Generate Visualization", type="primary", key="visualize_btn"):
            with st.spinner(f"Calling Thesys Visualize API with {data_source.lower()}..."):
                # Call the thesys_visualize function with instructions
                visualize(instructions=instructions, data=data_input, api_key=API_KEY)
    else:
        st.info("📤 Upload a file above or load demo data to get started.")


with tab2:
    # User input for custom messages
    user_message = st.text_input("Enter your message:",
                                 value=DEFAULT_USER_MESSAGE,
                                 help="Type a message to send to LLM")

    if st.button("Send Message", type="primary"):
        with st.spinner("Calling Thesys C1 API..."):
            try:
                # Send the user message to the Thesys C1 API
                response = client.chat.completions.create(
                    model="c1/anthropic/claude-sonnet-4/v-20250815",
                    messages=[
                        {"role": "user", "content": user_message}
                    ],
                )

                # Extract the response content
                c1_response = response.choices[0].message.content

                st.success("✅ Successfully received response from Thesys C1 API")

                # Store the response in session state for persistence
                st.session_state.c1_response = c1_response

            except Exception as e:
                st.error(f"❌ Error calling Thesys API: {str(e)}")
                st.info("Make sure you have a valid API key and internet connection")
                # Fallback to a demo response
                st.session_state.c1_response = f"Demo response for: '{user_message}' - This is a fallback since the API call failed."

    # Render the response using the Thesys component
    if hasattr(st.session_state, 'c1_response'):
        st.subheader("C1 Component Response:")
        action = render_response(st.session_state.c1_response)
        if action:
            st.write("User indicated the next turn . Next action:")
            st.write(action)
    else:
        st.info("👆 Click 'Send Message' to see the Thesys C1 component in action!")
