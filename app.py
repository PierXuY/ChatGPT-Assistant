from helper import *
import streamlit as st
import uuid
import copy
import pandas as pd
import openai
import re
from requests.models import ChunkedEncodingError

st.set_page_config(page_title='ChatGPT Assistant', layout='wide', page_icon='🤖')

# 自定义元素样式
# 第一个是减少侧边栏顶部空白，不同版本的st存在区别（此处适用1.19.0）
st.markdown("""
    <style>
    div.css-1vq4p4l.e1fqkh3o4 {
        padding-top: 2rem !important;
        }
    .avatar {
        display: flex;
        align-items: center;
        gap: 10px;
        pointer-events: none;
        margin:10px;
    }
    .avatar svg {
        width: 30px;
        height: 30px;
    }
    .avatar h2 {
        font-size: 20px;
        margin: 0px;
    } 

    .content-div {
        padding: 5px 20px;
        margin: 5px;
        text-align: left;
        border-radius: 10px;
        border: none;
        line-height: 1.6;   
        font-size:17px; 
        }
    .content-div p{
        padding: 4px;
        margin : 2px;
    } 
    #chat-window{
        padding: 10px 0px;
        text-decoration: none;
    }
    #chat-window:hover{
        color: blue;
    }
    </style>
""", unsafe_allow_html=True)
if "initial_settings" not in st.session_state:
    # 历史聊天窗口
    st.session_state['history_chats'] = get_history_chats()
    # ss参数初始化
    st.session_state['pre_chat'] = None
    st.session_state['if_chat_change'] = False
    st.session_state['error_info'] = ''
    st.session_state['user_input_content'] = ''
    st.session_state["current_chat_index"] = 0
    # 设置完成
    st.session_state["initial_settings"] = True

with st.sidebar:
    # 此处href与下文的st.header内容相对应，跳转锚点
    st.markdown("# 🤖 聊天窗口")
    current_chat = st.radio(
        label='历史聊天窗口',
        format_func=lambda x: x.split('_')[0] if '_' in x else x,
        options=st.session_state['history_chats'],
        label_visibility='collapsed',
        index=st.session_state["current_chat_index"],
        key='current_chat' + st.session_state['history_chats'][st.session_state["current_chat_index"]],
        # on_change=current_chat_callback  # 此处不适合用回调，无法识别到窗口增减的变动
    )
    if st.session_state['pre_chat'] != current_chat:
        st.session_state['pre_chat'] = current_chat
        st.session_state['if_chat_change'] = True
    st.write("---")


    def create_chat_button_callback():
        st.session_state['history_chats'] = ['New Chat_' + str(uuid.uuid4())] + st.session_state['history_chats']
        st.session_state["current_chat_index"] = 0


    def delete_chat_button_callback():
        if len(st.session_state['history_chats']) == 1:
            chat_init = 'New Chat_' + str(uuid.uuid4())
            st.session_state['history_chats'].append(chat_init)
            st.session_state['current_chat'] = chat_init
        pre_chat_index = st.session_state['history_chats'].index(current_chat)
        if pre_chat_index > 0:
            st.session_state["current_chat_index"] = st.session_state['history_chats'].index(current_chat) - 1
        else:
            st.session_state["current_chat_index"] = 0
        st.session_state['history_chats'].remove(current_chat)
        remove_data(current_chat)


    c1, c2 = st.columns(2)
    create_chat_button = c1.button('新建', use_container_width=True, key='create_chat_button',
                                   on_click=create_chat_button_callback)
    delete_chat_button = c2.button('删除', use_container_width=True, key='delete_chat_button',
                                   on_click=delete_chat_button_callback)
    
    st.write("\n")
    st.write("\n")
    st.markdown("<a href='#chatgpt-assistant' id='chat-window'>⬇️ 直达输入区</a>",unsafe_allow_html=True)

# 加载数据
if ("history" + current_chat not in st.session_state) or (st.session_state['if_chat_change']):
    for key, value in load_data(current_chat).items():
        if key == 'history':
            st.session_state[key + current_chat] = value
        else:
            for k, v in value.items():
                st.session_state[k + current_chat] = v
    st.session_state['if_chat_change'] = False

# 对话展示
show_messages(st.session_state["history" + current_chat])


# 数据写入文件
def write_data(new_chat_name=current_chat):
    st.session_state["paras"] = {
        "temperature": st.session_state["temperature" + current_chat],
        "top_p": st.session_state["top_p" + current_chat],
        "presence_penalty": st.session_state["presence_penalty" + current_chat],
        "frequency_penalty": st.session_state["frequency_penalty" + current_chat],
    }
    st.session_state["contexts"] = {
        "context_select": st.session_state["context_select" + current_chat],
        "context_input": st.session_state["context_input" + current_chat],
        "context_level": st.session_state["context_level" + current_chat],
    }
    save_data(new_chat_name, st.session_state["history" + current_chat], st.session_state["paras"],
              st.session_state["contexts"])


# 输入内容展示
area_user_svg = st.empty()
area_user_content = st.empty()
# 回复展示
area_gpt_svg = st.empty()
area_gpt_content = st.empty()
# 报错展示
area_error = st.empty()

st.write("\n")
st.header('ChatGPT Assistant')
tap_input, tap_context, tap_set = st.tabs(['💬 聊天', '🗒️ 预设', '⚙️ 设置'])

with tap_context:
    set_context_list = list(set_context_all.keys())
    context_select_index = set_context_list.index(st.session_state['context_select' + current_chat])
    st.selectbox(label='选择上下文', options=set_context_list, key='context_select' + current_chat,
                 index=context_select_index, on_change=write_data)
    st.caption(set_context_all[st.session_state['context_select' + current_chat]])
    st.text_area(label='补充或自定义上下文：', key="context_input" + current_chat,
                 value=st.session_state['context_input' + current_chat],
                 on_change=write_data)

with tap_set:
    def clear_button_callback():
        st.session_state['history' + current_chat] = copy.deepcopy(initial_content_history)
        write_data()


    st.button("清空聊天记录", use_container_width=True, on_click=clear_button_callback)

    st.caption("包含历史对话次数：")
    st.slider("Context Level", 0, 10, st.session_state['context_level' + current_chat], 1, on_change=write_data,
              key='context_level' + current_chat, help="表示每次会话中包含的历史对话次数，预设内容不计算在内。")

    st.caption("模型参数：")
    st.slider("Temperature", 0.0, 2.0, st.session_state["temperature" + current_chat], 0.1,
              help="""在0和2之间，应该使用什么样的采样温度？较高的值（如0.8）会使输出更随机，而较低的值（如0.2）则会使其更加集中和确定性。
              我们一般建议只更改这个参数或top_p参数中的一个，而不要同时更改两个。""",
              on_change=write_data, key='temperature' + current_chat)
    st.slider("Top P", 0.1, 1.0, st.session_state["top_p" + current_chat], 0.1,
              help="""一种替代采用温度进行采样的方法，称为“基于核心概率”的采样。在该方法中，模型会考虑概率最高的top_p个标记的预测结果。
              因此，当该参数为0.1时，只有包括前10%概率质量的标记将被考虑。我们一般建议只更改这个参数或采样温度参数中的一个，而不要同时更改两个。""",
              on_change=write_data, key='top_p' + current_chat)
    st.slider("Presence Penalty", -2.0, 2.0,
              st.session_state["presence_penalty" + current_chat], 0.1,
              help="""该参数的取值范围为-2.0到2.0。正值会根据新标记是否出现在当前生成的文本中对其进行惩罚，从而增加模型谈论新话题的可能性。""",
              on_change=write_data, key='presence_penalty' + current_chat)
    st.slider("Frequency Penalty", -2.0, 2.0,
              st.session_state["frequency_penalty" + current_chat], 0.1,
              help="""该参数的取值范围为-2.0到2.0。正值会根据新标记在当前生成的文本中的已有频率对其进行惩罚，从而减少模型直接重复相同语句的可能性。""",
              on_change=write_data, key='frequency_penalty' + current_chat)
    st.caption("[官网参数说明](https://platform.openai.com/docs/api-reference/completions/create)")

with tap_input:
    def get_history_input(history, level):
        df_history = pd.DataFrame(history)
        df_system = df_history.query('role=="system"')
        df_input = df_history.query('role!="system"')
        df_input = df_input[-level * 2:]
        res = pd.concat([df_system, df_input], ignore_index=True).to_dict('records')
        return res
    
    
    def remove_hashtag_space(text):
        res = re.sub(r"(#+)\s*", r"\1", text)
        return res

    
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


    def user_input_area_callback():
        # 清空输入框
        st.session_state['user_input_content'] = remove_hashtag_space(st.session_state['user_input_area'])
        st.session_state['user_input_area'] = ''

        # 修改窗口名称
        user_input_content = st.session_state['user_input_content']
        df_history = pd.DataFrame(st.session_state["history" + current_chat])
        if len(df_history.query('role!="system"')) == 0:
            remove_data(current_chat)
            current_chat_index = st.session_state['history_chats'].index(current_chat)
            new_name = extract_chars(user_input_content, 18) + '_' + str(uuid.uuid4())
            st.session_state['history_chats'][current_chat_index] = new_name
            st.session_state["current_chat_index"] = current_chat_index
            # 写入新文件
            write_data(new_name)


    st.text_area("**输入：**", key="user_input_area", on_change=user_input_area_callback)
    if st.session_state['user_input_content'].strip() != '':
        st.session_state['pre_user_input_content'] = st.session_state['user_input_content']
        st.session_state['user_input_content'] = ''
        show_each_message(st.session_state['pre_user_input_content'], 'user',
                          [area_user_svg.markdown, area_user_content.markdown])
        context_level_tem = st.session_state['context_level' + current_chat]
        history_tem = get_history_input(st.session_state["history" + current_chat], context_level_tem) + \
                      [{"role": "user", "content": st.session_state['pre_user_input_content'].replace('\n', '\n\n')}]
        history_need_input = ([{"role": "system",
                                "content": set_context_all[st.session_state['context_select' + current_chat]]}]
                              + [{"role": "system",
                                  "content": st.session_state['context_input' + current_chat]}]
                              + history_tem)
        paras_need_input = {
            "temperature": st.session_state["temperature" + current_chat],
            "top_p": st.session_state["top_p" + current_chat],
            "presence_penalty": st.session_state["presence_penalty" + current_chat],
            "frequency_penalty": st.session_state["frequency_penalty" + current_chat],
        }
        with st.spinner("🤔"):
            try:
                openai.api_key = st.secrets["apikey"]
                r = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=history_need_input, stream=True,
                                                 **paras_need_input)
            except (FileNotFoundError, KeyError):
                area_error.error("缺失 OpenAI API Key，请在复制项目后配置Secrets，详情见[项目仓库]("
                                 "https://github.com/PierXuY/ChatGPT-Assistant)。")
            except openai.error.AuthenticationError:
                area_error.error("无效的 OpenAI API Key。")
            except openai.error.APIConnectionError as e:
                area_error.error("连接超时，请重试。报错：   \n" + str(e.args[0]))
            except openai.error.InvalidRequestError as e:
                area_error.error("无效的请求，请重试。报错：   \n" + str(e.args[0]))
            except openai.error.RateLimitError as e:
                area_error.error("请求速率过快，请重试。报错：   \n" + str(e.args[0]))
            else:
                st.session_state["chat_of_r"] = current_chat
                st.session_state["r"] = r
                st.experimental_rerun()

if ("r" in st.session_state) and (current_chat == st.session_state["chat_of_r"]):
    if current_chat + 'report' not in st.session_state:
        st.session_state[current_chat + 'report'] = ""
    try:
        for e in st.session_state["r"]:
            if "content" in e["choices"][0]["delta"]:
                st.session_state[current_chat + 'report'] += e["choices"][0]["delta"]["content"]
                show_each_message(st.session_state['pre_user_input_content'], 'user',
                                  [area_user_svg.markdown, area_user_content.markdown])
                show_each_message(st.session_state[current_chat + 'report'], 'assistant',
                                  [area_gpt_svg.markdown, area_gpt_content.markdown])
    except ChunkedEncodingError:
        area_error.error("网络状况不佳，请刷新页面重试。")
    # 应对stop情形
    except Exception:
        pass
    else:
        # 保存内容
        st.session_state["history" + current_chat].append(
            {"role": "user", "content": st.session_state['pre_user_input_content']})
        st.session_state["history" + current_chat].append(
            {"role": "assistant", "content": st.session_state[current_chat + 'report']})
        write_data()

    # 用户在网页点击stop时，ss某些情形下会暂时为空
    if current_chat + 'report' in st.session_state:
        st.session_state.pop(current_chat + 'report')
    if 'r' in st.session_state:
        st.session_state.pop("r")
