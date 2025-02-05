import postalsend
from xcryptowatch.log import postal_logger as logger

def send_analysis(analysis, config):
    logger.info(f"Sending analysis to Postal API...")
    logger.debug(f"Server: {postalsend._app._get_server()} Key: {postalsend._app._get_api_key()}")
    subject = config['postal']['subject']
    try:
        postalsend.push_send(subject, tag=None, plain_body=analysis, html_body=None, attachments=None)
    except postalsend.errors.PostalError as e:
        logger.error(f"Error sending analysis to Postal API: {e}")

def status_update(status):
    logger.info(f"Sending status update to Postal API...")
    logger.debug(f"Server: {postalsend._app._get_server()} Key: {postalsend._app._get_api_key()}")
    try:
        postalsend.push_send("XCryptoWatch Status Update", tag=None, plain_body=("STATUS UPDATE: " + status), html_body=None, attachments=None)
    except postalsend.errors.PostalError as e:
        logger.error(f"Error sending status update to Postal API: {e}")