import gspread
from oauth2client.service_account import ServiceAccountCredentials
from flask import Flask, render_template, jsonify
from datetime import datetime

app = Flask(__name__)

def authorize_google_sheets(credentials_file, spreadsheet_id, worksheet_name):
    try:
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        credentials = ServiceAccountCredentials.from_json_keyfile_name(credentials_file, scope)
        client = gspread.authorize(credentials)

        spreadsheet = client.open_by_key(spreadsheet_id)
        worksheet = spreadsheet.worksheet(worksheet_name)

        return worksheet.get_all_values()

    except gspread.exceptions.APIError as e:
        if 'The caller does not have permission' in str(e):
            raise PermissionError("No tienes permisos para acceder a la hoja de cálculo.")
        else:
            raise

def parse_event_data(data):
    events_list = []

    for row in data[1:]:
        start_date_str = row[8]
        end_date_str = row[9]

        if start_date_str and end_date_str:
            start_date = datetime.strptime(start_date_str, '%m/%d').replace(year=2024).strftime('%Y-%m-%d')
            end_date = datetime.strptime(end_date_str, '%m/%d').replace(year=2024).strftime('%Y-%m-%d')

            event = {
                'title': row[3],
                'start': start_date,
                'end': end_date,
                'allDay': True,
                'address': row[2],
                'sub_task': row[4],
                'sub': row[5],
                'pm': row[0]
            }
            events_list.append(event)

    return events_list

@app.route('/')
def index():
    return render_template('calendar.html')

@app.route('/events')
def events():
    credentials_file = 'client_secret.json'
    spreadsheet_id = '1kW4ulLpuwWXxIzRKmePDSdR_OukucgVRmm5aLeQplvA'
    worksheet_name = 'Program'

    data = authorize_google_sheets(credentials_file, spreadsheet_id, worksheet_name)
    events_list = parse_event_data(data)

    return jsonify(events_list)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
