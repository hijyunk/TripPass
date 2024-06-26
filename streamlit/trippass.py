import streamlit as st
from streamlit_option_menu import option_menu
import main, plan, chat

st.set_page_config(layout="wide")

with st.sidebar:
    choice = option_menu("TRIPPASS", ["Main", "Trip", "Chatbot"],
                         icons=['house', 'kanban', 'bi bi-robot'],
                         menu_icon="app-indicator", default_index=0,
                         styles={
        "container": { "background-color": "#fafafa"},
        "icon": {"color": "black", "font-size": "25px"},
        "nav-link": {"font-size": "16px", "text-align": "left", "margin":"0px", "--hover-color": "#fafafa"},
        "nav-link-selected": {"background-color": "#08c7b4"},
    })


if choice == "Main":
    main.show()
if choice == "Trip":
    plan.show()
if choice == "Chatbot":
    chat.show()
