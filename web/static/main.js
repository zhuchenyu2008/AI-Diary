const apiBase = '/api/v1';
let token = localStorage.getItem('token');
let username = localStorage.getItem('username');

function showApp() {
    document.getElementById('auth').style.display = 'none';
    document.getElementById('app').style.display = 'block';
    document.getElementById('current-user').textContent = username;
    loadMoments();
    loadDiaries();
}

function showAuth() {
    document.getElementById('auth').style.display = 'block';
    document.getElementById('app').style.display = 'none';
}

async function registerUser(evt) {
    evt.preventDefault();
    const form = evt.target;
    const payload = {
        username: form.username.value,
        password: form.password.value,
        email: form.email.value || null
    };
    await fetch(apiBase + '/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });
    alert('注册成功，请登录');
    form.reset();
}

async function loginUser(evt) {
    evt.preventDefault();
    const form = evt.target;
    const payload = {
        username: form.username.value,
        password: form.password.value
    };
    const res = await fetch(apiBase + '/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });
    if (res.ok) {
        const data = await res.json();
        token = data.access_token;
        username = payload.username;
        localStorage.setItem('token', token);
        localStorage.setItem('username', username);
        showApp();
    } else {
        alert('登录失败');
    }
}

document.getElementById('register-form').addEventListener('submit', registerUser);
document.getElementById('login-form').addEventListener('submit', loginUser);

document.getElementById('logout-btn').addEventListener('click', () => {
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    token = null;
    showAuth();
});

async function loadMoments() {
    const res = await fetch(apiBase + '/moments', {
        headers: { 'Authorization': 'Bearer ' + token }
    });
    const list = document.getElementById('moment-list');
    list.innerHTML = '';
    if (res.ok) {
        const data = await res.json();
        data.forEach(m => {
            const li = document.createElement('li');
            li.textContent = (m.ai_description_final || m.ai_description_origin) + ' - ' + new Date(m.created_at).toLocaleString();
            list.appendChild(li);
        });
    }
}

async function loadDiaries() {
    const res = await fetch(apiBase + '/diaries/recent', {
        headers: { 'Authorization': 'Bearer ' + token }
    });
    const list = document.getElementById('diary-list');
    list.innerHTML = '';
    if (res.ok) {
        const data = await res.json();
        data.forEach(d => {
            const li = document.createElement('li');
            li.textContent = d.diary_date + ': ' + (d.content_final || d.content_origin);
            list.appendChild(li);
        });
    }
}

document.getElementById('moment-form').addEventListener('submit', async evt => {
    evt.preventDefault();
    const form = evt.target;
    const formData = new FormData();
    if (form.text.value) formData.append('text', form.text.value);
    if (form.image.files[0]) formData.append('image', form.image.files[0]);
    const res = await fetch(apiBase + '/moments', {
        method: 'POST',
        headers: { 'Authorization': 'Bearer ' + token },
        body: formData
    });
    if (res.ok) {
        form.reset();
        loadMoments();
    } else {
        alert('上传失败');
    }
});

document.getElementById('generate-diary-btn').addEventListener('click', async () => {
    const res = await fetch(apiBase + '/diaries/summarize-today', {
        method: 'POST',
        headers: { 'Authorization': 'Bearer ' + token }
    });
    if (res.ok) {
        loadDiaries();
    } else {
        alert('生成失败');
    }
});

if (token) {
    showApp();
} else {
    showAuth();
}
