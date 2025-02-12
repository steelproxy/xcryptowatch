import postalsend
import asyncio
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from xcryptowatch.config_json import postal_enabled, smtp_enabled
from xcryptowatch.log import postal_logger as logger


async def send_analysis(analysis, config):
    subject = config['email'].get('subject', 'XCryptoWatch Analysis')
    if postal_enabled(config):
        logger.info(f"Sending analysis to Postal API...")
        logger.debug(f"Server: {postalsend._app._get_server()} Key: {postalsend._app._get_api_key()}")
        try:
            await asyncio.to_thread(
                postalsend.push_send,
                subject, 
                tag=None, 
                plain_body=analysis, 
                html_body=None, 
                attachments=None
            )
        except postalsend.errors.PostalError as e:
            logger.error(f"Error sending analysis to Postal API: {e}")
    if smtp_enabled(config):
        logger.info(f"Sending analysis to SMTP server...")
        logger.debug(f"Server: {config['email']['smtp']['host']} Port: {config['email']['smtp']['port']} Username: {config['email']['smtp']['username']}")
        try:
            msg = MIMEMultipart()
            msg['From'] = config['email']['from_email']
            msg['To'] = ', '.join(config['email']['to_email'])
            msg['Subject'] = subject
            msg.attach(MIMEText(analysis, 'plain'))

            await asyncio.to_thread(
                _send_smtp_email,
                config['email']['smtp'],
                msg
            )
        except Exception as e:
            logger.error(f"Error sending analysis via SMTP: {e}")


async def status_update(status, config):
    subject = "XCryptoWatch Status Update"
    if postal_enabled(config):
        logger.info(f"Sending status update to Postal API...")
        logger.debug(f"Server: {postalsend._app._get_server()} Key: {postalsend._app._get_api_key()}")
        try:
            await asyncio.to_thread(
                postalsend.push_send,
                subject,
                tag=None, 
                plain_body=("STATUS UPDATE: " + status),
                html_body=None, 
                attachments=None
            )
        except postalsend.errors.PostalError as e:
            logger.error(f"Error sending status update to Postal API: {e}")
    elif smtp_enabled(config):
        logger.info(f"Sending status update to SMTP server...")
        try:
            msg = MIMEMultipart()
            msg['From'] = config['email']['from_email']
            msg['To'] = ', '.join(config['email']['to_email'])
            msg['Subject'] = subject
            msg.attach(MIMEText("STATUS UPDATE: " + status, 'plain'))

            await asyncio.to_thread(
                _send_smtp_email,
                config['email']['smtp'],
                msg
            )
        except Exception as e:
            logger.error(f"Error sending status update via SMTP: {e}")


def _send_smtp_email(smtp_config, msg):
    """Helper function to send email via SMTP"""
    with smtplib.SMTP(smtp_config['host'], smtp_config['port']) as server:
        if smtp_config['use_tls']:
            server.starttls()
        if smtp_config['username'] and smtp_config['password']:
            server.login(smtp_config['username'], smtp_config['password'])
        server.send_message(msg)