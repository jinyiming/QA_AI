import { sendQuestion, uploadFile, uploadFile_temp, sessionState } from './utils/api.js';
import { messageActions } from './utils/messageActions.js';

class App {
    constructor() {
        this.checkLogin();
        // 使用 DOMContentLoaded 事件来确保 DOM 完全加载
        document.addEventListener('DOMContentLoaded', () => {
            this.init();
        });
    }

    checkLogin() {
        const authToken = sessionStorage.getItem('authToken');
        if (!authToken) {
            // 如果没有登录，重定向到登录页面
            window.location.href = 'login.html';
        }
    }

    init() {
        this.setupEventListeners();
        this.updateGreeting();
        this.currentAIResponseController = null;
        this.currentAIMessageElement = null;
        this.currentResponseController = null;
        
        // 每次页面加载时重置 kb_id
        this.kb_id = null;
        this.fileName = null;
        sessionState.removeItem('kb_id');
        sessionState.removeItem('fileName');
    }   

    setupEventListeners() {
        // 在这里，我们应该检查每个元素是否存然后再添加事件器
        const inputField = document.querySelector('.input-field');
        const fileInput = document.getElementById('fileInput');
        const quickReadButtons = document.querySelectorAll('#quickReadButton, .action-button.read-button');
        const actionButtons = document.querySelectorAll('.action-button, .feature-button');
        const recommendedQuestionsButton = document.querySelector('.recommended-questions-button');
        const giveInspirationButton = document.querySelector('.give-inspiration-button');
        const logoutButton = document.getElementById('logoutButton');
        const commandCenterButton = document.getElementById('commandCenterButton');
        const closeModalButton = document.getElementById('closeModal');
        const toolCenterModal = document.getElementById('toolCenterModal');
        const voiceButton = document.getElementById('voiceButton');
        const addButton = document.getElementById('addButton');
        const writingAssistantButton = document.getElementById('writingAssistantButton');
        const topicInputModal = document.getElementById('topicInputModal');
        const closeTopicModalButton = document.getElementById('closeTopicModal');
        const submitTopicButton = document.getElementById('submitTopicButton');
        const topicInput = document.getElementById('topicInput');

        if (inputField) inputField.addEventListener('keypress', this.handleInput.bind(this));
        if (fileInput) fileInput.addEventListener('change', this.handleFileUpload.bind(this));
        quickReadButtons.forEach(button => {
            button.addEventListener('click', this.handleQuickRead.bind(this));
        });
        if (recommendedQuestionsButton) recommendedQuestionsButton.addEventListener('click', this.handleRecommendedQuestions.bind(this));
        if (giveInspirationButton) giveInspirationButton.addEventListener('click', this.handleGiveInspiration.bind(this));

        actionButtons.forEach(button => {
            button.addEventListener('click', this.handleActionButtonClick.bind(this));
        });

        if (logoutButton) {
            logoutButton.addEventListener('click', this.logout.bind(this));
        }

        if (commandCenterButton && toolCenterModal) {
            commandCenterButton.addEventListener('click', () => {
                console.log('指令中心按钮被点击');
                toolCenterModal.style.display = 'block';
                console.log('模态层显示状态:', toolCenterModal.style.display);
            });
        }

        if (closeModalButton && toolCenterModal) {
            closeModalButton.addEventListener('click', () => {
                toolCenterModal.style.display = 'none';
            });
        }

        window.addEventListener('click', (event) => {
            if (event.target === toolCenterModal) {
                toolCenterModal.style.display = 'none';
            }
        });

        const toolButtons = document.querySelectorAll('.modal .feature-button');
        toolButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                const toolName = e.currentTarget.querySelector('.feature-title').textContent;
                this.handleToolButtonClick(toolName);
            });
        });

        if (voiceButton) {
            voiceButton.addEventListener('click', () => {
                console.log('语音按钮被点击');
                const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
                recognition.lang = 'zh-CN'; // 设置语言为中文
                recognition.interimResults = false; // 不返回中间结果
                recognition.maxAlternatives = 1; // 只返回一个结果

                recognition.start();

                recognition.onresult = (event) => {
                    const transcript = event.results[0][0].transcript;
                    console.log('语音识别:', transcript);
                    const inputField = document.querySelector('.input-field');
                    inputField.value = transcript; // 将识别结果填入输入框
                };

                recognition.onerror = (event) => {
                    console.error('语音识别错误:', event.error);
                };
            });
        }

        if (addButton) {
            addButton.addEventListener('click', () => {
                console.log('加号按钮被点击');
                // 在这里添加加号按钮的逻辑，例如打开文件选择器
            });
        }

        if (writingAssistantButton) {
            writingAssistantButton.addEventListener('click', () => {
                topicInputModal.style.display = 'block'; // 显示主题输入模态层
            });
        }

        if (closeTopicModalButton) {
            closeTopicModalButton.addEventListener('click', () => {
                topicInputModal.style.display = 'none'; // 隐藏模态层
            });
        }


        if (topicInput) {
            topicInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    const topic = topicInput.value.trim();
                    if (topic) {
                        const inputField = document.querySelector('.input-field');
                        inputField.value = `帮我写一篇关于【${topic}】的工作报告。`; // 设置输入框内容
                        inputField.focus(); // 聚焦输入框
                        topicInputModal.style.display = 'none'; // 隐藏模态层
                    }
                }
            });
        }

        // 点击模态层外部关闭模态层
        window.addEventListener('click', (event) => {
            if (event.target === topicInputModal) {
                topicInputModal.style.display = 'none';
            }
        });

        // this.stopGenerationButton.addEventListener('click', this.handleStopGeneration.bind(this));

        document.addEventListener('click', (event) => {
            const target = event.target.closest('.action-button');
            if (!target) return;

            const messageElement = target.closest('.chat-message');
            if (!messageElement) return;

            const messageContent = messageElement.querySelector('.message-display').textContent;

            if (target.classList.contains('copy-button')) {
                this.copyToClipboard(messageContent);
            } else if (target.classList.contains('voice-button')) {
                this.voiceReadout(messageContent);
            } else if (target.classList.contains('best-answer-button')) {
                this.markAsBestAnswer(messageElement);
            } else if (target.classList.contains('error-button')) {
                this.reportError(messageElement);
            } else if (target.classList.contains('regenerate-button')) {
                const question = this.getLastUserQuestion(); // 你需要实现这个方法
                this.regenerateResponse(question);
            }
        });
    }

    updateGreeting() {
        const greetingElement = document.querySelector('.greeting h2');
        const currentHour = new Date().getHours();
        const username = sessionStorage.getItem('username') || '';
        let greeting;

        if (currentHour >= 5 && currentHour < 12) {
            greeting = '早上好';
        } else if (currentHour >= 12 && currentHour < 18) {
            greeting = '下午好';
        } else if (currentHour >= 18 && currentHour < 22) {
            greeting = '晚上好';
        } else {
            greeting = '夜深了';
        }

        greetingElement.textContent = `${username}，${greeting}👋`;
    }

    handleInput(e) {
        if (e.key === 'Enter') {
            const question = e.target.value.trim();
            this.appendMessage('user', question);
            e.target.value = ''; // 清空输入框
            this.getAIResponse(question);
        }
    }
    
    async handleFileUpload(event) {
        const file = event.target.files[0];
        if (file) {
            const maxSizeInMB = 16;
            const maxSizeInBytes = maxSizeInMB * 1024 * 1024;

            if (file.size > maxSizeInBytes) {
                alert(`文件大小不能超过 ${maxSizeInMB} MB`);
                return;
            }

            // 显示上传进度遮罩
            this.showUploadOverlay();

            try {
                const result = await this.uploadFile(file);
                console.log('File upload result:', result);
                this.kb_id = result.id;  // 设置 kb_id
                this.fileName = file.name;
                sessionState.setItem('kb_id', this.kb_id);
                sessionState.setItem('fileName', this.fileName);

                // 更新文件预览
                this.updateFilePreview(file);

                // 显示上传成功消息
                this.showUploadSuccess();
            } catch (error) {
                console.error('File upload error:', error);
                alert('文件上传失败，请重试。');
            } finally {
                // 隐藏上传进度遮罩
                this.hideUploadOverlay();
            }
        }
    }

    showUploadOverlay() {
        const overlay = document.createElement('div');
        overlay.id = 'uploadOverlay';
        overlay.innerHTML = `
            <div class="upload-content">
                <div class="spinner">
                    <img src="icons/running-person.svg" alt="正在上传" class="running-icon" />
                </div>
                <p>AI正在加足马力前进哦，请稍候...</p>
            </div>
        `;
        document.body.appendChild(overlay);
        document.body.style.overflow = 'hidden'; // 锁定页面滚动
    }

    hideUploadOverlay() {
        const overlay = document.getElementById('uploadOverlay');
        if (overlay) {
            overlay.remove();
            document.body.style.overflow = ''; // 恢复页面滚动
        }
    }

    showUploadSuccess() {
        const successMessage = document.createElement('div');
        successMessage.className = 'upload-success-message';
        successMessage.textContent = '文件上传成功！';
        document.body.appendChild(successMessage);

        // 添加显示类
        setTimeout(() => {
            successMessage.classList.add('show');
        }, 10); // 确保在添加类之前有一个小的延迟

        // 3秒后自动移除成功消息
        setTimeout(() => {
            successMessage.classList.add('hide'); // 添加隐藏类
            setTimeout(() => {
                successMessage.remove(); // 移除元素
            }, 500); // 等待过渡效果完成后再移除
        }, 2000);
    }

    updateFilePreview(file) {
        const filePreviewContainer = document.getElementById('filePreviewContainer');
        const fileName = document.getElementById('fileName');
        const fileSize = document.getElementById('fileSize');
        const fileIcon = filePreviewContainer.querySelector('.file-icon');

        // 根据文件类型设置图标
        const fileType = file.name.split('.').pop().toLowerCase();
        switch (fileType) {
            case 'pdf':
                fileIcon.innerHTML = '<i class="fas fa-file-pdf"></i>'; // PDF 图标
                break;
            case 'doc':
            case 'docx':
                fileIcon.innerHTML = '<i class="fas fa-file-word"></i>'; // Word 图标
                break;
            case 'ppt':
            case 'pptx':
                fileIcon.innerHTML = '<i class="fas fa-file-powerpoint"></i>'; // PowerPoint 图标
                break;
            case 'xls':
            case 'xlsx':
                fileIcon.innerHTML = '<i class="fas fa-file-excel"></i>'; // Excel 图标
                break;
            case 'txt':
                fileIcon.innerHTML = '<i class="fas fa-file-alt"></i>'; // 文本文件图标
                break;
            case 'wps':
                fileIcon.innerHTML = '<i class="fas fa-file-alt"></i>'; // WPS 图标
                break;
            case 'png':
            case 'jpg':
            case 'jpeg':
            case 'gif':
                fileIcon.innerHTML = '<i class="fas fa-file-image"></i>'; // 图片图标
                break;
            default:
                fileIcon.innerHTML = '<i class="fas fa-file"></i>'; // 默认文件图标
                break;
        }

        filePreviewContainer.style.display = 'flex';
        fileName.textContent = file.name;
        fileSize.textContent = `${(file.size / (1024 * 1024)).toFixed(2)} MB`;
    }

    async uploadFile(file) {
        // 这里使用之前的 uploadFile_temp 函数
        return await uploadFile_temp(file);
    }

    async handleQuickRead() {
        if (this.kb_id) {
            const userMessage = `帮我总结下这篇文档《${this.fileName}》`;
            this.appendMessage('user', userMessage);
            await this.getAIResponse(userMessage);
        } else {
            alert('请先上传文件');
        }
    }

    async handleRecommendedQuestions() {
        if (this.kb_id) {
            const userMessage = "基于本文内容，推荐几个问题";
            this.appendMessage('user', userMessage);
            await this.getAIResponse(userMessage);
        } else {
            alert('请先上传文件');
        }
    }

    handleActionButtonClick(event) {
        const buttons = document.querySelectorAll('.action-button, .feature-button');
        buttons.forEach(btn => btn.classList.remove('active'));
        event.target.classList.add('active');

        console.log(`${event.target.textContent} 按钮被点击`);
    }

    appendMessage(sender, message) {
        const chatContainer = document.querySelector('.chat-container');
        const messageElement = document.createElement('div');
        messageElement.classList.add('chat-message', sender);

        if (sender === 'user') {
            messageElement.innerHTML = `<div class="message-content">${message}</div>`;
        } else if (sender === 'ai') {
            messageElement.innerHTML = `
                <div class="ai-message-container">
                    <div class="message-icon">
                        <img src="icons/ai-avatar.svg" alt="AI" class="ai-icon">
                    </div>
                    <div class="message-content-wrapper">
                        <div class="message-display">
                            <span class="generated-text"></span>
                            <span class="writing-icon" style="display: none;">
                                <i class="fas fa-pen" title="正在书写"></i>
                            </span>
                        </div>
                        <div class="message-actions" style="display: none;">
                            <button class="stop-generation-button">
                                <i class="fas fa-stop-circle" style="color: red;"></i> 停止生成
                            </button>
                            <div class="action-buttons" style="display: none;">
                                <button class="action-button voice-button" title="语音朗诵">
                                    <i class="fas fa-volume-up"></i>
                                </button>
                                <button class="action-button copy-button" title="复制">
                                    <i class="fas fa-copy"></i>
                                </button>
                                <button class="action-button best-answer-button" title="最佳回复">
                                    <i class="fas fa-star"></i>
                                </button>
                                <button class="action-button error-button" title="错误回复">
                                    <i class="fas fa-exclamation-triangle"></i>
                                </button>
                                <button class="action-button regenerate-button" title="重新生成">
                                    <i class="fas fa-redo"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }

        chatContainer.appendChild(messageElement);
        chatContainer.scrollTop = chatContainer.scrollHeight;

        return messageElement;
    }

    async getAIResponse(question) {
        // 如果有正在进行的响应，取消它
        if (this.currentResponseController) {
            this.currentResponseController.abort();
        }

        // 创建新的 AbortController
        this.currentResponseController = new AbortController();

        let aiMessageElement = this.appendMessage('ai', '');
        const messageDisplay = aiMessageElement.querySelector('.message-display');
        const generatedTextSpan = messageDisplay.querySelector('.generated-text');
        const writingIcon = messageDisplay.querySelector('.writing-icon');
        const messageActions = aiMessageElement.querySelector('.message-actions');
        const stopButton = messageActions.querySelector('.stop-generation-button');
        const actionButtons = messageActions.querySelector('.action-buttons');
        
        // 初始状态：显示"正在思考"，隐藏钢笔图标
        generatedTextSpan.textContent = '正在思考...';
        writingIcon.style.display = 'none';
        messageActions.style.display = 'flex';
        stopButton.style.display = 'inline-block';
        actionButtons.style.display = 'none';
        stopButton.onclick = () => this.handleStopGeneration(aiMessageElement);

        try {
            console.log('发送问题:', question);
            const response = await sendQuestion(question, this.kb_id, this.currentResponseController.signal);

            let aiMessage = '';
            let docs = [];

            try {
                for await (const chunk of response) {
                    if (this.currentResponseController.signal.aborted) {
                        console.log('响应被中断');
                        break;
                    }
                    if (chunk.type === 'content') {
                        if (aiMessage === '') {
                            // 第一个内容块到达，清除"正在思考"并显示钢笔图标
                            generatedTextSpan.textContent = '';
                            writingIcon.style.display = 'inline-block';
                        }
                        aiMessage += chunk.data;
                        generatedTextSpan.textContent = aiMessage;
                        this.updateWritingIconPosition(messageDisplay, generatedTextSpan, writingIcon);
                        this.scrollToBottom();
                    } else if (chunk.type === 'docs') {
                        docs = chunk.data;
                    } else if (chunk.type === 'error' || chunk.type === 'warning') {
                        console.warn(`${chunk.type}:`, chunk.data);
                    }
                }
            } catch (iterationError) {
                if (iterationError.name === 'AbortError') {
                    console.log('响应处理被中断');
                } else {
                    console.error('迭代响应时出错:', iterationError);
                    throw iterationError;
                }
            }

            if (aiMessage === '') {
                this.updateAIMessage(aiMessageElement, '抱歉，我无法生成回答。');
            } else {
                const fullMessage = docs.length > 0 
                    ? `${aiMessage}\n\n参考文档：\n${docs.join('\n')}`
                    : aiMessage;
                this.updateAIMessage(aiMessageElement, fullMessage);
            }
        } catch (error) {
            if (error.name === 'AbortError') {
                console.log('请求被中断');
            } else {
                console.error('获取回答时出错:', error);
                this.updateAIMessage(aiMessageElement, '抱歉，我无法回答这个问题。');
            }
        } finally {
            this.currentResponseController = null;
            writingIcon.style.display = 'none';
            stopButton.style.display = 'none';
            actionButtons.style.display = 'flex'; // 显示其他操作按钮
        }
    }

    updateWritingIconPosition(messageDisplay, generatedTextSpan, writingIcon) {
        const textWidth = generatedTextSpan.offsetWidth;
        const textHeight = generatedTextSpan.offsetHeight;
        const iconWidth = writingIcon.offsetWidth;
        
        // 计算新的位置
        const newLeft = Math.min(textWidth, messageDisplay.offsetWidth - iconWidth);
        const newTop = textHeight;

        // 更新钢笔图标的位置
        writingIcon.style.left = `${newLeft}px`;
        writingIcon.style.top = `${newTop}px`;
    }

    updateAIMessage(element, message) {
        if (element) {
            const displayElement = element.querySelector('.message-display');
            if (displayElement) {
                displayElement.innerHTML = marked.parse(message, { sanitize: false });
                
                // 为问题链接添加样式
                const questionLinks = displayElement.querySelectorAll('.question-link');
                questionLinks.forEach(link => {
                    link.style.color = 'blue';
                    link.style.textDecoration = 'none';
                    link.style.cursor = 'pointer';
                    link.style.display = 'block';
                    link.style.margin = '5px 0';
                });

                // 滚动到页面底部
                this.scrollToBottom();
            }
        }
    }

    formatRecommendedQuestions(message) {
        // 将消息按行分割
        const lines = message.split('\n');
        // 过滤掉空，并给每个非空行添加编号
        const numberedLines = lines
            .filter(line => line.trim() !== '')
            .map((line, index) => `${index + 1}. ${line.trim()}`);
        // 将处理后的行重新组合成字符串
        return numberedLines.join('\n');
    }

    async handleGiveInspiration() {
        const userMessage = "给我一些问题做进一步了解。";
        this.appendMessage('user', userMessage);

        let aiMessageElement = this.appendMessage('ai', '');
        this.updateAIMessage(aiMessageElement, '正在思考...');

        try {
            const response = await sendQuestion(userMessage + "补充：不要其他概述，只返回5个问题，每个问题用换行符隔开，不要添加序号", this.kb_id);

            let aiMessage = '你可以向AI助理提供以下问题：\n\n';
            let fullResponse = '';

            try {
                for await (const chunk of response) {
                    if (chunk.type === 'content') {
                        fullResponse += chunk.data;
                        // 实时更新消息，显示正在生成的问题
                        this.updateAIMessage(aiMessageElement, aiMessage + fullResponse);
                    } else if (chunk.type === 'error') {
                        console.error('错误:', chunk.data);
                        throw new Error(chunk.data);
                    } else if (chunk.type === 'warning') {
                        console.warn('警告:', chunk.data);
                    }
                }
            } catch (iterationError) {
                console.error('迭代响应时出错:', iterationError);
                throw iterationError;
            }

            // 处理完整的响应
            const questions = fullResponse.split('\n').filter(q => q.trim() !== '');

            if (questions.length === 0) {
                this.updateAIMessage(aiMessageElement, '抱歉，我无法生成问题。');
            } else {
                aiMessage += questions.map((q, index) => `<a href="#" class="question-link" data-question="${q.trim()}">* ${q.trim()}</a>`).join('\n');
                this.updateAIMessage(aiMessageElement, aiMessage);
                this.addQuestionLinkListeners(aiMessageElement);
            }
        } catch (error) {
            console.error('获取灵感问题时出错:', error);
            this.updateAIMessage(aiMessageElement, '抱歉，生成灵感问题时现错误。');
        }
    }

    addQuestionLinkListeners(element) {
        const links = element.querySelectorAll('.question-link');
        links.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const question = e.target.getAttribute('data-question');
                this.appendMessage('user', question);
                this.getAIResponse(question);
            });
        });
    }

    logout() {
        sessionStorage.removeItem('authToken');
        sessionStorage.removeItem('username');
        window.location.href = 'login.html';
    }

    handleToolButtonClick(toolName) {
        const tagContainer = document.getElementById('tagContainer');
        
        // 创建新的标签元素
        const tag = document.createElement('div');
        tag.className = 'tag';
        tag.textContent = toolName;

        // 添加删除图标
        const removeTag = document.createElement('span');
        removeTag.className = 'remove-tag';
        removeTag.textContent = '✖'; // 删除图标
        removeTag.onclick = () => {
            tagContainer.removeChild(tag); // 删除标签
        };

        tag.appendChild(removeTag);
        tagContainer.appendChild(tag);
        
        // 更新输入框内容
        const inputField = document.querySelector('.input-field');
        inputField.value = ``;
        inputField.focus();
        
        // 关闭模态层
        const toolCenterModal = document.getElementById('toolCenterModal');
        if (toolCenterModal) {
            toolCenterModal.style.display = 'none';
        }
    }

    scrollToBottom() {
        const chatContainer = document.querySelector('.chat-container');
        if (chatContainer) {
            const previousScrollTop = chatContainer.scrollTop;
            chatContainer.scrollTop = chatContainer.scrollHeight;
            console.log('Scrolled chat container:', {
                previousScrollTop,
                newScrollTop: chatContainer.scrollTop,
                scrollHeight: chatContainer.scrollHeight
            });
        } else {
            console.warn('Chat container not found');
        }
        const previousPageYOffset = window.pageYOffset;
        window.scrollTo(0, document.body.scrollHeight);
        console.log('Scrolled window:', {
            previousPageYOffset,
            newPageYOffset: window.pageYOffset,
            bodyScrollHeight: document.body.scrollHeight
        });
    }

    handleStopGeneration(aiMessageElement) {
        if (this.currentResponseController) {
            this.currentResponseController.abort();
            this.updateAIMessage(aiMessageElement, '内容生成已停止。');
            const messageActions = aiMessageElement.querySelector('.message-actions');
            const stopButton = messageActions.querySelector('.stop-generation-button');
            const actionButtons = messageActions.querySelector('.action-buttons');
            stopButton.style.display = 'none';
            actionButtons.style.display = 'flex'; // 显示其他操作按钮
        }
    }

    copyToClipboard(text) {
        console.log('尝试复制内容:', text);
        const textArea = document.createElement("textarea");
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        let successful = false;
        try {
            successful = document.execCommand('copy');
        } catch (err) {
            console.error('复制失败:', err);
        }
        document.body.removeChild(textArea);
        
        if (successful) {
            console.log('内容已成功复制到剪贴板');
            // alert('内��已复制到剪��板');
        } else {
            console.error('复制失败');
            // alert('复制失败，请手动复制');
        }
    }

    voiceReadout(text) {
        const utterance = new SpeechSynthesisUtterance(text);
        speechSynthesis.speak(utterance);
    }

    markAsBestAnswer(messageElement) {
        messageElement.classList.add('best-answer');
        // 这里可以添加向服务器发送请求的逻辑
    }

    reportError(messageElement) {
        const errorReason = prompt('请描述错误原因：');
        if (errorReason) {
            console.log('错误报告:', errorReason);
            // 这里可以添加向服务器发送错误报告的逻辑
        }
    }

    regenerateResponse(question) {
        this.getAIResponse(question);
    }
}

// 创建 App 实例
const app = new App();

// 为了兼容性，保留全局函数
window.triggerFileUpload = () => {
    document.getElementById('fileInput').click();
};