import streamlit as st
import pandas as pd

# 일정 추가 함수
def add_to_schedule(time_of_day, place_info):
    plan_entry = {
        "type": place_info.get('type', None),
        "name": place_info.get('Name', None),
        "address": place_info.get('Address', None),
        "latitude": place_info.get('latitude', None),
        "longitude": place_info.get('longitude', None),
        "time": time_of_day
    }
    if not isinstance(st.session_state['user_df']['plan'], list):
        st.session_state['user_df']['plan'] = []
    st.session_state['user_df']['plan'].append(plan_entry)

# 일정 조회 함수
def show_schedule():
    schedule = st.session_state['user_df']['plan']
    if not schedule:
        return "아직 계획된 일정이 없습니다.", pd.DataFrame()
    
    response = "현재 계획된 일정입니다:\n"
    for entry in schedule:
        response += f"{entry['time']}: {entry['name']} (주소: {entry['address']}, 위도: {entry['latitude']}, 경도: {entry['longitude']})\n"
    
    # 지도에 표시할 데이터프레임 생성
    map_data = pd.DataFrame(schedule)
    
    return response, map_data

# 일정 초기화 함수 (optional)
def reset_schedule():
    st.session_state['user_df']['plan'] = []