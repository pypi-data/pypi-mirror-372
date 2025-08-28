"""
Slack integration tools for comprehensive workspace interaction.
Supports messaging, search, user management, and file operations.
"""

import json
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union

from langchain_core.tools import tool
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from broadie.config.integrations import get_integrations_config
from broadie.utils.exceptions import ToolError


def _get_slack_client() -> WebClient:
    """Get authenticated Slack client using bot token."""
    try:
        # Get configuration
        config = get_integrations_config()

        if not config.is_slack_configured():
            raise ToolError(
                "Slack not configured. Set SLACK_BOT_TOKEN environment variable. "
                "See setup instructions: python -c \"from broadie.core.tool_configurator import show_setup_instructions; show_setup_instructions('slack')\""
            )

        token = config.slack.bot_token
        if not token.startswith("xoxb-"):
            raise ToolError(
                "Invalid Slack token format. Bot tokens should start with 'xoxb-'. "
                "Get your bot token from https://api.slack.com/apps"
            )

        client = WebClient(token=token)
        # Test the connection
        client.auth_test()
        return client

    except SlackApiError as e:
        if e.response["error"] == "invalid_auth":
            raise ToolError(
                "Invalid Slack bot token. Please check your SLACK_BOT_TOKEN."
            )
        raise ToolError(f"Slack authentication failed: {e.response['error']}")
    except Exception as e:
        if "not configured" in str(e) or "Invalid Slack token" in str(e):
            raise e
        raise ToolError(f"Failed to connect to Slack: {str(e)}")


@tool(
    description="""Search across all Slack messages, channels, and conversations for relevant information.
Supports advanced search with filters, date ranges, and user-specific queries.

Example usage:
- search_slack_messages("project deadline")  # Find messages about project deadlines
- search_slack_messages("budget", channel="finance", days_back=30)  # Search finance channel, last 30 days
- search_slack_messages("meeting notes", from_user="john.doe")  # Messages from specific user
- search_slack_messages("error 404", in_channels=["dev-team", "bugs"])  # Search multiple channels

Perfect for: finding past discussions, locating decisions, gathering context, research."""
)
def search_slack_messages(
    query: str,
    channel: Optional[str] = None,
    from_user: Optional[str] = None,
    days_back: int = 30,
    in_channels: Optional[List[str]] = None,
    limit: int = 20,
) -> str:
    """
    Search Slack messages across workspace.

    Args:
        query: Search terms (supports Slack search syntax)
        channel: Channel name to search in (without #)
        from_user: Username or display name to search messages from
        days_back: How many days back to search (default 30)
        in_channels: List of channel names to search in
        limit: Maximum results to return

    Returns:
        Formatted search results with message content, authors, channels, and timestamps
    """
    try:
        client = _get_slack_client()

        # Build search query using Slack search syntax
        search_parts = [query]

        if channel:
            search_parts.append(f"in:#{channel}")
        elif in_channels:
            channel_filters = " OR ".join([f"in:#{ch}" for ch in in_channels])
            search_parts.append(f"({channel_filters})")

        if from_user:
            search_parts.append(f"from:@{from_user}")

        if days_back:
            date_filter = (datetime.now() - timedelta(days=days_back)).strftime(
                "%Y-%m-%d"
            )
            search_parts.append(f"after:{date_filter}")

        full_query = " ".join(search_parts)

        # Execute search
        response = client.search_messages(
            query=full_query, count=limit, sort="timestamp"
        )

        if not response["ok"]:
            return f"Search failed: {response.get('error', 'Unknown error')}"

        messages = response["messages"]["matches"]

        if not messages:
            return f"No messages found for query: '{query}'"

        # Format results
        output = f"Found {len(messages)} messages for '{query}':\n"
        output += "=" * 60 + "\n\n"

        for i, msg in enumerate(messages, 1):
            # Get message details
            text = msg.get("text", "No content")
            user_info = msg.get("user", {})
            username = user_info.get("name", "Unknown User")

            # Format timestamp
            try:
                timestamp = float(msg.get("ts", 0))
                time_str = datetime.fromtimestamp(timestamp).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            except:
                time_str = "Unknown time"

            # Get channel info
            channel_info = msg.get("channel", {})
            channel_name = channel_info.get("name", "Unknown Channel")

            # Format message preview (truncate if too long)
            if len(text) > 200:
                text_preview = text[:197] + "..."
            else:
                text_preview = text

            output += f"{i}. #{channel_name} - {time_str}\n"
            output += f"   👤 {username}\n"
            output += f"   💬 {text_preview}\n"

            # Add permalink if available
            if msg.get("permalink"):
                output += f"   🔗 {msg['permalink']}\n"

            output += "\n"

        return output.strip()

    except SlackApiError as e:
        return f"Slack API error: {e.response['error']}"
    except Exception as e:
        raise ToolError(f"Error searching Slack messages: {str(e)}")


@tool(
    description="""Send messages to Slack channels with rich formatting, mentions, and attachments.
Supports markdown formatting, user mentions, channel links, and threaded replies.

Example usage:
- send_slack_message("general", "Project update: Phase 1 complete! 🎉")
- send_slack_message("dev-team", "Deploy failed", thread_ts="1234567890.123")  # Reply to thread
- send_slack_message("alerts", "⚠️ Server down", mention_users=["admin", "devops"])
- send_slack_message("announcements", "*Important*: All hands meeting at 3pm")

Perfect for: status updates, alerts, announcements, team communication."""
)
def send_slack_message(
    channel: str,
    text: str,
    thread_ts: Optional[str] = None,
    mention_users: Optional[List[str]] = None,
    mention_channel: bool = False,
    blocks: Optional[List[Dict]] = None,
) -> str:
    """
    Send message to Slack channel.

    Args:
        channel: Channel name (without #) or channel ID
        text: Message text (supports Slack markdown)
        thread_ts: Timestamp of parent message to reply in thread
        mention_users: List of usernames to mention (@username)
        mention_channel: Whether to mention entire channel (@channel)
        blocks: Advanced Block Kit formatting (optional)

    Returns:
        Success message with message timestamp and channel info
    """
    try:
        client = _get_slack_client()

        # Add channel prefix if not present
        if not channel.startswith("#") and not channel.startswith("C"):
            channel = f"#{channel}"

        # Add mentions to text
        message_text = text
        if mention_users:
            mentions = " ".join([f"<@{user}>" for user in mention_users])
            message_text = f"{mentions} {message_text}"

        if mention_channel:
            message_text = f"<!channel> {message_text}"

        # Send message
        kwargs = {"channel": channel, "text": message_text}

        if thread_ts:
            kwargs["thread_ts"] = thread_ts

        if blocks:
            kwargs["blocks"] = blocks

        response = client.chat_postMessage(**kwargs)

        if not response["ok"]:
            return f"Failed to send message: {response.get('error', 'Unknown error')}"

        # Get channel name for response
        channel_info = response.get("channel", channel)
        message_ts = response.get("ts", "Unknown")

        thread_info = ""
        if thread_ts:
            thread_info = " (in thread)"

        return f"Message sent successfully to #{channel_info}{thread_info}!\nMessage ID: {message_ts}\n\nContent: {text[:100]}..."

    except SlackApiError as e:
        return f"Slack API error: {e.response['error']}"
    except Exception as e:
        raise ToolError(f"Error sending Slack message: {str(e)}")


@tool(
    description="""Send direct messages to Slack users privately for sensitive communications.
Supports user lookup by username, email, or display name.

Example usage:
- send_slack_dm("john.doe", "Hi John! Can we discuss the project timeline?")
- send_slack_dm("jane@company.com", "Your report is ready for review", by_email=True)
- send_slack_dm("U12345678", "Direct message using user ID")

Perfect for: private communications, sensitive information, personal follow-ups."""
)
def send_slack_dm(
    user: str, text: str, by_email: bool = False, blocks: Optional[List[Dict]] = None
) -> str:
    """
    Send direct message to Slack user.

    Args:
        user: Username, user ID, or email address
        text: Message content
        by_email: If True, lookup user by email address
        blocks: Advanced Block Kit formatting (optional)

    Returns:
        Success message with delivery confirmation
    """
    try:
        client = _get_slack_client()

        # Find user ID if not provided
        user_id = user
        if not user.startswith("U"):  # Not a user ID
            if by_email:
                # Lookup by email
                response = client.users_lookupByEmail(email=user)
                if response["ok"]:
                    user_id = response["user"]["id"]
                    username = response["user"]["name"]
                else:
                    return f"User not found with email: {user}"
            else:
                # Lookup by username
                users_response = client.users_list()
                if users_response["ok"]:
                    for member in users_response["members"]:
                        if (
                            member.get("name") == user
                            or member.get("real_name", "").lower() == user.lower()
                            or member.get("display_name", "").lower() == user.lower()
                        ):
                            user_id = member["id"]
                            username = member["name"]
                            break
                    else:
                        return f"User not found: {user}"
                else:
                    return f"Failed to lookup users: {users_response.get('error', 'Unknown error')}"
        else:
            username = user_id

        # Open DM conversation
        dm_response = client.conversations_open(users=[user_id])
        if not dm_response["ok"]:
            return f"Failed to open DM: {dm_response.get('error', 'Unknown error')}"

        dm_channel = dm_response["channel"]["id"]

        # Send message
        kwargs = {"channel": dm_channel, "text": text}

        if blocks:
            kwargs["blocks"] = blocks

        message_response = client.chat_postMessage(**kwargs)

        if not message_response["ok"]:
            return (
                f"Failed to send DM: {message_response.get('error', 'Unknown error')}"
            )

        return f"Direct message sent successfully to @{username}!\n\nContent: {text[:100]}..."

    except SlackApiError as e:
        return f"Slack API error: {e.response['error']}"
    except Exception as e:
        raise ToolError(f"Error sending Slack DM: {str(e)}")


@tool(
    description="""List all Slack channels in the workspace with metadata and member counts.
Helps agents understand workspace structure and find appropriate channels for communication.

Example usage:
- list_slack_channels()  # List all public channels
- list_slack_channels(include_private=True)  # Include private channels bot is member of
- list_slack_channels(show_members=True)  # Show member counts and purposes

Perfect for: workspace discovery, finding relevant channels, understanding team structure."""
)
def list_slack_channels(
    include_private: bool = False, show_members: bool = True, limit: int = 100
) -> str:
    """
    List Slack channels in workspace.

    Args:
        include_private: Include private channels (bot must be member)
        show_members: Show member count and channel purpose
        limit: Maximum channels to return

    Returns:
        Formatted list of channels with metadata
    """
    try:
        client = _get_slack_client()

        # Get channels
        types = "public_channel"
        if include_private:
            types += ",private_channel"

        response = client.conversations_list(
            types=types, limit=limit, exclude_archived=True
        )

        if not response["ok"]:
            return f"Failed to list channels: {response.get('error', 'Unknown error')}"

        channels = response["channels"]

        if not channels:
            return "No channels found."

        # Sort channels by member count (descending) or name
        if show_members:
            channels.sort(key=lambda x: x.get("num_members", 0), reverse=True)
        else:
            channels.sort(key=lambda x: x.get("name", ""))

        # Format output
        output = f"Found {len(channels)} channels:\n"
        output += "=" * 50 + "\n\n"

        for channel in channels:
            name = channel.get("name", "Unknown")
            channel_id = channel.get("id", "Unknown")
            is_private = channel.get("is_private", False)

            # Channel type indicator
            type_icon = "🔒" if is_private else "📢"

            output += f"{type_icon} #{name}\n"
            output += f"   ID: {channel_id}\n"

            if show_members:
                member_count = channel.get("num_members", 0)
                output += f"   👥 {member_count} members\n"

                # Channel purpose/topic
                purpose = channel.get("purpose", {}).get("value", "")
                topic = channel.get("topic", {}).get("value", "")

                if purpose:
                    output += (
                        f"   📝 Purpose: {purpose[:100]}...\n"
                        if len(purpose) > 100
                        else f"   📝 Purpose: {purpose}\n"
                    )
                elif topic:
                    output += (
                        f"   💭 Topic: {topic[:100]}...\n"
                        if len(topic) > 100
                        else f"   💭 Topic: {topic}\n"
                    )

            output += "\n"

        return output.strip()

    except SlackApiError as e:
        return f"Slack API error: {e.response['error']}"
    except Exception as e:
        raise ToolError(f"Error listing Slack channels: {str(e)}")


@tool(
    description="""List all users in the Slack workspace with profiles and status information.
Essential for user discovery, mentions, and understanding team structure.

Example usage:
- list_slack_users()  # List all active users
- list_slack_users(show_profiles=True)  # Include titles, emails, phone numbers
- list_slack_users(include_bots=True)  # Include bot users

Perfect for: finding team members, getting user IDs for mentions, directory lookup."""
)
def list_slack_users(
    show_profiles: bool = False, include_bots: bool = False, limit: int = 200
) -> str:
    """
    List users in Slack workspace.

    Args:
        show_profiles: Include profile information (title, email, phone)
        include_bots: Include bot users in results
        limit: Maximum users to return

    Returns:
        Formatted list of users with profile information
    """
    try:
        client = _get_slack_client()

        response = client.users_list(limit=limit)

        if not response["ok"]:
            return f"Failed to list users: {response.get('error', 'Unknown error')}"

        members = response["members"]

        # Filter users
        filtered_members = []
        for member in members:
            # Skip deleted users
            if member.get("deleted", False):
                continue

            # Skip bots unless requested
            if member.get("is_bot", False) and not include_bots:
                continue

            filtered_members.append(member)

        if not filtered_members:
            return "No users found."

        # Sort by real name or username
        filtered_members.sort(key=lambda x: x.get("real_name", x.get("name", "")))

        # Format output
        output = f"Found {len(filtered_members)} users:\n"
        output += "=" * 50 + "\n\n"

        for user in filtered_members:
            username = user.get("name", "Unknown")
            user_id = user.get("id", "Unknown")
            real_name = user.get("real_name", username)

            # Status indicators
            is_admin = user.get("is_admin", False)
            is_owner = user.get("is_owner", False)
            is_bot = user.get("is_bot", False)

            status_icons = []
            if is_owner:
                status_icons.append("👑")
            elif is_admin:
                status_icons.append("⭐")
            if is_bot:
                status_icons.append("🤖")

            status_str = " ".join(status_icons) + " " if status_icons else ""

            output += f"{status_str}👤 {real_name} (@{username})\n"
            output += f"   ID: {user_id}\n"

            if show_profiles:
                profile = user.get("profile", {})

                # Title/role
                title = profile.get("title", "")
                if title:
                    output += f"   💼 {title}\n"

                # Email
                email = profile.get("email", "")
                if email:
                    output += f"   📧 {email}\n"

                # Phone
                phone = profile.get("phone", "")
                if phone:
                    output += f"   📞 {phone}\n"

                # Status
                status_text = profile.get("status_text", "")
                status_emoji = profile.get("status_emoji", "")
                if status_text or status_emoji:
                    output += f"   💭 {status_emoji} {status_text}\n"

            output += "\n"

        return output.strip()

    except SlackApiError as e:
        return f"Slack API error: {e.response['error']}"
    except Exception as e:
        raise ToolError(f"Error listing Slack users: {str(e)}")


@tool(
    description="""Get detailed information about a specific Slack user including profile, status, and activity.
Perfect for user lookup before sending messages or gathering team member details.

Example usage:
- get_slack_user_info("john.doe")  # Get info by username
- get_slack_user_info("jane@company.com", by_email=True)  # Lookup by email
- get_slack_user_info("U12345678")  # Get info by user ID

Returns comprehensive profile including contact info, role, status, timezone."""
)
def get_slack_user_info(user: str, by_email: bool = False) -> str:
    """
    Get detailed information about a Slack user.

    Args:
        user: Username, user ID, or email address
        by_email: If True, lookup user by email address

    Returns:
        Detailed user profile information
    """
    try:
        client = _get_slack_client()

        # Find user
        if user.startswith("U"):
            # User ID provided
            response = client.users_info(user=user)
            if not response["ok"]:
                return f"User not found: {response.get('error', 'Unknown error')}"
            user_data = response["user"]
        elif by_email:
            # Email lookup
            response = client.users_lookupByEmail(email=user)
            if not response["ok"]:
                return f"User not found with email {user}: {response.get('error', 'Unknown error')}"
            user_data = response["user"]
        else:
            # Username lookup
            users_response = client.users_list()
            if not users_response["ok"]:
                return f"Failed to fetch users: {users_response.get('error', 'Unknown error')}"

            user_data = None
            for member in users_response["members"]:
                if (
                    member.get("name") == user
                    or member.get("real_name", "").lower() == user.lower()
                    or member.get("display_name", "").lower() == user.lower()
                ):
                    user_data = member
                    break

            if not user_data:
                return f"User not found: {user}"

        # Format user information
        username = user_data.get("name", "Unknown")
        user_id = user_data.get("id", "Unknown")
        real_name = user_data.get("real_name", username)

        output = f"User Profile: {real_name}\n"
        output += "=" * 40 + "\n\n"

        output += f"👤 Display Name: {real_name}\n"
        output += f"🏷️ Username: @{username}\n"
        output += f"🆔 User ID: {user_id}\n"

        # Status and role information
        is_admin = user_data.get("is_admin", False)
        is_owner = user_data.get("is_owner", False)
        is_bot = user_data.get("is_bot", False)

        roles = []
        if is_owner:
            roles.append("Workspace Owner")
        elif is_admin:
            roles.append("Workspace Admin")
        if is_bot:
            roles.append("Bot User")

        if roles:
            output += f"⭐ Role: {', '.join(roles)}\n"

        # Profile information
        profile = user_data.get("profile", {})

        title = profile.get("title", "")
        if title:
            output += f"💼 Title: {title}\n"

        email = profile.get("email", "")
        if email:
            output += f"📧 Email: {email}\n"

        phone = profile.get("phone", "")
        if phone:
            output += f"📞 Phone: {phone}\n"

        # Current status
        status_text = profile.get("status_text", "")
        status_emoji = profile.get("status_emoji", "")
        if status_text or status_emoji:
            output += f"💭 Status: {status_emoji} {status_text}\n"

        # Timezone
        tz_label = user_data.get("tz_label", "")
        if tz_label:
            output += f"🌍 Timezone: {tz_label}\n"

        # Account status
        if user_data.get("deleted", False):
            output += "⚠️ Status: Deactivated\n"
        else:
            output += "✅ Status: Active\n"

        return output

    except SlackApiError as e:
        return f"Slack API error: {e.response['error']}"
    except Exception as e:
        raise ToolError(f"Error getting user info: {str(e)}")


@tool(
    description="""Create threaded discussions in Slack channels for organized conversations.
Perfect for starting focused discussions, Q&A sessions, or detailed project updates.

Example usage:
- create_slack_thread("general", "Weekly Team Update", "Here's what happened this week...")
- create_slack_thread("dev", "Bug Discussion", "Found critical issue in payment flow", mention_users=["lead-dev"])

Helps keep channels organized and discussions focused."""
)
def create_slack_thread(
    channel: str,
    subject: str,
    initial_message: str,
    mention_users: Optional[List[str]] = None,
) -> str:
    """
    Create a threaded discussion in Slack channel.

    Args:
        channel: Channel name (without #) or channel ID
        subject: Thread subject/title
        initial_message: Opening message for the thread
        mention_users: List of usernames to mention in thread

    Returns:
        Success message with thread information
    """
    try:
        client = _get_slack_client()

        # Format the thread starter message
        thread_text = f"*{subject}*\n\n{initial_message}"

        # Add mentions if specified
        if mention_users:
            mentions = " ".join([f"<@{user}>" for user in mention_users])
            thread_text = f"{mentions}\n\n{thread_text}"

        # Add channel prefix if needed
        if not channel.startswith("#") and not channel.startswith("C"):
            channel = f"#{channel}"

        # Send initial message
        response = client.chat_postMessage(
            channel=channel, text=thread_text, unfurl_links=True, unfurl_media=True
        )

        if not response["ok"]:
            return f"Failed to create thread: {response.get('error', 'Unknown error')}"

        thread_ts = response.get("ts")
        channel_info = response.get("channel", channel)

        # Send follow-up instruction in thread
        follow_up = "💬 Reply to this message to join the discussion thread!"
        client.chat_postMessage(channel=channel, text=follow_up, thread_ts=thread_ts)

        return f"Thread created successfully in #{channel_info}!\n\nSubject: {subject}\nThread ID: {thread_ts}\n\nParticipants can now reply to continue the discussion in an organized thread."

    except SlackApiError as e:
        return f"Slack API error: {e.response['error']}"
    except Exception as e:
        raise ToolError(f"Error creating thread: {str(e)}")


@tool(
    description="""Upload files to Slack channels with comments and sharing options.
Supports various file types including documents, images, spreadsheets, and code files.

Example usage:
- upload_slack_file("reports", "/path/to/report.pdf", "Q4 financial report")
- upload_slack_file("general", "data.csv", "Analysis results", share_with_users=["analyst"])
- upload_slack_file("dev-team", "bug_fix.py", "Fix for login issue", thread_ts="1234567890.123")

Perfect for: sharing documents, code reviews, image sharing, file collaboration."""
)
def upload_slack_file(
    channel: str,
    file_path: str,
    comment: Optional[str] = None,
    filename: Optional[str] = None,
    thread_ts: Optional[str] = None,
    share_with_users: Optional[List[str]] = None,
) -> str:
    """
    Upload file to Slack channel.

    Args:
        channel: Channel name (without #) or channel ID
        file_path: Path to file to upload
        comment: Comment to add with the file
        filename: Custom filename (defaults to file's actual name)
        thread_ts: Upload to specific thread
        share_with_users: List of usernames to share file with

    Returns:
        Success message with file information
    """
    try:
        client = _get_slack_client()

        # Check if file exists
        if not os.path.exists(file_path):
            return f"File not found: {file_path}"

        # Add channel prefix if needed
        if not channel.startswith("#") and not channel.startswith("C"):
            channel = f"#{channel}"

        # Prepare upload parameters
        upload_params = {
            "channels": channel,
            "file": file_path,
        }

        if comment:
            upload_params["initial_comment"] = comment

        if filename:
            upload_params["filename"] = filename

        if thread_ts:
            upload_params["thread_ts"] = thread_ts

        # Upload file
        response = client.files_upload(**upload_params)

        if not response["ok"]:
            return f"Failed to upload file: {response.get('error', 'Unknown error')}"

        file_info = response["file"]
        file_name = file_info.get("name", "Unknown file")
        file_size = file_info.get("size", 0)
        file_type = file_info.get("filetype", "unknown")
        file_url = file_info.get("url_private", "No URL")

        # Format file size
        if file_size > 1024 * 1024:
            size_str = f"{file_size/(1024*1024):.1f}MB"
        elif file_size > 1024:
            size_str = f"{file_size/1024:.1f}KB"
        else:
            size_str = f"{file_size}B"

        output = f"File uploaded successfully to #{channel}!\n\n"
        output += f"📄 File: {file_name}\n"
        output += f"📏 Size: {size_str}\n"
        output += f"🏷️ Type: {file_type.upper()}\n"

        if comment:
            output += f"💬 Comment: {comment}\n"

        if thread_ts:
            output += "📍 Uploaded to thread\n"

        # Share with specific users if requested
        if share_with_users:
            file_id = file_info.get("id")
            if file_id:
                try:
                    for user in share_with_users:
                        client.files_sharedPublicURL(file=file_id)
                    output += f"👥 Shared with: {', '.join(share_with_users)}\n"
                except:
                    output += f"⚠️ Could not share with specified users\n"

        return output

    except SlackApiError as e:
        return f"Slack API error: {e.response['error']}"
    except Exception as e:
        raise ToolError(f"Error uploading file: {str(e)}")
