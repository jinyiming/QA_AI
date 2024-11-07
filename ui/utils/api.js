export const API_URL = 'http://localhost:7878'; // 确保这是正确的后端地址

// 创建一个简单的 sessionState 对象
export const sessionState = {
    setItem(key, value) {
        sessionStorage.setItem(key, JSON.stringify(value));
    },
    getItem(key) {
        const value = sessionStorage.getItem(key);
        return value ? JSON.parse(value) : null;
    },
    removeItem(key) {
        sessionStorage.removeItem(key);
    },
    clear() {
        sessionStorage.clear();
    }
};


// 示例：使用 sessionState 存储和获取属性值
// sessionState.setItem('user', { name: '张三', age: 30 });
// const user = sessionState.getItem('user');
// console.log(user); // 输出: { name: '张三', age: 30 }

function getAuthHeaders() {
    const authToken = sessionStorage.getItem('authToken');
    return authToken ? { 'Authorization': `Bearer ${authToken}` } : {};
}

export async function sendQuestion(question, kb_id, signal) {
    console.log('sendQuestion 被调用，参数:', { question, kb_id });
    
    const messages = [{ role: "user", content: question }];
    const body = {
        messages: messages,
        stream: true,
        mode: "temp_kb",
        kb_name: kb_id,
    };

    console.log('发送请求到服务器，body:', body);
    let response;
    const headers = {
        'Content-Type': 'application/json',
        ...getAuthHeaders()
    };

    if (kb_id) {
        response = await fetch(`${API_URL}/knowledge_base/temp_kb/${kb_id}/chat/completions`, {
            method: 'POST',
            headers: headers,
            body: JSON.stringify(body),
            signal: signal // 添加这一行以支持中断
        });
    } else {
        const history = []
        const new_question = question +"。补充：请格式化输出回答。" + '|||' + sessionStorage.getItem('authToken') +
         '|||' + sessionStorage.getItem('userId') + '|||' + '[]' + '|||' + sessionStorage.getItem('systemNo') + '|||' + sessionStorage.getItem('orgNo');
        //   对办公系统你有什么需要了解的么？|||undefined|||null|||NaNCSXT|||D02190
          const chatBody = {
            messages: [{'role': 'user', 'content': question}],
            model: 'qwen2',
            stream: true,
            temperature: 0.6,  // 添加 temperature 参数
            // 移除 extra_body，将其内容直接放在主体中
            metadata: null,
            chat_model_config: {},
            conversation_id: 'dbba3b7f22194ea9a4d7c0a9eff4c586',
            tool_input: {},
            upload_image: null
        };
        const tags = Array.from(document.querySelectorAll('.tag')).map(tag => tag.textContent.replace('✖', '').trim());
        const toolMapping = {
            '办公系统': 'search_oa',
            '天气情况': 'weather',
            '时序年轮': 'candla',
            '其他工具': 'other'
        }
        const selectedTools = tags.map(tag => toolMapping[tag] || '').filter(tool => tool);
        if (selectedTools.length > 0) {
            chatBody['tools'] = selectedTools;
            chatBody['tool_choice'] = selectedTools[0];
            chatBody['tool_input'] = {
                'query': new_question
            };
            chatBody['messages'] = [{'role': 'user', 'content': new_question}];
        }
        console.log('chatBody:', chatBody);
        // 调用 /chat/chat 接口
        console.log('调用 /chat/chat 接口');
        response = await fetch(`${API_URL}/chat/chat/completions`, {
            method: 'POST',
            headers: headers,
            body: JSON.stringify(chatBody),
        });
    }

    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }

    console.log('收到服务器响应');
    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    // 保持原有的响应处理逻辑
    return {
        async *[Symbol.asyncIterator]() {
            let buffer = '';
            while (true) {
                const { done, value } = await reader.read();
                if (done) {
                    console.log("流结束");
                    break;
                }
                
                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split('\n');
                buffer = lines.pop();

                for (const line of lines) {
                    if (line.trim() === '') continue;
                    
                    if (line.startsWith('data: ')) {
                        const jsonStr = line.slice(5).trim();
                        try {
                            const data = JSON.parse(jsonStr);
                            console.log('解析的数据:', data);
                            if (data.object === 'chat.completion.chunk') {
                                if (data.choices && data.choices[0] && data.choices[0].delta && data.choices[0].delta.content) {
                                    // console.log('生成内容块:', data.choices[0].delta.content);
                                    yield { type: 'content', data: data.choices[0].delta.content };
                                } else if (data.content) {
                                    // console.log('生成内容:', data.content);
                                    yield { type: 'content', data: data.content };
                                }
                                if (data.docs) {
                                    console.log('文档:', data.docs);
                                    yield { type: 'docs', data: data.docs };
                                }
                            } else if (data.error) {
                                // console.error('服务器错误:', data.error);
                                yield { type: 'error', data: data.error };
                            } else {
                                console.warn('意外的数据格式:', data);
                            }
                        } catch (error) {
                            console.error('解析 JSON 时出错:', jsonStr);
                            yield { type: 'error', data: '无效的 JSON', raw: jsonStr };
                        }
                    } else if (line.startsWith(': ping')) {
                        console.log('收到 ping:', line);
                        // 忽略 ping 消息，不中断流
                        continue;
                    } else {
                        console.warn('意外的行格式:', line);
                        // 不要 yield 警告，而是继续处理下一行
                        continue;
                    }
                }
            }
        }
    };
}

export async function uploadFile(file) {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_URL}/upload`, {
        method: 'POST',
        body: formData,
    });

    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
}

// 临时上传文件接口，用于测试
export async function uploadFile_temp(files, prevId = null, chunkSize = 500, chunkOverlap = 50, zhTitleEnhance = true) {
    const formData = new FormData();
    
    // 支持单个文件或多个文件
    if (Array.isArray(files)) {
        files.forEach((file, index) => {
            formData.append('files', file);
        });
    } else {
        formData.append('files', files);
    }

    if (prevId) formData.append('prev_id', prevId);
    formData.append('chunk_size', chunkSize);
    formData.append('chunk_overlap', chunkOverlap);
    formData.append('zh_title_enhance', zhTitleEnhance);

    const response = await fetch(`${API_URL}/knowledge_base/upload_temp_docs`, {
        method: 'POST',
        body: formData,
    });

    if (!response.ok) {
        const errorText = await response.text();
        console.error('Upload error:', errorText);
        throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
    }

    
    const result = await response.json();
    
    if (result.code !== 200) {
        console.error('Upload failed:', result.msg);
        throw new Error(`Upload failed: ${result.msg}`);
    }

    // 解析返回的数据
    const { id, failed_files } = result.data;
    sessionState.setItem('kb_id', id);  // 存储 kb_id
    console.log('Upload successful. ID:', id);
    if (failed_files.length > 0) {
        console.warn('Some files failed to upload:', failed_files);
    }

    return { id, failedFiles: failed_files };
}
