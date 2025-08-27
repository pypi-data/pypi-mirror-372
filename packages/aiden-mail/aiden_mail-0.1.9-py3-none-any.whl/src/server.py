import json
from typing import Optional
from dataclasses import dataclass
from fastmcp import FastMCP
from .mail_service.mail_service import EmailService

CREDENTIAL_ARG = "__credential__"

@dataclass
class ToolCredential:
    service: str
    account: str
    token: str

    @classmethod
    def from_dict(cls, data: dict) -> "ToolCredential":
        return cls(**data)


mcp = FastMCP(name="Aiden Mail")

@mcp.tool(name="send_email", exclude_args=[CREDENTIAL_ARG])
async def send_email(subject: str, body: str, recipient: str, __credential__: dict = {}) -> str:
    credential = ToolCredential.from_dict(__credential__)
    email_service = EmailService(
        provider=credential.service,
        email_address=credential.account,
        password=credential.token
    )
    email_service.send_email(
        to_address=recipient,
        subject=subject,
        body=body
    )
    return "Email sent successfully"

@mcp.tool(name="list_emails", exclude_args=[CREDENTIAL_ARG])
async def list_emails(folder: str = "INBOX", limit: int = 10, __credential__: dict = {}) -> str:
    credential = ToolCredential.from_dict(__credential__)
    email_service = EmailService(
        provider=credential.service,
        email_address=credential.account,
        password=credential.token
    )
    # only return emails uid and subject
    emails = email_service.list_emails(folder, limit)
    return json.dumps({
        "emails": [{
            "uid": email["uid"],
            "subject": email["subject"],
            "date": email["date"]
        } for email in emails]
    })

@mcp.tool(name="search_emails", exclude_args=[CREDENTIAL_ARG])
async def search_emails(query: Optional[str] = None, from_addr: Optional[str] = None, to_addr: Optional[str] = None, subject: Optional[str] = None, folder: str = "INBOX", limit: int = 5, __credential__: dict = {}) -> str:
    credential = ToolCredential.from_dict(__credential__)
    email_service = EmailService(
        provider=credential.service,
        email_address=credential.account,
        password=credential.token
    )
    emails = email_service.search_emails(query, from_addr, to_addr, subject, folder, limit)
    return json.dumps({
        "emails": [{
            "uid": email["uid"],
            "subject": email["subject"],
            "date": email["date"]
        } for email in emails]
    })

@mcp.tool(name="get_email_by_uid", exclude_args=[CREDENTIAL_ARG], description="Get email details by uid")
async def get_email_by_uid(uid: str, __credential__: dict = {}) -> str:
    credential = ToolCredential.from_dict(__credential__)
    email_service = EmailService(
        provider=credential.service,
        email_address=credential.account,
        password=credential.token
    )
    return json.dumps(email_service.get_email_by_uid(uid))

@mcp.tool(name="delete_email", exclude_args=[CREDENTIAL_ARG])
async def delete_email(uid: str, __credential__: dict = {}) -> str:
    credential = ToolCredential.from_dict(__credential__)
    email_service = EmailService(
        provider=credential.service,
        email_address=credential.account,
        password=credential.token
    )
    return json.dumps(email_service.delete_email(uid))

@mcp.tool(name="move_email", exclude_args=[CREDENTIAL_ARG])
async def move_email(uid: str, from_folder: str = "INBOX", to_folder: str = "Trash", __credential__: dict = {}) -> str:
    credential = ToolCredential.from_dict(__credential__)
    email_service = EmailService(
        provider=credential.service,
        email_address=credential.account,
        password=credential.token
    )
    return json.dumps(email_service.move_email(uid, from_folder, to_folder))

@mcp.tool(name="mark_email_as_read", exclude_args=[CREDENTIAL_ARG])
async def mark_as_read(uid: str, __credential__: dict = {}) -> str:
    credential = ToolCredential.from_dict(__credential__)
    email_service = EmailService(
        provider=credential.service,
        email_address=credential.account,
        password=credential.token
    )
    return json.dumps(email_service.mark_as_read(uid))

@mcp.tool(name="mark_email_as_unread", exclude_args=[CREDENTIAL_ARG])
async def mark_as_unread(uid: str, __credential__: dict = {}) -> str:
    credential = ToolCredential.from_dict(__credential__)
    email_service = EmailService(
        provider=credential.service,
        email_address=credential.account,
        password=credential.token
    )
    return json.dumps(email_service.mark_as_unread(uid))

@mcp.tool(name="get_email_folders", exclude_args=[CREDENTIAL_ARG])
async def get_mail_folders(__credential__: dict = {}) -> str:
    credential = ToolCredential.from_dict(__credential__)
    email_service = EmailService(
        provider=credential.service,
        email_address=credential.account,
        password=credential.token
    )
    return json.dumps(email_service.get_folders())

@mcp.tool(name="get_email_count", exclude_args=[CREDENTIAL_ARG])
async def get_email_count(folder: str = "INBOX", __credential__: dict = {}) -> str:
    credential = ToolCredential.from_dict(__credential__)
    email_service = EmailService(
        provider=credential.service,
        email_address=credential.account,
        password=credential.token
    )
    return json.dumps(email_service.get_email_count(folder))


def main():
    mcp.run()


if __name__ == "__main__":
    main()
