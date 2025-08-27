import imaplib
import smtplib
import ssl
import email
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from email.header import decode_header
from typing import List, Dict, Optional
from datetime import datetime
import re


PROVIDER_PRESET = {
    "gmail": {
        "imap_server": "imap.gmail.com",
        "smtp_server": "smtp.gmail.com",
        "imap_port": 993,
        "smtp_port": 587,
    },
    # "outlook": {
    #     "imap_server": "outlook.office365.com",
    #     "smtp_server": "smtp.office365.com",
    #     "imap_port": 993,
    #     "smtp_port": 587,
    # },
    "icloud": {
        "imap_server": "imap.mail.me.com",
        "smtp_server": "smtp.mail.me.com",
        "imap_port": 993,
        "smtp_port": 587,
    },
    "qq": {
        "imap_server": "imap.qq.com",
        "smtp_server": "smtp.qq.com",
        "imap_port": 993,
        "smtp_port": 587,
    },
    "163": {
        "imap_server": "imap.163.com",
        "smtp_server": "smtp.163.com",
        "imap_port": 993,
        "smtp_port": 465,
    }
}



class EmailService:
    """Email service class supporting IMAP and SMTP functionality"""
    
    def __init__(self, 
                 provider: str,
                 email_address: str,
                 password: str):
        """
        Initialize email service
        
        Args:
            provider: Email service provider
            email_address: Email address
            password: Email password or app-specific password
        """
        # lowercase the provider
        provider = provider.lower()
        if provider not in PROVIDER_PRESET:
            raise ValueError(f"Unsupported email service provider: {provider}")
        self.provider = provider
        self.email_address = email_address
        self.password = password
        
        if not self.email_address or not self.password:
            raise ValueError("Email address and password must be provided")
    
    def _connect_imap(self) -> imaplib.IMAP4_SSL:
        """Connect to IMAP server"""
        try:
            imap = imaplib.IMAP4_SSL(PROVIDER_PRESET[self.provider]['imap_server'], PROVIDER_PRESET[self.provider]['imap_port'])
            imap.login(self.email_address, self.password)
            return imap
        except Exception as e:
            raise ConnectionError(f"IMAP connection failed: {str(e)}")
    
    def _connect_smtp(self) -> smtplib.SMTP:
        """Connect to SMTP server"""
        try:
            smtp = smtplib.SMTP(PROVIDER_PRESET[self.provider]['smtp_server'], PROVIDER_PRESET[self.provider]['smtp_port'])
            smtp.starttls(context=ssl.create_default_context())
            smtp.login(self.email_address, self.password)
            return smtp
        except Exception as e:
            raise ConnectionError(f"SMTP connection failed: {str(e)}")
    
    def _encode_folder_name(self, folder_name: str) -> str:
        """
        Encode folder name to adapt to IMAP commands
        
        Args:
            folder_name: Original folder name
            
        Returns:
            Encoded folder name
        """
        if not folder_name:
            return 'INBOX'
        
        # Check if contains non-ASCII characters (including Chinese)
        has_non_ascii = any(ord(char) > 127 for char in folder_name)
        
        # If contains spaces, special characters, or non-ASCII characters, need to wrap in quotes
        if (' ' in folder_name or '[' in folder_name or ']' in folder_name or 
            has_non_ascii):
            return f'"{folder_name}"'
        
        return folder_name
    
    def _encode_imap_string(self, text: str, use_quotes: bool = True) -> str:
        """
        Unified handling of IMAP string encoding
        
        Args:
            text: String to encode
            use_quotes: Whether to wrap in quotes
            
        Returns:
            Encoded string
        """
        if not text:
            return '""' if use_quotes else ''
        
        try:
            # Try UTF-8 encoding (IMAP protocol supports it)
            text_bytes = text.encode('utf-8')
            if use_quotes:
                return f'"{text}"'
            else:
                return str(text_bytes)
        except UnicodeEncodeError:
            # If UTF-8 encoding fails, try ASCII-compatible parts
            try:
                text_ascii = text.encode('ascii', errors='ignore').decode('ascii')
                if text_ascii:
                    if use_quotes:
                        return f'"{text_ascii}"'
                    else:
                        return text_ascii
                else:
                    # If all characters are ignored, return empty string
                    return '""' if use_quotes else ''
            except Exception:
                # Final fallback
                return '""' if use_quotes else ''
    
    def _decode_email_header(self, header: str) -> str:
        """Decode email header information"""
        try:
            decoded_parts = decode_header(header)
            decoded_string = ""
            for part, encoding in decoded_parts:
                if isinstance(part, bytes):
                    if encoding:
                        try:
                            decoded_string += part.decode(encoding)
                        except UnicodeDecodeError:
                            # If specified encoding fails, try other encodings
                            for fallback_encoding in ['utf-8', 'gbk', 'gb2312', 'latin-1']:
                                try:
                                    decoded_string += part.decode(fallback_encoding)
                                    break
                                except UnicodeDecodeError:
                                    continue
                            else:
                                # If all encodings fail, use errors='ignore'
                                decoded_string += part.decode('utf-8', errors='ignore')
                    else:
                        # Try multiple encoding methods
                        for encoding in ['utf-8', 'gbk', 'gb2312', 'latin-1']:
                            try:
                                decoded_string += part.decode(encoding)
                                break
                            except UnicodeDecodeError:
                                continue
                        else:
                            decoded_string += part.decode('utf-8', errors='ignore')
                else:
                    decoded_string += str(part)
            return decoded_string
        except Exception as e:
            print(f"Failed to decode email header: {str(e)}")
            return str(header)
    
    def _parse_email_message(self, msg_data: bytes) -> Dict:
        """Parse email message"""
        email_message = email.message_from_bytes(msg_data)
        
        # Parse email headers
        subject = self._decode_email_header(email_message.get('Subject', ''))
        from_addr = self._decode_email_header(email_message.get('From', ''))
        to_addr = self._decode_email_header(email_message.get('To', ''))
        date_str = email_message.get('Date', '')
        
        # Parse email content
        body = ""
        content_type = ""
        
        if email_message.is_multipart():
            for part in email_message.walk():
                content_type_part = part.get_content_type()
                if content_type_part == "text/plain":
                    try:
                        payload = part.get_payload(decode=True)
                        if isinstance(payload, bytes):
                            # Try multiple encoding methods
                            for encoding in ['utf-8', 'gbk', 'gb2312', 'latin-1']:
                                try:
                                    body = payload.decode(encoding)
                                    break
                                except UnicodeDecodeError:
                                    continue
                            else:
                                # If all encodings fail, use errors='ignore'
                                body = payload.decode('utf-8', errors='ignore')
                        else:
                            body = str(payload)
                        content_type = "text/plain"
                        break
                    except Exception as e:
                        print(f"Failed to parse plain text content: {str(e)}")
                        payload = part.get_payload(decode=True)
                        if isinstance(payload, bytes):
                            body = payload.decode('utf-8', errors='ignore')
                        else:
                            body = str(payload)
                        content_type = "text/plain"
                elif content_type_part == "text/html" and not body:
                    try:
                        payload = part.get_payload(decode=True)
                        if isinstance(payload, bytes):
                            # Try multiple encoding methods
                            for encoding in ['utf-8', 'gbk', 'gb2312', 'latin-1']:
                                try:
                                    body = payload.decode(encoding)
                                    break
                                except UnicodeDecodeError:
                                    continue
                            else:
                                # If all encodings fail, use errors='ignore'
                                body = payload.decode('utf-8', errors='ignore')
                        else:
                            body = str(payload)
                        content_type = "text/html"
                    except Exception as e:
                        print(f"Failed to parse HTML content: {str(e)}")
                        payload = part.get_payload(decode=True)
                        if isinstance(payload, bytes):
                            body = payload.decode('utf-8', errors='ignore')
                        else:
                            body = str(payload)
                        content_type = "text/html"
        else:
            try:
                payload = email_message.get_payload(decode=True)
                if isinstance(payload, bytes):
                    # Try multiple encoding methods
                    for encoding in ['utf-8', 'gbk', 'gb2312', 'latin-1']:
                        try:
                            body = payload.decode(encoding)
                            break
                        except UnicodeDecodeError:
                            continue
                    else:
                        # If all encodings fail, use errors='ignore'
                        body = payload.decode('utf-8', errors='ignore')
                else:
                    body = str(payload)
                content_type = email_message.get_content_type()
            except Exception as e:
                print(f"Failed to parse email content: {str(e)}")
                payload = email_message.get_payload(decode=True)
                if isinstance(payload, bytes):
                    body = payload.decode('utf-8', errors='ignore')
                else:
                    body = str(payload)
                content_type = email_message.get_content_type()
        
        return {
            'subject': subject,
            'from': from_addr,
            'to': to_addr,
            'date': date_str,
            'body': body,
            'content_type': content_type
        }
    
    def list_emails(self, folder: str = 'INBOX', limit: int = 50) -> List[Dict]:
        """
        List emails
        
        Args:
            folder: Email folder name
            limit: Limit on number of emails to return
            
        Returns:
            List of emails
        """
        imap = self._connect_imap()
        try:
            encoded_folder = self._encode_folder_name(folder)
            imap.select(encoded_folder)
            _, message_numbers = imap.search(None, 'ALL')
            
            email_list = []
            if len(message_numbers) == 0 or not message_numbers[0]:
                return email_list
            
            message_list = message_numbers[0].split()
            
            # Get latest emails
            for num in message_list[-limit:]:
                _, msg_data = imap.fetch(num, '(RFC822)')
                if msg_data and msg_data[0] and len(msg_data[0]) > 1:
                    msg_bytes = msg_data[0][1]
                    if isinstance(msg_bytes, bytes):
                        email_info = self._parse_email_message(msg_bytes)
                        email_info['uid'] = num.decode()
                        email_list.append(email_info)
            
            return email_list[::-1]  # Return latest emails first
        finally:
            imap.logout()
    
    def search_emails(self, 
                     query: Optional[str] = None,
                     from_addr: Optional[str] = None,
                     to_addr: Optional[str] = None,
                     subject: Optional[str] = None,
                     folder: str = 'INBOX',
                     limit: int = 50) -> List[Dict]:
        """
        Search emails
        
        Args:
            query: Search keywords
            from_addr: Sender address
            to_addr: Recipient address
            subject: Subject keywords
            folder: Email folder name
            limit: Limit on number of emails to return
            
        Returns:
            Search results list
        """
        imap = self._connect_imap()
        try:
            encoded_folder = self._encode_folder_name(folder)
            imap.select(encoded_folder)
            
            # Build search criteria using unified encoding handling
            search_criteria = []
            if query:
                encoded_query = self._encode_imap_string(query, use_quotes=False)
                if encoded_query:
                    search_criteria.append(f'TEXT {encoded_query}')
            if from_addr:
                encoded_from = self._encode_imap_string(from_addr, use_quotes=False)
                if encoded_from:
                    search_criteria.append(f'FROM {encoded_from}')
            if to_addr:
                encoded_to = self._encode_imap_string(to_addr, use_quotes=False)
                if encoded_to:
                    search_criteria.append(f'TO {encoded_to}')
            if subject:
                encoded_subject = self._encode_imap_string(subject, use_quotes=False)
                if encoded_subject:
                    search_criteria.append(f'SUBJECT {encoded_subject}')
            
            if not search_criteria:
                search_criteria.append('ALL')
            
            search_string = ' '.join(search_criteria)
            _, message_numbers = imap.search(None, search_string)
            
            email_list = []
            message_list = message_numbers[0].split()
            
            # Get search results
            for num in message_list[-limit:]:
                _, msg_data = imap.fetch(num, '(RFC822)')
                if msg_data and msg_data[0] and len(msg_data[0]) > 1:
                    msg_bytes = msg_data[0][1]
                    if isinstance(msg_bytes, bytes):
                        email_info = self._parse_email_message(msg_bytes)
                        email_info['uid'] = num.decode()
                        email_list.append(email_info)
            
            return email_list[::-1]
        finally:
            imap.logout()
    
    def get_email_by_uid(self, uid: str, folder: str = 'INBOX') -> Optional[Dict]:
        """
        Get specific email by UID
        
        Args:
            uid: Email UID
            folder: Email folder name
            
        Returns:
            Email information
        """
        imap = self._connect_imap()
        try:
            encoded_folder = self._encode_folder_name(folder)
            imap.select(encoded_folder)
            _, msg_data = imap.fetch(uid, '(RFC822)')
            
            if not msg_data or not msg_data[0] or len(msg_data[0]) <= 1:
                return None
            
            msg_bytes = msg_data[0][1]
            if not isinstance(msg_bytes, bytes):
                return None
            
            email_info = self._parse_email_message(msg_bytes)
            email_info['uid'] = uid
            return email_info
        finally:
            imap.logout()
    
    def delete_email(self, uid: str, folder: str = 'INBOX') -> str:
        """
        Delete email
        
        Args:
            uid: Email UID
            folder: Email folder name
            
        Returns:
            Whether deletion was successful
        """
        imap = self._connect_imap()
        try:
            encoded_folder = self._encode_folder_name(folder)
            imap.select(encoded_folder)
            imap.store(uid, '+FLAGS', '\\Deleted')
            imap.expunge()
            return "Email deleted successfully"
        except Exception as e:
            print(f"Failed to delete email: {str(e)}")
            return "Email deletion failed"
        finally:
            imap.logout()
    
    def move_email(self, uid: str, from_folder: str = 'INBOX', to_folder: str = 'Trash') -> str:
        """
        Move email to another folder
        
        Args:
            uid: Email UID
            from_folder: Source folder
            to_folder: Target folder
            
        Returns:
            Whether movement was successful
        """
        imap = self._connect_imap()
        try:
            encoded_from_folder = self._encode_folder_name(from_folder)
            encoded_to_folder = self._encode_folder_name(to_folder)
            
            imap.select(encoded_from_folder)
            _, msg_data = imap.fetch(uid, '(RFC822)')
            
            if not msg_data or not msg_data[0] or len(msg_data[0]) <= 1:
                return "Email not found"
            
            msg_bytes = msg_data[0][1]
            if not isinstance(msg_bytes, bytes):
                return "Email not found"
            
            # Copy to target folder
            imap.append(encoded_to_folder, '', imaplib.Time2Internaldate(datetime.now()), msg_bytes)
            
            # Delete from source folder
            imap.store(uid, '+FLAGS', '\\Deleted')
            imap.expunge()
            
            return "Email moved successfully"
        except Exception as e:
            print(f"Failed to move email: {str(e)}")
            return "Email movement failed"
        finally:
            imap.logout()
    
    def send_email(self, 
                  to_address: str,
                  subject: str,
                  body: str,
                  cc: Optional[List[str]] = None,
                  bcc: Optional[List[str]] = None,
                  attachments: Optional[List[str]] = None,
                  html_body: Optional[str] = None) -> bool:
        """
        Send email
        
        Args:
            to_address: Recipient address
            subject: Email subject
            body: Email body
            cc: CC address list
            bcc: BCC address list
            attachments: Attachment file path list
            html_body: HTML format email body
            
        Returns:
            Whether sending was successful
        """
        smtp = self._connect_smtp()
        try:
            # Create email message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.email_address
            msg['To'] = to_address
            msg['Subject'] = subject
            
            if cc:
                msg['Cc'] = ', '.join(cc)
            
            # Add text content
            text_part = MIMEText(body, 'plain', 'utf-8')
            msg.attach(text_part)
            
            # Add HTML content
            if html_body:
                html_part = MIMEText(html_body, 'html', 'utf-8')
                msg.attach(html_part)
            
            # Add attachments
            if attachments:
                for file_path in attachments:
                    if os.path.exists(file_path):
                        with open(file_path, 'rb') as attachment:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(attachment.read())
                        
                        encoders.encode_base64(part)
                        # Handle attachment filename encoding
                        filename = os.path.basename(file_path)
                        try:
                            # Try UTF-8 encoding for filename
                            filename_encoded = filename.encode('utf-8').decode('utf-8')
                        except UnicodeEncodeError:
                            # If failed, use ASCII-compatible parts
                            filename_encoded = filename.encode('ascii', errors='ignore').decode('ascii')
                            if not filename_encoded:
                                filename_encoded = 'attachment'
                        
                        part.add_header(
                            'Content-Disposition',
                            f'attachment; filename= {filename_encoded}'
                        )
                        msg.attach(part)
            
            # Send email
            all_recipients = [to_address]
            if cc:
                all_recipients.extend(cc)
            if bcc:
                all_recipients.extend(bcc)
            
            smtp.sendmail(self.email_address, all_recipients, msg.as_string())
            return True
            
        except Exception as e:
            print(f"Failed to send email: {str(e)}")
            return False
        finally:
            smtp.quit()
    
    def get_folders(self) -> List[str]:
        """
        Get all email folders
        
        Returns:
            Folder name list
        """
        imap = self._connect_imap()
        try:
            _, folders = imap.list()
            folder_list = []
            for folder in folders:
                if isinstance(folder, bytes):
                    try:
                        folder_str = folder.decode('utf-8')
                    except UnicodeDecodeError:
                        # If UTF-8 decoding fails, try other encodings
                        try:
                            folder_str = folder.decode('latin-1')
                        except UnicodeDecodeError:
                            folder_str = folder.decode('ascii', errors='ignore')
                else:
                    folder_str = str(folder)
                
                # Parse folder name, extract complete folder path
                # IMAP LIST returns format: (\HasNoChildren) "/" "INBOX"
                # or: (\HasNoChildren) "/" "[Gmail]/Sent Mail"
                match = re.search(r'"/" "([^"]+)"', folder_str)
                if match:
                    folder_name = match.group(1)
                    # Handle folder name encoding - try multiple encoding methods
                    folder_name_decoded = None
                    for encoding in ['utf-8', 'gbk', 'gb2312', 'latin-1']:
                        try:
                            # If folder name is byte string, decode first
                            if isinstance(folder_name, bytes):
                                folder_name_decoded = folder_name.decode(encoding)
                            else:
                                # If string, try encode then decode
                                folder_name_decoded = folder_name.encode(encoding).decode(encoding)
                            break
                        except (UnicodeError, UnicodeDecodeError, UnicodeEncodeError):
                            continue
                    
                    if folder_name_decoded:
                        folder_list.append(folder_name_decoded)
                    else:
                        folder_list.append(folder_name)
                else:
                    # Fallback parsing method
                    parts = folder_str.split('"')
                    if len(parts) >= 3:
                        folder_name = parts[-2]
                        # Handle folder name encoding - try multiple encoding methods
                        folder_name_decoded = None
                        for encoding in ['utf-8', 'gbk', 'gb2312', 'latin-1']:
                            try:
                                # If folder name is byte string, decode first
                                if isinstance(folder_name, bytes):
                                    folder_name_decoded = folder_name.decode(encoding)
                                else:
                                    # If string, try encode then decode
                                    folder_name_decoded = folder_name.encode(encoding).decode(encoding)
                                break
                            except (UnicodeError, UnicodeDecodeError, UnicodeEncodeError):
                                continue
                        
                        if folder_name_decoded:
                            folder_list.append(folder_name_decoded)
                        else:
                            folder_list.append(folder_name)
            
            return folder_list
        finally:
            imap.logout()
    
    def get_email_count(self, folder: str = 'INBOX') -> int:
        """
        Get email count in folder
        
        Args:
            folder: Email folder name
            
        Returns:
            Email count
        """
        imap = self._connect_imap()
        try:
            encoded_folder = self._encode_folder_name(folder)
            imap.select(encoded_folder)
            _, message_numbers = imap.search(None, 'ALL')
            return len(message_numbers[0].split())
        finally:
            imap.logout()
    
    def mark_as_read(self, uid: str, folder: str = 'INBOX') -> bool:
        """
        Mark email as read
        
        Args:
            uid: Email UID
            folder: Email folder name
            
        Returns:
            Whether operation was successful
        """
        imap = self._connect_imap()
        try:
            encoded_folder = self._encode_folder_name(folder)
            imap.select(encoded_folder)
            imap.store(uid, '+FLAGS', '\\Seen')
            return True
        except Exception as e:
            print(f"Failed to mark as read: {str(e)}")
            return False
        finally:
            imap.logout()
    
    def mark_as_unread(self, uid: str, folder: str = 'INBOX') -> bool:
        """
        Mark email as unread
        
        Args:
            uid: Email UID
            folder: Email folder name
            
        Returns:
            Whether operation was successful
        """
        imap = self._connect_imap()
        try:
            encoded_folder = self._encode_folder_name(folder)
            imap.select(encoded_folder)
            imap.store(uid, '-FLAGS', '\\Seen')
            return True
        except Exception as e:
            print(f"Failed to mark as unread: {str(e)}")
            return False
        finally:
            imap.logout()
