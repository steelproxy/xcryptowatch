import postalsend
from log import postal_logger as logger

def send_analysis(analysis, config):
    logger.info(f"Sending analysis to Postal API...")
    logger.debug(f"Server: {postalsend._app._get_server()} Key: {postalsend._app._get_api_key()}")
    subject = config['postal']['subject']
    postalsend.push_send(subject, tag=None, plain_body=analysis, html_body=None, attachments=None)

def status_update(status):
    logger.info(f"Sending status update to Postal API...")
    logger.debug(f"Server: {postalsend._app._get_server()} Key: {postalsend._app._get_api_key()}")
    postalsend.push_send("XCryptoWatch Status Update", tag=None, plain_body=("STATUS UPDATE: " + status), html_body=None, attachments=None)