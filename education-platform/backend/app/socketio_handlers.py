# backend/app/socketio_handlers.py
from flask_socketio import emit, join_room, leave_room, disconnect
from flask import request
from .models import db
from .models.user import User
from .models.student import Student
from .models.teacher import Teacher
from .models.session import VideoSession
from . import socketio
from datetime import datetime
import uuid

# Store active users
waiting_students = []
available_teachers = {}
active_sessions = {}

@socketio.on('connect')
def handle_connect():
    print(f'Client connected: {request.sid}')
    emit('connected', {'sid': request.sid})


@socketio.on('disconnect')
def handle_disconnect():
    print(f'Client disconnected: {request.sid}')
    
    # Remove from waiting lists
    global waiting_students, available_teachers
    
    if request.sid in waiting_students:
        waiting_students.remove(request.sid)
    
    if request.sid in available_teachers:
        del available_teachers[request.sid]
    
    # Handle active session cleanup
    for room_id, session_data in list(active_sessions.items()):
        if request.sid in [session_data.get('student_sid'), session_data.get('teacher_sid')]:
            # End the session
            handle_end_call({'room_id': room_id})


@socketio.on('student_join_queue')
def handle_student_join_queue(data):
    try:
        user_id = data.get('user_id')
        student_sid = request.sid
        
        # Verify student
        user = User.query.get(user_id)
        if not user or user.role != 'student':
            emit('error', {'message': 'Invalid student'})
            return
        
        student = user.student_profile
        
        print(f'Student {student.name} joined queue')
        
        # Check if there's an available teacher
        if available_teachers:
            # Match with first available teacher
            teacher_sid, teacher_data = available_teachers.popitem()
            
            # Create room
            room_id = str(uuid.uuid4())
            
            # Create session in database
            session = VideoSession(
                student_id=student.id,
                teacher_id=teacher_data['teacher_id'],
                room_id=room_id,
                status='active'
            )
            db.session.add(session)
            db.session.commit()
            
            # Store active session
            active_sessions[room_id] = {
                'session_id': session.id,
                'student_sid': student_sid,
                'teacher_sid': teacher_sid,
                'student_id': student.id,
                'teacher_id': teacher_data['teacher_id'],
                'start_time': datetime.utcnow()
            }
            
            # Join both to room
            join_room(room_id, sid=student_sid)
            join_room(room_id, sid=teacher_sid)
            
            # Notify both parties
            emit('match_found', {
                'room_id': room_id,
                'session_id': session.id,
                'partner_type': 'teacher',
                'partner_name': teacher_data['teacher_name']
            }, room=student_sid)
            
            emit('match_found', {
                'room_id': room_id,
                'session_id': session.id,
                'partner_type': 'student',
                'partner_name': student.name
            }, room=teacher_sid)
            
            print(f'Matched: Student {student.name} with Teacher {teacher_data["teacher_name"]}')
        else:
            # Add to waiting queue
            if student_sid not in waiting_students:
                waiting_students.append(student_sid)
                emit('waiting', {'message': 'Waiting for teacher...'})
                print(f'Student added to queue. Queue size: {len(waiting_students)}')
    
    except Exception as e:
        print(f'Error in student_join_queue: {str(e)}')
        emit('error', {'message': str(e)})


@socketio.on('teacher_available')
def handle_teacher_available(data):
    try:
        user_id = data.get('user_id')
        teacher_sid = request.sid
        
        # Verify teacher
        user = User.query.get(user_id)
        if not user or user.role != 'teacher':
            emit('error', {'message': 'Invalid teacher'})
            return
        
        teacher = user.teacher_profile
        
        print(f'Teacher {teacher.name} is available')
        
        # Check if there's a waiting student
        if waiting_students:
            # Match with first waiting student
            student_sid = waiting_students.pop(0)
            
            # Get student info from socket
            # Note: In production, you'd want to pass student_id with the socket connection
            # For now, we'll emit back to get student info
            
            # Create room
            room_id = str(uuid.uuid4())
            
            # We need student_id, so let's store teacher as available for now
            available_teachers[teacher_sid] = {
                'teacher_id': teacher.id,
                'teacher_name': teacher.name
            }
            
            # Notify student to send their info
            emit('teacher_ready', {'teacher_sid': teacher_sid}, room=student_sid)
        else:
            # Add to available teachers
            available_teachers[teacher_sid] = {
                'teacher_id': teacher.id,
                'teacher_name': teacher.name
            }
            emit('waiting', {'message': 'Waiting for student...'})
            print(f'Teacher added to available. Available count: {len(available_teachers)}')
    
    except Exception as e:
        print(f'Error in teacher_available: {str(e)}')
        emit('error', {'message': str(e)})


@socketio.on('webrtc_offer')
def handle_webrtc_offer(data):
    room_id = data.get('room_id')
    offer = data.get('offer')
    
    # Send offer to other peer in the room
    emit('webrtc_offer', {'offer': offer}, room=room_id, include_self=False)


@socketio.on('webrtc_answer')
def handle_webrtc_answer(data):
    room_id = data.get('room_id')
    answer = data.get('answer')
    
    # Send answer to other peer in the room
    emit('webrtc_answer', {'answer': answer}, room=room_id, include_self=False)


@socketio.on('webrtc_ice_candidate')
def handle_ice_candidate(data):
    room_id = data.get('room_id')
    candidate = data.get('candidate')
    
    # Send ICE candidate to other peer
    emit('webrtc_ice_candidate', {'candidate': candidate}, room=room_id, include_self=False)


@socketio.on('end_call')
def handle_end_call(data):
    try:
        room_id = data.get('room_id')
        
        if room_id not in active_sessions:
            emit('error', {'message': 'Session not found'})
            return
        
        session_data = active_sessions[room_id]
        
        # Calculate duration
        end_time = datetime.utcnow()
        start_time = session_data['start_time']
        duration = int((end_time - start_time).total_seconds())
        
        # Update database
        session = VideoSession.query.get(session_data['session_id'])
        session.end_time = end_time
        session.duration = duration
        session.status = 'completed'
        
        # Update student video time
        student = Student.query.get(session_data['student_id'])
        student.total_video_time += duration
        
        # Update teacher teaching time
        teacher = Teacher.query.get(session_data['teacher_id'])
        teacher.total_teaching_time += duration
        
        db.session.commit()
        
        # Notify both parties
        emit('call_ended', {
            'duration': duration,
            'message': 'Call ended successfully'
        }, room=room_id)
        
        # Clean up
        leave_room(room_id, sid=session_data['student_sid'])
        leave_room(room_id, sid=session_data['teacher_sid'])
        del active_sessions[room_id]
        
        print(f'Session ended. Duration: {duration}s')
    
    except Exception as e:
        print(f'Error ending call: {str(e)}')
        emit('error', {'message': str(e)})


@socketio.on('toggle_audio')
def handle_toggle_audio(data):
    room_id = data.get('room_id')
    audio_enabled = data.get('audio_enabled')
    
    emit('peer_audio_toggle', {'audio_enabled': audio_enabled}, room=room_id, include_self=False)


@socketio.on('toggle_video')
def handle_toggle_video(data):
    room_id = data.get('room_id')
    video_enabled = data.get('video_enabled')
    
    emit('peer_video_toggle', {'video_enabled': video_enabled}, room=room_id, include_self=False)