import streamlit as st
import sqlite3
import pandas as pd
import os
from openai import OpenAI
# ================================
# 🎨 Streamlit Page Config
# ================================
st.set_page_config(
    page_title="Investment Incentive Query Tool",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================================
# 💰 Custom CSS for Styling
# ================================
st.markdown("""
    <style>
        /* Main App Background */
        .stApp {
            background-color: #f7f9fc;
        }
        
        /* Title Style */
        .title {
            text-align: center;
            color: #2c3e50;
            font-size: 40px;
            font-weight: bold;
            margin-bottom: 10px;
        }
        
        /* Sub Title */
        .sub-title {
            text-align: center;
            color: #7f8c8d;
            font-size: 18px;
            margin-bottom: 20px;
        }

        /* Buttons */
        .stButton button {
            background-color: #3498db;
            color: white;
            border-radius: 8px;
            padding: 8px 18px;
            font-size: 16px;
            border: none;
            transition: 0.3s;
        }
        .stButton button:hover {
            background-color: #2980b9;
        }

        /* Dataframe container */
        .dataframe-container {
            border: 1px solid #e0e0e0;
            padding: 10px;
            border-radius: 10px;
            background-color: white;
            box-shadow: 0px 2px 6px rgba(0, 0, 0, 0.05);
        }
    </style>
""", unsafe_allow_html=True)

# ================================
# Title Section
# ================================
st.markdown("""
    <div style="
        background-color: #F5E0B2;  
        padding: 15px; 
        border-radius: 10px;
        text-align: center;
        ">
        <h1 style="color: black; font-size: 38px;">
            💰Investment Query Tool
        </h1>
    </div>
""", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Run SQL queries directly on the Investment Incentive database</div>", unsafe_allow_html=True)

# ================================
# Database Connection
# ================================

# DB Connection
DB_PATH = os.path.join(os.path.dirname(__file__), 'Incentive.db')


# Function to fetch data
def run_query(query):
    conn = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except Exception as e:
        conn.close()
        raise e

# ================================
# Layout: 2 Columns
# ================================
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📝 Write Your SQL Query")
    query = st.text_area(
        "SQL Query",
        "SELECT * FROM Incentive LIMIT 10;",
        height=150
    )

with col2:
    st.subheader("ℹ️ Information")
    st.markdown("""
    - *Write custom SQL queries* to fetch data.  
    - Click *Run Query* to execute and view results.  
    - Click *Analyze Data* to get summary statistics.  
    """)

# ================================
# Buttons for Actions
# ================================


st.markdown("---")
action_col1, action_col2 = st.columns([1, 1])

with action_col1:
    run_button = st.button("🚀 Run Query", use_container_width=True)

with action_col2:
    analyze_button = st.button("📊 Analyze Data", use_container_width=True)

# ================================
# Run the Query and Display
# ================================
if run_button:
    try:
        df = run_query(query)
        st.markdown("### 📋 Query Results")
        st.markdown("<div class='dataframe-container'>", unsafe_allow_html=True)
        st.dataframe(df, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    except Exception as e:
        st.error(f"❌ Error running query: {e}")




# ================================
# Connecting with LLM
# ================================


# Hugging Face API Key

HF_API_KEY=st.secrets("HF_API_KEY")   # store token in streamlit secrets
headers = {"Authorization": f"Bearer {HF_API_KEY}"}      # headers will be passed as Autorized Key to connect to Hugging Face

# Updated Available Models (verified working models)
MODEL_OPTIONS = {   
    "GPT-oss": {"id":"openai/gpt-oss-120b:cerebras","task":"conversational"},        #Text Generation task and Conversational task are different(don't maintain context ,maintain context for future messages as well as current message)
    "DeepSeek": {"id":"deepseek-ai/DeepSeek-R1-Distill-Llama-70B:groq","task":"Conversational"},
    "llama-3.1":{"id":"meta-llama/Llama-3.1-8B-Instruct","task":"conversational"},
    "DeepSeekV3": {"id":"deepseek-ai/DeepSeek-V3.1:fireworks-ai","task":"Conversational"}
}

# Select LLM model
st.sidebar.header("⚙️ LLM Settings")
selected_model = st.sidebar.selectbox("Choose Model:", list(MODEL_OPTIONS.keys()))
Model_cfg=MODEL_OPTIONS[selected_model]

# ================================
# Analyze the Data
# ================================


if analyze_button:
    try:
        df = run_query(query)
        st.markdown("<div class='dataframe-container'>", unsafe_allow_html=True)
        #st.dataframe(df_summary, use_container_width=True)
        try:
            #df = st.session_state['query_result']
            #query = st.session_state['last_query']
            
           

            prompt = f'''Analyze this {df} generated by executing nSQL query: {query} Give clear insights.'''
            
            client = OpenAI(                                      # Open AI Compatible API Endpoint use for Open AI as well as Hugging Face Hosted Models
                base_url="https://router.huggingface.co/v1",
                api_key=HF_API_KEY,
            )

            completion = client.chat.completions.create(
                model=Model_cfg['id'],
                messages=[
                    {
                        "role": "user",         # Setting the user role to provide the main input prompt(How User Going to provide input)
                        "content":prompt
                    },
                    {
                        "role": "system",             # Setting the system role to guide the model's behavior(How to generate the response)
                        "content": "You are a helpful financial analyst. Always answer in bullet points and use Indian Rupees.Please keep response in Simple English and engaging. Try to show comparisons and trends where possible in tabular form. If the data is insufficient to provide insights, respond with 'Data Insufficient for Insights'."
                        "Columns context:Month=Booking Month,BU=Business Unit,Emp ID=Employee ID,Agent Name=Employee Name,Agening range=Tenurity of Employee,"
                        "Process= Under which tag Agent Get Incentive,Sourced APE=Sourcing Amount,Issued APE=Sourcing Amount After Issuance,Total Issued Weighted APE=Total Amount After Issuance and Some Applied Factors,Booking Incentive=Incentive Calculated based on Number of Bookings,M CTC=Monthly CTC of Employee,Inc Basis CJ=Did Employee Able to justify his CTC if 0 then its means No,"
                        "Incentive for This Month=Incentive of Employee for that month,Incentive After Arrear & Clawback=Incentive of Employee for that month + Previous Month Incentive Difference"
                    }
                ],
            )
            
            
            


            with st.spinner(f"Analyzing with {selected_model}..."):
            
                  # LangChain ka magic
                st.subheader("🤖 AI Insights")
                st.write(completion.choices[0].message.content)        #Completion object ka content(Dictinoary nahi hai therefore accessing the content key by .contet)
              
                
           
            
        except Exception as e:
            st.error(f"Error while generating insights: {e}")

        st.markdown("</div>", unsafe_allow_html=True)
    except Exception as e:

        st.error(f"❌ Error analyzing data: {e}")
