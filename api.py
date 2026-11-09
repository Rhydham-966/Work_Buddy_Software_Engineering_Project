# api.py — Flask REST API for WorkBuddy Frontend
# Robust version with comprehensive error handling

from flask import Flask, request, jsonify, session, send_from_directory
from flask_cors import CORS
from decimal import Decimal
from datetime import date, datetime, timedelta
import traceback

# --- Import existing services ---
from services.auth_service import register_user, verify_otp, login_user, get_user_by_id
from services.customer_service import view_services, get_professionals_for_service
from services.booking_service import (
    create_booking, get_customer_bookings, get_customer_history,
    get_professional_bookings, get_professional_history,
    cancel_booking, accept_booking, reject_booking, complete_booking,
    get_available_slots_for_professional
)
from services.professional_service import (
    create_profile, add_service_pricing, add_slot,
    get_profile, get_my_services, get_my_slots, get_available_services
)
from services.payment_service import process_payment
from services.admin_service import add_service, approve_professional
from repositories.professional_repository import (
    get_pending_professionals, reject_professional as repo_reject_professional
)

app = Flask(__name__, static_folder='frontend', static_url_path='')
app.secret_key = 'workbuddy-secret-key-2026'
CORS(app, supports_credentials=True)


# ──────────────────────────────────────────────
#  SERIALIZATION HELPERS
# ──────────────────────────────────────────────
def serialize_value(val):
    """Convert non-JSON-serializable types."""
    if val is None:
        return None
    if isinstance(val, Decimal):
        return float(val)
    if isinstance(val, datetime):
        return val.strftime('%Y-%m-%d %H:%M:%S')
    if isinstance(val, date):
        return val.strftime('%Y-%m-%d')
    if isinstance(val, timedelta):
        total = int(val.total_seconds())
        hours, remainder = divmod(total, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    if isinstance(val, bytes):
        return bool(val)  # MySQL returns BOOLEAN as bytes sometimes
    return val

def serialize_dict(d):
    """Serialize all values in a dictionary."""
    if not d:
        return d
    return {k: serialize_value(v) for k, v in d.items()}

def serialize_list(lst):
    """Serialize all dicts in a list."""
    if not lst:
        return []
    return [serialize_dict(d) for d in lst]

def api_error(message, status=400):
    return jsonify({'success': False, 'message': message}), status

def api_success(data=None, message='OK'):
    resp = {'success': True, 'message': message}
    if data:
        resp.update(data)
    return jsonify(resp)

def get_current_user():
    """Get the current user from session, or None."""
    return session.get('user')

def require_auth(role=None):
    """Check authentication and optional role."""
    user_session = get_current_user()
    if not user_session:
        return None, api_error('Not logged in', 401)
    
    # Verify user still exists in DB (to handle stale sessions after reset)
    db_user = get_user_by_id(user_session.get('id'))
    if not db_user:
        session.clear()
        return None, api_error('Session invalid/expired. Please login again.', 401)
        
    if role and user_session.get('role') != role:
        return None, api_error('Unauthorized role', 403)
    return user_session, None


# ──────────────────────────────────────────────
#  FRONTEND SERVING
# ──────────────────────────────────────────────
@app.route('/')
def serve_frontend():
    return send_from_directory('frontend', 'index.html')

@app.route('/favicon.ico')
def favicon():
    return '', 204


# ──────────────────────────────────────────────
#  AUTH ENDPOINTS
# ──────────────────────────────────────────────
@app.route('/api/register', methods=['POST'])
def api_register():
    try:
        data = request.json or {}
        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        phone = data.get('phone', '').strip()
        password = data.get('password', '')
        role = data.get('role', '')

        if not all([name, email, phone, password, role]):
            return api_error('All fields are required')

        if role not in ('customer', 'professional', 'admin'):
            return api_error('Invalid role')

        register_result = register_user(name, email, phone, password, role)

        if register_result is None:
            return api_error('User with this phone already exists', 409)

        user_id, otp = register_result

        return api_success({'user_id': user_id, 'otp': otp}, 'Registration successful. Please verify OTP.')
    except Exception as e:
        traceback.print_exc()
        return api_error(f'Server error: {str(e)}', 500)


@app.route('/api/verify-otp', methods=['POST'])
def api_verify_otp():
    try:
        data = request.json or {}
        user_id = data.get('user_id')
        otp = data.get('otp', '').strip()

        if not user_id or not otp:
            return api_error('User ID and OTP required')

        result = verify_otp(user_id, otp)

        if result:
            return api_success(message='OTP verified successfully')
        else:
            return api_error('Invalid or expired OTP', 401)
    except Exception as e:
        traceback.print_exc()
        return api_error(f'Server error: {str(e)}', 500)


@app.route('/api/login', methods=['POST'])
def api_login():
    try:
        data = request.json or {}
        phone = data.get('phone', '').strip()
        password = data.get('password', '')

        if not phone or not password:
            return api_error('Phone and password required')

        user = login_user(phone, password)

        if user is None:
            return api_error('Invalid credentials or unverified account', 401)

        session['user'] = {
            'id': user['id'],
            'name': user['name'],
            'email': user['email'],
            'phone': user['phone'],
            'role': user['role']
        }

        return api_success({'user': session['user']}, 'Login successful')
    except Exception as e:
        traceback.print_exc()
        return api_error(f'Server error: {str(e)}', 500)


@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.clear()
    return api_success(message='Logged out')


@app.route('/api/me', methods=['GET'])
def api_me():
    user = get_current_user()
    if not user:
        return api_error('Not logged in', 401)
    return api_success({'user': user})


# ──────────────────────────────────────────────
#  CUSTOMER ENDPOINTS
# ──────────────────────────────────────────────
@app.route('/api/services', methods=['GET'])
def api_get_services():
    try:
        services = view_services()
        return api_success({'services': serialize_list(services)})
    except Exception as e:
        traceback.print_exc()
        return api_error(str(e), 500)


@app.route('/api/professionals/<int:service_id>', methods=['GET'])
def api_get_professionals(service_id):
    try:
        professionals = get_professionals_for_service(service_id)
        return api_success({'professionals': serialize_list(professionals)})
    except Exception as e:
        traceback.print_exc()
        return api_error(str(e), 500)


@app.route('/api/slots/<int:professional_id>', methods=['GET'])
def api_get_slots(professional_id):
    try:
        slots = get_available_slots_for_professional(professional_id)
        return api_success({'slots': serialize_list(slots)})
    except Exception as e:
        traceback.print_exc()
        return api_error(str(e), 500)


@app.route('/api/bookings', methods=['POST'])
def api_create_booking():
    try:
        user, err = require_auth('customer')
        if err:
            return err

        data = request.json or {}
        professional_id = data.get('professional_id')
        service_id = data.get('service_id')
        booking_type = data.get('booking_type', 'scheduled')
        payment_method = data.get('payment_method', 'cash')
        total_price = data.get('total_price', 0)
        slot_id = data.get('slot_id')

        if not professional_id or not service_id:
            return api_error('Professional and service are required')

        booking_id = create_booking(
            user['id'], professional_id, service_id,
            booking_type, payment_method, total_price, slot_id=slot_id
        )

        if booking_id:
            # Process payment: UPI = paid immediately, cash = pending
            process_payment(booking_id, payment_method, total_price)
            return api_success({'booking_id': booking_id}, 'Booking created successfully!')
        else:
            return api_error('Booking failed', 500)
    except Exception as e:
        traceback.print_exc()
        return api_error(f'Server error: {str(e)}', 500)


@app.route('/api/customer/bookings', methods=['GET'])
def api_customer_bookings():
    try:
        user, err = require_auth()
        if err:
            return err
        bookings = get_customer_bookings(user['id'])
        return api_success({'bookings': serialize_list(bookings)})
    except Exception as e:
        traceback.print_exc()
        return api_error(str(e), 500)


@app.route('/api/customer/history', methods=['GET'])
def api_customer_history():
    try:
        user, err = require_auth()
        if err:
            return err
        history = get_customer_history(user['id'])
        return api_success({'bookings': serialize_list(history)})
    except Exception as e:
        traceback.print_exc()
        return api_error(str(e), 500)


@app.route('/api/customer/cancel/<int:booking_id>', methods=['POST'])
def api_cancel_booking(booking_id):
    try:
        user, err = require_auth()
        if err:
            return err
        success, msg = cancel_booking(booking_id, user['id'])
        if success:
            return api_success(message=msg)
        else:
            return api_error(msg)
    except Exception as e:
        traceback.print_exc()
        return api_error(str(e), 500)


# ──────────────────────────────────────────────
#  PROFESSIONAL ENDPOINTS
# ──────────────────────────────────────────────
@app.route('/api/professional/profile', methods=['GET'])
def api_get_profile():
    try:
        user, err = require_auth()
        if err:
            return err

        profile = get_profile(user['id'])
        if profile:
            profile = serialize_dict(profile)
            # Ensure is_approved is a proper boolean
            profile['is_approved'] = bool(profile.get('is_approved', False))
            services = get_my_services(profile['id'])
            return api_success({'profile': profile, 'services': serialize_list(services)})
        else:
            return api_success({'profile': None, 'services': []})
    except Exception as e:
        traceback.print_exc()
        return api_error(str(e), 500)


@app.route('/api/professional/profile', methods=['POST'])
def api_create_profile():
    try:
        user, err = require_auth('professional')
        if err:
            return err

        data = request.json or {}
        experience = data.get('experience')
        area = data.get('area', '').strip()
        work_radius = data.get('work_radius')

        if not experience or not area or not work_radius:
            return api_error('All profile fields are required')

        pid = create_profile(user['id'], experience, area, work_radius)
        if pid:
            return api_success({'professional_id': pid}, 'Profile created successfully!')
        else:
            return api_error('Profile already exists', 409)
    except Exception as e:
        traceback.print_exc()
        return api_error(str(e), 500)


@app.route('/api/professional/services', methods=['POST'])
def api_add_service_pricing():
    try:
        user, err = require_auth('professional')
        if err:
            return err

        profile = get_profile(user['id'])
        if not profile:
            return api_error('Create profile first')

        data = request.json or {}
        service_id = data.get('service_id')
        custom_price = data.get('custom_price')

        if not service_id or not custom_price:
            return api_error('Service ID and price are required')

        add_service_pricing(profile['id'], service_id, custom_price)
        return api_success(message='Service pricing added successfully!')
    except Exception as e:
        traceback.print_exc()
        return api_error(str(e), 500)


@app.route('/api/professional/slots', methods=['GET'])
def api_get_my_slots():
    try:
        user, err = require_auth()
        if err:
            return err

        profile = get_profile(user['id'])
        if not profile:
            return api_success({'slots': []})

        slots = get_my_slots(profile['id'])
        return api_success({'slots': serialize_list(slots)})
    except Exception as e:
        traceback.print_exc()
        return api_error(str(e), 500)


@app.route('/api/professional/slots', methods=['POST'])
def api_add_slot():
    try:
        user, err = require_auth('professional')
        if err:
            return err

        profile = get_profile(user['id'])
        if not profile:
            return api_error('Create profile first')

        if not profile.get('is_approved'):
            return api_error('Your profile is not yet approved by admin. Please wait for approval.', 403)

        data = request.json or {}
        slot_date = data.get('slot_date')
        start_time = data.get('start_time')
        end_time = data.get('end_time')

        if not slot_date or not start_time or not end_time:
            return api_error('Date, start time, and end time are required')

        slot_id = add_slot(profile['id'], slot_date, start_time, end_time)
        if slot_id:
            return api_success({'slot_id': slot_id}, 'Time slot added successfully!')
        else:
            return api_error('Failed to add slot', 500)
    except Exception as e:
        traceback.print_exc()
        return api_error(str(e), 500)


@app.route('/api/professional/bookings', methods=['GET'])
def api_professional_bookings():
    try:
        user, err = require_auth()
        if err:
            return err

        profile = get_profile(user['id'])
        if not profile:
            return api_success({'bookings': []})

        bookings = get_professional_bookings(profile['id'])
        return api_success({'bookings': serialize_list(bookings)})
    except Exception as e:
        traceback.print_exc()
        return api_error(str(e), 500)


@app.route('/api/professional/history', methods=['GET'])
def api_professional_history():
    try:
        user, err = require_auth()
        if err:
            return err

        profile = get_profile(user['id'])
        if not profile:
            return api_success({'bookings': []})

        history = get_professional_history(profile['id'])
        return api_success({'bookings': serialize_list(history)})
    except Exception as e:
        traceback.print_exc()
        return api_error(str(e), 500)


@app.route('/api/professional/accept/<int:booking_id>', methods=['POST'])
def api_accept_booking(booking_id):
    try:
        user, err = require_auth('professional')
        if err:
            return err

        profile = get_profile(user['id'])
        if not profile:
            return api_error('No professional profile')

        success, msg = accept_booking(booking_id, profile['id'])
        if success:
            return api_success(message=msg)
        else:
            return api_error(msg)
    except Exception as e:
        traceback.print_exc()
        return api_error(str(e), 500)


@app.route('/api/professional/reject/<int:booking_id>', methods=['POST'])
def api_reject_booking(booking_id):
    try:
        user, err = require_auth('professional')
        if err:
            return err

        profile = get_profile(user['id'])
        if not profile:
            return api_error('No professional profile')

        success, msg = reject_booking(booking_id, profile['id'])
        if success:
            return api_success(message=msg)
        else:
            return api_error(msg)
    except Exception as e:
        traceback.print_exc()
        return api_error(str(e), 500)


@app.route('/api/professional/complete/<int:booking_id>', methods=['POST'])
def api_complete_booking(booking_id):
    try:
        user, err = require_auth('professional')
        if err:
            return err

        profile = get_profile(user['id'])
        if not profile:
            return api_error('No professional profile')

        success, msg = complete_booking(booking_id, profile['id'])
        if success:
            return api_success(message=msg)
        else:
            return api_error(msg)
    except Exception as e:
        traceback.print_exc()
        return api_error(str(e), 500)


@app.route('/api/available-services', methods=['GET'])
def api_available_services():
    try:
        services = get_available_services()
        return api_success({'services': serialize_list(services)})
    except Exception as e:
        traceback.print_exc()
        return api_error(str(e), 500)


# ──────────────────────────────────────────────
#  ADMIN ENDPOINTS
# ──────────────────────────────────────────────
@app.route('/api/admin/services', methods=['POST'])
def api_add_service():
    try:
        user, err = require_auth('admin')
        if err:
            return err

        data = request.json or {}
        name = data.get('name', '').strip()
        description = data.get('description', '').strip()
        base_price = data.get('base_price')
        estimated_time = data.get('estimated_time', '').strip()

        if not name or not base_price:
            return api_error('Service name and price are required')

        success, msg = add_service(name, description, base_price, estimated_time)
        if success:
            return api_success(message=msg)
        else:
            return api_error(msg)
    except Exception as e:
        traceback.print_exc()
        return api_error(str(e), 500)


@app.route('/api/admin/professionals', methods=['GET'])
def api_pending_professionals():
    try:
        user, err = require_auth('admin')
        if err:
            return err

        professionals = get_pending_professionals()
        result = []
        for p in professionals:
            p_data = serialize_dict(p)
            services = get_my_services(p['id'])
            p_data['services_offered'] = serialize_list(services)
            result.append(p_data)

        return api_success({'professionals': result})
    except Exception as e:
        traceback.print_exc()
        return api_error(str(e), 500)


@app.route('/api/admin/approve/<int:professional_id>', methods=['POST'])
def api_approve_professional(professional_id):
    try:
        user, err = require_auth('admin')
        if err:
            return err

        success, msg = approve_professional(professional_id)
        if success:
            return api_success(message=msg)
        else:
            return api_error(msg)
    except Exception as e:
        traceback.print_exc()
        return api_error(str(e), 500)


@app.route('/api/admin/reject/<int:professional_id>', methods=['POST'])
def api_reject_professional(professional_id):
    try:
        user, err = require_auth('admin')
        if err:
            return err

        repo_reject_professional(professional_id)
        return api_success(message='Professional rejected')
    except Exception as e:
        traceback.print_exc()
        return api_error(str(e), 500)


if __name__ == '__main__':
    print("\nWorkBuddy API Server starting...")
    print("   Frontend: http://localhost:5000")
    print("   API Base: http://localhost:5000/api\n")
    app.run(debug=True, port=5000)
