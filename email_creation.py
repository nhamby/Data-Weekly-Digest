import os
import pandas as pd
import smtplib
from dotenv import load_dotenv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from datetime import datetime

load_dotenv()
GMAIL_EMAIL_ADDRESS = os.getenv("GMAIL_EMAIL_ADDRESS")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
# ARCHIE_EMAIL_ADDRESS = os.getenv("ARCHIE_EMAIL_ADDRESS")
# ARCHIE_APP_PASSWORD = os.getenv("ARCHIE_APP_PASSWORD")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")

# HEADING_COLOR = "#148afe"
HEADING_COLOR = "#00054B"  # Blue color for headings
LOGO_PATH = "archie_logo_final.png"
LOGO_CID = "archie_logo"
COMPANY_LOGO_ATH = "bsd_logo.png"
COMPANY_LOGO_CID = "bsd_logo"


def create_email_body(df: pd.DataFrame) -> str:
    return f"""
    <html>
      <body
        style="
          margin:0;
          padding:0;
          /* fallback for Outlook */
          background-color:#88bef5;
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
                <!-- ARCHie logo -->
                <tr>
                  <td align="center" style="padding:20px 0 2px;">
                    <img
                      src="cid:{LOGO_CID}"
                      alt="ARCHie logo"
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
                      Good morning and happy Monday, Blue Street!<br/>
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


def send_news_email(df: pd.DataFrame, recipient_email: str):
    sender_email = GMAIL_EMAIL_ADDRESS
    sender_password = GMAIL_APP_PASSWORD
    # smtp_server = "smtp.office365.com"
    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    email_subject = f"Archie's Digest - {datetime.now().strftime('%Y-%m-%d')}"
    email_body_html = create_email_body(df)

    # msg = MIMEText(email_body_html, "html")
    msg = MIMEMultipart("related")
    msg["Subject"] = email_subject
    msg["From"] = sender_email
    msg["To"] = recipient_email

    alt = MIMEMultipart("alternative")
    alt.attach(MIMEText(create_email_body(df), "html"))
    msg.attach(alt)

    with open(LOGO_PATH, "rb") as img_file:
        img = MIMEImage(img_file.read())
        img.add_header("Content-ID", f"<{LOGO_CID}>")
        img.add_header(
            "Content-Disposition", "inline", filename=os.path.basename(LOGO_PATH)
        )
        msg.attach(img)

    with open(COMPANY_LOGO_ATH, "rb") as img_file:
        company_logo = MIMEImage(img_file.read())
        company_logo.add_header("Content-ID", f"<{COMPANY_LOGO_CID}>")
        company_logo.add_header(
            "Content-Disposition", "inline", filename=os.path.basename(COMPANY_LOGO_ATH)
        )
        msg.attach(company_logo)

        try:
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, recipient_email, msg.as_string())
        except Exception as e:
            print(f"Failed to send email: {e}")
