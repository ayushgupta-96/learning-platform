// frontend/static/js/auth.js
async function handleStudentSignup(formData) {
    try {
        const response = await API.post('/auth/student/signup', formData);
        
        API.setToken(response.access_token);
        localStorage.setItem('user', JSON.stringify(response.user));
        localStorage.setItem('profile', JSON.stringify(response.profile));
        
        window.location.href = '/student/dashboard';
    } catch (error) {
        document.getElementById('errorMessage').textContent = error.message;
    }
}

async function handleStudentLogin(formData) {
    try {
        const response = await API.post('/auth/student/login', formData);
        
        API.setToken(response.access_token);
        localStorage.setItem('user', JSON.stringify(response.user));
        localStorage.setItem('profile', JSON.stringify(response.profile));
        
        window.location.href = '/student/dashboard';
    } catch (error) {
        document.getElementById('errorMessage').textContent = error.message;
    }
}

async function handleTeacherSignup(formData) {
    try {
        const response = await API.post('/auth/teacher/signup', formData);
        
        API.setToken(response.access_token);
        localStorage.setItem('user', JSON.stringify(response.user));
        localStorage.setItem('profile', JSON.stringify(response.profile));
        
        window.location.href = '/teacher/dashboard';
    } catch (error) {
        document.getElementById('errorMessage').textContent = error.message;
    }
}

async function handleTeacherLogin(formData) {
    try {
        const response = await API.post('/auth/teacher/login', formData);
        
        API.setToken(response.access_token);
        localStorage.setItem('user', JSON.stringify(response.user));
        localStorage.setItem('profile', JSON.stringify(response.profile));
        
        window.location.href = '/teacher/dashboard';
    } catch (error) {
        document.getElementById('errorMessage').textContent = error.message;
    }
}


 