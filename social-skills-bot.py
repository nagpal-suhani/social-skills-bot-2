import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')
st.set_page_config(page_title="Gemini LLM Social Skills Trainer")

theme = {
    "base": "light",
    "primaryColor": "#2e7d32",  # Dark green
    "secondaryBackgroundColor": "#f0f8f0",  # Very light green
    "backgroundColor": "#ffffff",  # White
    "textColor": "#000000",  # Black
    "font": "sans serif",
    "mainBackgroundColor": "#e0f2e7",   # Light green main content
    "sidebarBackgroundColor": "#e0f2e7", # Light green sidebar (same as main)
    "sidebarBorderColor": "#1b5e20",    # Dark green sidebar border
    "buttonBackgroundColor": "#a5d6a7",  # Light green button background
    "buttonTextColor": "#000000",      # Black button text
    "buttonBorderColor": "#1b5e20",    # Darker green button border
    "headerFooterColor": "#2e7d32",    # Dark green header/footer
}
st.markdown(
    f"""
    <style>
    body {{
        color: {theme["textColor"]};
        background-color: {theme["mainBackgroundColor"]}; /* Default to main content background */
        font-family: {theme["font"]};
    }}
    .stApp {{
        background-color: {theme["mainBackgroundColor"]}; /* Overall app background */
    }}
    .st-emotion-cache-k2z1pe {{ /* Sidebar container */
        background-color: {theme["sidebarBackgroundColor"]};
        color: {theme["textColor"]};
        border-right: 5px solid {theme["sidebarBorderColor"]}; /* Dark green right border */
    }}
    .st-emotion-cache-6qob1r {{ /* Sidebar content */
        background-color: {theme["sidebarBackgroundColor"]};
        color: {theme["textColor"]};
    }}
    .st-emotion-cache-8atqhb button {{ /* Buttons */
        background-color: {theme["buttonBackgroundColor"]};
        color: {theme["buttonTextColor"]};
        border-color: {theme["buttonBorderColor"]};
    }}
    
    .st-emotion-cache-1yiq2ps {{ /* Main content container */
        background-color: {theme["mainBackgroundColor"]};
        color: {theme["textColor"]};
    }}
    .st-emotion-cache-bm2z3a {{ /* Main content area */
        background-color: {theme["mainBackgroundColor"]};
        color: {theme["textColor"]};
    }}
    .st-emotion-cache-1d2o6qs {{ /* Main block container */
        background-color: {theme["mainBackgroundColor"]};
        color: {theme["textColor"]};
    }}
    div[data-testid="stChatMessage"] {{ /* Chat message boxes */
        background-color: {theme["secondaryBackgroundColor"]};
        border-radius: 5px;
        padding: 0.5rem;
        margin-bottom: 0.5rem;
    }}
    /* Target assistant messages specifically to set text color to black */
    div[data-testid="stChatMessage"][data-streamlit="false"] div[data-testid="stMarkdownContainer"] p,
    div[data-testid="stChatMessage"][data-streamlit="false"] div[data-testid="stMarkdownContainer"] li {{
        color: {theme["textColor"]};
    }}
    div[data-testid="stChatMessage"][data-streamlit="true"] div[data-testid="stMarkdownContainer"] p,
    div[data-testid="stChatMessage"][data-streamlit="true"] div[data-testid="stMarkdownContainer"] li {{
        color: {theme["textColor"]}; /* Ensure user text is also black */
    }}
    div[data-testid="stChatInputContainer"] {{ /* Chat input container */
        background-color: {theme["backgroundColor"]};
        border-top: 1px solid #ccc;
        padding-top: 1rem;
    }}
    div[data-testid="stChatInputContainer"] textarea {{ /* Chat input textarea */
        color: {theme["textColor"]};
        background-color: #e0f2e7; /* Light green input */
        border-radius: 5px;
        padding: 0.5rem;
    }}
    h1, h2, h3, h4, h5, h6,p {{
        color: {theme["textColor"]}; /* Use primary color for headings */
    }}
    .stChatInput{{
        color: #e0f2e7;
    }}
    .stSidebarTitle {{
        color: {theme["primaryColor"]};
    }}
    .stAppHeader{{
        background-color: {theme["mainBackgroundColor"]};
    }}
    .st-emotion-cache-hzygls{{
        background-color: {theme["mainBackgroundColor"]};
    }}
    .st-emotion-cache-a6qe2i button:hover {{
        background-color: #ffffff; /* Darker green on hover */
        
    }}
    .stBottomBlockContainer{{
        background-color: {theme["mainBackgroundColor"]};
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# Initialize session state for messages if it doesn't exist
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.current_scenario = "Networking Event"  # Default scenario
    st.session_state.scenario_prompt = ""
    st.session_state.custom_scenario_input = "" # Initialize custom input

# Predefined scenarios and instructions
scenarios = {
    "Job Interview": {
        "description": "Practice answering common interview questions, handling unexpected questions, and demonstrating professionalism.",
        "prompt": "Act as a social skills coach. Simulate a job interview. I am the interviewee. Ask me the first interview question and provide feedback on my responses.",
    },
    "Networking Event": {
        "description": "Simulate introducing yourself, making small talk, and exchanging contact information.",
        "prompt": "Act as a social skills coach at a networking event. Initiate a conversation with me and guide me through introducing myself and making small talk. Provide feedback on my approachability, conversation skills, and ability to build rapport after my responses.",
    },
    "Doctor's Appointment": {
        "description": "Practice clearly explaining symptoms, asking questions, and understanding medical advice.",
        "prompt": "Act as a doctor. I am your patient. Start the appointment by asking about my reason for visiting today. Provide feedback on my clarity and accuracy in describing my symptoms and answering your questions.",
    },
    "Attending a Party": {
        "description": "Practice navigating social situations, making introductions, and engaging in conversations.",
        "prompt": "Act as a social skills coach at a party. Initiate a casual conversation with me. Provide feedback on my social awareness, conversation skills, and ability to mingle after my responses.",
    },
    "Handling disagreements": {
        "description": "Practice stating your opinion in a respectful manner.",
        "prompt": "Act as a social skills coach. Let's role-play a scenario where we have different opinions on a topic. I will state my initial view. You then present a contrasting view and provide feedback on how I express my disagreement and respond to your view.",
    },
    "Custom Scenario": {
        "description": "Enter your own custom social scenario.",
        "prompt": "Act as a social skills coach. Simulate the following social scenario: ",  # combined with user input
    }
}

def initialize_scenario(scenario_name, custom_prompt=""):
    st.session_state.messages = []
    st.session_state.scenario_prompt = ""
    if scenario_name == "Custom Scenario" and custom_prompt:
        st.session_state.scenario_prompt = scenarios["Custom Scenario"]["prompt"] + custom_prompt
        first_response = model.generate_content(st.session_state.scenario_prompt).text
        st.session_state.messages.append({"role": "assistant", "content": first_response})
    elif scenario_name != "Custom Scenario":
        st.session_state.scenario_prompt = scenarios[scenario_name]["prompt"]
        first_response = model.generate_content(st.session_state.scenario_prompt).text
        st.session_state.messages.append({"role": "assistant", "content": first_response})
    elif scenario_name == "Custom Scenario" and not custom_prompt:
        st.session_state.scenario_prompt = ""
        st.warning("Please enter your custom scenario.")

def change_scenario(scenario_name):
    st.session_state.current_scenario = scenario_name
    st.session_state.custom_scenario_input = "" # Clear previous custom input
    initialize_scenario(st.session_state.current_scenario) # Initialize when scenario changes

st.sidebar.title("Choose Scenario")
for scenario_name in scenarios:
    st.sidebar.button(scenario_name, on_click=change_scenario, args=(scenario_name,))

if st.session_state.current_scenario:
    st.header(f"Scenario: {st.session_state.current_scenario} - {scenarios[st.session_state.current_scenario]['description']}")

custom_scenario_text = ""
if st.session_state.current_scenario == "Custom Scenario":
    custom_scenario_text = st.text_area("Describe your custom social scenario:", key="custom_scenario_input")
    if custom_scenario_text and not st.session_state.messages:
        initialize_scenario("Custom Scenario", custom_scenario_text)
    elif not custom_scenario_text and not st.session_state.messages:
        st.warning("Please enter your custom scenario to start.")
elif not st.session_state.messages and st.session_state.current_scenario != "Custom Scenario":
    initialize_scenario(st.session_state.current_scenario)

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if st.session_state.scenario_prompt and st.session_state.current_scenario != "Custom Scenario":
    if prompt := st.chat_input("Your response:"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        full_conversation = ""
        for msg in st.session_state.messages:
            full_conversation += f"{msg['role']}: {msg['content']}\n\n"

        feedback_prompt = f"""Continue the social skills coaching scenario based on the following conversation:

        {full_conversation}

        As the social skills coach, provide the next turn in the conversation, and then provide specific feedback on the user's last response, focusing on approachability, conversation skills, and rapport-building (or other relevant skills for the chosen scenario). If the user's response was ineffective, explain why and suggest how they could have responded better.
        """

        with st.chat_message("assistant"):
            response = model.generate_content(feedback_prompt).text
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

elif st.session_state.current_scenario == "Custom Scenario" and st.session_state.scenario_prompt:
    if prompt := st.chat_input("Your response:"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        full_conversation = ""
        for msg in st.session_state.messages:
            full_conversation += f"{msg['role']}: {msg['content']}\n\n"

        feedback_prompt = f"""Continue the social skills coaching scenario based on the following conversation:

        {full_conversation}

        As the social skills coach, provide the next turn in the conversation, and then provide specific feedback on the user's last response, focusing on the social skills relevant to the custom scenario. If the user's response was ineffective, explain why and suggest how they could have responded better.
        """

        with st.chat_message("assistant"):
            response = model.generate_content(feedback_prompt).text
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})