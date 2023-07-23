# --- import modules start ---
# import streamlit 
import streamlit as st
# import data analysis modules
import pandas as pd
import matplotlib.cm as cm
import matplotlib.colors as colors
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# import mongodb module
import pymongo

# import map visualization module
import folium

# GIS modules
import networkx as nx
import osmnx as ox
import geopandas as gpd

# import another modules
import json
import requests
import math
import re

from src.database import *

# --- import modules end ---

# func: initalize Session State
def initializeApp():
  st.session_state.sessionState = 1
  st.session_state.G = nx.Graph()
  st.session_state.df_code = pd.read_csv('data/감염여부_코드.csv')
  st.session_state.df_hospital = pd.read_csv('data/hospital.csv')
  st.session_state.old_address = None

def readDB():
  if 'db' not in st.session_state:
    db = connectDB(st.secrets.DBPASS)
    st.session_state.db = db
  else:
    db = st.session_state.db

  return db

# func: read Data from Repository
def readData():
  db = readDB()
    
  G = nx.Graph()
  for item in db.code_A.find():
    G = makeGraph(item, G)
  for item in db.code_B.find():
    G = makeGraph(item, G)

  st.session_state.G = G # 세션 저장

# func: make graph with NetworkX
def makeGraph(item, G):
  # 진료과 + 응급도 등급으로 도출되도록 변경 필요
  # 그래프에서 관련된 여러 과가 나오도록 변경 필요
  G.add_edge(item['firstCode'] + item['secondCode'] + item['thirdCode'] + item['fourthCode'], item['description'].split(', ')[2] + ' ' + str(item['level']))

def getDepartment():
  mergeCode = st.session_state.mergeCode
  if 'G' in st.session_state:
    G = st.session_state.G
    possible_departments = []

    for code in mergeCode:
      for node in G.nodes:
        if code in node:
          data = list(dict(G_A[node]).keys())
          for d in data:
            d.split(', ')
            for i in d:
              possible_departments.append(d)

    departments = []

    for p in possible_departments:
      data = p.split(', ')
      for d in data:
        if d in departments:
          break
        departments.append(d)
    label = "도출된 진료과는 "
    for i in departments:
      label += i
      label += ", "
    label = label[:-2] + "입니다."
    st.write(label)
    st.session_state.departments = departments
    
def main():
  # Streamlit App Setting
  db = readDB()
  
  st.title('C-ITS')
  st.subheader('Made By SobanGchA (소 방 차)')

  # 나이 선택
  age = st.selectbox(
      '환자의 나이를 골라주세요.',
      ('15세 이상의 성인', '15세 미만의 아동'))
  if age == '15세 이상의 성인':
    ageCode = 'A'
  else:
    ageCode = 'B'
    
  # step4
  step4 = st.text_input('증상의 키워드를 입력하세요.(여러개일 경우, 띄어쓰기로 구분)')
  step4 = step4.split(" ")
  keyword = ""
  keyword = "|".join(step4)

  if ageCode == 'A':
    response = db.code_A.find({"description": {"$regex": keyword[1:-1], "$options": "i"}})
    st.session_state.response = response

  step3_list2 = []
  step3_list = []
  for key in response:
    step3_list.append(key)
    step3_list2.append(key['description'].split(', ')[2])

  # step3
  key = tuple(set(step3_list2))
  step3 = st.multiselect(
      '환자의 응급상황 정보를 선택해주세요.',
      (key))
  keyword2 = ""
  keyword2 = "|".join(step3)

  #step2
  step2_list = []
  for k in step3_list:
    if k['description'].contains(keyword2):
      step2_list.append(k)
  st.write(step2_list)
  
  '''
  if age == '15세 이상의 성인':
    
    step3_list = df_A[df_A['4단계'].str.contains(keyword[:-1])]
    step3_list_2 = step3_list["3단계"].drop_duplicates()
    step3 = st.multiselect(
      '환자의 응급상황 정보를 선택해주세요.',
      (tuple(step3_list_2.values.tolist())))
    keyword2 = ""
    for i in step3:
      keyword2 += str(i)
      keyword2 += '|'
    step2 = step3_list[step3_list['3단계'].str.contains(keyword2[:-1])]
    mergeCode = "A" + step2["2단계 코드"] + step2["3단계 코드"] + step2["4단계 코드"]
  elif age == '15세 미만의 아동':
    step4 = st.text_input('증상의 키워드를 입력하세요.(여러개일 경우, 띄워쓰기로 구분)')
    step4 = step4.split(" ")
    keyword = ""
    for i in step4:
      keyword += str(i)
      keyword += '|'
    step3_list = df_B[df_B['4단계'].str.contains(keyword[:-1])]
    step3_list_2 = step3_list["3단계"].drop_duplicates()
    step3 = st.multiselect(
      '환자의 응급상황 정보를 선택해주세요.',
      (tuple(step3_list_2.values.tolist())))
    keyword2 = ""
    for i in step3:
      keyword2 += str(i)
      keyword2 += '|'
    step2 = step3_list[step3_list['3단계'].str.contains(keyword2[:-1])]
    mergeCode = "B" + step2["2단계 코드"] + step2["3단계 코드"] + step2["4단계 코드"]
  st.session_state.mergeCode = mergeCode
  getDepartment()
  '''

if __name__ == "__main__":
  st.set_page_config(page_title="C-ITS", layout="wide")
  if 'sessionState' not in st.session_state: # 세션 코드가 없는 경우
    initializeApp() # 앱 초기화
  if 'G' not in st.session_state or 'df_code' not in st.session_state or 'df_hospital' not in st.session_state: # 그래프, 감염여부 코드, 병원 정보 중 하나라도 없는 경우
    readData()
  #df_A = st.session_state.df_A
  #df_B = st.session_state.df_B
  df_code = st.session_state.df_code
  df_hospital = st.session_state.df_hospital
  #if 'G' not in st.session_state:
    #makeGraph()
  main()
