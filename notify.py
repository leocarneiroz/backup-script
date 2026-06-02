#!/usr/bin/env python3
"""

Notification module for sending alerts via webhook (Discord/Slack).
Supports enviroment variable and direct URL configuration.
"""

import os
import json
import logging
import requests

# Module-level logger
logger = logging.getLogger(__name__)


def send_webhook(message, url=None):
    """
    
    Sends a plain text message to a Discord/Slack webhook.
    
    Args:
        message: The message text to send (str)
        url: Webhook URL. If None, reads from WEBHOOK_URL enviroment variable.
        
    Returns:
        bool: True if message was sent successfully, False otherwise
    """

    url = url or os.getenv('WEBHOOK_URL')

    if not url:
        logger.warning('WEBHOOK_URL not set. Skipping notification.')
        print('WEBHOOK_URL not set. Skipping notification.')
        return False
    
    # Discord and Slackk both accept this JSON format

    payload = {'content': message}

    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status() # Raises an error for 4xx/5xx status codes
        logger.info(f'Notification sent successfully')
        return True
    except requests.exceptions.Timeout as e:
        logger.error('Webhook request failed: {e}')
        print(f'Notification failed: {e}')
        return False
    
def send_rich_notification(title, fields, url=None, color=65280):
    """
    
    Sends a rich embed message to Discord (Discord-specific feature).
    Falls back to plain text for Slack of if fields are empty.
    
    Args:
        tile: Embed title (str)
        fields: Dictionaty of {name: value} pairs to display
        url: Webhook URL
        color: Embed color as decimal integer (default: green)
        
    Returns:
        bool: True if sent successfully
    """

    url = url or os.getenv('WEBHOOK_URL')

    if not url:
        logger.warning('WEBHOOK_URL not set. Skipping rich notification')
        return False
    
    # Build embed fields
    embed_fields = []
    for name, value in fields.items():
        embed_fields.append({
            'name': name,
            'value': str(value),
            'inline': True
        })

    payload = {
        'embeds': [{
            'title': title,
            'fields': embed_fields,
            'color': color,
            'timestamp': __import__('datetime').datetime.now().isoformat()
        }]
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        logger.info('Rich notification sent')
        return True
    except requests.exception.RequestException as e:
        logger.error(f'Rich notification failed: {e}')
        # Fallback: try plain text
        plain_text = f"{title}\n" + "\n".join([f"{k}: {v}" for k, v in fields.items()])
        return send_webhook(plain_text, url)
    
# Quick test when run directly
if __name__ == '__main__':
    # Test plain message
    send_webhook('Test notification from backup script!')

    # Test rich embed
    send_rich_notification(
        title='Backup Script Test',
        fields={
            'Status': 'Testing',
            'Files': 3,
            'Size': '0.02 MB',
            'Duration': '0,5s'
        }
    )
