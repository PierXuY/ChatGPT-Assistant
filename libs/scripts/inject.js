function checkElements() {
    const textinput = window.parent.document.querySelector("textarea[aria-label='**输入：**']");   //label需要相对应
    const textarea = window.parent.document.querySelector("div[data-baseweb = 'textarea']");
    const button = window.parent.document.querySelector("button[kind='secondaryFormSubmit']");
    const tabs = window.parent.document.querySelectorAll('button[data-baseweb="tab"] p');
    const tabs_div = window.parent.document.querySelector('div[role="tablist"]');
    const tab_panels = window.parent.document.querySelectorAll('div[data-baseweb="tab-panel"]');

    if (textinput && textarea && button && tabs && tabs_div && tab_panels) {
        // 双击点位输入框，同时抑制双击时选中文本事件
        window.parent.document.addEventListener('dblclick', function (event) {
            let activeTab = tabs_div.querySelector('button[aria-selected="true"]');
            if (activeTab.querySelector('p').textContent === '💬 聊天') {
                textinput.focus();
            } else {
                tabs[0].click();
                const waitMs = 50;

                function waitForFocus() {
                    if (window.parent.document.activeElement === textinput) {
                    } else {
                        setTimeout(function () {
                            textinput.focus();
                            waitForFocus();
                        }, waitMs);
                    }
                }

                waitForFocus();
            }
        });

        // 按下/键时定位输入框
        window.parent.document.addEventListener('keydown', function (event) {
            if (event.key === '/') {
                // 没有聚焦在'INPUT', 'TEXTAREA'或者不存在activeElement
                if (!window.parent.document.activeElement || !['INPUT', 'TEXTAREA'].includes(window.parent.document.activeElement.tagName.toUpperCase())) {
                    let activeTab = tabs_div.querySelector('button[aria-selected="true"]');
                    if (activeTab.querySelector('p').textContent === '💬 聊天') {
                        event.preventDefault(); 
                        textinput.focus();
                    } else {
                        tabs[0].click();
                        const waitMs = 50;

                        function waitForFocus() {
                            if (window.parent.document.activeElement === textinput) {
                            } else {
                                setTimeout(function () {
                                    textinput.focus();
                                    waitForFocus();
                                }, waitMs);
                            }
                        }

                        waitForFocus();
                    }
                }
            }
        });

        window.parent.document.addEventListener('mousedown', (event) => {
            if (event.detail === 2) {
                event.preventDefault();
            }
        });
        // textinput.addEventListener('focusin', function (event) {
        //     event.stopPropagation();
        //     textarea.style.borderColor = 'rgb(255,75,75)';
        // });
        // textinput.addEventListener('focusout', function (event) {
        //     event.stopPropagation();
        //     textarea.style.borderColor = 'white';
        // });

        // Ctrl + Enter快捷方式
        window.parent.document.addEventListener("keydown", event => {
            if (event.ctrlKey && event.key === "Enter") {
                if (textinput.textContent !== '') {
                    button.click();
                }
                textinput.blur();
            }
        });

        // 设置 Tab 键
        textinput.addEventListener('keydown', function (event) {
            if (event.keyCode === 9) {
                // 阻止默认行为
                event.preventDefault();
                if (!window.parent.getSelection().toString()) {
                    // 获取当前光标位置
                    const start = this.selectionStart;
                    const end = this.selectionEnd;
                    // 在光标位置插入制表符
                    this.value = this.value.substring(0, start) + '\t' + this.value.substring(end);
                    // 将光标移动到插入的制表符之后
                    this.selectionStart = this.selectionEnd = start + 1;
                }
            }
        });

        // // 处理tabs 在第一次切换时的渲染问题
        // tabs.forEach(function (tab, index) {
        //     const tab_panel_child = tab_panels[index].querySelectorAll("*");

        //     function set_visibility(state) {
        //         tab_panels[index].style.visibility = state;
        //         tab_panel_child.forEach(function (child) {
        //             child.style.visibility = state;
        //         });
        //     }

        //     tab.addEventListener("click", function (event) {
        //         set_visibility('hidden')

        //         let element = tab_panels[index].querySelector('div[data-testid="stVerticalBlock"]');
        //         let main_block = window.parent.document.querySelector('section.main div[data-testid="stVerticalBlock"]');
        //         const waitMs = 50;

        //         function waitForLayout() {
        //             if (element.offsetWidth === main_block.offsetWidth) {
        //                 set_visibility("visible");
        //             } else {
        //                 setTimeout(waitForLayout, waitMs);
        //             }
        //         }

        //         waitForLayout();
        //     });
        // });
    } else {
        setTimeout(checkElements, 100);
    }
}

checkElements()
