import base64
import os
import pandas as pd
import pyperclip
from datetime import datetime
from email_creation import create_email_body, LOGO_PATH, COMPANY_LOGO_ATH


def export_standalone_html(df: pd.DataFrame, output_dir: str = "html_archives") -> str:

    os.makedirs(output_dir, exist_ok=True)

    html_content = create_email_body(df)

    standalone_html = _convert_images_to_base64(html_content)

    timestamp = datetime.now().strftime("%Y-%m-%d")
    filename = f"archie_digest_{timestamp}.html"
    filepath = os.path.join(output_dir, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(standalone_html)

    return filepath


def get_html_for_crm(df: pd.DataFrame) -> str:

    html_content = create_email_body(df)

    crm_html = _remove_embedded_images(html_content)

    return crm_html


def export_html_to_clipboard(df: pd.DataFrame) -> bool:
    html_content = get_html_for_crm(df)
    pyperclip.copy(html_content)
    return html_content


def _convert_images_to_base64(html_content: str) -> str:
    try:
        with open(LOGO_PATH, "rb") as img_file:
            logo_data = base64.b64encode(img_file.read()).decode("utf-8")
            logo_data_uri = f"data:image/png;base64,{logo_data}"

        with open(COMPANY_LOGO_ATH, "rb") as img_file:
            company_logo_data = base64.b64encode(img_file.read()).decode("utf-8")
            company_logo_data_uri = f"data:image/png;base64,{company_logo_data}"

        html_content = html_content.replace(
            'src="cid:archie_logo"', f'src="{logo_data_uri}"'
        )
        html_content = html_content.replace(
            'src="cid:bsd_logo"', f'src="{company_logo_data_uri}"'
        )

    except FileNotFoundError as e:
        print(f"Warning: Image file not found: {e}")
        html_content = _remove_embedded_images(html_content)

    return html_content


def _remove_embedded_images(html_content: str) -> str:
    html_content = html_content.replace(
        f'<img\n                      src="cid:archie_logo"\n                      alt="ARCHie logo"\n                      width="250"\n                      style="display:block; border:none;"\n                    />',
        '<h1 style="margin:0; color:#00054B; font-size:28px; font-weight:700;">ARCHie</h1>',
    )

    html_content = html_content.replace(
        f'<img\n                      src="cid:bsd_logo"\n                      alt="Company logo"\n                      width="100"\n                      style="display:block; border:none;"\n                    />',
        '<p style="margin:0; color:#888; font-size:14px;">Blue Street Data</p>',
    )

    return html_content
