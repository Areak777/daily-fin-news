# -*- coding: utf-8 -*-
"""
每日财经新闻盘前纪要 - 邮件发送脚本
从 Markdown 报告生成 HTML 邮件并发送
"""
import os
import sys
import re
import json
import glob
import requests
import argparse
from datetime import datetime


def read_md(filepath):
    """读取 Markdown 文件，支持通配符"""
    files = glob.glob(filepath)
    if not files:
        print(f"ERROR: No file found matching: {filepath}")
        sys.exit(1)
    target = files[0]
    print(f"Reading: {target}")
    with open(target, "r", encoding="utf-8") as f:
        return f.read(), target


def md_table_to_html(table_str):
    """将 Markdown 表格转为 HTML 表格"""
    lines = [l.strip() for l in table_str.strip().split("\n") if l.strip()]
    if len(lines) < 2:
        return ""
    # Parse header
    headers = [c.strip() for c in lines[0].split("|")[1:-1]]
    html = "<table style='width:100%;border-collapse:collapse;margin:12px 0;font-size:13px'>"
    # Header row
    html += "<tr style='background:#f0f4f8'>"
    for h in headers:
        html += f"<th style='padding:8px 10px;text-align:left;border-bottom:2px solid #ddd;font-weight:600;color:#333'>{h}</th>"
    html += "</tr>"
    # Data rows (skip separator line)
    for line in lines[2:]:
        cells = [c.strip() for c in line.split("|")[1:-1]]
        html += "<tr style='border-bottom:1px solid #eee'>"
        for i, c in enumerate(cells):
            color = "#e74c3c" if "涨" in c or "+" in c or "红" in c else "#27ae60" if "跌" in c or "-" in c else "#333"
            html += f"<td style='padding:8px 10px;color:{color}'>{c}</td>"
        html += "</tr>"
    html += "</table>"
    return html


def md_to_email_html(md_content, today_str):
    """将 Markdown 报告转为邮件 HTML"""
    lines = md_content.split("\n")
    
    # Extract title
    title = "每日财经新闻盘前纪要"
    for l in lines:
        if l.startswith("# "):
            title = l.replace("# ", "").strip()
            break
    
    # Extract subtitle / date info
    subtitle = today_str
    meta_lines = []
    for l in lines:
        if l.startswith(">"):
            meta_lines.append(l.replace(">", "").strip())
    
    # Build sections
    sections = []
    current_section = None
    current_content = []
    current_subsection = None
    current_sub_content = []
    
    for l in lines:
        if re.match(r'^##\s+', l):
            if current_sub_content:
                if current_section is not None:
                    sections.append((current_section, current_content))
                current_section = None
            if current_content:
                sections.append((current_subsection, current_sub_content))
            current_subsection = l.replace("## ", "").strip()
            current_sub_content = []
        elif re.match(r'^###\s+', l):
            if current_sub_content:
                if current_section is not None:
                    sections.append((current_section, current_content))
                    current_section = None
                sections.append((current_subsection, current_sub_content))
            current_section = l.replace("### ", "").strip()
            current_content = []
        elif re.match(r'^---', l):
            if current_content and current_section:
                pass
        elif current_subsection is not None:
            current_sub_content.append(l)
        elif current_section is not None:
            current_content.append(l)
    
    # Flush remaining
    if current_sub_content:
        sections.append((current_subsection, current_sub_content))
    if current_content and current_section:
        sections.append((current_section, current_content))
    
    # Convert sections to HTML
    section_colors = [
        ("一、三大报精华", "#2980b9"),
        ("二、盘前个股重要公告", "#e74c3c"),
        ("三、热门题材", "#f39c12"),
        ("四、隔夜外盘", "#8e44ad"),
        ("五、重要事件", "#27ae60"),
        ("六、昨日热点", "#d35400"),
        ("七、下周关注", "#16a085"),
    ]
    
    def get_color(name):
        for pattern, color in section_colors:
            if pattern in name:
                return color
        return "#2c3e50"
    
    body_html = ""
    for sec_title, sec_lines in sections:
        color = get_color(sec_title)
        content_html = ""
        
        # Check if contains tables
        joined = "\n".join(sec_lines)
        tables = re.split(r'\n(?=\|)', joined)
        
        if "|" in joined:
            # Has table content
            # Extract text before first table
            pre_text = []
            in_table = False
            table_lines = []
            table_blocks = []
            
            for l in sec_lines:
                stripped = l.strip()
                if stripped.startswith("|"):
                    if not in_table:
                        in_table = True
                        table_lines = [stripped]
                    else:
                        table_lines.append(stripped)
                else:
                    if in_table:
                        table_blocks.append("\n".join(table_lines))
                        table_lines = []
                        in_table = False
                    pre_text.append(l)
            
            if in_table:
                table_blocks.append("\n".join(table_lines))
            
            for t in pre_text:
                if t.strip():
                    if t.strip().startswith("- "):
                        content_html += f'<li style="margin:4px 0;padding-left:4px;color:#444">{t.strip()[2:]}</li>'
                    elif t.strip().startswith("  - "):
                        content_html += f'<li style="margin:2px 0 2px 16px;color:#666;font-size:13px">{t.strip()[4:]}</li>'
                    elif re.match(r'^\d+\.\s', t.strip()):
                        content_html += f'<p style="margin:6px 0;color:#444;line-height:1.7">{t.strip()}</p>'
                    elif t.strip().startswith("**") and t.strip().endswith("**"):
                        content_html += f'<p style="margin:8px 0 4px;font-weight:600;color:#222">{t.strip()}</p>'
                    elif t.strip():
                        content_html += f'<p style="margin:4px 0;color:#444;line-height:1.6">{t.strip()}</p>'
            
            for tb in table_blocks:
                content_html += md_table_to_html(tb)
        else:
            for l in sec_lines:
                stripped = l.strip()
                if not stripped:
                    continue
                if stripped.startswith("- "):
                    content_html += f'<li style="margin:4px 0;padding-left:4px;color:#444">{stripped[2:]}</li>'
                elif stripped.startswith("  - "):
                    content_html += f'<li style="margin:2px 0 2px 16px;color:#666;font-size:13px">{stripped[4:]}</li>'
                elif re.match(r'^\d+\.\s', stripped):
                    content_html += f'<p style="margin:6px 0;color:#444;line-height:1.7">{stripped}</p>'
                elif stripped.startswith("**") and stripped.endswith("**"):
                    content_html += f'<p style="margin:8px 0 4px;font-weight:600;color:#222">{stripped}</p>'
                elif stripped:
                    content_html += f'<p style="margin:4px 0;color:#444;line-height:1.6">{stripped}</p>'
        
        if content_html:
            body_html += f"""
            <div style="margin-bottom:24px">
                <h2 style="font-size:17px;color:{color};margin:0 0 12px;padding-bottom:8px;border-bottom:2px solid {color}">{sec_title}</h2>
                <div style="font-size:14px;line-height:1.8">{content_html}</div>
            </div>"""
    
    # Wrap in email template
    html = f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;background:#f5f6fa;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Microsoft YaHei',sans-serif">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f5f6fa;padding:20px 0">
<tr><td align="center">
<table width="680" cellpadding="0" cellspacing="0" style="background:#fff;border-radius:8px;overflow:hidden;margin:0 16px">
    <tr><td style="background:linear-gradient(135deg,#1a1a2e,#0f3460);padding:32px 28px;text-align:center">
        <h1 style="color:#fff;font-size:22px;margin:0 0 6px">{title}</h1>
        <p style="color:rgba(255,255,255,.7);font-size:13px;margin:0">{subtitle}</p>
    </td></tr>
    <tr><td style="padding:24px 28px">
        {body_html}
    </td></tr>
    <tr><td style="padding:16px 24px;text-align:center;font-size:11px;color:#bbb;border-top:1px solid #f0f0f0">
        由 GitHub Actions 自动生成 | 数据来源公开搜索 | 仅供参考，不构成投资建议
    </td></tr>
</table>
</td></tr>
</table>
</body></html>"""
    
    return html


def send_email(api_key, to_email, subject, html_content, from_email="onboarding@resend.dev"):
    """通过 Resend API 发送邮件"""
    resp = requests.post(
        "https://api.resend.com/emails",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        json={
            "from": f"财经新闻 <{from_email}>",
            "to": [to_email],
            "subject": subject,
            "html": html_content,
        },
        timeout=30,
    )
    return resp


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--md", required=True, help="Markdown report file path")
    args = parser.parse_args()
    
    api_key = os.environ.get("RESEND_API_KEY", "")
    to_email = os.environ.get("EMAIL_TO", "")
    from_email = os.environ.get("EMAIL_FROM", "onboarding@resend.dev")
    
    if not api_key or not to_email:
        print("ERROR: RESEND_API_KEY and EMAIL_TO must be set")
        sys.exit(1)
    
    # Read markdown (returns content and actual file path)
    md_content, actual_path = read_md(args.md)
    
    # Get date from filename or content
    today_str = datetime.now().strftime("%Y年%m月%d日")
    
    # Convert to email HTML
    html = md_to_email_html(md_content, today_str)
    
    # Save HTML for preview
    html_path = actual_path.replace(".md", "_email.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Email HTML saved: {html_path}")
    
    # Send email
    subject = f"每日财经新闻盘前纪要 {today_str}"
    print(f"Sending email to {to_email}...")
    resp = send_email(api_key, to_email, subject, html, from_email)
    
    if resp.status_code == 200:
        print(f"Email sent successfully! ID: {resp.json().get('id')}")
    else:
        print(f"Email failed: {resp.status_code} {resp.text}")
        sys.exit(1)


if __name__ == "__main__":
    main()
