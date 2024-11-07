export const messageActions = {
    voiceReadout(message) {
        const utterance = new SpeechSynthesisUtterance(message);
        speechSynthesis.speak(utterance);
    },

    copyToClipboard(message) {
        console.log('尝试复制内容:', message);
        
        // 创建一个临时的 textarea 元素
        const textArea = document.createElement("textarea");
        textArea.value = message;
        
        // 将 textarea 添加到文档中
        document.body.appendChild(textArea);
        
        // 选中文本
        textArea.select();
        textArea.setSelectionRange(0, 99999); // 对于移动设备
        
        // 尝试复制文本
        let successful = false;
        try {
            successful = document.execCommand('copy');
        } catch (err) {
            console.error('复制失败:', err);
        }
        
        // 从文档中移除 textarea
        document.body.removeChild(textArea);
        
        if (successful) {
            console.log('内容已成功复制到剪贴板');
            alert('内容已复制到剪贴板');
        } else {
            console.error('复制失败');
            alert('复制失败，请手动复制');
        }
    },

    fallbackCopyTextToClipboard(text) {
        console.log('使用回退方法复制文本');
        const textArea = document.createElement("textarea");
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        try {
            const successful = document.execCommand('copy');
            const msg = successful ? '成功' : '失败';
            console.log('回退方法: 复制文本 ' + msg);
            alert('内容已复制到剪贴板');
        } catch (err) {
            console.error('回退方法: 复制失败', err);
            alert('复制失败，请手动复制');
        }
        document.body.removeChild(textArea);
    },

    markAsBestAnswer(messageElement) {
        messageElement.classList.add('best-answer');
        // 这里可以添加向服务器发送请求的逻辑
    },

    reportError(messageElement) {
        const errorReason = prompt('请描述错误原因：');
        if (errorReason) {
            console.log('错误报告:', errorReason);
        }
    },

    regenerateResponse(question, getAIResponse) {
        getAIResponse(question);
    }
};
