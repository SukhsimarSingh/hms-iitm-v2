from backend.celery_app import celery_app
from backend.database import db
from backend.models import Appointment, Doctor, User
from datetime import datetime, timedelta
import csv
import io
from flask import current_app

@celery_app.task(name='backend.tasks.send_daily_reminders')
def send_daily_reminders():
    """
    Send reminders to patients with same-day appointments.
    Runs daily at 9 AM.
    """
    try:
        from backend import create_app
        app = create_app()
        
        with app.app_context():
            today = datetime.now().date()
            
            # Get all appointments for today
            today_appointments = Appointment.query.filter(
                db.func.date(Appointment.date) == today,
                Appointment.status.in_(['scheduled', 'confirmed'])
            ).all()
            
            reminder_count = 0
            for appointment in today_appointments:
                # Get patient and doctor info
                patient = User.query.get(appointment.patient_id)
                doctor = User.query.get(appointment.doctor_id)
                
                if patient and doctor:
                    # Simple console log for now (can be extended to email/SMS later)
                    message = f"Reminder: You have an appointment with Dr. {doctor.first_name} {doctor.last_name} today at {appointment.time}"
                    print(f"[REMINDER] Patient {patient.email}: {message}")
                    reminder_count += 1
            
            print(f"[TASK COMPLETE] Sent {reminder_count} reminders")
            return {'status': 'success', 'reminders_sent': reminder_count}
    
    except Exception as e:
        print(f"[ERROR] Failed to send reminders: {str(e)}")
        return {'status': 'error', 'message': str(e)}


@celery_app.task(name='backend.tasks.generate_monthly_reports')
def generate_monthly_reports():
    """
    Generate monthly reports for all doctors.
    Includes: appointments, treatments, and diagnosis summary.
    Runs on the 1st of every month at 8 AM.
    """
    try:
        from backend import create_app
        app = create_app()
        
        with app.app_context():
            # Get the last month
            today = datetime.now().date()
            first_day_this_month = today.replace(day=1)
            last_day_prev_month = first_day_this_month - timedelta(days=1)
            first_day_prev_month = last_day_prev_month.replace(day=1)
            
            # Get all doctors
            doctors = Doctor.query.all()
            report_count = 0
            
            for doctor in doctors:
                # Get appointments for the doctor in the previous month
                appointments = Appointment.query.filter(
                    Appointment.doctor_id == doctor.user_id,
                    db.func.date(Appointment.date) >= first_day_prev_month,
                    db.func.date(Appointment.date) <= last_day_prev_month
                ).all()
                
                if appointments:
                    # Generate simple HTML report
                    html_report = generate_doctor_report_html(doctor, appointments, first_day_prev_month, last_day_prev_month)
                    
                    # Save report (can be extended to email or store in database)
                    report_filename = f"report_doctor_{doctor.id}_{last_day_prev_month.strftime('%Y_%m')}.html"
                    print(f"[REPORT] Generated {report_filename}")
                    report_count += 1
            
            print(f"[TASK COMPLETE] Generated {report_count} monthly reports")
            return {'status': 'success', 'reports_generated': report_count}
    
    except Exception as e:
        print(f"[ERROR] Failed to generate reports: {str(e)}")
        return {'status': 'error', 'message': str(e)}


def generate_doctor_report_html(doctor, appointments, start_date, end_date):
    """
    Generate HTML report for a doctor's monthly activity.
    """
    appointment_count = len(appointments)
    completed_count = len([a for a in appointments if a.status == 'completed'])
    cancelled_count = len([a for a in appointments if a.status == 'cancelled'])
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Monthly Report - Dr. {doctor.name}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            h1 {{ color: #333; }}
            table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
            th, td {{ border: 1px solid #ddd; padding: 10px; text-align: left; }}
            th {{ background-color: #0d6efd; color: white; }}
            .summary {{ background-color: #f8f9fa; padding: 15px; margin: 20px 0; border-radius: 5px; }}
        </style>
    </head>
    <body>
        <h1>Monthly Report</h1>
        <p><strong>Doctor:</strong> Dr. {doctor.name}</p>
        <p><strong>Specialization:</strong> {doctor.specialization}</p>
        <p><strong>Period:</strong> {start_date} to {end_date}</p>
        
        <div class="summary">
            <h2>Summary</h2>
            <p><strong>Total Appointments:</strong> {appointment_count}</p>
            <p><strong>Completed:</strong> {completed_count}</p>
            <p><strong>Cancelled:</strong> {cancelled_count}</p>
        </div>
        
        <h2>Appointments</h2>
        <table>
            <tr>
                <th>Patient</th>
                <th>Date</th>
                <th>Time</th>
                <th>Status</th>
            </tr>
    """
    
    for appointment in appointments:
        patient = User.query.get(appointment.patient_id)
        patient_name = f"{patient.first_name} {patient.last_name}" if patient else "N/A"
        html += f"""
            <tr>
                <td>{patient_name}</td>
                <td>{appointment.date}</td>
                <td>{appointment.time}</td>
                <td>{appointment.status}</td>
            </tr>
        """
    
    html += """
        </table>
    </body>
    </html>
    """
    
    return html


@celery_app.task(name='backend.tasks.export_patient_history_csv')
def export_patient_history_csv(patient_id):
    """
    Export patient's treatment history as CSV.
    Called asynchronously when user requests export.
    """
    try:
        from backend import create_app
        app = create_app()
        
        with app.app_context():
            patient = User.query.get(patient_id)
            if not patient:
                return {'status': 'error', 'message': 'Patient not found'}
            
            # Get patient's appointments
            appointments = Appointment.query.filter_by(patient_id=patient_id).all()
            
            # Create CSV
            csv_buffer = io.StringIO()
            csv_writer = csv.writer(csv_buffer)
            
            csv_writer.writerow(['Appointment ID', 'Doctor', 'Date', 'Time', 'Status', 'Diagnosis', 'Treatment'])
            
            for appointment in appointments:
                doctor = User.query.get(appointment.doctor_id)
                doctor_name = f"Dr. {doctor.first_name} {doctor.last_name}" if doctor else "N/A"
                diagnosis = appointment.diagnosis or "N/A"
                treatment = appointment.treatment or "N/A"
                
                csv_writer.writerow([
                    appointment.id,
                    doctor_name,
                    appointment.date,
                    appointment.time,
                    appointment.status,
                    diagnosis,
                    treatment
                ])
            
            csv_content = csv_buffer.getvalue()
            
            # In a real app, you'd save this and send email notification
            print(f"[EXPORT] Generated CSV for patient {patient_id}")
            
            return {
                'status': 'success',
                'patient_id': patient_id,
                'csv_data': csv_content,
                'filename': f"patient_{patient_id}_history_{datetime.now().strftime('%Y%m%d')}.csv"
            }
    
    except Exception as e:
        print(f"[ERROR] Failed to export CSV: {str(e)}")
        return {'status': 'error', 'message': str(e)}
