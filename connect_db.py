from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME')
    )

@app.route('/review')
def review_applications():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT `COL 1` FROM applications_tsv;")
    raw_rows = cursor.fetchall()
    cursor.close()
    conn.close()

    applications = []
    for row in raw_rows:
        cols = row[0].split('\t')
        if cols[0] == 'a_email':  # skip header row
            continue
        application = {
            'a_email': cols[0],
            'a_f_name': cols[1],
            'a_l_name': cols[2],
            'a_street_addr': cols[3],
            'a_city': cols[4],
            'a_state': cols[5],
            'a_postal_code': cols[6],
            'a_phone': cols[7],
            'a_family_size': cols[8],
            'app_date': cols[9],
            'IsApproved': cols[10],
            'IsRejected': cols[11],
            'approved_date': cols[12] if len(cols) > 12 else '',
            'rejected_date': cols[13] if len(cols) > 13 else '',
        }
        if application['IsApproved'] == '0' and application['IsRejected'] == '0':
            applications.append(application)

    return render_template('review_applications.html', applications=applications)

@app.route('/approve', methods=['POST'])
def approve():
    a_email = request.form['a_email']
    app_date = request.form['app_date']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT `COL 1` FROM applications_tsv;")
    rows = cursor.fetchall()

    for row in rows:
        cols = row[0].split('\t')
        if cols[0] == 'a_email':  # skip header
            continue
        if cols[0] == a_email and cols[9] == app_date:
            cols[10] = '1'  # Set IsApproved to 1
            updated_row = '\t'.join(cols)
            cursor.execute("UPDATE applications_tsv SET `COL 1` = %s WHERE `COL 1` = %s", (updated_row, row[0]))
            conn.commit()
            break

    cursor.close()
    conn.close()
    return redirect(url_for('review_applications'))

@app.route('/reject', methods=['POST'])
def reject():
    a_email = request.form['a_email']
    app_date = request.form['app_date']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT `COL 1` FROM applications_tsv;")
    rows = cursor.fetchall()

    for row in rows:
        cols = row[0].split('\t')
        if cols[0] == 'a_email':  # skip header
            continue
        if cols[0] == a_email and cols[9] == app_date:
            cols[11] = '1'  # Set IsRejected to 1
            updated_row = '\t'.join(cols)
            cursor.execute("UPDATE applications_tsv SET `COL 1` = %s WHERE `COL 1` = %s", (updated_row, row[0]))
            conn.commit()
            break

    cursor.close()
    conn.close()
    return redirect(url_for('review_applications'))

if __name__ == '__main__':
    app.run(debug=True)


