"""
Handler untuk /uploadhelp command.
Menampilkan help message untuk upload commands.
"""

import logging
from typing import Dict, Any
from utils.upload_formatter import UploadFormatter

logger = logging.getLogger(__name__)


class UploadHelpHandler:
    """Handler untuk menampilkan upload help message."""
    
    def __init__(self, client):
        """
        Initialize upload help handler.
        
        Args:
            client: Telethon client instance
        """
        self.client = client
    
    async def handle(self, parsed_command) -> Dict[str, Any]:
        """
        Handle /uploadhelp command.
        
        Args:
            parsed_command: Parsed command object
            
        Returns:
            Dict dengan success status dan message
        """
        try:
            return {
                'success': True,
                'message': UploadFormatter.format_help_message()
            }
            
        except Exception as e:
            logger.error(f"Error in upload help handler: {e}")
            return {
                'success': False,
                'message': f"Error: {str(e)}"
            }
