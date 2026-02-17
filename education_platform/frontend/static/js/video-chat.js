// frontend/static/js/video-chat.js
if (!checkAuth()) {
    throw new Error('Not authenticated');
}

const socket = io();
const user = JSON.parse(localStorage.getItem('user'));
const profile = JSON.parse(localStorage.getItem('profile'));
const userRole = user.role || 'student'; // Can be overridden in template

let localStream = null;
let remoteStream = null;
let peerConnection = null;
let currentRoomId = null;
let timerInterval = null;
let startTime = null;

const configuration = {
    iceServers: [
        { urls: 'stun:stun.l.google.com:19302' },
        { urls: 'stun:stun1.l.google.com:19302' }
    ]
};

// Initialize video chat
async function initVideoChat() {
    try {
        localStream = await navigator.mediaDevices.getUserMedia({
            video: true,
            audio: true
        });
        
        document.getElementById('localVideo').srcObject = localStream;
        
        // Join queue based on role
        if (userRole === 'student') {
            socket.emit('student_join_queue', { user_id: user.id });
        } else {
            socket.emit('teacher_available', { user_id: user.id });
        }
    } catch (error) {
        alert('Error accessing camera/microphone: ' + error.message);
        console.error(error);
    }
}

// Socket event handlers
socket.on('connected', (data) => {
    console.log('Connected to socket server:', data.sid);
});

socket.on('waiting', (data) => {
    console.log(data.message);
});

socket.on('match_found', async (data) => {
    console.log('Match found!', data);
    currentRoomId = data.room_id;
    
    document.getElementById('waitingScreen').style.display = 'none';
    document.getElementById('videoContainer').style.display = 'block';
    
    // Create peer connection
    await createPeerConnection();
    
    // Start timer
    startTimer();
});

socket.on('webrtc_offer', async (data) => {
    console.log('Received offer');
    
    if (!peerConnection) {
        await createPeerConnection();
    }
    
    await peerConnection.setRemoteDescription(new RTCSessionDescription(data.offer));
    const answer = await peerConnection.createAnswer();
    await peerConnection.setLocalDescription(answer);
    
    socket.emit('webrtc_answer', {
        room_id: currentRoomId,
        answer: answer
    });
});

socket.on('webrtc_answer', async (data) => {
    console.log('Received answer');
    await peerConnection.setRemoteDescription(new RTCSessionDescription(data.answer));
});

socket.on('webrtc_ice_candidate', async (data) => {
    console.log('Received ICE candidate');
    
    if (peerConnection && data.candidate) {
        await peerConnection.addIceCandidate(new RTCIceCandidate(data.candidate));
    }
});

socket.on('call_ended', (data) => {
    console.log('Call ended:', data);
    alert(`Call ended. Duration: ${Math.floor(data.duration / 60)} minutes`);
    window.location.href = userRole === 'student' ? '/student/dashboard' : '/teacher/dashboard';
});

socket.on('peer_audio_toggle', (data) => {
    console.log('Peer toggled audio:', data.audio_enabled);
});

socket.on('peer_video_toggle', (data) => {
    console.log('Peer toggled video:', data.video_enabled);
});

socket.on('error', (data) => {
    alert('Error: ' + data.message);
});

// Create WebRTC peer connection
async function createPeerConnection() {
    peerConnection = new RTCPeerConnection(configuration);
    
    // Add local stream tracks
    localStream.getTracks().forEach(track => {
        peerConnection.addTrack(track, localStream);
    });
    
    // Handle remote stream
    peerConnection.ontrack = (event) => {
        console.log('Received remote track');
        
        if (!remoteStream) {
            remoteStream = new MediaStream();
            document.getElementById('remoteVideo').srcObject = remoteStream;
        }
        
        remoteStream.addTrack(event.track);
    };
    
    // Handle ICE candidates
    peerConnection.onicecandidate = (event) => {
        if (event.candidate) {
            socket.emit('webrtc_ice_candidate', {
                room_id: currentRoomId,
                candidate: event.candidate
            });
        }
    };
    
    // If we're the initiator (e.g., student), create offer
    if (userRole === 'student') {
        const offer = await peerConnection.createOffer();
        await peerConnection.setLocalDescription(offer);
        
        socket.emit('webrtc_offer', {
            room_id: currentRoomId,
            offer: offer
        });
    }
}

// Control functions
function toggleAudio() {
    const audioTrack = localStream.getAudioTracks()[0];
    audioTrack.enabled = !audioTrack.enabled;
    
    const btn = document.getElementById('toggleAudio');
    btn.textContent = audioTrack.enabled ? '🎤 Mute' : '🎤 Unmute';
    btn.className = audioTrack.enabled ? 'control-btn btn-success' : 'control-btn btn-warning';
    
    socket.emit('toggle_audio', {
        room_id: currentRoomId,
        audio_enabled: audioTrack.enabled
    });
}

function toggleVideo() {
    const videoTrack = localStream.getVideoTracks()[0];
    videoTrack.enabled = !videoTrack.enabled;
    
    const btn = document.getElementById('toggleVideo');
    btn.textContent = videoTrack.enabled ? '📹 Turn Off Camera' : '📹 Turn On Camera';
    btn.className = videoTrack.enabled ? 'control-btn btn-success' : 'control-btn btn-warning';
    
    socket.emit('toggle_video', {
        room_id: currentRoomId,
        video_enabled: videoTrack.enabled
    });
}

function endCall() {
    if (confirm('Are you sure you want to end the call?')) {
        socket.emit('end_call', { room_id: currentRoomId });
        
        // Stop local stream
        if (localStream) {
            localStream.getTracks().forEach(track => track.stop());
        }
        
        // Close peer connection
        if (peerConnection) {
            peerConnection.close();
        }
        
        // Stop timer
        if (timerInterval) {
            clearInterval(timerInterval);
        }
    }
}

function startTimer() {
    startTime = new Date();
    timerInterval = setInterval(() => {
        const elapsed = Math.floor((new Date() - startTime) / 1000);
        const hours = Math.floor(elapsed / 3600);
        const minutes = Math.floor((elapsed % 3600) / 60);
        const seconds = elapsed % 60;
        
        document.getElementById('timer').textContent = 
            `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
    }, 1000);
}

// Initialize on page load
initVideoChat();

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (localStream) {
        localStream.getTracks().forEach(track => track.stop());
    }
    if (peerConnection) {
        peerConnection.close();
    }
    socket.disconnect();
});