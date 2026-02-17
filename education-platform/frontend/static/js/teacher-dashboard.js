// frontend/static/js/teacher-dashboard.js
if (!checkAuth()) {
    throw new Error('Not authenticated');
}

async function loadDashboard() {
    try {
        const profile = JSON.parse(localStorage.getItem('profile'));
        document.getElementById('teacherName').textContent = profile.name;
        
        const stats = await API.get('/teacher/dashboard-stats');
        
        document.getElementById('teachingTime').textContent = Math.floor(stats.total_teaching_time / 60) + ' min';
        document.getElementById('totalSessions').textContent = stats.total_sessions;
        document.getElementById('monthSessions').textContent = stats.sessions_this_month;
        document.getElementById('availability').textContent = stats.is_available ? 'Online' : 'Offline';
        document.getElementById('availabilityStatus').textContent = 
            `You are currently ${stats.is_available ? 'available' : 'unavailable'} for sessions`;
    } catch (error) {
        console.error('Error loading dashboard:', error);
    }
}

async function toggleAvailability() {
    try {
        const response = await API.post('/teacher/toggle-availability', {});
        document.getElementById('availabilityStatus').textContent = 
            `You are now ${response.is_available ? 'available' : 'unavailable'} for sessions`;
        loadDashboard();
    } catch (error) {
        alert('Error toggling availability: ' + error.message);
    }
}

async function loadSessionHistory() {
    try {
        const response = await API.get('/teacher/session-history');
        const container = document.getElementById('historyContainer');
        const section = document.getElementById('sessionHistory');
        
        if (response.sessions.length === 0) {
            container.innerHTML = '<p>No sessions yet</p>';
        } else {
            container.innerHTML = response.sessions.map(s => `
                <div class="session-item">
                    <p><strong>Date:</strong> ${new Date(s.start_time).toLocaleString()}</p>
                    <p><strong>Duration:</strong> ${Math.floor(s.duration / 60)} minutes</p>
                    <p><strong>Status:</strong> ${s.status}</p>
                </div>
            `).join('');
        }
        
        section.style.display = 'block';
    } catch (error) {
        alert('Error loading history: ' + error.message);
    }
}

loadDashboard();