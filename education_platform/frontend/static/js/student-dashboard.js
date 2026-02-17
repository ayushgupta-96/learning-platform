// frontend/static/js/student-dashboard.js
if (!checkAuth()) {
    throw new Error('Not authenticated');
}

async function loadDashboard() {
    try {
        const profile = JSON.parse(localStorage.getItem('profile'));
        document.getElementById('studentName').textContent = profile.name;
        
        const stats = await API.get('/student/dashboard-stats');
        
        document.getElementById('pointsBalance').textContent = stats.points_balance;
        document.getElementById('videoTime').textContent = Math.floor(stats.total_video_time / 60) + ' min';
        document.getElementById('progress').textContent = stats.training_progress + '%';
        document.getElementById('totalSessions').textContent = stats.total_sessions;
        
        displayProfile(profile);
    } catch (error) {
        console.error('Error loading dashboard:', error);
    }
}

function displayProfile(profile) {
    const container = document.getElementById('profileInfo');
    container.innerHTML = `
        <p><strong>Email:</strong> ${JSON.parse(localStorage.getItem('user')).email}</p>
        <p><strong>Age:</strong> ${profile.age || 'N/A'}</p>
        <p><strong>Education:</strong> ${profile.education || 'N/A'}</p>
        <p><strong>Profession:</strong> ${profile.profession || 'N/A'}</p>
        <p><strong>Mobile:</strong> ${profile.mobile}</p>
    `;
}

loadDashboard();


 