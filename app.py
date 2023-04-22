from helper import *
import streamlit as st
import uuid
import copy
import pandas as pd
import openai
from requests.models import ChunkedEncodingError
from streamlit.components import v1
from custom import css_code, js_code, set_context_all

st.set_page_config(page_title='ChatGPT Assistant', layout='wide', page_icon='🤖')
# 自定义元素样式
st.markdown(css_code, unsafe_allow_html=True)

if "initial_settings" not in st.session_state:
    # 历史聊天窗口
    st.session_state["path"] = 'history_chats_file'
    st.session_state['history_chats'] = get_history_chats(st.session_state["path"])
    # ss参数初始化
    st.session_state['error_info'] = ''
    st.session_state["current_chat_index"] = 0
    st.session_state['user_input_content'] = ''
    # 设置完成
    st.session_state["initial_settings"] = True

with st.sidebar:
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
    st.write("---")

    c1, c2 = st.columns(2)

    create_chat_button = c1.button('新建', use_container_width=True, key='create_chat_button')
    if create_chat_button:
        st.session_state['history_chats'] = ['New Chat_' + str(uuid.uuid4())] + st.session_state['history_chats']
        st.session_state["current_chat_index"] = 0
        st.experimental_rerun()

    delete_chat_button = c2.button('删除', use_container_width=True, key='delete_chat_button')
    if delete_chat_button:
        if len(st.session_state['history_chats']) == 1:
            chat_init = 'New Chat_' + str(uuid.uuid4())
            st.session_state['history_chats'].append(chat_init)
        pre_chat_index = st.session_state['history_chats'].index(current_chat)
        if pre_chat_index > 0:
            st.session_state["current_chat_index"] = st.session_state['history_chats'].index(current_chat) - 1
        else:
            st.session_state["current_chat_index"] = 0
        st.session_state['history_chats'].remove(current_chat)
        remove_data(st.session_state["path"], current_chat)
        st.experimental_rerun()

    for i in range(5):
        st.write("\n")
    st.caption("""
    - 双击页面可直接定位输入栏
    - Ctrl + Enter 可快捷提交问题
    """)
    st.markdown('<a href="https://github.com/PierXuY/ChatGPT-Assistant" target="_blank" rel="ChatGPT-Assistant">'
                '<img src="https://badgen.net/badge/icon/GitHub?icon=github&amp;label=ChatGPT Assistant" alt="GitHub">'
                '</a>', unsafe_allow_html=True)

# 加载数据
if "history" + current_chat not in st.session_state:
    for key, value in load_data(st.session_state["path"], current_chat).items():
        if key == 'history':
            st.session_state[key + current_chat] = value
        else:
            for k, v in value.items():
                st.session_state[k + current_chat + "value"] = v

# 对话展示
show_messages(st.session_state["history" + current_chat])


# 数据写入文件
def write_data(new_chat_name=current_chat):
    # 防止高频创建时组件尚未渲染完成，不影响正常写入
    if "frequency_penalty" + current_chat in st.session_state:
        if "apikey" in st.secrets:
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
            save_data(st.session_state["path"], new_chat_name, st.session_state["history" + current_chat],
                      st.session_state["paras"], st.session_state["contexts"])


# 输入内容展示
area_user_svg = st.empty()
area_user_content = st.empty()
# 回复展示
area_gpt_svg = st.empty()
area_gpt_content = st.empty()
# 报错展示
area_error = st.empty()

st.write("\n")
st.write("\n")
st.header('ChatGPT Assistant')
tap_input, tap_context, tap_set = st.tabs(['💬 聊天', '🗒️ 预设', '⚙️ 设置'])

with tap_context:
    set_context_list = list(set_context_all.keys())
    context_select_index = set_context_list.index(st.session_state['context_select' + current_chat + "value"])
    st.session_state['context_select' + current_chat + "value"] = st.selectbox(
        label='选择上下文',
        options=set_context_list,
        key='context_select' + current_chat,
        index=context_select_index,
        on_change=write_data)
    st.caption(set_context_all[st.session_state['context_select' + current_chat + "value"]])

    st.session_state['context_input' + current_chat + "value"] = st.text_area(
        label='补充或自定义上下文：', key="context_input" + current_chat,
        value=st.session_state['context_input' + current_chat + "value"],
        on_change=write_data)
    st.caption(st.session_state['context_input' + current_chat + "value"])

with tap_set:
    def clear_button_callback():
        st.session_state['history' + current_chat] = copy.deepcopy(initial_content_history)
        write_data()


    st.button("清空聊天记录", use_container_width=True, on_click=clear_button_callback)

    st.markdown("OpenAI API Key (可选)")
    st.text_input("OpenAI API Key (可选)", type='password', key='apikey_input', label_visibility='collapsed')
    st.caption(
        "此Key仅在当前网页有效，且优先级高于Secrets中的配置，仅自己可用，他人无法共享。[官网获取](https://platform.openai.com/account/api-keys)")

    st.markdown("包含对话次数：")
    st.session_state['context_level' + current_chat + "value"] = st.slider(
        "Context Level", 0, 10,
        st.session_state['context_level' + current_chat + "value"], 1,
        on_change=write_data,
        key='context_level' + current_chat, help="表示每次会话中包含的历史对话次数，预设内容不计算在内。")

    st.markdown("模型参数：")
    (
        st.session_state["temperature" + current_chat + "value"],
        st.session_state["top_p" + current_chat + "value"],
        st.session_state["presence_penalty" + current_chat + "value"],
        st.session_state["frequency_penalty" + current_chat + "value"]
    ) = (
        st.slider("Temperature", 0.0, 2.0, st.session_state["temperature" + current_chat + "value"], 0.1,
                  help="""在0和2之间，应该使用什么样的采样温度？较高的值（如0.8）会使输出更随机，而较低的值（如0.2）则会使其更加集中和确定性。
              我们一般建议只更改这个参数或top_p参数中的一个，而不要同时更改两个。""",
                  on_change=write_data, key='temperature' + current_chat),
        st.slider("Top P", 0.1, 1.0, st.session_state["top_p" + current_chat + "value"], 0.1,
                  help="""一种替代采用温度进行采样的方法，称为“基于核心概率”的采样。在该方法中，模型会考虑概率最高的top_p个标记的预测结果。
              因此，当该参数为0.1时，只有包括前10%概率质量的标记将被考虑。我们一般建议只更改这个参数或采样温度参数中的一个，而不要同时更改两个。""",
                  on_change=write_data, key='top_p' + current_chat),
        st.slider("Presence Penalty", -2.0, 2.0,
                  st.session_state["presence_penalty" + current_chat + "value"], 0.1,
                  help="""该参数的取值范围为-2.0到2.0。正值会根据新标记是否出现在当前生成的文本中对其进行惩罚，从而增加模型谈论新话题的可能性。""",
                  on_change=write_data, key='presence_penalty' + current_chat),
        st.slider("Frequency Penalty", -2.0, 2.0,
                  st.session_state["frequency_penalty" + current_chat + "value"], 0.1,
                  help="""该参数的取值范围为-2.0到2.0。正值会根据新标记在当前生成的文本中的已有频率对其进行惩罚，从而减少模型直接重复相同语句的可能性。""",
                  on_change=write_data, key='frequency_penalty' + current_chat)
    )
    st.caption("[官网参数说明](https://platform.openai.com/docs/api-reference/completions/create)")

with tap_input:
    def input_callback():
        if st.session_state['user_input_area'] != "":
            # 修改窗口名称
            user_input_content = st.session_state['user_input_area']
            df_history = pd.DataFrame(st.session_state["history" + current_chat])
            if len(df_history.query('role!="system"')) == 0:
                remove_data(st.session_state["path"], current_chat)
                current_chat_index = st.session_state['history_chats'].index(current_chat)
                new_name = extract_chars(user_input_content, 18) + '_' + str(uuid.uuid4())
                st.session_state['history_chats'][current_chat_index] = new_name
                st.session_state["current_chat_index"] = current_chat_index
                # 写入新文件
                write_data(new_name)


    with st.form("input_form", clear_on_submit=True):
        user_input = st.text_area("**输入：**", key="user_input_area")
        submitted = st.form_submit_button("确认提交", use_container_width=True, on_click=input_callback)
    if submitted:
        st.session_state['user_input_content'] = user_input

    if st.session_state['user_input_content'] != '':
        if 'r' in st.session_state:
            st.session_state.pop("r")
            st.session_state[current_chat + 'report'] = ""
        st.session_state['pre_user_input_content'] = (remove_hashtag_right__space(st.session_state['user_input_content']
                                                                                  .replace('\n', '\n\n')))
        st.session_state['user_input_content'] = ''
        show_each_message(st.session_state['pre_user_input_content'], 'user',
                          [area_user_svg.markdown, area_user_content.markdown])
        context_level_tem = st.session_state['context_level' + current_chat]
        history_tem = get_history_input(st.session_state["history" + current_chat], context_level_tem) + \
                      [{"role": "user", "content": st.session_state['pre_user_input_content']}]
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
                if apikey := st.session_state['apikey_input']:
                    openai.api_key = apikey
                else:
                    openai.api_key = st.secrets["apikey"]
                r = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=history_need_input, stream=True,
                                                 **paras_need_input)
            except (FileNotFoundError, KeyError):
                area_error.error("缺失 OpenAI API Key，请在复制项目后配置Secrets，或者在设置中进行临时配置。"
                                 "详情见[项目仓库](https://github.com/PierXuY/ChatGPT-Assistant)。")
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

# 添加事件监听
v1.html(js_code, height=0)
