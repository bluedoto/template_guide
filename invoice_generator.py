from datetime import date
import io
import streamlit as st
from PIL import Image as PILImage

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# --- Page Configuration ---
st.set_page_config(
    page_title="Invoice Generator",
    page_icon="📄",
    layout="wide"
)

hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
div[data-testid="stToolbar"] {visibility: hidden; height: 0%; position: fixed;}
div[data-testid="stDecoration"] {visibility: hidden; height: 0%; position: fixed;}
div[data-testid="stStatusWidget"] {visibility: hidden; height: 0%; position: fixed;}

.block-container {
    padding-top: 0.5rem !important;
    padding-bottom: 0.5rem !important;
    max-width: 100% !important;
}

/* Hide default file uploader text instructions to make it clean & modern */
[data-testid="stFileUploader"] section div[data-testid="stMarkdownContainer"] p {
    display: none !important;
}
[data-testid="stFileUploader"] section small {
    display: none !important;
}
[data-testid="stFileUploader"] section {
    background-color: #fafbfc !important;
    border: 1.5px dashed #cbd5e0 !important;
    border-radius: 6px;
    padding: 8px !important;
    min-height: unset !important;
}
[data-testid="stFileUploader"] section:hover {
    border-color: #1a202c !important;
}
[data-testid="stFileUploader"] button {
    background-color: #1a202c !important;
    color: white !important;
    border-radius: 4px;
    font-weight: 500;
    font-size: 11px !important;
    padding: 2px 10px !important;
}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# --- Custom CSS for Ultra-Compact Single-Page Laptop View ---
st.markdown(
    """
    <style>
    .stApp {
        background-color: #f4f5f7;
    }
    .invoice-card {
        background-color: white;
        padding: 12px 18px;
        border-radius: 6px;
        color: #333333;
        box-shadow: 0 2px 12px rgba(0,0,0,0.04);
        border: 1px solid #e2e8f0;
    }
    .top-header {
        text-align: center;
        margin-bottom: 2px;
    }
    .invoice-table-header {
        background-color: #1a202c;
        color: white;
        padding: 5px 10px;
        border-radius: 4px 4px 0 0;
        display: flex;
        align-items: center;
        font-size: 11px;
        font-weight: 600;
    }
    .section-label {
        font-size: 10px;
        font-weight: 600;
        color: #4a5568;
        margin-bottom: 1px;
    }
    /* Compact input sizing */
    div[data-testid="stTextInput"] input, div[data-testid="stDateInput"] input {
        min-height: 28px !important;
        height: 28px !important;
        padding-top: 0px !important;
        padding-bottom: 0px !important;
        font-size: 12px !important;
    }
    div[data-testid="stTextArea"] textarea {
        height: 42px !important;
        min-height: 42px !important;
        font-size: 12px !important;
    }
    div[data-testid="stNumberInput"] input {
        min-height: 28px !important;
        height: 28px !important;
        font-size: 12px !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Initialize Session State ---
if "invoice_items" not in st.session_state:
    st.session_state.invoice_items = [
        {"description": "", "qty": 1, "rate": None}
    ]

def add_item():
    st.session_state.invoice_items.append({"description": "", "qty": 1, "rate": None})

def remove_item(index):
    if len(st.session_state.invoice_items) > 1:
        st.session_state.invoice_items.pop(index)

# --- Top Website Header ---
st.markdown("""
    <div class="top-header">
        <h1 style="color: #1a202c; font-weight: 800; font-size: 1.3rem; margin-bottom: 0px;">Free Invoice Template</h1>
        <p style="color: #718096; font-size: 0.8rem; margin: 0;">Create professional invoices with one click!</p>
    </div>
""", unsafe_allow_html=True)

# --- Centered Layout Columns Optimized for Single-Page View ---
_, center_app_col, _ = st.columns([0.5, 4.0, 0.5])

# --- CENTER INVOICE APP CONTAINER ---
with center_app_col:
    with st.container():
        st.markdown('<div class="invoice-card">', unsafe_allow_html=True)

        top_left, top_right = st.columns([1, 1])
        with top_left:
            st.markdown("<p class='section-label'>Upload Logo</p>", unsafe_allow_html=True)
            uploaded_logo = st.file_uploader("Upload Logo", type=["png", "jpg", "jpeg"], label_visibility="collapsed")
            if uploaded_logo:
                st.image(uploaded_logo, width=80)

        with top_right:
            st.markdown("""
                <div style="text-align: left;">
                    <h1 style="color: #1a202c; letter-spacing: 2px; margin: 0; font-size: 1.6rem;">INVOICE</h1>
                </div>
            """, unsafe_allow_html=True)
            st.markdown("<p class='section-label' style='text-align: left;'>Invoice Number</p>", unsafe_allow_html=True)
            invoice_number = st.text_input("Invoice #", value="", placeholder="Invoice number", label_visibility="collapsed")

        st.markdown("<div style='margin-bottom: 4px;'></div>", unsafe_allow_html=True)

        col_from, col_dates = st.columns(2)
        with col_from:
            st.markdown("<p class='section-label'>From</p>", unsafe_allow_html=True)
            sender_address = st.text_area("Who is this from?", value="", placeholder="Who is this from?", label_visibility="collapsed")
        with col_dates:
            c_d1, c_d2 = st.columns([1, 1.2])
            with c_d1:
                st.markdown("<p class='section-label'>Date</p>", unsafe_allow_html=True)
                invoice_date = st.date_input("Date", date.today(), label_visibility="collapsed")
                st.markdown("<p class='section-label'>Payment Terms</p>", unsafe_allow_html=True)
                payment_terms = st.text_input("Payment Terms", value="", placeholder="", label_visibility="collapsed")
            with c_d2:
                st.markdown("<p class='section-label'>Due Date</p>", unsafe_allow_html=True)
                due_date = st.date_input("Due Date", date.today(), label_visibility="collapsed")
                st.markdown("<p class='section-label'>PO Number</p>", unsafe_allow_html=True)
                po_number = st.text_input("PO Number", value="", placeholder="", label_visibility="collapsed")

        col_bill, col_ship = st.columns(2)
        with col_bill:
            st.markdown("<p class='section-label'>Bill To</p>", unsafe_allow_html=True)
            client_address = st.text_area("Bill To", value="", placeholder="Who is this to?", label_visibility="collapsed")
        with col_ship:
            st.markdown("<p class='section-label'>Ship To (optional)</p>", unsafe_allow_html=True)
            ship_address = st.text_area("Ship To", value="", placeholder="", label_visibility="collapsed")

        st.markdown("<div style='margin-bottom: 6px;'></div>", unsafe_allow_html=True)

        col_widths = [3.5, 1.0, 1.0, 1.0, 0.4]

        st.markdown("""
            <div class="invoice-table-header">
                <div style="flex: 3.5;">Item</div>
                <div style="flex: 1.0; text-align: center;">Quantity</div>
                <div style="flex: 1.0; text-align: center;">Rate</div>
                <div style="flex: 1.0; text-align: right;">Amount</div>
                <div style="flex: 0.4;"></div>
            </div>
        """, unsafe_allow_html=True)

        subtotal = 0.0
        for i, item in enumerate(st.session_state.invoice_items):
            row_cols = st.columns(col_widths)
            with row_cols[0]:
                item["description"] = st.text_input(f"Desc {i}", item["description"], placeholder="Description...", label_visibility="collapsed", key=f"desc_{i}")
            with row_cols[1]:
                item["qty"] = st.number_input(f"Qty {i}", value=item["qty"] if item["qty"] is not None else 1, placeholder="1", label_visibility="collapsed", key=f"qty_{i}")
            with row_cols[2]:
                item["rate"] = st.number_input(f"Rate {i}", value=item["rate"], placeholder="0.00", label_visibility="collapsed", key=f"rate_{i}")
            with row_cols[3]:
                q_val = item["qty"] if item["qty"] is not None else 1
                r_val = item["rate"] if item["rate"] is not None else 0.0
                line_total = q_val * r_val
                subtotal += line_total
                st.markdown(f"<div style='padding-top: 5px; text-align: right; font-weight: 500; font-size: 12px;'>${line_total:,.2f}</div>", unsafe_allow_html=True)
            with row_cols[4]:
                if st.button("✕", key=f"del_{i}", help="Remove row"):
                    remove_item(i)
                    st.rerun()

        if st.button("+ Line Item", use_container_width=True):
            add_item()
            st.rerun()

        st.markdown("<hr style='margin: 8px 0; border: none; border-top: 1px solid #edf2f7;'>", unsafe_allow_html=True)

        col_notes, col_totals = st.columns([1.2, 1])

        with col_notes:
            st.markdown("<p class='section-label'>Notes</p>", unsafe_allow_html=True)
            notes = st.text_area("Notes", value="", placeholder="Notes...", label_visibility="collapsed")

            st.markdown("<p class='section-label'>Terms</p>", unsafe_allow_html=True)
            terms = st.text_area("Terms", value="", placeholder="Terms...", label_visibility="collapsed")

        with col_totals:
            tax_rate = st.number_input("Tax Rate (%)", value=None, placeholder="0.0")
            shipping_fee = st.number_input("Shipping Fee", value=None, placeholder="0.00")

            t_rate_val = tax_rate if tax_rate is not None else 0.0
            s_fee_val = shipping_fee if shipping_fee is not None else 0.0

            tax_amount = subtotal * (t_rate_val / 100.0)
            total_amount = subtotal + tax_amount + s_fee_val

            st.markdown(f"""
                <div style="font-size: 11px; color: #4a5568; margin-top: 2px;">
                    <div style="display: flex; justify-content: space-between; padding: 2px 0;">
                        <span>Subtotal</span><span>${subtotal:,.2f}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; padding: 2px 0;">
                        <span>Tax ({t_rate_val}%)</span><span>${tax_amount:,.2f}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; padding: 2px 0;">
                        <span>Shipping Fee</span><span>${s_fee_val:,.2f}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; padding: 3px 0; font-size: 12px; font-weight: bold; color: #1a202c; border-top: 1px solid #cbd5e0; margin-top: 2px;">
                        <span>Total</span><span>${total_amount:,.2f}</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)

        amount_paid = st.number_input("Amount Paid", value=None, placeholder="0.00")
        a_paid_val = amount_paid if amount_paid is not None else 0.0
        balance_due = total_amount - a_paid_val

        st.markdown(f"""
            <div style="display: flex; justify-content: space-between; padding: 5px 0; font-size: 12px; font-weight: bold; color: #1a202c; border-top: 2px solid #1a202c; margin-top: 3px;">
                <span>Balance Due</span><span>${balance_due:,.2f}</span>
            </div>
        """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        def generate_pdf():
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
            story = []
            styles = getSampleStyleSheet()

            right_style = ParagraphStyle(
                'RightText',
                parent=styles['Normal'],
                alignment=2
            )

            left_title_style = ParagraphStyle(
                'LeftTitle',
                parent=styles['Normal'],
                fontName='Helvetica-Bold',
                fontSize=26,
                leading=30,
                alignment=0
            )

            if uploaded_logo is not None:
                try:
                    uploaded_logo.seek(0)
                    pil_img = PILImage.open(uploaded_logo)

                    max_dim = 100.0
                    w, h = pil_img.size
                    if w > h:
                        display_w = max_dim
                        display_h = max_dim * (h / float(w))
                    else:
                        display_h = max_dim
                        display_w = max_dim * (w / float(h))

                    img_buffer = io.BytesIO()
                    pil_img.save(img_buffer, format="PNG")
                    img_buffer.seek(0)

                    logo_element = RLImage(img_buffer, width=display_w, height=display_h)
                except Exception:
                    logo_element = Paragraph("INVOICE", left_title_style)
            else:
                logo_element = Paragraph("INVOICE", left_title_style)

            display_inv_num = invoice_number if invoice_number else "Invoice number"
            header_data = [
                [logo_element,
                 Paragraph(f"<b>INVOICE</b><br/><b>Invoice Number:</b> {display_inv_num}<br/><b>Date:</b> {invoice_date}<br/><b>Due Date:</b> {due_date}<br/><b>PO Number:</b> {po_number}", right_style)]
            ]
            header_table = Table(header_data, colWidths=[3.25 * inch, 3.25 * inch])
            header_table.setStyle(TableStyle([
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('ALIGN', (1,0), (1,0), 'RIGHT'),
            ]))
            story.append(header_table)
            story.append(Spacer(1, 15))

            final_sender = sender_address if sender_address else "Who is this from?"
            final_client = client_address if client_address else "Who is this to?"
            address_data = [
                [Paragraph(f"<b>From:</b><br/>{final_sender.replace(chr(10), '<br/>')}", styles['Normal']),
                 Paragraph(f"<b>Bill To:</b><br/>{final_client.replace(chr(10), '<br/>')}", right_style)]
            ]
            address_table = Table(address_data, colWidths=[3.25 * inch, 3.25 * inch])
            address_table.setStyle(TableStyle([
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('ALIGN', (1,0), (1,0), 'RIGHT'),
            ]))
            story.append(address_table)
            story.append(Spacer(1, 20))

            table_data = [["Description", "Qty", "Unit Price", "Amount"]]
            for item in st.session_state.invoice_items:
                q_val = item["qty"] if item["qty"] is not None else 1
                r_val = item["rate"] if item["rate"] is not None else 0.0
                line_total = q_val * r_val
                desc_text = item["description"] if item["description"] else "Description of item/service..."
                q_text = str(q_val)
                table_data.append([desc_text, q_text, f"${r_val:,.2f}", f"${line_total:,.2f}"])

            item_table = Table(table_data, colWidths=[3.5 * inch, 1.0 * inch, 1.0 * inch, 1.0 * inch])
            item_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1a202c")),
                ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                ('ALIGN', (1,0), (-1,-1), 'CENTER'),
                ('ALIGN', (3,0), (3,-1), 'RIGHT'),
                ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
            ]))
            story.append(item_table)
            story.append(Spacer(1, 15))

            totals_data = [
                ["Subtotal:", f"${subtotal:,.2f}"],
                [f"Tax ({t_rate_val}%):", f"${tax_amount:,.2f}"],
                ["Shipping Fee:", f"${s_fee_val:,.2f}"],
                ["Total:", f"${total_amount:,.2f}"],
                ["Amount Paid:", f"${a_paid_val:,.2f}"],
                ["Balance Due:", f"${balance_due:,.2f}"]
            ]
            totals_table = Table(totals_data, colWidths=[5.5 * inch, 1.0 * inch])
            totals_table.setStyle(TableStyle([
                ('ALIGN', (0,0), (0,-1), 'RIGHT'),
                ('ALIGN', (1,0), (1,-1), 'RIGHT'),
                ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
                ('LINEABOVE', (0,-1), (-1,-1), 1, colors.black),
            ]))
            story.append(totals_table)
            story.append(Spacer(1, 20))

            final_notes = notes if notes else "Notes - any relevant information not already covered"
            final_terms = terms if terms else "Terms and conditions - late fees, payment methods, delivery schedule"
            story.append(Paragraph(f"<b>Notes:</b><br/>{final_notes}<br/><br/><b>Terms:</b><br/>{final_terms}", styles['Normal']))

            doc.build(story)
            buffer.seek(0)
            return buffer.getvalue()

    pdf_data = generate_pdf()

    # --- Centered Small Download Button ---
    st.markdown("<div style='margin-top: 4px;'></div>", unsafe_allow_html=True)
    col_left, col_center, col_right = st.columns([1, 1.2, 1])
    with col_center:
        st.download_button(
            label="⬇ Download PDF",
            data=pdf_data,
            file_name=f"invoice_{invoice_number if invoice_number else 'invoice'}.pdf",
            mime="application/pdf",
            use_container_width=True,
            type="primary"
        )