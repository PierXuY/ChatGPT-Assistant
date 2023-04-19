import json
import os
import re
import builtins
import shutil
import uuid
from functools import wraps
import streamlit as st
import pandas as pd
from custom import *


# 聊天记录处理
def clear_folder(path):
    if not os.path.exists(path):
        return
    for file_name in os.listdir(path):
        file_path = os.path.join(path, file_name)
        try:
            shutil.rmtree(file_path)
        except Exception:
            pass


def set_chats_path():
    save_path = 'chat_history'
    if 'apikey' not in st.secrets:
        clear_folder('tem_files')
        save_path = 'tem_files/tem_chat' + str(uuid.uuid4())
    return save_path


# 重新open函数，路径不存在时自动创建
def create_path(func):
    @wraps(func)
    def wrapper(path, *args, **kwargs):
        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))
        return func(path, *args, **kwargs)

    return wrapper


open = create_path(builtins.open)


def get_history_chats(path):
    try:
        os.makedirs(path)
    except FileExistsError:
        pass
    files = [f for f in os.listdir(f'./{path}') if f.endswith('.json')]
    files_with_time = [(f, os.stat(f'./{path}/' + f).st_ctime) for f in files]
    sorted_files = sorted(files_with_time, key=lambda x: x[1], reverse=True)
    chat_names = [os.path.splitext(f[0])[0] for f in sorted_files]
    if len(chat_names) == 0:
        chat_names.append('New Chat_' + str(uuid.uuid4()))
    return chat_names


def save_data(path: str, file_name: str, history: list, paras: dict, contexts: dict, **kwargs):
    with open(f"./{path}/{file_name}.json", 'w', encoding='utf-8') as f:
        json.dump({"history": history, "paras": paras, "contexts": contexts, **kwargs}, f)


def remove_data(path: str, file_name: str):
    try:
        os.remove(f"./{path}/{file_name}.json")
    except FileNotFoundError:
        pass


def load_data(path: str, file_name: str) -> dict:
    try:
        with open(f"./{path}/{file_name}.json", 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data
    except FileNotFoundError:
        with open(f"./{path}/{file_name}.json", 'w', encoding='utf-8') as f:
            f.write(json.dumps(initial_content_all))
        return initial_content_all


def show_each_message(message, role, area=None):
    if area is None:
        area = [st.markdown] * 2
    if role == 'user':
        icon = user_svg
        name = user_name
        background_color = user_background_color
    else:
        icon = gpt_svg
        name = gpt_name
        background_color = gpt_background_color
    area[0](f"\n<div class='avatar'>{icon}<h2>{name}：</h2></div>", unsafe_allow_html=True)
    area[1](f"""<div class='content-div' style='background-color: {background_color};'>\n\n{message}""",
            unsafe_allow_html=True)


def show_messages(messages: list):
    for each in messages:
        if (each["role"] == "user") or (each["role"] == "assistant"):
            show_each_message(each["content"], each["role"])
        if each["role"] == "assistant":
            st.write("---")


# 根据context_level提取history
def get_history_input(history, level):
    df_history = pd.DataFrame(history)
    df_system = df_history.query('role=="system"')
    df_input = df_history.query('role!="system"')
    df_input = df_input[-level * 2:]
    res = pd.concat([df_system, df_input], ignore_index=True).to_dict('records')
    return res


# 去除#号右边的空格
def remove_hashtag_right__space(text):
    res = re.sub(r"(#+)\s*", r"\1", text)
    return res


# 提取文本
def extract_chars(text, num):
    char_num = 0
    chars = ''
    for char in text:
        # 汉字算两个字符
        if '\u4e00' <= char <= '\u9fff':
            char_num += 2
        else:
            char_num += 1
        chars += char
        if char_num >= num:
            break
    return chars
