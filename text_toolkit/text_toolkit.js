//// init.js
function sendMessageToStreamlitClient(type, data) {
    const outData = Object.assign({
        isStreamlitMessage: true,
        type: type,
    }, data);
    window.parent.postMessage(outData, "*");
}

function init() {
    sendMessageToStreamlitClient("streamlit:componentReady", {apiVersion: 1});
}

function setFrameHeight(height) {
    sendMessageToStreamlitClient("streamlit:setFrameHeight", {height: height});
}

// The `data` argument can be any JSON-serializable value.
function sendDataToPython(data) {
    sendMessageToStreamlitClient("streamlit:setComponentValue", data);
}

init()


//// text_toolkit.js
const playBtn = document.getElementById("play-btn");
const toggleBtn = document.getElementById("toggle-btn");
const stopBtn = document.getElementById("stop-btn");
const speedSelect = document.getElementById('speed');
const copyButton = document.getElementById('copy-btn');
const deleteButton = document.getElementById('delete-btn');
const synth = window.parent.speechSynthesis;
let utterance = new SpeechSynthesisUtterance()
let TIMEOUT_KEEP_SYNTHESIS_WORKING = null;
let speechStatus
let IGNORE_CODE_BLOCKS = true;
let iframes = window.parent.document.querySelectorAll('iframe');
window.parent.textSound = []
iframes.forEach(iframe => {
    let btn = iframe.contentDocument.querySelector('.sound')
    let recordBtn = iframe.contentDocument.querySelector('button#record-btn')
    if (btn) {
        window.parent.textSound.push(btn)
    }
    if (recordBtn) {
        window.parent.recordBtn = recordBtn;
    }
})


// 接收来自Python的参数
function onDataFromPython(event) {
    playBtn.setAttribute("data-idr", event.data.args.data_idr);
    if (event.data.args.data_idr.includes('assistant')) {
        deleteButton.style.display = 'inline-block';
    }
}

window.addEventListener("message", onDataFromPython, false);

function btnDisplay(value) {
    if (value === "inline-block") {
        playBtn.style.display = "inline-block";
        toggleBtn.style.display = "none";
        stopBtn.style.display = "none";

    } else {
        playBtn.style.display = "none";
        toggleBtn.style.display = "inline-block";
        stopBtn.style.display = "inline-block";
    }
}

function btnClass(value) {
    if (value === 'fa-pause') {
        toggleBtn.querySelector('.fas').classList.add('fa-pause');
        toggleBtn.querySelector('.fas').classList.remove('fa-play');
    } else {
        toggleBtn.querySelector('.fas').classList.add('fa-play');
        toggleBtn.querySelector('.fas').classList.remove('fa-pause');

    }
}

function skipCode(divElement, excludeSelector) {
    let excludeElements = Array.from(divElement.querySelectorAll(excludeSelector));

    return Array.from(divElement.childNodes)
        .filter(node => node.nodeType === Node.TEXT_NODE && node.textContent.trim() !== '' || node.nodeType === Node.ELEMENT_NODE && !excludeElements.includes(node))
        .map(node => node.textContent)
        .join('')
}

function KeepSpeechSynthesisActive() {
    synth.pause();
    synth.resume();
    TIMEOUT_KEEP_SYNTHESIS_WORKING = setTimeout(KeepSpeechSynthesisActive, 3500);
}

playBtn.addEventListener("click", () => {
    // 关闭录音
    if (window.parent.recordBtn) {
        if (window.parent.recordBtn.classList.contains("recording")) {
            window.parent.recordBtn.click()
        }
    }
    // 关闭现有播放
    synth.cancel();
    window.parent.current_idr = playBtn.getAttribute("data-idr")
    // 全部重置为喇叭图标
    window.parent.textSound.forEach(value => {
        {
            value.querySelector('#play-btn').style.display = "inline-block";
            value.querySelector('#toggle-btn').style.display = "none";
            value.querySelector('#stop-btn').style.display = "none";
        }
    })

    let textElement = window.parent.document.querySelector(`div[data-idr="${window.parent.current_idr}"]`)
    let sayOutText = "";
    if (IGNORE_CODE_BLOCKS) {
        sayOutText = skipCode(textElement, 'div.stCodeBlock')
    } else {
        sayOutText = textElement.textContent
    }

    if (sayOutText !== '') {
        utterance.text = sayOutText;
        utterance.rate = speedSelect.value;
        if (window.parent.selectedVoiceName) {
            utterance.voice = window.parent.voices.find(function (v) {
                return v.name === window.parent.selectedVoiceName;
            });
            utterance.lang = utterance.voice.lang
        }
        utterance.onstart = () => {
            clearTimeout(TIMEOUT_KEEP_SYNTHESIS_WORKING);
            TIMEOUT_KEEP_SYNTHESIS_WORKING = setTimeout(KeepSpeechSynthesisActive, 3500);
        }
        btnClass('fa-pause')
        btnDisplay('none');
        synth.speak(utterance)
        speechStatus = 'speaking';


    }
});

function toggleSpeech() {
    if (speechStatus === 'speaking') {
        synth.pause();
        btnClass('fa-play')
        speechStatus = "paused"

    } else {
        synth.resume();
        btnClass('fa-pause')
        speechStatus = "speaking";
    }
}

toggleBtn.addEventListener('click', toggleSpeech);

stopBtn.addEventListener("click", () => {
    synth.cancel();
    speechStatus = "stop"
    btnDisplay('inline-block');
});

utterance.onend = function () {
    btnDisplay('inline-block');
    speechStatus = "stop"
    clearTimeout(TIMEOUT_KEEP_SYNTHESIS_WORKING);
};

speedSelect.addEventListener('change', () => {
    if (window.parent.current_idr === playBtn.getAttribute("data-idr")) {
        synth.cancel();
        utterance.rate = parseFloat(speedSelect.value);
        if (speechStatus === "speaking") {
            synth.speak(utterance);
        }
    }
});


//// copy.js
copyButton.addEventListener('click', () => {
    let data_idr = playBtn.getAttribute("data-idr")
    let text = window.parent.document.querySelector(`div[data-idr="${data_idr}"]`).innerText
    navigator.clipboard.writeText(text)
        // .then(() => {
        //     // copyTips.classList.add('copy-success');
        //     // copyTips.innerText = '复制成功';
        //     setTimeout(() => {
        //         // copyTips.classList.remove('copy-success');
        //         // copyTips.innerText = '点击复制';
        //     }, 1500);
        // })
        .catch((err) => {
            console.error('无法复制到剪贴板：', err);
        });
});


//// delete.js
if (!("deleteCount" in window.parent)) {
    window.parent.deleteCount = 0
}

deleteButton.addEventListener('click', () => {
    sendDataToPython({
        "value":
            {
                'deleteCount': window.parent.deleteCount
            }
    })
    window.parent.deleteCount += 1
})

// 设置组件高度
window.addEventListener("DOMContentLoaded", function () {
    setFrameHeight(21)
});