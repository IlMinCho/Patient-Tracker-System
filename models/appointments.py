import sqlite3
from flask import *
import bcrypt
from datetime import datetime, timedelta
from models.doctor import Doctor

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

    def create(self, patient_email, doctor_email, date, time, reason):
        apt_id = self.get_id()
        self.cur.execute('SELECT * FROM doctor_availability WHERE doctor_email = ? AND day = ? AND start_time = ?', (doctor_email, date, time))
        availaibility = self.cur.fetchone()
        if availaibility:
            # If no overlap, insert the appointment
            try:
                self.cur.execute('INSERT INTO appointment VALUES (?,?,?,?,?,?,?,?)', (apt_id, patient_email, doctor_email, date, time, reason, "", "started"))
                self.conn.commit()
            except:
                raise Exception("Appointment can't be booked. Try again!")
        else:
            raise Exception("Not available for selected slot!")

