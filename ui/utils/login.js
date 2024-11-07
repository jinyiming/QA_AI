import { API_URL } from './api.js';

console.log('login.js loaded');

document.addEventListener('DOMContentLoaded', () => {
    console.log('DOMContentLoaded event fired');
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        console.log('Login form found');
        loginForm.addEventListener('submit', handleLogin);
    } else {
        console.error('Login form not found');
    }
});

async function handleLogin(e) {
    console.log('handleLogin function called');
    e.preventDefault();
    const username = encodeURIComponent(document.getElementById('username').value);
    const password = encodeURIComponent(document.getElementById('password').value);
    
    console.log('Attempting login with:', { username, password });
    
    try {
        const url = `${API_URL}/login/_userLogin_sso?username=${username}&password=${password}`;
        console.log(`Sending request to ${url}`);
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'accept': 'application/json'
            }
        });

        console.log('Response received:', response);

        if (response.ok) {
            const data = await response.json();
            console.log('Login successful, data:', data);
            sessionStorage.setItem('authToken', data['x-auth-token']);
            sessionStorage.setItem('username', data['name']); // 存储用户名
            sessionStorage.setItem('systemNo', data['systemNo']);
            sessionStorage.setItem('orgNo', data['orgNo']);
            sessionStorage.setItem('userId', data['username']);
            console.log('Auth token and username stored in sessionStorage');
            window.location.href = 'index.html';
        } else {
            const errorData = await response.json();
            console.error('Login failed, error:', errorData);
            document.getElementById('errorMessage').textContent = errorData.detail || '登录失败';
        }
    } catch (error) {
        console.error('Login error:', error);
        document.getElementById('errorMessage').textContent = '登录时发生错误，请稍后再试';
    }
}

// 新增函数：获取工具列表
async function fetchTools() {
    console.log('fetchTools function called');
    try {
        const response = await fetch(`${API_URL}/tools`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${sessionStorage.getItem('authToken')}`,
                'Content-Type': 'application/json',
            },
        });

        console.log('Tools response received:', response);

        if (response.ok) {
            const toolsData = await response.json();
            console.log('工具列表:', toolsData.data);
            // 这里可以处理工具数据，例如存储或显示
        } else {
            console.error('获取工具列表失败:', response.statusText);
        }
    } catch (error) {
        console.error('获取工具列表时出错:', error);
    }
}
