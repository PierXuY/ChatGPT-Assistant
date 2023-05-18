# 🤖 ChatGPT-Assistant
基于Streamlit搭建的ChatGPT对话助手，简单易用，不易断连，支持以下功能：
- 多聊天窗口
- 历史对话留存
- 预设聊天上下文 
- 模型参数调节
- 对话导出为Markdown文件
- ChatGPT语音交流（推荐电脑端Edge浏览器）
## 🤩 [已部署项目](https://pearxuy-gpt.streamlit.app/)
- 直接使用已部署项目，可在网页的设置选项中配置Openai Key，此时不会留存历史对话，仅在用户当前会话有效，他人不会共享。
- 自行部署项目，在Secrets中配置Openai Key后，将留存历史对话记录，此时需设置为私人应用，打造为个人GPT助理。   

**感谢由[@echoopen](https://github.com/echoopen)提供的临时key，目前可免费使用已部署项目（随时可能失效）。**
### 使用技巧：
- 双击页面可直接定位输入栏
- Ctrl + Enter 可快捷提交问题

# 部署

## Streamlit Cloud部署（推荐）
轻松免费部署，且无须科学上网即可使用，注意设置为私人应用。   
可参考由[@Hannah11111](https://github.com/Hannah11111)提供的[详细步骤](https://github.com/PierXuY/ChatGPT-Assistant/blob/main/Tutorial.md)。
1. `Fork`本项目到个人Github仓库。
2. 注册[Streamlit Cloud账号](https://share.streamlit.io/)，并连接到Github。
3. 开始部署应用，具体可参考[官方教程](https://docs.streamlit.io/streamlit-community-cloud/get-started)。   
4. 在应用的Secrets中配置Openai Key，具体格式参考下图：
<div style="display: flex;">
  <img src="https://pic3.58cdn.com.cn/nowater/webim/big/n_v28dd73c5ea1b34277976a4cf8916c4c0b.png" alt="advanced-setting.png" style="flex: 1; width: 40%;"/>
  <img src="https://pic1.58cdn.com.cn/nowater/webim/big/n_v29272f48753c742d088f124336023f480.png" alt="set-apikey.png" style="flex: 1; width: 40%;" />
</div>   
也可以在部署完成后再进行配置。

## 本地部署
本地部署需要科学上网。
1. 建立虚拟环境（建议）

2. 克隆项目（也可以手动下载到本地）
```bash
git clone https://github.com/PierXuY/ChatGPT-Assistant.git
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

4. 设置API Key   

- 在 `.streamlit/secrets.toml`文件中写入`apikey = "Your Openai Key"`

5. 启动应用
```bash
streamlit run app.py
```

# 说明
- 在[custom.py](https://github.com/PierXuY/ChatGPT-Assistant/blob/main/custom.py)文件中可自定义用户名和SVG格式头像[(来源)](https://www.dicebear.com/playground?style=identicon)。
- 在部署的项目源码中编辑[set_context.py](https://github.com/PierXuY/ChatGPT-Assistant/blob/main/set_context.py)，即可增加预设定的上下文选项，会自动同步到应用中。
- 有条件的可以考虑把[helper.py](https://github.com/PierXuY/ChatGPT-Assistant/blob/main/helper.py)中的文件读写逻辑改为云数据库操作，防止历史记录丢失。


# 致谢
- 最早是基于[shan-mx/ChatGPT_Streamlit](https://github.com/shan-mx/ChatGPT_Streamlit)项目进行的改造，感谢。
- 预设的[上下文功能](https://github.com/PierXuY/ChatGPT-Assistant/blob/main/set_context.py)参考自[binary-husky/chatgpt_academic](https://github.com/binary-husky/chatgpt_academic)项目和[f/awesome-chatgpt-prompts](https://github.com/f/awesome-chatgpt-prompts)项目，感谢。
- 语音交互功能参考了项目[talk-to-chatgpt](https://github.com/C-Nedelcu/talk-to-chatgpt)和[Voice Control for ChatGPT](https://chrome.google.com/webstore/detail/voice-control-for-chatgpt/eollffkcakegifhacjnlnegohfdlidhn)的实现，感谢。
