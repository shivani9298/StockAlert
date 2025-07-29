import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from config import Config

class EmailNotifier:
    def __init__(self):
        self.smtp_server = Config.SMTP_SERVER
        self.smtp_port = Config.SMTP_PORT
        self.email_address = Config.EMAIL_ADDRESS
        self.email_password = Config.EMAIL_PASSWORD
        self.recipient_email = Config.RECIPIENT_EMAIL
    
    def send_alert(self, analysis):
        if not self._validate_config():
            print("Email configuration incomplete. Cannot send alert.")
            return False
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_address
            msg['To'] = self.recipient_email
            msg['Subject'] = self._create_subject(analysis)
            
            body = self._create_email_body(analysis)
            msg.attach(MIMEText(body, 'html'))
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_address, self.email_password)
                server.send_message(msg)
            
            print(f"Alert sent for {analysis['symbol']}: {analysis['signal']}")
            return True
            
        except Exception as e:
            print(f"Failed to send email alert: {e}")
            return False
    
    def send_daily_summary(self, all_analyses):
        if not self._validate_config():
            print("Email configuration incomplete. Cannot send summary.")
            print(f"Email address: {self.email_address}")
            print(f"Recipient: {self.recipient_email}")
            print(f"Password set: {'Yes' if self.email_password else 'No'}")
            return False
        
        try:
            print(f"Attempting to send email from {self.email_address} to {self.recipient_email}")
            
            msg = MIMEMultipart()
            msg['From'] = self.email_address
            msg['To'] = self.recipient_email
            msg['Subject'] = f"Daily Stock Market Summary - {datetime.now().strftime('%Y-%m-%d')}"
            
            body = self._create_summary_body(all_analyses)
            msg.attach(MIMEText(body, 'html'))
            
            print(f"Connecting to SMTP server: {self.smtp_server}:{self.smtp_port}")
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.set_debuglevel(1)  # Enable debug output
                print("Starting TLS...")
                server.starttls()
                print("Logging in...")
                server.login(self.email_address, self.email_password)
                print("Sending message...")
                server.send_message(msg)
            
            print("Daily summary sent successfully")
            return True
            
        except Exception as e:
            print(f"Failed to send daily summary: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _validate_config(self):
        return all([
            self.email_address,
            self.email_password,
            self.recipient_email,
            self.smtp_server,
            self.smtp_port
        ])
    
    def _create_subject(self, analysis):
        signal_emoji = "📈" if analysis['signal'] == 'BUY' else "📉" if analysis['signal'] == 'SELL' else "📊"
        confidence = analysis['confidence']
        
        return f"{signal_emoji} {analysis['signal']} Alert: {analysis['symbol']} ({confidence} Confidence)"
    
    def _create_email_body(self, analysis):
        signal_color = "#28a745" if analysis['signal'] == 'BUY' else "#dc3545" if analysis['signal'] == 'SELL' else "#6c757d"
        
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; margin: 20px;">
            <h2 style="color: {signal_color};">{analysis['signal']} Alert: {analysis['symbol']}</h2>
            
            <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 10px 0;">
                <h3>Current Market Data</h3>
                <p><strong>Symbol:</strong> {analysis['symbol']}</p>
                <p><strong>Current Price:</strong> ${analysis['current_price']:.2f}</p>
                <p><strong>Change:</strong> <span style="color: {'#28a745' if analysis['change_percent'] >= 0 else '#dc3545'};">
                    {analysis['change_percent']:+.2f}%</span></p>
                <p><strong>Signal:</strong> <span style="color: {signal_color}; font-weight: bold;">
                    {analysis['signal']}</span></p>
                <p><strong>Confidence:</strong> {analysis['confidence']}</p>
            </div>
            
            <div style="background-color: #e9ecef; padding: 15px; border-radius: 5px; margin: 10px 0;">
                <h3>Analysis Reasons</h3>
                <ul>
        """
        
        for reason in analysis['reasons']:
            html += f"<li>{reason}</li>"
        
        if 'technical_signals' in analysis and analysis['technical_signals']:
            html += "</ul><h4>Technical Indicators</h4><ul>"
            for signal in analysis['technical_signals']:
                html += f"<li>{signal}</li>"
        
        html += f"""
                </ul>
            </div>
            
            <div style="margin-top: 20px; font-size: 12px; color: #6c757d;">
                <p>Alert generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p><em>This is an automated alert. Please do your own research before making investment decisions.</em></p>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _create_summary_body(self, all_analyses):
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; margin: 20px;">
            <h2>Daily Stock Market Summary</h2>
            <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            
            <table style="border-collapse: collapse; width: 100%; margin: 20px 0;">
                <thead>
                    <tr style="background-color: #f8f9fa;">
                        <th style="border: 1px solid #dee2e6; padding: 10px; text-align: left;">Symbol</th>
                        <th style="border: 1px solid #dee2e6; padding: 10px; text-align: right;">Price</th>
                        <th style="border: 1px solid #dee2e6; padding: 10px; text-align: right;">Change %</th>
                        <th style="border: 1px solid #dee2e6; padding: 10px; text-align: center;">Signal</th>
                        <th style="border: 1px solid #dee2e6; padding: 10px; text-align: center;">Confidence</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for symbol, analysis in all_analyses.items():
            if analysis:
                signal_color = "#28a745" if analysis['signal'] == 'BUY' else "#dc3545" if analysis['signal'] == 'SELL' else "#6c757d"
                change_color = "#28a745" if analysis['change_percent'] >= 0 else "#dc3545"
                
                html += f"""
                    <tr>
                        <td style="border: 1px solid #dee2e6; padding: 10px;">{analysis['symbol']}</td>
                        <td style="border: 1px solid #dee2e6; padding: 10px; text-align: right;">${analysis['current_price']:.2f}</td>
                        <td style="border: 1px solid #dee2e6; padding: 10px; text-align: right; color: {change_color};">
                            {analysis['change_percent']:+.2f}%</td>
                        <td style="border: 1px solid #dee2e6; padding: 10px; text-align: center; color: {signal_color}; font-weight: bold;">
                            {analysis['signal']}</td>
                        <td style="border: 1px solid #dee2e6; padding: 10px; text-align: center;">{analysis['confidence']}</td>
                    </tr>
                """
        
        html += """
                </tbody>
            </table>
            
            <div style="margin-top: 20px; font-size: 12px; color: #6c757d;">
                <p><em>This is an automated summary. Please do your own research before making investment decisions.</em></p>
            </div>
        </body>
        </html>
        """
        
        return html