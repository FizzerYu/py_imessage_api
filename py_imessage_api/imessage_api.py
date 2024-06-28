import sqlite3
from typing import List, Dict, Literal, Optional, Tuple
import pandas as pd
import os
import datetime
import subprocess

class IMessageAPI:
    def init(self, db_location: str = '~/Library/Messages/chat.db'):
        """
        Initialize the IMessageAPI.

        :param db_location: Path to the iMessage database file
        """
        self.db_location = db_location
        self.conn = None

        # Set up the Unix timestamp for date conversion
        date_string = '2001-01-01'
        mod_date = datetime.datetime.strptime(date_string, '%Y-%m-%d')
        self._unix_timestamp = int(mod_date.timestamp())*1000000000

    def _connect(self):
        """
        Establish a connection to the SQLite database.

        :return: SQLite connection object
        """
        if not self.conn:
            self.conn = sqlite3.connect(self.db_location)
        return self.conn

    def _close(self):
        """
        Close the database connection if it's open.
        """
        if self.conn:
            self.conn.close()
            self.conn = None

    def _execute_query(self, query: str, params: tuple = ()):
        """
        Execute an SQL query and return the results as a pandas DataFrame.

        :param query: SQL query string
        :param params: Query parameters (optional)
        :return: pandas DataFrame with query results
        """
        conn = self._connect()
        return pd.read_sql_query(query, conn, params=params)

    def _extrace_my_message(self, attributed_body) -> str:
        """
        Extract the message content from the attributed body.

        :param attributed_body: Attributed body of the message
        :return: Extracted message content
        """
        if attributed_body is None:
            return None
        else:
            attributed_body = attributed_body.decode('utf-8', errors='replace')

            if "NSNumber" in str(attributed_body):
                attributed_body = str(attributed_body).split("NSNumber")[0]
                if "NSString" in attributed_body:
                    attributed_body = str(attributed_body).split("NSString")[1]
                    if "NSDictionary" in attributed_body:
                        attributed_body = str(attributed_body).split("NSDictionary")[0]
                        attributed_body = attributed_body[6:-12]
                        body = attributed_body
            return body

    def get_all_recipients(self) -> pd.DataFrame:
        """
        Retrieve all recipients in the chat history

        - uncanonicalized_id 是去掉国家后手机号
        - The person_centric_id is used to map handles that represent the same contact across ids (numbers, emails, etc) and across services (iMessage, Jabber, iChat, SMS, etc)

        :return: pandas DataFrame with recipient information
        """
        query = """
        SELECT id, service, country, uncanonicalized_id
        FROM handle
        """
        return self._execute_query(query)

    def get_messages(self, recipient: Optional[str] = None, n: Optional[int] = None, is_group: bool = False) -> List[Dict]:
        """
        Retrieve chat messages with a specified recipient

        :param recipient: Recipient's identifier (phone number, Apple ID, or group ID), if None, retrieve all messages
        :param n: Number of messages to retrieve, if None, retrieve all messages
        :param is_group: Whether the recipient is a group
        :return: pandas DataFrame with message information
        """
        query = """
        SELECT message.ROWID, message.date, 
                message.subject, message.text, message.is_audio_message, message.cache_has_attachments,
                message.attributedBody, handle.id, message.is_from_me, message.cache_roomnames,
                attachment.filename, attachment.mime_type, attachment.total_bytes
        FROM message
        LEFT JOIN handle ON message.handle_id = handle.ROWID
        LEFT JOIN message_attachment_join ON message.ROWID = message_attachment_join.message_id
        LEFT JOIN attachment ON message_attachment_join.attachment_id = attachment.ROWID
        ORDER BY message.date DESC
        """
        if recipient is not None:
            query += f" WHERE handle.id = '{recipient}'"
        if n is not None:
            query += f" LIMIT {n}"
        
        df = self._execute_query(query)

        # Process the data
        df['role'] = df['is_from_me'].apply(lambda x: 'Me' if x else 'Friend')
        df['message'] = df.apply(lambda x: self._extrace_my_message(x['attributedBody']) if x['is_from_me'] else x['text'], axis=1)
        df['date_readable'] = df['date'].apply(lambda date: (
            datetime.datetime.fromtimestamp(int((date + self._unix_timestamp) / 1000000000)) + datetime.timedelta(hours=8)
        ).strftime("%Y-%m-%d %H:%M:%S"))

        # Process attachment information
        df['has_attachment'] = df['filename'].notnull()
        df['attachment_type'] = df['mime_type'].apply(lambda x: x.split('/')[0] if x else None)
        df['attachment_size'] = df['total_bytes'].apply(lambda x: f"{x/1024/1024:.2f} MB" if x else None)

        return df   


def send_message(self, content: str, recipient: str, message_type: Literal["text", "file"] = "text", is_group: bool = False) -> Tuple[bool, str]:
    """
    Send a message or file to a specified recipient or group.

    :param content: Content of the message or file path
    :param recipient: Recipient's contact info (phone number, Apple ID, or group ID)
    :param message_type: Type of message, can be 'text' or 'file' (including voice files)
    :param is_group: Whether the recipient is a group
    :return: Tuple of (success: bool, error_message: str)
    """
    if message_type == 'file':
        pictures_dir = os.path.expanduser("~/Pictures")
        if not content.startswith(pictures_dir):
            print(f"Warning: File path should be in the Pictures directory: {pictures_dir}")
        if not os.path.exists(content):
            return False, f"File not found: {content}"
        file_path = os.path.abspath(content)
        command = f'send POSIX file "{file_path}"'
    else:
        temp_file = 'imessage_tmp.txt'
        with open(temp_file, 'w') as f:
            f.write(content)
        file_path = os.path.abspath(temp_file)
        command = f'send (read (POSIX file "{file_path}") as «class utf8»)'

    target = "chat" if is_group else "buddy"
    full_command = f'tell application "Messages" to {command} to {target} "{recipient}"'

    try:
        subprocess.run(['osascript', '-e', full_command], check=True, capture_output=True, text=True)
        success, error_message = True, ""
    except subprocess.CalledProcessError as e:
        success, error_message = False, e.stderr

    if message_type == "text":
        os.remove(temp_file)

    status = "Successfully sent" if success else "Failed to send"
    print(f"{status} {message_type} to {recipient}. {error_message}")

    return success, error_message