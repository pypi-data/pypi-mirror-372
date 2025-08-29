import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os

class Mailer:
    def __init__(self, env, recipient_emails, sender_email, sender_password):
        self.env = env
        self.recipient_emails = recipient_emails
        self.sender_email = sender_email
        self.smtp_user = sender_email
        self.smtp_password = sender_password

    def get_netsuite_env(self):
        if self.env == 'production':
            return 'Production'
        else:
            return 'Sandbox'

    def create_message(self, report, subject, body_text):
        msg = MIMEMultipart()
        msg['From'] = self.sender_email
        msg['To'] = ", ".join(self.recipient_emails)
        msg['Subject'] = subject

        body = MIMEText(body_text, 'html')
        msg.attach(body)

        if report:
            with open(report, 'rb') as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename={os.path.basename(report)}',
            )
            msg.attach(part)

        return msg

    def get_report_mail_body_text(self, period, business_unit):
        return(
            f"""
            <html>
              <body>
                <p>Dear Team,</p>
                <p>Please find attached the CSV report for <strong>{period}</strong>.</p>
                <p>This report includes the revenue data for the {business_unit} business unit for the specified month. The data will also be uploaded to NetSuite {self.get_netsuite_env()} environment for <strong>{period}</strong>. </p>
                <p>Best regards,<br>Revenue Assurance Team</p>
              </body>
            </html>
            """
        )


    def get_failure_mail_body_text(self, missing_mappings, period):
        html_content = """\
        <html>
          <body style="font-family: Roboto, sans-serif; color: #333;">
            <table width="100%" cellpadding="0" cellspacing="0" border="0">
              <tr>
                <td style="padding: 20px;">
                  <p>Dear Team,</p>

                  <p>We have identified that some records are missing in NetSuite. Below is the list of affected records that need to be updated:</p>

                  <table width="100%" cellpadding="10" cellspacing="0" border="1" style="border-collapse: collapse; margin: 20px 0;">
                    <tr style="background-color: #f2f2f2;">
                      <th align="left">Record</th>
                      <th align="left">Missing Value</th>
                    </tr>"""

        for field, values in missing_mappings.items():
            for value in values:
                html_content += f"""
                    <tr>
                        <td>{field}</td>
                      <td>{value}</td>
                    </tr>
                """

        html_content += f"""\
                  </table>

                  <p>
                    We kindly request you to update the missing fields in the records as soon as possible. Once the updates are completed, please inform us so that we can manually rerun the workflow to process the updated records for {period}.
                  </p>

                  <p>
                    Should you require any assistance or have any questions, feel free
                    to reach out to our team.
                  </p>

                  <p>Thank you for your prompt attention to this matter.</p>

                  <p>Best regards,<br/>Revenue Assurance Team</p>
                </td>
              </tr>
            </table>
          </body>
        </html>
        """

        return html_content

    def get_success_mail_body_text(self, period, business_unit):
        return(
            f"""
            <html>
              <body>
                <p>Dear Team,</p>
                <p>The revenue data for the {business_unit} business unit for the month of <strong>{period}</strong> has been successfully processed and uploaded to NetSuite.</p>
                <p>Best regards,<br>Revenue Assurance Team</p>
              </body>
            </html>
            """
        )

    def send_email(self, message):
        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(self.smtp_user, self.smtp_password)
            server.sendmail(self.sender_email, self.recipient_emails, message.as_string())
            server.quit()
            print("Email sent successfully")
        except Exception as e:
            print(f"Failed to send email: {str(e)}")

    def send_revenue_report(self, report, period, business_unit):
        subject = f'Monthly {business_unit} Report - {period}'
        body_text = self.get_report_mail_body_text(period, business_unit)
        message = self.create_message(report, subject, body_text)
        self.send_email(message)

    def send_failure_notification(self, missing_mappings, period, business_unit):
        env = self.get_netsuite_env()
        subject = f'{business_unit} {env} NetSuite Pipeline Failure Notification - {period}'
        body_text = self.get_failure_mail_body_text(missing_mappings, period)
        message = self.create_message(None, subject, body_text)
        self.send_email(message)

    def send_success_notification(self, period, business_unit):
        env = self.get_netsuite_env()
        subject = f'{business_unit} {env} NetSuite Pipeline Success Notification - {period}'
        body_text = self.get_success_mail_body_text(period, business_unit)
        message = self.create_message(None, subject, body_text)
        self.send_email(message)
