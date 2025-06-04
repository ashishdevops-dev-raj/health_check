import os
import requests
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import csv

urls = [
    "https://swimmersweb.com/",
        "https://swimmersweb.com/fake-broken-link",
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

def try_request(url, retries=2):
    headers = {"User-Agent": "Mozilla/5.0 (LinkCheckerBot/1.0)"}
    for attempt in range(retries + 1):
        try:
            return requests.get(url, headers=headers, timeout=10)
        except requests.RequestException as e:
            if attempt == retries:
                raise
    return None

def check_links(urls):
    report = []
    for url in urls:
        try:
            response = try_request(url)
            status = f"{response.status_code} OK" if response.status_code in (200, 301, 302) else f"{response.status_code} ERROR"
            report.append((url, status, response.elapsed.total_seconds()))
        except requests.exceptions.RequestException as e:
            report.append((url, f"RequestError: {type(e).__name__} - {e}", "-"))
    return report

def generate_html_report(report):
    date_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    rows = ""
    error_count = 0
    total_time = 0
    time_count = 0

    for url, status, response_time in report:
        color = "#28a745" if "OK" in status else "#dc3545"
        if "ERROR" in status or "RequestError" in status:
            error_count += 1
        if isinstance(response_time, (int, float)):
            total_time += response_time
            time_count += 1
        rows += f"<tr><td>{url}</td><td style='color:{color}'>{status}</td><td>{response_time}s</td></tr>"

    avg_time = round(total_time / time_count, 3) if time_count else "-"
    summary = f"""
    <p><strong>📊 SwimmersWeb - Daily Link Check Report</strong><br>
    🕒 Date: {date_str}<br>
    ✅ Healthy Links: {len(report) - error_count}<br>
    ❌ Errors: {error_count}<br>
    ⏱️ Avg Response Time: {avg_time}s</p>
    """

    html = f"""
    <html>
    <body>
    {summary}
    <table border='1' cellpadding='5' cellspacing='0'>
        <tr><th>URL</th><th>Status</th><th>Response Time</th></tr>
        {rows}
    </table>
    </body>
    </html>
    """
    return html, error_count > 0

def write_csv(report):
    with open("report.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["URL", "Status", "Response Time"])
        writer.writerows(report)

def send_email(html_report):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "❗ SwimmersWeb - Link Health Check Failures"
    msg["From"] = os.environ["SMTP_USER"]
    msg["To"] = os.environ["EMAIL_TO"]

    mime_html = MIMEText(html_report, "html")
    msg.attach(mime_html)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(os.environ["SMTP_USER"], os.environ["SMTP_PASS"])
        server.send_message(msg)

if __name__ == "__main__":
    report = check_links(urls)
    write_csv(report)

    html_report, has_errors = generate_html_report(report)

    # Only send email if there's an error
    if has_errors:
        send_email(html_report)

    # Optionally log for GitHub artifact or local archive
    with open("link_check_log.txt", "a") as log:
        log.write(f"{datetime.now()} - Errors: {has_errors}\n")
