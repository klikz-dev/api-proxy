from http.server import BaseHTTPRequestHandler
import os
import environ
import json
import pysftp
import csv
import datetime
import pytz
import paramiko

env = environ.Env()
environ.Env.read_env(os.path.join('', '.env'))
SFTP_HOST = env.get_value('SFTP_HOST')
SFTP_USERNAME = env.get_value('SFTP_USERNAME')
SFTP_PASSWORD = env.get_value('SFTP_PASSWORD')


class handler(BaseHTTPRequestHandler):

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers',
                         'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version')
        self.end_headers()
        return

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        request_body = self.rfile.read(content_length).decode('utf-8')

        self.uploadToSFTP(json.loads(request_body)['conversation'])

        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        return

    def convertDataToCSV(self, data):
        csv_rows = []
        for row in data:
            csv_rows.append(','.join(row))
        csv_content = '\n'.join(csv_rows)
        return csv_content

    def uploadToSFTP(self, conversation):
        data = conversation['data']
        message = conversation['message']
        user = conversation['user']

        now = datetime.datetime.now(pytz.timezone("America/New_York"))
        date = now.strftime("%d/%m/%Y")
        time = now.strftime("%H:%M")

        if "Same Billing Address" in data:
            same_billing = "Y"
        else:
            same_billing = "N"

        class My_Connection(pysftp.Connection):
            def __init__(self, *args, **kwargs):
                try:
                    if kwargs.get('cnopts') is None:
                        kwargs['cnopts'] = pysftp.CnOpts()
                except pysftp.HostKeysException as e:
                    self._init_error = True
                    raise paramiko.ssh_exception.SSHException(str(e))
                else:
                    self._init_error = False

                self._sftp_live = False
                self._transport = None
                super().__init__(*args, **kwargs)

            def __del__(self):
                if not self._init_error:
                    self.close()

        cnopts = pysftp.CnOpts()
        cnopts.hostkeys = None
        with My_Connection(
            host=SFTP_HOST,
            port=22,
            username=SFTP_USERNAME,
            password=SFTP_PASSWORD,
            cnopts=cnopts
        ) as sftp:

            with sftp.cd('SRs'):

                filename = f"{data.get('Vehicle Type', '')}-{now.strftime('%Y-%m-%d')}-{now.strftime('%H-%M')}.csv"

                with sftp.open(filename, 'w') as file:
                    writer = csv.DictWriter(
                        file, fieldnames=['field_name', 'field_data'])

                    writer.writerow(
                        {'field_name': 'SR_STAGE_ID', 'field_data': '12345'})
                    writer.writerow(
                        {'field_name': 'SR_DATE_SUBMITTED', 'field_data': f"{date} {time}"})
                    writer.writerow(
                        {'field_name': 'CREATION_DATE', 'field_data': f"{date} {time}"})
                    writer.writerow({'field_name': 'CREATED_BY',
                                    'field_data': "Service-Ridefox Shopify"})
                    writer.writerow(
                        {'field_name': 'LAST_UPDATE_DATE', 'field_data': f"{date} {time}"})
                    writer.writerow(
                        {'field_name': 'LAST_UPDATED_BY', 'field_data': ""})
                    writer.writerow(
                        {'field_name': 'LEGACY_CUST_ACCOUNT_NUMBER', 'field_data': ""})
                    writer.writerow(
                        {'field_name': 'EBS_CUST_ACCOUNT_NUMBER', 'field_data': ""})
                    writer.writerow(
                        {'field_name': 'PARTY_TYPE', 'field_data': ""})
                    writer.writerow(
                        {'field_name': 'SHOP_NAME', 'field_data': ""})
                    writer.writerow(
                        {'field_name': 'PERSON_FIRST_NAME', 'field_data': f"{data.get('First Name', '')}"})
                    writer.writerow(
                        {'field_name': 'PERSON_LAST_NAME', 'field_data': f"{data.get('Last Name', '')}"})
                    writer.writerow(
                        {'field_name': 'SALES_CHANNEL', 'field_data': "Service"})
                    writer.writerow(
                        {'field_name': 'BILL_TO_ADDRESS1', 'field_data': f"{data.get('Address 1', '')}"})
                    writer.writerow(
                        {'field_name': 'BILL_TO_ADDRESS2', 'field_data': f"{data.get('Address 2', '')}"})
                    writer.writerow(
                        {'field_name': 'BILL_TO_ADDRESS3', 'field_data': ""})
                    writer.writerow(
                        {'field_name': 'BILL_TO_ADDRESS4', 'field_data': ""})
                    writer.writerow(
                        {'field_name': 'BILL_TO_CITY', 'field_data': f"{data.get('City', '')}"})
                    writer.writerow(
                        {'field_name': 'BILL_TO_STATE', 'field_data': f"{data.get('State', '')}"})
                    writer.writerow(
                        {'field_name': 'BILL_TO_POSTAL_CODE', 'field_data': f"{data.get('Zip Code', '')}"})
                    writer.writerow(
                        {'field_name': 'BILL_TO_COUNTY', 'field_data': ""})
                    writer.writerow(
                        {'field_name': 'BILL_TO_PROVINCE', 'field_data': ""})
                    writer.writerow(
                        {'field_name': 'BILL_TO_COUNTRY', 'field_data': f"{data.get('Country', '')}"})
                    writer.writerow(
                        {'field_name': 'SHIP_TO_SAME_AS_BILL_TO', 'field_data': f"{same_billing}"})
                    writer.writerow(
                        {'field_name': 'SHIP_TO_ADDRESS1', 'field_data': f"{data.get('Address 1', '')}"})
                    writer.writerow(
                        {'field_name': 'SHIP_TO_ADDRESS2', 'field_data': f"{data.get('Address 2', '')}"})
                    writer.writerow(
                        {'field_name': 'SHIP_TO_ADDRESS3', 'field_data': ""})
                    writer.writerow(
                        {'field_name': 'SHIP_TO_ADDRESS4', 'field_data': ""})
                    writer.writerow(
                        {'field_name': 'SHIP_TO_CITY', 'field_data': f"{data.get('City', '')}"})
                    writer.writerow(
                        {'field_name': 'SHIP_TO_STATE', 'field_data': f"{data.get('State', '')}"})
                    writer.writerow(
                        {'field_name': 'SHIP_TO_POSTAL_CODE', 'field_data': f"{data.get('Zip Code', '')}"})
                    writer.writerow(
                        {'field_name': 'SHIP_TO_COUNTY', 'field_data': ""})
                    writer.writerow(
                        {'field_name': 'SHIP_TO_PROVINCE', 'field_data': ""})
                    writer.writerow(
                        {'field_name': 'SHIP_TO_COUNTRY', 'field_data': f"{data.get('Country', '')}"})
                    writer.writerow(
                        {'field_name': 'PERSON_PHONE_LINE_TYPE', 'field_data': "GEN"})
                    writer.writerow(
                        {'field_name': 'PERSON_PHONE_AREA_CODE', 'field_data': f"{data.get('Phone', '')[0:3]}"})
                    writer.writerow(
                        {'field_name': 'PERSON_PHONE_NUMBER', 'field_data': f"{data.get('Phone', '')[3:]}"})
                    writer.writerow(
                        {'field_name': 'PERSON_PHONE_EXTENSION', 'field_data': ""})
                    writer.writerow(
                        {'field_name': 'PERSON_EMAIL_ADDRESS', 'field_data': f"{user.get('email', '')}"})
                    writer.writerow(
                        {'field_name': 'CARD_HOLDER_PARTY_NAME', 'field_data': f"{user.get('name', '')}"})
                    writer.writerow(
                        {'field_name': 'TOKENIZED_CARD_NUMBER', 'field_data': f"{data.get('Credit Card Number', '')}"})
                    writer.writerow(
                        {'field_name': 'CARD_EXPIRATION_DATE', 'field_data': f"{data.get('Expires', '')}"})
                    writer.writerow(
                        {'field_name': 'CARD_DESCRIPTION', 'field_data': ""})
                    writer.writerow(
                        {'field_name': 'PROBLEM_SUMMARY', 'field_data': f"{message.get('body', '')}"})
                    writer.writerow(
                        {'field_name': 'SEVERITY_ID', 'field_data': ""})
                    writer.writerow(
                        {'field_name': 'URGENCY_ID', 'field_data': ""})
                    writer.writerow(
                        {'field_name': 'STATUS_ID', 'field_data': ""})
                    writer.writerow(
                        {'field_name': 'PUBLISH_FLAG', 'field_data': ""})
                    writer.writerow(
                        {'field_name': 'SERVICE_REQUEST_TYPE', 'field_data': "Fox Warranty Service"})
                    writer.writerow(
                        {'field_name': 'CUST_PO_NUMBER', 'field_data': ""})
                    writer.writerow(
                        {'field_name': 'ORACLE_INV_ORGN_CODE', 'field_data': ""})
                    writer.writerow(
                        {'field_name': 'ORACLE_INV_ITEM_NAME', 'field_data': ""})
                    writer.writerow({'field_name': 'BIKE_YEAR',
                                    'field_data': f"{data.get('Behicle Year', '')}"})
                    writer.writerow(
                        {'field_name': 'BIKE_MFG_BY', 'field_data': f"{data.get('Behicle Manufacturer', '')}"})
                    writer.writerow({'field_name': 'BIKE_MODEL',
                                    'field_data': f"{data.get('Behicle Model', '')}"})
                    writer.writerow(
                        {'field_name': 'SERIAL_NUMBER', 'field_data': f"{data.get('sn', '')}"})
                    writer.writerow(
                        {'field_name': 'RIDER_WEIGHT', 'field_data': f"{data.get('Rider Weight Unit', '')}"})
                    writer.writerow(
                        {'field_name': 'SERVICE_PRIORITY', 'field_data': ""})
                    writer.writerow(
                        {'field_name': 'WARRANTY_EVALUATION', 'field_data': ""})
                    writer.writerow(
                        {'field_name': 'CRANK_ARM_LENGTH', 'field_data': ""})
                    writer.writerow(
                        {'field_name': 'CRANKARM_SIDE', 'field_data': ""})
                    writer.writerow(
                        {'field_name': 'SEATPOST_DIAMETER', 'field_data': ""})
                    writer.writerow(
                        {'field_name': 'SEATPOST_DROPPER_TRAVEL', 'field_data': ""})
                    writer.writerow(
                        {'field_name': 'SPINDLE_DIAMETER', 'field_data': ""})
                    writer.writerow(
                        {'field_name': 'SPINDLE_LENGTH', 'field_data': ""})
                    writer.writerow(
                        {'field_name': 'PRODUCT_DESCRIPTION', 'field_data': ""})
                    writer.writerow(
                        {'field_name': 'PRODUCT_ISSUE_DETAIL', 'field_data': f"{message.get('body', '')}"})
                    writer.writerow(
                        {'field_name': 'PRODUCT_TYPE', 'field_data': f"{data.get('Product Type', '')}"})
                    writer.writerow(
                        {'field_name': 'PRODUCT_BRAND', 'field_data': f"{data.get('Product Brand', '')}"})
                    writer.writerow(
                        {'field_name': 'PRODUCT_ITEM', 'field_data': ""})
                    writer.writerow(
                        {'field_name': 'PRODUCT_MODEL', 'field_data': f"{data.get('Product Model', '')}"})
                    writer.writerow(
                        {'field_name': 'PRODUCT_SERIES', 'field_data': f"{data.get('Product Series', '')}"})
                    writer.writerow(
                        {'field_name': 'BRING_BACK', 'field_data': ""})
                    writer.writerow(
                        {'field_name': 'FREIGHT_TERMS', 'field_data': ""})
                    writer.writerow(
                        {'field_name': 'SHIPPING_METHOD', 'field_data': ""})
                    writer.writerow(
                        {'field_name': 'PAYMENT_TERMS', 'field_data': ""})
                    writer.writerow(
                        {'field_name': 'CC_AUTHORIZATION_STATUS', 'field_data': "Y"})
                    writer.writerow(
                        {'field_name': 'SERVICE_DISCOUNT_REASON_CODE', 'field_data': ""})
                    writer.writerow(
                        {'field_name': 'AVAILABILITY_OVERRIDE', 'field_data': ""})
                    writer.writerow({'field_name': 'FILE_NAME',
                                    'field_data': f"{message.get('attachments', '')}"})
                    writer.writerow(
                        {'field_name': 'COMPLETE', 'field_data': ""})
                    writer.writerow(
                        {'field_name': 'EBS_SERVICE_REQUEST_NUMBER', 'field_data': ""})
                    writer.writerow(
                        {'field_name': 'EBS_RESULT_STATUS', 'field_data': ""})
                    writer.writerow(
                        {'field_name': 'EBS_RESULT_MSG', 'field_data': ""})
                    writer.writerow(
                        {'field_name': 'USERAGENT', 'field_data': ""})
