#!/usr/bin/env python3
"""
Email Service Command Line Tool
"""

import argparse
import sys
from mail_service.mail_service import EmailService


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Email Service Command Line Tool')
    parser.add_argument('--email', help='Email address')
    parser.add_argument('--password', help='Email password')
    parser.add_argument('--provider', help='Email provider')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # List emails command
    list_parser = subparsers.add_parser('list', help='List emails')
    list_parser.add_argument('--folder', default='INBOX', help='Email folder')
    list_parser.add_argument('--limit', type=int, default=10, help='Number of emails to display')
    
    # Search emails command
    search_parser = subparsers.add_parser('search', help='Search emails')
    search_parser.add_argument('--query', help='Search keywords')
    search_parser.add_argument('--from', dest='from_addr', help='Sender address')
    search_parser.add_argument('--to', dest='to_addr', help='Recipient address')
    search_parser.add_argument('--subject', help='Subject keywords')
    search_parser.add_argument('--folder', default='INBOX', help='Email folder')
    search_parser.add_argument('--limit', type=int, default=10, help='Number of emails to display')
    
    # Send email command
    send_parser = subparsers.add_parser('send', help='Send email')
    send_parser.add_argument('--to', required=True, help='Recipient address')
    send_parser.add_argument('--subject', required=True, help='Email subject')
    send_parser.add_argument('--body', required=True, help='Email body')
    send_parser.add_argument('--html', help='HTML format body')
    send_parser.add_argument('--cc', help='CC addresses (comma separated)')
    send_parser.add_argument('--bcc', help='BCC addresses (comma separated)')
    send_parser.add_argument('--attachment', help='Attachment file paths (comma separated)')
    
    # Delete email command
    delete_parser = subparsers.add_parser('delete', help='Delete email')
    delete_parser.add_argument('--uid', required=True, help='Email UID')
    delete_parser.add_argument('--folder', default='INBOX', help='Email folder')
    
    # Get email details command
    get_parser = subparsers.add_parser('get', help='Get email details')
    get_parser.add_argument('--uid', required=True, help='Email UID')
    get_parser.add_argument('--folder', default='INBOX', help='Email folder')
    
    # Get email count command
    count_parser = subparsers.add_parser('count', help='Get email count')
    count_parser.add_argument('--folder', default='INBOX', help='Email folder')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        # Create email service instance
        email_service = EmailService(
            email_address=args.email,
            password=args.password,
            provider=args.provider,
        )
        
        if args.command == 'list':
            emails = email_service.list_emails(args.folder, args.limit)
            print(f"\nRecent {len(emails)} emails in {args.folder}:")
            for i, email_info in enumerate(emails, 1):
                print(f"{i}. Subject: {email_info['subject']}")
                print(f"   From: {email_info['from']}")
                print(f"   Date: {email_info['date']}")
                print(f"   UID: {email_info['uid']}")
                print()
        
        elif args.command == 'search':
            search_results = email_service.search_emails(
                query=args.query,
                from_addr=args.from_addr,
                to_addr=args.to_addr,
                subject=args.subject,
                folder=args.folder,
                limit=args.limit
            )
            print(f"\nFound {len(search_results)} emails:")
            for i, email_info in enumerate(search_results, 1):
                print(f"{i}. Subject: {email_info['subject']}")
                print(f"   From: {email_info['from']}")
                print(f"   Date: {email_info['date']}")
                print(f"   UID: {email_info['uid']}")
                print()
        
        elif args.command == 'send':
            cc_list = args.cc.split(',') if args.cc else None
            bcc_list = args.bcc.split(',') if args.bcc else None
            attachment_list = args.attachment.split(',') if args.attachment else None
            
            success = email_service.send_email(
                to_address=args.to,
                subject=args.subject,
                body=args.body,
                html_body=args.html,
                cc=cc_list,
                bcc=bcc_list,
                attachments=attachment_list
            )
            
            if success:
                print("Email sent successfully!")
            else:
                print("Failed to send email!")
                sys.exit(1)
        
        elif args.command == 'delete':
            success = email_service.delete_email(args.uid, args.folder)
            if success:
                print(f"Email {args.uid} deleted successfully!")
            else:
                print(f"Failed to delete email {args.uid}!")
                sys.exit(1)
        
        elif args.command == 'get':
            email_detail = email_service.get_email_by_uid(args.uid, args.folder)
            if email_detail:
                print(f"\nEmail details (UID: {args.uid}):")
                print(f"Subject: {email_detail['subject']}")
                print(f"From: {email_detail['from']}")
                print(f"To: {email_detail['to']}")
                print(f"Date: {email_detail['date']}")
                print(f"Content type: {email_detail['content_type']}")
                print(f"Content:\n{email_detail['body']}")
            else:
                print(f"Email {args.uid} not found")
                sys.exit(1)
        
        elif args.command == 'count':
            count = email_service.get_email_count(args.folder)
            print(f"There are {count} emails in {args.folder}")
    
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
