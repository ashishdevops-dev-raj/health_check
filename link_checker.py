import os
import requests
from datetime import datetime
import smtplib
from email.mime.text import MIMEText

urls = [
     "https://swimmersweb.com/",
    "https://swimmersweb.com/register",
    "https://swimmersweb.com/login",
    "https://swimmersweb.com/favorites",
    "https://swimmersweb.com/profile",
    "https://swimmersweb.com/privacy-policy",
    "https://swimmersweb.com/terms-conditions",
    "https://swimmersweb.com/contact",
    "https://swimmersweb.com/services",
    "https://swimmersweb.com/swimmer-search",
    "https://swimmersweb.com/swimmer-report",
    "https://swimmersweb.com/team-search",
    "https://swimmersweb.com/team-member-search",
    "https://swimmersweb.com/meet-search",
    "https://swimmersweb.com/meet-detail",
    "https://swimmersweb.com/motivational-time",
    "https://swimmersweb.com/swim-compare",
    "https://swimmersweb.com/tools",
    "https://swimmersweb.com/upcoming-meet",
    "https://swimmersweb.com/lap-timer"
]

def check_links(urls):
    report = []
    headers = {"User-Agent": "Mozilla/5.0 (LinkCheckerBot/1.0)"}
    for url in urls:
        try:
            response = requests.get(url, headers=headers, timeout=10)
            status = f"{response.status_code} OK" if response.status_code in (200, 301, 302) else f"{response.status_code} ERROR"
            report.append((url, status, response.elapsed.total_seconds()))
        except requests.exceptions.RequestException as e:
            report.append((url, f"RequestError: {type(e).__name__} - {e}", "-"))
    return report

def generate_report(report):
    lines = [
        "📊 SwimmersWeb - Daily Link Check Report",
        f"🕒 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        ""
    ]
    for url, status, response_time in report:
        lines.append(f"{url} - {status} - Response Time: {response_time}s")
    return "\n".join(lines)

def send_email(report_text):
    msg = MIMEText(report_text)
    msg["Subject"] = "SwimmersWeb - Daily Link Health Check"
    msg["From"] = os.environ["SMTP_USER"]
    msg["To"] = os.environ["EMAIL_TO"]

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(os.environ["SMTP_USER"], os.environ["SMTP_PASS"])
        server.send_message(msg)

if __name__ == "__main__":
    report = check_links(urls)
    report_text = generate_report(report)
    send_email(report_text)
