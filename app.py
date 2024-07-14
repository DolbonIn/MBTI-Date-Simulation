import streamlit as st
import time
import random
import requests
import json

BASE_API_URL = "http://localhost:7860/api/v1/run"
FLOW_ID = "fba6b57c-1912-4fcb-a40e-b7321b7ec209"

def run_flow(message, endpoint, output_type="chat", input_type="chat", tweaks=None):
    api_url = f"{BASE_API_URL}/{endpoint}"
    payload = {
        "input_value": message,
        "output_type": output_type,
        "input_type": input_type,
    }
    if tweaks:
        payload["tweaks"] = tweaks
    response = requests.post(api_url, json=payload)
    return response.json()

st.set_page_config(layout="wide")

# Initialize session state variables
if 'page' not in st.session_state:
    st.session_state.page = 'input'
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'step' not in st.session_state:
    st.session_state.step = 1

# MBTI list
mbti_types = ['ISTJ', 'ISFJ', 'INFJ', 'INTJ', 'ISTP', 'ISFP', 'INFP', 'INTP', 
              'ESTP', 'ESFP', 'ENFP', 'ENTP', 'ESTJ', 'ESFJ', 'ENFJ', 'ENTJ']

# MBTI Persona mapping (simplified for brevity)
MBTI_PERSONAS = {
    "ENTP": "Embody an ENTP personality:\n\nBe extraverted, intuitive, thinking, and perceiving.\nShow curiosity, wit, creativity, and love for intellectual discourse.\nDisplay confidence, but avoid arrogance.\nExhibit a tendency for debate and playful argumentation.\nShow enthusiasm for new ideas and experiences.",
    # Add other MBTI types here
}

# Step instructions and queries
STEP_INSTRUCTIONS = {
    1: "ENTP has expressed interest in talking to the user through a mutual friend and got the user's contact number. They want to ask the user on a date and get to know them. ENTP greets and introduces themselves first. Remember this is the initial contact and ENTP is interested in the user, so let the ENTP personality seep through in the greeting and possibly a pickup line depending on the personality.",
    2: "ENTP asks if the user is available to meet over the weekend and suggests a time and place. Remember this is the initial contact, so let the ENTP personality shine through while keeping the conversation simple and not overbearing. If the personality type isn’t the best planner, let that show.",
    3: "Transition smoothly from the previous conversation by asking about favourite foods or what the user would like to eat on their first date. Remember this is early in the communication, so ENTP's personality should come through when setting up the date, but keep the conversation simple and not overbearing. Suggest going to eat the food the user likes, as entp is the one interested.",
    4: "It’s the first time they meet in person. ENTP greets the user in person and talks about their hobbies on the way to the restaurant. Ask the questions to get to know how the user feels about entp’s hobbies or more generally, their attitude towards these activities.",
    5: "Answer and react appropriately to the user being mindful of entp personality. Transition to ENTP talking about their job or major and recent activities, then asks the user about their job, how they feel about their job or something like it to find out more about the user's lifestyle, values, and passion.",
    6: "Show how ENTP empathizes with the user’s response. Show how ENTP responds to the user’s discussion about their job or project. Phrase the instruction to let the AI decide how the ENTP chooses to empathize, whether it’s through curiosity, shared enthusiasm, or practical advice, reflecting their unique personality.",
    7: "ENTP now gets deeper into the conversation to talk about relationship style and asks the user about theirs. They are on their first date, so it’s important that they learn this about each other. Make it sincere and let it naturally flow from the last conversation.",
    8: "Respond and transition from the user’s answer to leaving the restaurant naturally. As an ENTP personality, decide how the payment will happen reflecting ENTP’s general belief and attitude towards a first date, and ask the user how they feel about ENTP’s decision.",
    9: "As you both leave the restaurant, if the user’s response conflicts with ENTP’s decision, show how ENTP would respond to this value conflict. Otherwise, respond to the user’s compliance with payment in an ENTP way.",
    10: "With the overview of the date, decide critically and thoughtfully as an entp if you’d like to continue getting to know each other. If you think entp type is not as compatible with the user based on the chat history, do not suggest a second date and make up a bizarre excuse to never meet again. If you think they are compatible, ask the user on a second date based on personality or chat history."
}

STEP_QUERIES = {
    1: "자기소개, 성격, 첫 만남",
    2: "약속 잡기, 만남 제안, 시간, 장소",
    3: "음식 취향, 식당",
    4: "취미",
    5: "직업, 일",
    6: "공감, 반응",
    7: "연애 스타일",
    8: "데이트, 돈, 가치관",
    9: "의견 차이, 성향, 데이트",
    10: "연애, 취미"
}

def get_tweaks(user_name, target_mbti, step):
    return {
        "TextInput-OtVSC": {"input_value": MBTI_PERSONAS.get(target_mbti, "")},
        "TextInput-scuMd": {"input_value": f"{target_mbti.lower()}-cohere"},
        "TextInput-57M8e": {"input_value": STEP_INSTRUCTIONS.get(step, "")},
        "TextInput-VqkYz": {"input_value": STEP_QUERIES.get(step, "")},
        "TextInput-gYOmP": {"input_value": user_name}
    }

def get_bot_response(response_data):
    return response_data['outputs'][0]['outputs'][0]['results']['message']['data']['text']

def parse_options(options_data):
    options_text = options_data['outputs'][0]['outputs'][1]['results']['message']['data']['text']
    options = []
    for line in options_text.split('\n'):
        if line.startswith('1. <') or line.startswith('2. <') or line.startswith('3. <') or line.startswith('4. <'):
            options.append(line[4:-1].strip())
    return options

# Input page
if st.session_state.page == 'input':
    st.title("MBTI Date Simulation")
    
    col1, col2 = st.columns(2)
    
    with col1:
        user_name = st.text_input("Enter your name")
        user_mbti = st.selectbox("Select your MBTI", mbti_types)
    
    with col2:
        target_mbti = st.selectbox("Select the MBTI of the person you want to date", mbti_types)
    
    if st.button("Start Chatting"):
        if user_name and user_mbti and target_mbti:
            st.session_state.user_name = user_name
            st.session_state.user_mbti = user_mbti
            st.session_state.target_mbti = target_mbti
            st.session_state.page = 'loading'
            st.rerun()
        else:
            st.error("Enter all the fields")

# Loading page
elif st.session_state.page == 'loading':
    st.title("Requesting...")
    progress_bar = st.progress(0)
    for i in range(100):
        time.sleep(0.01)
        progress_bar.progress(i + 1)
    st.session_state.page = 'chat'
    st.rerun()

# Chat page
elif st.session_state.page == 'chat':
    st.title(f"{st.session_state.user_name}'s Date Simulation")

    # Chat container
    chat_container = st.container()

    # Input container
    input_container = st.container()

    # Display chat messages
    with chat_container:
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.write(f'<div class="chat-message user-message">{message["content"]}</div>', unsafe_allow_html=True)
            else:
                st.write(f'<div class="chat-message bot-message">{message["content"]}</div>', unsafe_allow_html=True)

    # Handle user input
    with input_container:
        col1, col2 = st.columns([1, 3])
        with col1:
            st.write(f"Name: {st.session_state.user_name}")
            st.write(f"My MBTI: {st.session_state.user_mbti}")
            st.write(f"Data partner's MBTI: {st.session_state.target_mbti}")
            st.write(f"Corrent Score: {st.session_state.score}")
            st.write(f"Corrnet Step: {st.session_state.step}/10")
        with col2:
            if st.session_state.step <= 10:
                if 'current_options' not in st.session_state or not st.session_state.current_options:
                    # Get bot response and options
                    tweaks = get_tweaks(st.session_state.user_name, st.session_state.target_mbti, st.session_state.step)
                    response = run_flow("", FLOW_ID, tweaks=tweaks)
                    
                    bot_response = get_bot_response(response)
                    options = parse_options(response)
                    
                    # Display bot response
                    st.write(f'<div class="chat-message bot-message">{bot_response}</div>', unsafe_allow_html=True)
                    st.session_state.messages.append({"role": "assistant", "content": bot_response})
                    
                    # Store options in session state
                    st.session_state.current_options = options
                    random.shuffle(st.session_state.current_options)

                # Display options as buttons
                for i, option in enumerate(st.session_state.current_options, 1):
                    if st.button(f"Option {i}: {option}", key=f"option_{i}_{st.session_state.step}"):
                        st.session_state.score += 5 - i
                        st.session_state.messages.append({"role": "user", "content": option})
                        st.session_state.step += 1
                        st.session_state.current_options = []  # Clear current options
                        st.rerun()
            else:
                st.write("Thank you for chatting with me!")
                st.write(f"Final Score: {st.session_state.score}")





# Apply styles
st.markdown("""
<style>
.chat-message {
    padding: 1.5rem;
    border-radius: 0.5rem;
    margin-bottom: 1rem;
    display: flex;
    max-width: 80%;
    color: black;
}
.user-message {
    background-color: #DCF8C6;
    margin-left: auto;
    border-bottom-right-radius: 0;
}
.bot-message {
    background-color: #FFFFFF;
    margin-right: auto;
    border-bottom-left-radius: 0;
}
.stApp {
    max-width: 80%;
    margin: 0 auto;
}
</style>
""", unsafe_allow_html=True)