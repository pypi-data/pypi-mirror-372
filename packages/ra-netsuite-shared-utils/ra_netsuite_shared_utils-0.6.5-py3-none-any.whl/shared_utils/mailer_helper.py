import requests
from datetime import datetime, timezone

class MailerHelper:
    def __init__(self, env, daakiya_url, bundle_uuid, sender_email_id, recipient_emails):
        self.env = env
        self.daakiya_url = daakiya_url
        self.bundle_uuid = bundle_uuid
        self.sender_email_id = sender_email_id
        self.recipient_emails = recipient_emails

    def send_email(self, bucket_name, object_key, subject, body):
        try:
            url = self.daakiya_url
            headers = {"Content-Type": "application/json"}
            payload = {
                "event_type": "publish_event",
                "bundle": {
                    "bundle_type": "direct_bundle",
                    "bundle_uuid": self.bundle_uuid,
                    "request_ts": int(datetime.now(timezone.utc).timestamp() * 1000),
                    "mail_packet": {
                        "packet_type": "solo_packet",
                        "sender_mail_id": self.sender_email_id,
                        "receivers_mail_id_info": {
                            "to": self.recipient_emails,
                            "cc": [],
                            "bcc": []
                        },
                        "subject": subject,
                        "body": {
                            "body_type": "file_attachment_body",
                            "content": {
                                "content_type": "html",
                                "html_content": body
                            }
                        }
                    }
                }
            }

            if bucket_name and object_key:
                payload["bundle"]["mail_packet"]["body"]["attachments"] = [
                    {
                        "location": {
                            "storage_provider": "GCS",
                            "bucket": bucket_name,
                            "key": object_key
                        }
                    }
                ]

            response = requests.post(url, headers=headers, json=payload)

            if not response.ok:
                print(f"Error response from server: {response.text}")

            response.raise_for_status()
            print(f"Email sent successfully: {response.text}")

        except requests.exceptions.RequestException as req_error:
            print(f"Failed to send email: {req_error}")
            print(f"Response content: {req_error.response.text if hasattr(req_error, 'response') else 'No response content'}")
            raise RuntimeError(f"Error sending email: {req_error}")

    def get_missing_mappings_subject(self, env, business_unit, execution_date,  period):
        return f"{business_unit} {env} NetSuite Pipeline Failure Notification - {execution_date} - {period}"

    def get_failure_subject(self, env, business_unit):
        return f"{env.capitalize()} {business_unit} Pipeline Failed"

    def get_revenue_report_subject(self, business_unit, execution_date, posting_period_val):
        return f"Daily {business_unit} Report for execution date - {execution_date}, period - {posting_period_val}"

    def get_missing_mappings_body(self, missing_mappings,  period):
        body = f"""\
        <html>
          <body style="font-family: Roboto, sans-serif; color: #333;">
            <table width="100%" cellpadding="0" cellspacing="0" border="0">
              <tr>
                <td style="padding: 20px;">
                  <p>Dear Team,</p>

                  <p>We have identified missing mappings in the system for the specified posting period <strong>{period}</strong>. 
                  Kindly review the details below:</p>

                  <table width="100%" cellpadding="10" cellspacing="0" border="1" style="border-collapse: collapse; margin: 20px 0;">
                    <tr style="background-color: #f2f2f2;">
                      <th align="left">Field</th>
                      <th align="left">Missing Value</th>
                    </tr>"""

        for field, values in missing_mappings.items():
            for value in values:
                body += f"""\
                    <tr>
                      <td>{field}</td>
                      <td>{value}</td>
                    </tr>"""

        body += f"""\
                  </table>

                  <p><strong>Action Required:</strong> Please update the missing fields at the earliest. 
                  Once done, notify us to manually rerun the workflow for <strong>{period}</strong>.</p>

                  <p>For any assistance or queries, feel free to reach out to the Revenue Assurance Team.</p>

                  <p>Thank you for your prompt attention.</p>

                  <p>Best regards,<br/>
                  <strong>Revenue Assurance Team</strong></p>
                </td>
              </tr>
            </table>
          </body>
        </html>
        """
        return body

    def get_failure_body(self, error_message, business_unit):
        return f"""<html>
        <body>
            <p>An error occurred while executing the {business_unit} Pipeline:</p>
            <pre>{error_message}</pre>
            <p>Please check logs for more information.</p>
        </body>
    </html>"""
 
    def get_revenue_report_body(self, env, business_unit, execution_date, period):
        env_context = "NetSuite Production" if env.lower() == "production" else "NetSuite Sandbox"
        return f"""<html>
        <body>
           <p>Dear Team,</p>
           <p>The revenue data for the {business_unit} business unit for the date of <strong>{execution_date}</strong>, in the period of <strong>{period}</strong> has been successfully processed and uploaded to {env_context}.</p>
           <p>Best regards,<br>Revenue Assurance Team</p>
        </body>
    </html>"""

    def get_success_subject(self, env, business_unit, execution_date, period):
        return f"{business_unit} {env} NetSuite Pipeline Success Notification - Execution Date - {execution_date} - Period - {period}"

    def get_success_body(self, env, business_unit, execution_date, period):
        env_context = "NetSuite Production" if env.lower() == "production" else "NetSuite Sandbox"
        return f"""<html>
        <body>
            <p>Dear Team,</p>
            <p>The revenue data for the {business_unit} business unit for the date of <strong>{execution_date}</strong>, in the period of <strong>{period}</strong> has been successfully processed and uploaded to {env_context}.</p>
            <p>Best regards,<br>Revenue Assurance Team</p>
        </body>
    </html>"""

    def send_job_success_mail(self, job_id, execution_date, business_unit, subsidiary=None):
        try:
            subsidiary_info = f" - {subsidiary}" if subsidiary else ""
            subject = f"{self.env.upper()} {business_unit} NetSuite Pipeline Success Notification{subsidiary_info} - {execution_date}"
            body = f"""<html>
            <body>
                <p>Dear Team,</p>
                <p>The revenue data for the <strong>{business_unit}</strong> business unit<strong>{subsidiary_info}</strong> (job id: {job_id}) for the date of <strong>{execution_date}</strong> has been successfully processed and uploaded to NetSuite.</p>
                <p>Best regards,<br>Revenue Assurance Team</p>
            </body>
            </html>"""
            
            self.send_email(None, None, subject, body)
            print(f"Success notification sent for completed job {job_id}{subsidiary_info}")
            return True
            
        except Exception as mail_error:
            print(f"Error sending success notification email: {mail_error}")
            return False

    def send_job_failure_mail(self, job_id, execution_date, business_unit, subsidiary=None):
        try:
            subsidiary_info = f" - {subsidiary}" if subsidiary else ""
            subject = f"{self.env.upper()} {business_unit} NetSuite Pipeline Failure Notification{subsidiary_info} - {execution_date}"
            body = f"""<html>
            <body>
                <p>Dear Team,</p>
                <p>NetSuite pipeline<strong>{subsidiary_info}</strong> (job id: {job_id}) has failed for execution date <strong>{execution_date}</strong>. Please investigate the failure in NetSuite.</p>
                <p>Best regards,<br>Revenue Assurance Team</p>
            </body>
            </html>"""
            
            self.send_email(None, None, subject, body)
            print(f"Failure notification sent for failed job {job_id}{subsidiary_info}")
            return True
            
        except Exception as mail_error:
            print(f"Error sending failure email: {mail_error}")
            return False

    def send_job_timeout_mail(self, job_id, execution_date, business_unit, subsidiary=None):
        try:
            subsidiary_info = f" - {subsidiary}" if subsidiary else ""
            subject = f"{self.env.upper()} {business_unit} NetSuite Pipeline Timeout Notification{subsidiary_info} - {execution_date}"
            body = f"""<html>
            <body>
                <p>Dear Team,</p>
                <p>NetSuite pipeline<strong>{subsidiary_info}</strong> (job id: {job_id}) is still in progress after 30 minutes of monitoring for execution date <strong>{execution_date}</strong>. Please manually check the pipeline status in NetSuite.</p>
                <p>Best regards,<br>Revenue Assurance Team</p>
            </body>
            </html>"""
            
            self.send_email(None, None, subject, body)
            print(f"Timeout notification sent for job {job_id}{subsidiary_info}")
            return True
            
        except Exception as mail_error:
            print(f"Error sending timeout notification email: {mail_error}")
            return False

    def send_job_monitor_error_mail(self, job_id, execution_date, error_message, business_unit, subsidiary=None):
        try:
            subsidiary_info = f" - {subsidiary}" if subsidiary else ""
            subject = f"{self.env.upper()} {business_unit} NetSuite Pipeline Error Notification{subsidiary_info}"
            body = f"""<html>
            <body>
                <p>Dear Team,</p>
                <p>An error occurred while monitoring NetSuite pipeline<strong>{subsidiary_info}</strong> (job id: {job_id}) for execution date <strong>{execution_date}</strong>.</p>
                <p>Error: {error_message}</p>
                <p>Please investigate the pipeline monitor function logs.</p>
                <p>Best regards,<br>Revenue Assurance Team</p>
            </body>
            </html>"""
            
            self.send_email(None, None, subject, body)
            print(f"Error notification sent for job monitor failure on job {job_id}{subsidiary_info}")
            return True
            
        except Exception as mail_error:
            print(f"Error sending error notification email: {mail_error}")
            return False
