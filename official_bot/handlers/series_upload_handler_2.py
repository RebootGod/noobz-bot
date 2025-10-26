"""
Series Upload Handler (Part 2)
Handles episode status checking, bulk upload flow, and manual mode.
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes

from services.noobz_api_service_2 import NoobzApiServicePart2
from ui.messages import SeriesMessages, EpisodeMessages, ErrorMessages
from ui.keyboards_series import SeriesUploadKeyboards, EpisodeProgressKeyboards
from ui.formatters import SeriesFormatters, EpisodeFormatters, format_progress_bar
from utils.parsers import BulkUploadParser

logger = logging.getLogger(__name__)


class SeriesUploadHandlerPart2:
    """Handler for series upload operations - Part 2: Episode Status & Bulk Upload."""
    
    def __init__(self, main_handler):
        """
        Initialize part 2 handler.
        
        Args:
            main_handler: Reference to main SeriesUploadHandler instance
        """
        self.main_handler = main_handler
        self.session_service = main_handler.session_service
        self.tmdb_service = main_handler.tmdb_service
        self.context_service = main_handler.context_service
        self.noobz_api_service_2 = NoobzApiServicePart2()
        logger.info("SeriesUploadHandlerPart2 initialized")
    
    async def show_episode_status(
        self, 
        update: Update, 
        context: ContextTypes.DEFAULT_TYPE,
        tmdb_id: int,
        season_number: int
    ) -> None:
        """
        Show episode status for selected season.
        
        Args:
            update: Telegram update object
            context: Telegram context object
            tmdb_id: TMDB series ID
            season_number: Season number
        """
        try:
            query = update.callback_query
            
            # Fetch season data from TMDB
            season_data = await self.tmdb_service.get_season(tmdb_id, season_number)
            
            if not season_data:
                await query.edit_message_text(
                    ErrorMessages.api_error(),
                    parse_mode='HTML'
                )
                return
            
            # Get episode status from Noobz API
            status_result = await self.noobz_api_service_2.get_episodes_status(
                tmdb_id, 
                season_number
            )
            
            if not status_result['success']:
                await query.edit_message_text(
                    ErrorMessages.api_error(status_result.get('message')),
                    parse_mode='HTML'
                )
                return
            
            # Check if TMDB data available
            tmdb_available = status_result.get('tmdb_data_available', True)
            episodes = status_result.get('episodes', [])
            
            # Save episode list to context
            context.user_data['current_episodes'] = episodes
            context.user_data['current_season_data'] = season_data
            
            if not tmdb_available or len(episodes) == 0:
                # TMDB data incomplete - show manual mode option
                await self._show_manual_mode_option(query, context, tmdb_id, season_number)
                return
            
            # Format episode status display
            series_title = season_data.get('series_title', 'Series')
            status_text = f"📺 <b>{series_title} - Season {season_number}</b>\n"
            status_text += f"📊 {len(episodes)} Episodes\n\n"
            status_text += "<b>Status:</b>\n"
            
            complete_count = 0
            for ep in episodes[:10]:  # Show first 10
                status_emoji = EpisodeFormatters.get_episode_status_emoji(ep['status'])
                ep_title = ep.get('title', f"Episode {ep['episode_number']}")
                if len(ep_title) > 30:
                    ep_title = ep_title[:27] + "..."
                
                status_text += f"{status_emoji} E{ep['episode_number']:02d} - {ep_title}"
                
                if ep['status'] == 'complete':
                    complete_count += 1
                    status_text += " ✅\n"
                elif ep['status'] == 'needs_update':
                    status_text += " ⚠️\n"
                else:
                    status_text += " ❌\n"
            
            if len(episodes) > 10:
                status_text += f"\n<i>... and {len(episodes) - 10} more episodes</i>\n"
            
            # Progress bar
            progress = format_progress_bar(complete_count, len(episodes))
            status_text += f"\n{progress}"
            
            # Upload mode keyboard
            keyboard = SeriesUploadKeyboards.episode_status_actions(
                tmdb_id=tmdb_id,
                season_number=season_number
            )
            
            await query.edit_message_text(
                status_text,
                reply_markup=keyboard,
                parse_mode='HTML'
            )
            
            logger.info(
                f"Showed episode status for season {season_number} "
                f"(TMDB: {tmdb_id}, {complete_count}/{len(episodes)} complete)"
            )
            
        except Exception as e:
            logger.error(f"Error in show_episode_status: {e}", exc_info=True)
            await query.edit_message_text(
                ErrorMessages.generic_error(),
                parse_mode='HTML'
            )
    
    async def _show_manual_mode_option(
        self, 
        query, 
        context: ContextTypes.DEFAULT_TYPE,
        tmdb_id: int,
        season_number: int
    ) -> None:
        """
        Show manual mode option when TMDB data unavailable.
        
        Args:
            query: Callback query object
            context: Telegram context object
            tmdb_id: TMDB series ID
            season_number: Season number
        """
        season_context = self.context_service.get_context(
            query.from_user.id, 
            'season'
        )
        series_title = season_context.get('series_title', 'Series')
        
        msg = SeriesMessages.tmdb_data_unavailable(series_title, season_number)
        
        keyboard = SeriesUploadKeyboards.manual_mode_entry(tmdb_id, season_number)
        
        await query.edit_message_text(
            msg,
            reply_markup=keyboard,
            parse_mode='HTML'
        )
    
    async def prompt_bulk_upload(
        self, 
        update: Update, 
        context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """
        Prompt user for bulk episode upload input.
        
        Args:
            update: Telegram update object
            context: Telegram context object
        """
        try:
            query = update.callback_query
            await query.answer()
            
            # Parse callback data: bulk_upload_{tmdb_id}_{season_number}
            callback_parts = query.data.split('_')
            tmdb_id = int(callback_parts[2])
            season_number = int(callback_parts[3])
            
            # Get season context
            season_context = self.context_service.get_context(
                update.effective_user.id, 
                'season'
            )
            
            series_title = season_context.get('series_title', 'Series')
            
            # Set awaiting state
            context.user_data['awaiting_bulk_upload'] = True
            context.user_data['bulk_upload_tmdb_id'] = tmdb_id
            context.user_data['bulk_upload_season'] = season_number
            
            # Send instructions
            instructions = EpisodeMessages.bulk_upload_instructions(
                series_title, 
                season_number
            )
            
            await query.edit_message_text(
                instructions,
                parse_mode='HTML'
            )
            
            logger.info(
                f"User {update.effective_user.id} prompted for bulk upload "
                f"(TMDB: {tmdb_id}, Season: {season_number})"
            )
            
        except Exception as e:
            logger.error(f"Error in prompt_bulk_upload: {e}", exc_info=True)
            await update.callback_query.answer("❌ Error")
    
    async def handle_bulk_upload_input(
        self, 
        update: Update, 
        context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """
        Handle bulk upload input from user.
        
        Args:
            update: Telegram update object
            context: Telegram context object
        """
        try:
            # Check if we're expecting bulk upload
            if not context.user_data.get('awaiting_bulk_upload', False):
                return
            
            user = update.effective_user
            bulk_input = update.message.text.strip()
            
            tmdb_id = context.user_data.get('bulk_upload_tmdb_id')
            season_number = context.user_data.get('bulk_upload_season')
            
            # Delete user's message
            try:
                await update.message.delete()
            except Exception as e:
                logger.warning(f"Could not delete message: {e}")
            
            # Send validating message
            validating_msg = await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=EpisodeMessages.validating()
            )
            
            # Parse bulk input
            parsed_episodes = BulkUploadParser.parse_bulk_upload(bulk_input)
            
            if not parsed_episodes['valid']:
                # Validation errors
                error_msg = EpisodeMessages.validation_result(
                    parsed_episodes['valid_count'],
                    parsed_episodes['error_count'],
                    parsed_episodes['errors']
                )
                
                await validating_msg.edit_text(
                    error_msg,
                    parse_mode='HTML'
                )
                
                # Keep awaiting state for retry
                return
            
            # Get current episodes status
            current_episodes = context.user_data.get('current_episodes', [])
            
            # Build preview
            preview_text = EpisodeMessages.validation_result(
                parsed_episodes['valid_count'],
                0,
                []
            )
            
            preview_text += "\n\n<b>Preview:</b>\n"
            for ep_data in parsed_episodes['episodes'][:10]:
                ep_num = ep_data['episode_number']
                
                # Check if episode exists
                existing_ep = next(
                    (e for e in current_episodes if e['episode_number'] == ep_num),
                    None
                )
                
                if existing_ep and existing_ep['status'] == 'complete':
                    status = "Update (exists)"
                elif existing_ep:
                    status = "Update (no URLs)"
                else:
                    status = "New"
                
                preview_text += f"• E{ep_num:02d}: {status}\n"
            
            if len(parsed_episodes['episodes']) > 10:
                preview_text += f"<i>... and {len(parsed_episodes['episodes']) - 10} more</i>\n"
            
            # Save to context
            context.user_data['bulk_episodes_to_upload'] = parsed_episodes['episodes']
            context.user_data['awaiting_bulk_upload'] = False
            
            # Confirmation keyboard
            keyboard = EpisodeProgressKeyboards.bulk_upload_confirmation(
                tmdb_id, 
                season_number,
                len(parsed_episodes['episodes'])
            )
            
            await validating_msg.edit_text(
                preview_text,
                reply_markup=keyboard,
                parse_mode='HTML'
            )
            
            logger.info(
                f"User {user.id} bulk upload validated: "
                f"{parsed_episodes['valid_count']} episodes"
            )
            
        except Exception as e:
            logger.error(f"Error in handle_bulk_upload_input: {e}", exc_info=True)
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=ErrorMessages.generic_error()
            )
            context.user_data['awaiting_bulk_upload'] = False
    
    async def execute_bulk_upload(
        self, 
        update: Update, 
        context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """
        Execute bulk episode upload.
        
        Args:
            update: Telegram update object
            context: Telegram context object
        """
        try:
            query = update.callback_query
            await query.answer()
            
            user = update.effective_user
            
            # Parse callback data
            callback_parts = query.data.split('_')
            tmdb_id = int(callback_parts[3])
            season_number = int(callback_parts[4])
            
            episodes_to_upload = context.user_data.get('bulk_episodes_to_upload', [])
            
            if not episodes_to_upload:
                await query.answer("❌ No episodes to upload")
                return
            
            # Show uploading message
            await query.edit_message_text(
                "⏳ <b>Uploading episodes...</b>\n\nPlease wait...",
                parse_mode='HTML'
            )
            
            # Upload episodes
            total = len(episodes_to_upload)
            success_count = 0
            failed_episodes = []
            
            for idx, ep_data in enumerate(episodes_to_upload, 1):
                # Update progress
                progress = format_progress_bar(idx - 1, total)
                await query.edit_message_text(
                    f"⏳ <b>Uploading episodes...</b>\n{progress}\n\n"
                    f"Processing E{ep_data['episode_number']:02d}...",
                    parse_mode='HTML'
                )
                
                # Upload episode
                result = await self.noobz_api_service_2.create_episode(
                    tmdb_id=tmdb_id,
                    season_number=season_number,
                    episode_number=ep_data['episode_number'],
                    embed_url=ep_data['embed_url'],
                    download_url=ep_data.get('download_url')
                )
                
                if result['success']:
                    success_count += 1
                else:
                    failed_episodes.append({
                        'episode': ep_data['episode_number'],
                        'error': result.get('message', 'Unknown error')
                    })
            
            # Show summary
            summary_msg = EpisodeMessages.upload_summary(
                success_count, 
                len(failed_episodes),
                failed_episodes
            )
            
            keyboard = EpisodeProgressKeyboards.post_upload_actions(tmdb_id, season_number)
            
            await query.edit_message_text(
                summary_msg,
                reply_markup=keyboard,
                parse_mode='HTML'
            )
            
            # Clear upload data
            context.user_data.pop('bulk_episodes_to_upload', None)
            
            logger.info(
                f"User {user.id} bulk upload completed: "
                f"{success_count}/{total} successful"
            )
            
        except Exception as e:
            logger.error(f"Error in execute_bulk_upload: {e}", exc_info=True)
            await query.edit_message_text(
                ErrorMessages.api_error(),
                parse_mode='HTML'
            )
