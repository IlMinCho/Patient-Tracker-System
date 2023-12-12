import sqlite3
from flask import *
import bcrypt
from datetime import datetime, timedelta

#creates the appointment
class Appointment:
    def __init__(self):
        self.conn = sqlite3.connect('./healthdb.db')
        self.cur = self.conn.cursor()
        self.setup_db()

    def setup_db(self):
        self.cur.execute('CREATE TABLE IF NOT EXISTS appointment (apt_id TEXT PRIMARY KEY, patient_email TEXT, doctor_email TEXT, date TEXT, time TEXT, reason TEXT, prescription TEXT, status TEXT)')
        self.conn.commit()

    def get_id(self):
        self.cur.execute('SELECT MAX(apt_id) FROM appointment;')
        result = self.cur.fetchone()[0]
        return str(int(result)+1) if result else 1
    
    def get_appointment_unavailable(self, doctor_email):
        query = 'SELECT date, time FROM appointment WHERE doctor_email = ? AND (status = ?);'
        self.cur.execute(query, (doctor_email, 'inprogress'))
        result = self.cur.fetchall()
        return result

    def create(self, patient_email, doctor_email, date, time, reason):
        apt_id = self.get_id()
        self.cur.execute('SELECT * FROM doctor_availability WHERE doctor_email = ? AND day = ? AND start_time <= ? AND end_time >= ?', (doctor_email, date, time, time))

        if not self.cur.fetchone():
            raise Exception("Doctor is not available at the requested time")
        
        unavailable_times = self.get_appointment_unavailable(doctor_email)
        new_start = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
        new_end = new_start + timedelta(hours=1)

        for date, time in unavailable_times:
            unavailable_start = datetime.strptime(f"{date}T{time}", "%Y-%m-%dT%H:%M")
            unavailable_end = end_datetime = unavailable_start + timedelta(hours=1) 

        if new_start <= unavailable_end and new_end >= unavailable_start:
            raise Exception("Appointment time overlaps with an unavailable slot")

        # If no overlap, insert the appointment
        self.cur.execute('INSERT INTO appointment VALUES (?,?,?,?,?,?,?,?)', (apt_id, patient_email, doctor_email, date, time, reason, "", "started"))
        self.conn.commit()

