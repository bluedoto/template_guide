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
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# --- Custom CSS for Clean Layout & Solid Header Bar ---
st.markdown(
    """
    <style>
    .stApp {
        background-color: #f4f5f7;
    }
    .invoice-card {
        background-color: white;
        padding: 40px;
        border-radius: 6px;
        color: #333333;
        box-shadow: 0 4px 25px rgba(0,0,0,0.05);
        border: 1px solid #e2e8f0;
    }
    .top-header {
        text-align: center;
        margin-bottom: 30px;
    }
    .invoice-table-header {
        background-color: #1a202c;
        color: white;
        padding: 10px 15px;
        border-radius: 4px 4px 0 0;
        display: flex;
        align-items: center;
        font-size: 13px;
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Initialize Session State ---
if "invoice_items" not in st.session_state:
    st.session_state.invoice_items = [
        {"description": "", "qty": 1, "rate": 0.0}
    ]

def add_item():
    st.session_state.invoice_items.append({"description": "", "qty": 1, "rate": 0.0})

def remove_item(index):
    if len(st.session_state.invoice_items) > 1:
        st.session_state.invoice_items.pop(index)

# --- Top Website Header ---
st.markdown("""
    <div class="top-header">
        <h1 style="color: #1a202c; font-weight: 800; font-size: 2.3rem; margin-bottom: 5px;">Free Invoice Template</h1>
        <p style="color: #718096; font-size: 1.05rem;">Create professional invoices with one click!</p>
    </div>
""", unsafe_allow_html=True)

# --- Centered Layout Columns ---
_, center_app_col, _ = st.columns([1, 3.5, 1])

# --- CENTER INVOICE APP CONTAINER ---
with center_app_col:
    with st.container():
        st.markdown('<div class="invoice-card">', unsafe_allow_html=True)

        top_left, top_right = st.columns([1, 1])
        with top_left:
            uploaded_logo = st.file_uploader("Add Your Logo", type=["png", "jpg", "jpeg"], label_visibility="collapsed")
            if not uploaded_logo:
                st.markdown("""
                    <div style="border: 2px dashed #cbd5e0; border-radius: 6px; padding: 25px 10px; text-align: center; color: #a0aec0; background: #fafbfc; font-size: 13px;">
                        + Add Your Logo
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.image(uploaded_logo, width=110)

        with top_right:
            st.markdown("<h1 style='text-align: right; color: #1a202c; letter-spacing: 2px; margin: 0;'>INVOICE</h1>", unsafe_allow_html=True)
            invoice_number = st.text_input("Invoice #", "Invoice number", label_visibility="collapsed")

        st.markdown("<br>", unsafe_allow_html=True)

        col_from, col_dates = st.columns(2)
        with col_from:
            sender_address = st.text_area("Who is this from?", "Who is this from?", label_visibility="collapsed", height=95)
        with col_dates:
            c_d1, c_d2 = st.columns([1, 1.2])
            with c_d1:
                st.markdown("<p style='font-size:12px; color:#4a5568; margin-bottom:2px;'>Date</p>", unsafe_allow_html=True)
                invoice_date = st.date_input("Date", date.today(), label_visibility="collapsed")
                st.markdown("<p style='font-size:12px; color:#4a5568; margin-bottom:2px;'>Payment Terms</p>", unsafe_allow_html=True)
                payment_terms = st.text_input("Payment Terms", "", label_visibility="collapsed")
            with c_d2:
                st.markdown("<p style='font-size:12px; color:#4a5568; margin-bottom:2px;'>Due Date</p>", unsafe_allow_html=True)
                due_date = st.date_input("Due Date", date.today(), label_visibility="collapsed")
                st.markdown("<p style='font-size:12px; color:#4a5568; margin-bottom:2px;'>PO Number</p>", unsafe_allow_html=True)
                po_number = st.text_input("PO Number", "", label_visibility="collapsed")

        col_bill, col_ship = st.columns(2)
        with col_bill:
            st.markdown("<p style='font-size:12px; font-weight:600; color:#4a5568; margin-bottom:4px;'>Bill To</p>", unsafe_allow_html=True)
            client_address = st.text_area("Bill To", "Who is this to?", label_visibility="collapsed", height=85)
        with col_ship:
            st.markdown("<p style='font-size:12px; font-weight:600; color:#4a5568; margin-bottom:4px;'>Ship To (optional)</p>", unsafe_allow_html=True)
            ship_address = st.text_area("Ship To", "", label_visibility="collapsed", height=85)

        st.markdown("<br>", unsafe_allow_html=True)

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
                item["description"] = st.text_input(f"Desc {i}", item["description"], placeholder="Description of item/service...", label_visibility="collapsed", key=f"desc_{i}")
            with row_cols[1]:
                item["qty"] = st.number_input(f"Qty {i}", min_value=1, value=item["qty"], label_visibility="collapsed", key=f"qty_{i}")
            with row_cols[2]:
                item["rate"] = st.number_input(f"Rate {i}", min_value=0.0, value=item["rate"], label_visibility="collapsed", key=f"rate_{i}")
            with row_cols[3]:
                line_total = item["qty"] * item["rate"]
                subtotal += line_total
                st.markdown(f"<div style='padding-top: 10px; text-align: right; font-weight: 500; font-size: 14px;'>${line_total:,.2f}</div>", unsafe_allow_html=True)
            with row_cols[4]:
                if st.button("✕", key=f"del_{i}", help="Remove row"):
                    remove_item(i)
                    st.rerun()

        if st.button("+ Line Item", use_container_width=True):
            add_item()
            st.rerun()

        st.markdown("<hr style='margin: 20px 0; border: none; border-top: 1px solid #edf2f7;'>", unsafe_allow_html=True)

        col_notes, col_totals = st.columns([1.2, 1])

        with col_notes:
            st.markdown("<p style='font-size:12px; font-weight:600; color:#4a5568; margin-bottom:2px;'>Notes</p>", unsafe_allow_html=True)
            notes = st.text_area("Notes", "Notes - any relevant information not already covered", label_visibility="collapsed", height=70)

            st.markdown("<p style='font-size:12px; font-weight:600; color:#4a5568; margin-bottom:2px;'>Terms</p>", unsafe_allow_html=True)
            terms = st.text_area("Terms", "Terms and conditions - late fees, payment methods, delivery schedule", label_visibility="collapsed", height=70)

        with col_totals:
            tax_rate = st.number_input("Tax Rate (%)", min_value=0.0, max_value=100.0, value=0.0, step=0.5)
            shipping_fee = st.number_input("Shipping Fee", min_value=0.0, value=0.0, step=0.0)

            tax_amount = subtotal * (tax_rate / 100.0)
            total_amount = subtotal + tax_amount + shipping_fee

            st.markdown(f"""
                <div style="font-size: 13px; color: #4a5568; margin-top: 10px;">
                    <div style="display: flex; justify-content: space-between; padding: 4px 0;">
                        <span>Subtotal</span><span>${subtotal:,.2f}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; padding: 4px 0;">
                        <span>Tax ({tax_rate}%)</span><span>${tax_amount:,.2f}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; padding: 4px 0;">
                        <span>Shipping Fee</span><span>${shipping_fee:,.2f}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; padding: 8px 0; font-size: 15px; font-weight: bold; color: #1a202c; border-top: 1px solid #cbd5e0; margin-top: 5px;">
                        <span>Total</span><span>${total_amount:,.2f}</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)

        amount_paid = st.number_input("Amount Paid", min_value=0.0, value=0.0, step=0.0)
        balance_due = total_amount - amount_paid

        st.markdown(f"""
            <div style="display: flex; justify-content: space-between; padding: 10px 0; font-size: 15px; font-weight: bold; color: #1a202c; border-top: 2px solid #1a202c; margin-top: 8px;">
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

            logo_element = Paragraph("<b>INVOICE</b>", styles['Title'])
            if uploaded_logo is not None:
                try:
                    uploaded_logo.seek(0)
                    pil_img = PILImage.open(uploaded_logo)

                    display_w = 110.0
                    aspect = pil_img.height / float(pil_img.width)
                    display_h = display_w * aspect

                    scale_factor = 3.0
                    high_res_w = int(display_w * scale_factor)
                    high_res_h = int(display_h * scale_factor)

                    pil_img = pil_img.resize((high_res_w, high_res_h), PILImage.Resampling.LANCZOS)

                    img_buffer = io.BytesIO()
                    pil_img.save(img_buffer, format="PNG", dpi=(300, 300))
                    img_buffer.seek(0)

                    logo_element = RLImage(img_buffer, width=display_w, height=display_h)
                except Exception:
                    pass

            header_data = [
                [logo_element,
                 Paragraph(f"<b>INVOICE</b><br/><b>Invoice #:</b> {invoice_number}<br/><b>Date:</b> {invoice_date}<br/><b>Due Date:</b> {due_date}<br/><b>PO #:</b> {po_number}", right_style)]
            ]
            header_table = Table(header_data, colWidths=[3.25 * inch, 3.25 * inch])
            header_table.setStyle(TableStyle([
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('ALIGN', (1,0), (1,0), 'RIGHT'),
            ]))
            story.append(header_table)
            story.append(Spacer(1, 20))

            address_data = [
                [Paragraph(f"<b>From:</b><br/>{sender_address.replace(chr(10), '<br/>')}", styles['Normal']),
                 Paragraph(f"<b>Bill To:</b><br/>{client_address.replace(chr(10), '<br/>')}", right_style)]
            ]
            address_table = Table(address_data, colWidths=[3.25 * inch, 3.25 * inch])
            address_table.setStyle(TableStyle([
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('ALIGN', (1,0), (1,0), 'RIGHT'),
            ]))
            story.append(address_table)
            story.append(Spacer(1, 25))

            table_data = [["Description", "Qty", "Unit Price", "Amount"]]
            for item in st.session_state.invoice_items:
                line_total = item["qty"] * item["rate"]
                table_data.append([item["description"], str(item["qty"]), f"${item['rate']:,.2f}", f"${line_total:,.2f}"])

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
                [f"Tax ({tax_rate}%):", f"${tax_amount:,.2f}"],
                ["Shipping Fee:", f"${shipping_fee:,.2f}"],
                ["Total:", f"${total_amount:,.2f}"],
                ["Amount Paid:", f"${amount_paid:,.2f}"],
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
            story.append(Spacer(1, 25))

            story.append(Paragraph(f"<b>Notes:</b><br/>{notes}<br/><br/><b>Terms:</b><br/>{terms}", styles['Normal']))

            doc.build(story)
            buffer.seek(0)
            return buffer.getvalue()

    pdf_data = generate_pdf()

    # --- Centered Small Download Button ---
    st.markdown("<br>", unsafe_allow_html=True)
    col_left, col_center, col_right = st.columns([1, 1.2, 1])
    with col_center:
        st.download_button(
            label="⬇ Download PDF",
            data=pdf_data,
            file_name=f"invoice_{invoice_number}.pdf",
            mime="application/pdf",
            use_container_width=True,
            type="primary"
        )