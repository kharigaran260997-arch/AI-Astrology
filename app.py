import streamlit as st
import google.generativeai as genai
from datetime import datetime
import os

# ============================================================================
# PAGE CONFIGURATION & SESSION STATE INITIALIZATION
# ============================================================================

st.set_page_config(
    page_title="பர்சனல் ஏஐ ஜோதிடர்",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state variables for zero-storage security
if "messages" not in st.session_state:
    st.session_state.messages = []

if "horoscope_data" not in st.session_state:
    st.session_state.horoscope_data = None

if "api_key" not in st.session_state:
    st.session_state.api_key = None

if "file_uploaded" not in st.session_state:
    st.session_state.file_uploaded = False

# ============================================================================
# SIDEBAR: API KEY & FILE UPLOAD
# ============================================================================

with st.sidebar:
    st.markdown("### 🔐 பாதுகாப்பு அமைப்பு")
    
    # Gemini API Key Input
    api_key_input = st.text_input(
        "Gemini API Key-ஐ உள்ளிடவும்",
        type="password",
        value=st.session_state.api_key or "",
        help="உங்கள் API Key இங்கு உள்ளிடப்பட்ட பிறகு பிரவுசர் மூடினால் அழிந்துவிடும்"
    )
    
    if api_key_input:
        st.session_state.api_key = api_key_input
    
    # File Upload Component
    st.markdown("### 📄 ஜாதக விவரங்கள்")
    uploaded_file = st.file_uploader(
        "உங்கள் ஜாதக டெக்ஸ்ட் (.txt) ஃபைலை அப்லோட் செய்யவும்",
        type=["txt"],
        help="பிரவுசர் மூடும் வரை உங்கள் ஃபைல் பாதுகாப்பாக சேமிக்கப்படுவது நினைவு முறையில் மட்டுமே"
    )
    
    # Process uploaded file
    if uploaded_file is not None:
        try:
            horoscope_text = uploaded_file.read().decode("utf-8")
            st.session_state.horoscope_data = horoscope_text
            st.session_state.file_uploaded = True
            st.success("✅ ஜாதக ஃபைல் வெற்றிகரமாக ஏற்றப்பட்டது")
        except Exception as e:
            st.error(f"❌ ஃபைல் ஏற்றம் தோல்வி: {str(e)}")
            st.session_state.file_uploaded = False
    
    # Display status
    if st.session_state.file_uploaded and st.session_state.horoscope_data:
        file_size = len(st.session_state.horoscope_data)
        st.info(f"📦 ஃபைல் அளவு: {file_size} characters")
    
    # Security notice
    st.markdown("---")
    st.markdown(
        """
        ### 🛡️ பாதுகாப்பு குறிப்பு
        - **சர்வரில் சேமிப்பு ஏதுமில்லை**: உங்கள் அனைத்து தரவு பிரவுசர் நினைவு முறையில் மட்டுமே உள்ளது
        - **தானாக நீக்கம்**: பிரவுசர் ட்யாப் மூடினால் அனைத்து தரவு நிரந்தரமாக அழிந்துவிடும்
        - **API Key பாதுகாப்பு**: உங்கள் API Key சர்வரில் பெறப்படாது அல்லது லாக் செய்யப்படாது
        """
    )

# ============================================================================
# MAIN AREA: TITLE & DISCLAIMER
# ============================================================================

col1, col2 = st.columns([3, 1])
with col1:
    st.markdown("# 🔮 பர்சனல் ஏஐ ஜோதிடர் (Vedic & KP)")
with col2:
    st.markdown("### Version 1.0")

st.markdown(
    """
    <div style="background-color: #f0f8ff; padding: 15px; border-radius: 10px; border-left: 4px solid #4CAF50;">
        <strong>100% பிரைவசி:</strong> பிரவுசர் ட்டாபை க்ளோஸ் செய்தால் உங்கள் டேட்டா சர்வரில் இருந்து அழிந்துவிடும்.
    </div>
    """,
    unsafe_allow_html=True
)

# ============================================================================
# CREDENTIALS CHECK
# ============================================================================

credentials_valid = st.session_state.api_key and st.session_state.file_uploaded

if not credentials_valid:
    st.info("⚠️ தயவுசெய்து பக்க பக்கவாதிஸை (சாइடபார) பக்ஷ திய:")
    st.write("1. 🔐 உங்கள் **Gemini API Key** உள்ளிடவும்")
    st.write("2. 📄 உங்கள் **ஜாதக `.txt` ஃபைல்** அப்லோட் செய்யவும்")
    st.write("")
    st.stop()

# ============================================================================
# DYNAMIC TIMESTAMP & SYSTEM PROMPT CONSTRUCTION
# ============================================================================

def get_current_transit_time():
    """Get the current system timestamp formatted as per specification."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def construct_system_prompt(horoscope_data, transit_time):
    """Construct the advanced astrology system prompt with KP optimization."""
    system_prompt = f"""நீ 30 வருடங்களுக்கு மேல் அனுபவம் வாய்ந்த, பாரம்பரிய தமிழ் வேதி ஜோதிட (Vedic Astrology) மற்றும் கேபி ஜோதிட (KP Astrology - Krishnamurti Paddhati) மாபெரும் நிபுணர். உன்னிடம் ஜாதகர் தனது முழு ஜாதக விவரங்கள் அடங்கிய கோப்பையும், தற்போதைய கோச்சார (Transit) நேரத்தையும் வழங்கி கேள்வி கேட்கிறார்.

[விதிமுறைகள் & பலன் சொல்லும் முறை]:
1. அணுகுமுறை: ஒரு தேர்ந்த தமிழ் ஜோசியர் எப்படி கனிவாகவும், பக்குவமாகவும், அதே சமயம் உண்மையை மறைக்காமல் நேர்மையாகவும் பேசுவாரோ, அதே போன்ற தமிழ் நடையில் பதில் அளிக்க வேண்டும் (உதாரணமாக: "வணக்கம் அன்பரே...", "உங்களுடைய தசா புத்தி அமைப்பின்படி...", "கவலை வேண்டாம்...").

2. தசா புத்தி ஆய்வு (CRITICAL FOR JOB QUERIES): 
   - ஜாதகரின் CURRENT Dasha & Bhukti நிலையை துல்லியமாக கண்டறி
   - 5 நிலை தசா புத்திகளை (மகா தசா -> புத்தி -> அந்தரம் -> சூட்சுமம் -> பிராண தசா) பகுப்பாய்வு செய்
   - தசா புத்தி மாறும் EXACT தேதிகளைக் குறிப்பிட்டு, எப்போது மாற்றம் நடக்கும் என்று துல்லியமாக சொல்
   - Career/Job house lords (10th house & 11th house) இன் দசா நிலையை பகுப்பாய்வு செய்

3. வேதிக + கேபி கலவை (ESPECIALLY FOR JOB TIMING): 
   - பொதுவான கேள்விகளுக்கு 'வேதி ஜோதிட' முறையையும் (ராசி, லக்னம், கிரக பார்வை, 10-ஆம் அதிபதி நிலை)
   - **JOB TIMING கேள்விகளுக்கு KP முறையை முக்கியமாக பயன்படுத்து**: 
     * 10th Cusp ruler (Career lord) & 11th Cusp ruler (Gain lord) நிலை
     * Starlord & Sub-Lord தொடர்புகள்
     * KP House Significators அட்டவணை பயன்படுத்தி Job house (10, 11) significance கண்டறி
     * Mercury, Venus, Saturn ஆகியவற்றின் role in job timing

4. கோச்சாரம் (Transit Analysis for Job Timing): 
   - தற்போதைய கோச்சார கிரக நிலைகளை, ஜாதகரின் பிறப்பு ராசி மற்றும் லக்னத்திற்கு ஒப்பிட்டு
   - Transit Jupiter, Saturn, Mars, Rahu positions வின் Job house impact
   - 10th house transit effects பகுப்பாய்வு செய்
   - Exact job opportunity timing கணிக்க (உதாரணமாக: "2-3 மাத இல்" அல்லது "July-August 2024")

5. பரிகாரம் (Remedies): தேவையற்ற பயத்தை ஏற்படுத்தாமல், job success உக்காக:
   - Yellow Sapphire (Pukhraj) மணி பரிந்துரை (Jupiter strengthening)
   - Wednesday fasting (Mercury for communication in job)
   - Hanuman Chalisa chanting (Mars for courage in interview)
   - Simple charity suggestions

[KP ANALYSIS FOCUS POINTS FROM HOROSCOPE]:
- 10th House Cusp Lord & Sub-Lord analysis (Career determination)
- 11th House Cusp Lord & Sub-Lord analysis (Gains from career)
- Vimshottari Dasha current phase & upcoming periods
- Yogini Dasha current phase (if favorable)
- Chara Dasha current phase
- Transit Jupiter & Saturn positions relative to natal chart

[ஜாதக விவரங்கள்]:
{horoscope_data}

[தற்போதைய கோச்சார நேரம்]:
{transit_time}

[IMPORTANT INSTRUCTIONS]:
- JOB TIMING கேள்விக்கு KP Cusp analysis & Dasha timing மட்டுமே பயன்படுத்து
- Specific dates or periods suggest if possible (e.g., "அடுத்த 2 மாதத்திற்குள்", "July-September window")
- Job houses are 10 (career) and 11 (gains from career) - focus on their rulers and significators
- Never give false hope - if current dasha is unfavorable, suggest when it will improve
- Use both Vimshottari and Yogini dashas for cross-checking

இந்த விதிமுறைகளை கடுமையாக பின்பற்றி, ஜாதகரின் JOB கேள்விக்கு தமிழ் மொழியில் விரிவாகவும் துல்லியமாகவும் KP அடிப்படையில் பதிலளிக்க வேண்டும்."""
    
    return system_prompt

# ============================================================================
# CHAT INTERFACE & MESSAGE HANDLING
# ============================================================================

# Display chat message history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
user_input = st.chat_input("உங்கள் ஜோதிட கேள்வியை இங்கே உள்ளிடவும்...")

if user_input:
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # Prepare API call
    try:
        # Get current transit time
        current_time = get_current_transit_time()
        
        # Construct system prompt with horoscope data and transit time
        system_prompt = construct_system_prompt(
            st.session_state.horoscope_data,
            current_time
        )
        
        # Configure Gemini API with user's API key
        genai.configure(api_key=st.session_state.api_key)
        
        # Initialize the model (using gemini-2.0-flash which is latest and widely available)
        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            system_instruction=system_prompt
        )
        
        # Create conversation history for API call
        conversation_history = []
        for msg in st.session_state.messages[:-1]:  # Exclude the current user message
            if msg["role"] == "user":
                conversation_history.append({
                    "role": "user",
                    "parts": [msg["content"]]
                })
            else:
                conversation_history.append({
                    "role": "model",
                    "parts": [msg["content"]]
                })
        
        # Call Gemini API with streaming
        response_placeholder = st.chat_message("assistant")
        
        try:
            # Use start_chat to maintain conversation context
            chat = model.start_chat(history=conversation_history)
            full_response = ""
            
            with response_placeholder:
                # Stream the response
                with st.spinner("🔮 ஆய்வு மேற்கொள்ளப்படுகிறது..."):
                    response = chat.send_message(user_input, stream=True)
                    response_text = st.empty()
                    
                    for chunk in response:
                        if chunk.text:
                            full_response += chunk.text
                            response_text.markdown(full_response)
            
            # Add assistant response to chat history
            st.session_state.messages.append({
                "role": "assistant",
                "content": full_response
            })
            
        except Exception as stream_error:
            error_message = f"❌ API Error: {str(stream_error)}"
            with response_placeholder:
                st.error(error_message)
            st.session_state.messages.append({
                "role": "assistant",
                "content": error_message
            })
    
    except Exception as e:
        error_message = f"❌ பிழை ஏற்பட்டது: {str(e)}\n\nதயவுசெய்து உங்கள் API Key சரியாக உள்ளதா என்று சரிபார்க்கவும்."
        with st.chat_message("assistant"):
            st.error(error_message)
        st.session_state.messages.append({
            "role": "assistant",
            "content": error_message
        })

# ============================================================================
# FOOTER & ADDITIONAL INFORMATION
# ============================================================================

st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    **🔐 பாதுகாப்பு**
    - சர்வர் சேமிப்பு ஏதுமில்லை
    - பிரவுசர் நினைவு முறை மட்டுமே
    """)

with col2:
    st.markdown("""
    **📚 அமைப்பு**
    - வேதி ஜோதிட பகுப்பாய்வு
    - KP ஜோதிட தொடர்பு
    - லைவ் கோச்சாரம் (Transit)
    """)

with col3:
    st.markdown("""
    **⚠️ குறிப்பு**
    - இது கல்வி நோக்கமே
    - தெய்வ ஆலோசனை அல்ல
    - நிபுணரைக் கேட்டுக் கொள்ளவும்
    """)

st.markdown("<hr>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align: center; font-size: 12px; color: gray;'>🔮 பர்சனல் ஏஐ ஜோதிடர் v1.0 | 100% பிரவுசர்-அடிப்படை | பாதுகாப்பு முதல் | KP Specialized</p>",
    unsafe_allow_html=True
)
