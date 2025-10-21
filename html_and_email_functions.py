"""HTML email generation and sending functions for digest delivery."""

import logging
import os
import smtplib
from datetime import datetime
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

import pandas as pd
import pyperclip
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

load_dotenv()
GMAIL_EMAIL_ADDRESS = os.getenv("GMAIL_EMAIL_ADDRESS")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")

RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")

HEADING_COLOR = "#00054B"
LOGO_PATH = "logos/archie_logo.png"
LOGO_CID = "archie_logo"
COMPANY_LOGO_PATH = "logos/bsd_logo.png"
COMPANY_LOGO_CID = "bsd_logo"


def create_email_body(df: pd.DataFrame) -> str:

    return f"""
    <html>
      <body
        style="
          margin:0;
          padding:0;
          /* fallback for Outlook */
          background-color:transparent;
          /* modern clients */
          background-image: linear-gradient(135deg, #EAF3FF 0%, #FFFFFF 100%);
          font-family:'Inter',sans-serif;
        "
      >
        <!-- outer wrapper to center everything -->
        <table
          width="100%" cellpadding="0" cellspacing="0"
          style="min-width:100%;"
        >
          <tr>
            <td align="center" style="padding:40px 0;">
              
              <!-- main container -->
              <table
                width="600" cellpadding="0" cellspacing="0"
                style="
                  background-color:#FFFFFF;
                  border-radius:8px;
                  overflow:hidden;
                  /* subtle shadow in clients that support it */
                  box-shadow:0 4px 12px rgba(0,0,0,0.05);
                "
              >
                <!-- Archie logo -->
                <tr>
                  <td align="center" style="padding:20px 0 2px;">
                    <img
                      src="cid:{LOGO_CID}"
                      alt="Archie logo"
                      width="250"
                      style="display:block; border:none;"
                    />
                  </td>
                </tr>

                <!-- gradient accent bar -->
                <tr>
                  <td style="padding:0;">
                    <div style="
                      height:3px;
                      background: linear-gradient(90deg, #0056b3, #4A90E2);
                    "></div>
                  </td>
                </tr>

                <!-- main heading -->
                <tr>
                  <td align="center" style="padding:20px;">
                    <h1 style="
                      margin:0;
                      color: {HEADING_COLOR};
                      font-size:35px;
                      font-weight:700;
                    ">
                      Archie's Weekly Digest 🥣
                    </h1>
                  </td>
                </tr>

                <!-- sub‐headline -->
                <tr>
                  <td align="center" style="padding:0 20px 30px;">
                    <p style="
                      margin:0;
                      color: #132770;
                      font-size:16px;
                      line-height:1.5;
                    ">
                      Good morning and happy {datetime.now().strftime('%A')}, Blue Street!<br/>
                      I've fetched this week's most interesting news in the tech & data space.<br/>
                        Until next week, enjoy the read!<br/>
                        <strong>— Archie</strong>
                    </p>
                  </td>
                </tr>

                <!-- articles w/ bone emoji + gold stripe -->
                {"".join([
                  f'''
                  <tr>
                    <td style="padding:0 20px 20px;">
                      <table width="100%" cellpadding="0" cellspacing="0" style="
                        background-color:#CFE9FF;
                        border-radius:6px;
                        padding:15px;
                        border-left:6px solid #FFD700;
                      ">
                        <tr>
                          <td>
                            <h2 style="margin:0 0 8px; font-size:18px; color:#00054B;">
                              🦴&nbsp;
                              <a href="{row['url']}" style="color:#00054B; text-decoration:none;">
                                {row['title']}
                              </a>
                            </h2>
                            <p style="margin:0 0 8px; color:#00054B; font-size:14px;">
                              <strong>Source:</strong> {row['source']}
                            </p>
                            <p style="margin:0; color:#00054B; font-size:15px; line-height:1.4;">
                              {row['summary']}
                            </p>
                          </td>
                        </tr>
                      </table>
                    </td>
                  </tr>
                  ''' for _, row in df.iterrows()
                ])}

                <!-- company logo footer -->
                <tr>
                  <td align="center" style="padding:30px 0 10px; background-color:#FFFFFF;">
                    <img
                      src="cid:{COMPANY_LOGO_CID}"
                      alt="Company logo"
                      width="100"
                      style="display:block; border:none;"
                    />
                  </td>
                </tr>

                <!-- bottom social / spacer row (optional) -->
                <tr>
                  <td align="center" style="padding:10px; font-size:12px; color:#888888;">
                    <a href="https://www.linkedin.com/company/blue-street-data/posts/?feedView=all" style="margin:0 5px; text-decoration:none;">🔗 LinkedIn</a>
                  </td>
                </tr>
              </table>

            </td>
          </tr>
        </table>
      </body>
    </html>
    """


def create_email_body_CRM(df: pd.DataFrame, HEADING_COLOR: str = "#0056b3") -> str:

    outer_wrapper_table_style = "width:100%; border-collapse:collapse; mso-table-lspace:0pt; mso-table-rspace:0pt; background-color:transparent; font-family:'Inter',sans-serif;"
    outer_td_style = (
        "padding-top:0px; padding-bottom:0px; text-align:center; vertical-align:top;"
    )

    main_container_table_style = "width:600px; background-color:#FFFFFF; border-collapse:collapse; mso-table-lspace:0pt; mso-table-rspace:0pt;"

    main_heading_td_style = "padding-top:20px; padding-right:20px; padding-bottom:20px; padding-left:20px; text-align:center;"
    main_heading_h1_style = f"margin-top:0; margin-right:0; margin-bottom:0; margin-left:0; color:{HEADING_COLOR}; font-size:35px; font-weight:700; line-height:1.2;"
    sub_headline_td_style = "padding-top:0; padding-right:20px; padding-bottom:30px; padding-left:20px; text-align:center;"
    sub_headline_p_style = "margin-top:0; margin-right:0; margin-bottom:0; margin-left:0; color:#132770; font-size:16px; line-height:1.5;"

    article_td_outer_style = (
        "padding-top:0; padding-right:20px; padding-bottom:20px; padding-left:20px;"
    )
    article_table_style = "width:100%; background-color:#CFE9FF; border-collapse:collapse; mso-table-lspace:0pt; mso-table-rspace:0pt; border-left:6px solid #FFD700;"
    article_content_td_style = (
        "padding-top:15px; padding-right:15px; padding-bottom:15px; padding-left:15px;"
    )
    article_heading_h2_style = "margin-top:0; margin-right:0; margin-bottom:8px; margin-left:0; font-size:18px; color:#00054B; line-height:1.3;"
    article_link_style = "color:#00054B; text-decoration:none;"
    article_source_p_style = "margin-top:0; margin-right:0; margin-bottom:8px; margin-left:0; color:#00054B; font-size:14px; line-height:1.4;"
    article_summary_p_style = "margin-top:0; margin-right:0; margin-bottom:0; margin-left:0; color:#00054B; font-size:15px; line-height:1.4;"

    intro = f"""
    Good morning and happy {datetime.now().strftime('%A')}!<br/>
    I've fetched this week's most interesting news in the tech & data space.<br/>
    Until next week, enjoy the read!<br/>
    """

    return f"""
        <table border="0" cellpadding="0" cellspacing="0" role="presentation" style="{outer_wrapper_table_style}">
          <tr>
            <td align="center" valign="top" style="{outer_td_style}">
              
              <table border="0" cellpadding="0" cellspacing="0" role="presentation" style="{main_container_table_style}" width="600">

                <tr>
                  <td align="center" style="{main_heading_td_style}">
                    <h1 style="{main_heading_h1_style}">
                      Archie's Weekly Digest
                    </h1>
                  </td>
                </tr>

                <tr>
                  <td align="center" style="{sub_headline_td_style}">
                    <p style="{sub_headline_p_style}">
                      {intro}
                      <strong>&mdash; Archie</strong>
                    </p>
                  </td>
                </tr>

                {"".join([
                  f'''
                  <tr>
                    <td style="{article_td_outer_style}">
                      <table border="0" cellpadding="0" cellspacing="0" role="presentation" style="{article_table_style}" width="100%">
                        <tr>
                          <td style="{article_content_td_style}">
                            <h2 style="{article_heading_h2_style}">
                              <a href="{row['url']}" style="{article_link_style}">
                                {row['title']}
                              </a>
                            </h2>
                            <p style="{article_source_p_style}">
                              <strong>Source:</strong> {row['source']}
                            </p>
                            <p style="{article_summary_p_style}">
                              {row['summary']}
                            </p>
                          </td>
                        </tr>
                      </table>
                    </td>
                  </tr>
                  ''' for _, row in df.iterrows()
                ])}
              </table>
              
            </td>
          </tr>
        </table>
    """


def export_standalone_html(
    df: pd.DataFrame,
    output_dir: str = "archives_html",
    timestamp: str = datetime.now().strftime("%Y-%m-%d"),
) -> str:

    os.makedirs(output_dir, exist_ok=True)

    html_content = create_email_body_CRM(df)

    pyperclip.copy(html_content)

    filename = f"archie_digest_{timestamp}.html"
    filepath = os.path.join(output_dir, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html_content)

    return filepath


def send_news_email(df: pd.DataFrame, recipient_email: str):

    sender_email = GMAIL_EMAIL_ADDRESS
    sender_password = GMAIL_APP_PASSWORD

    if not sender_email or not sender_password:
        raise RuntimeError(
            "GMAIL_EMAIL_ADDRESS or GMAIL_APP_PASSWORD is not set in .env file"
        )

    # smtp_server = "smtp.office365.com"
    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    email_subject = f"Archie's Digest - {datetime.now().strftime('%d %B %Y')}"
    email_body_html = create_email_body(df)

    msg = MIMEMultipart("related")
    msg["Subject"] = email_subject
    msg["From"] = sender_email
    msg["To"] = recipient_email

    alt = MIMEMultipart("alternative")
    alt.attach(MIMEText(email_body_html, "html"))
    msg.attach(alt)

    with open(LOGO_PATH, "rb") as img_file:
        img = MIMEImage(img_file.read())
        img.add_header("Content-ID", f"<{LOGO_CID}>")
        img.add_header(
            "Content-Disposition", "inline", filename=os.path.basename(LOGO_PATH)
        )
        msg.attach(img)

    with open(COMPANY_LOGO_PATH, "rb") as img_file:
        company_logo = MIMEImage(img_file.read())
        company_logo.add_header("Content-ID", f"<{COMPANY_LOGO_CID}>")
        company_logo.add_header(
            "Content-Disposition",
            "inline",
            filename=os.path.basename(COMPANY_LOGO_PATH),
        )
        msg.attach(company_logo)

        try:
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, recipient_email, msg.as_string())

        except Exception as e:
            print(f"failed to send email: {e}")
