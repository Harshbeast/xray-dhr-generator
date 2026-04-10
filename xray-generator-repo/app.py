import streamlit as st
import pandas as pd
import re
import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER 

# --- EMBEDDED DHR DATA ---
# This acts as your permanent dhr.csv file
DHR_CSV_DATA = """S.no,Test parameter/Description,Tube potential [kV],LSL [kV],USL [kV],LSL [mA],USL [mA],Status
1,S.F. Normal Dynamic 2.4mA 33.33ms 30fr/s,40,38,42,0.34,0.46,Pass/Fail
2,S.F. Normal Dynamic 2.4mA 33.33ms 30fr/s,48,45.6,50.4,0.408,0.552,Pass/Fail
3,S.F. Normal Dynamic 2.4mA 33.33ms 30fr/s,57,54.15,59.85,0.672,0.909,Pass/Fail
4,S.F. Normal Dynamic 2.4mA 33.33ms 30fr/s,65,61.75,68.25,1.326,1.794,Pass/Fail
5,S.F. Normal Dynamic 2.4mA 33.33ms 30fr/s,100,95,105,1.998,2.703,Pass/Fail
6,S.F. Normal Dynamic 5.4mA 37ms 15fr/s,40,38,42,0.765,1.035,Pass/Fail
7,S.F. Normal Dynamic 5.4mA 37ms 15fr/s,48,45.6,50.4,0.918,1.242,Pass/Fail
8,S.F. Normal Dynamic 5.4mA 37ms 15fr/s,57,54.15,59.85,1.513,2.047,Pass/Fail
9,S.F. Normal Dynamic 5.4mA 37ms 15fr/s,65,61.75,68.25,2.984,4.037,Pass/Fail
10,S.F. Normal Dynamic 5.4mA 37ms 15fr/s,100,95,105,4.497,6.084,Pass/Fail
11,S.F. Normal Dynamic 5.4mA 131ms 1.875fr/s,40,38,42,0.765,1.035,Pass/Fail
12,S.F. Normal Dynamic 5.4mA 131ms 1.875fr/s,48,45.6,50.4,0.918,1.242,Pass/Fail
13,S.F. Normal Dynamic 5.4mA 131ms 1.875fr/s,57,54.15,59.85,1.513,2.047,Pass/Fail
14,S.F. Normal Dynamic 5.4mA 131ms 1.875fr/s,65,61.75,68.25,2.984,4.037,Pass/Fail
15,S.F. Normal Dynamic 5.4mA 131ms 1.875fr/s,100,95,105,4.497,6.084,Pass/Fail
16,S.F. Normal Dynamic 7.2mA 33ms 15fr/s,40,38,42,1.02,1.38,Pass/Fail
17,S.F. Normal Dynamic 7.2mA 33ms 15fr/s,48,45.6,50.4,1.224,1.656,Pass/Fail
18,S.F. Normal Dynamic 7.2mA 33ms 15fr/s,57,54.15,59.85,2.023,2.737,Pass/Fail
19,S.F. Normal Dynamic 7.2mA 33ms 15fr/s,65,61.75,68.25,3.987,5.394,Pass/Fail
20,S.F. Normal Dynamic 7.2mA 33ms 15fr/s,100,95,105,6.001,8.119,Pass/Fail
21,S.F. Normal 9mA 35ms 3.75fr/s,40,38,42,1.275,1.725,Pass/Fail
22,S.F. Normal Dynamic 9mA 35ms 3.75fr/s,48,45.6,50.4,1.522,2.059,Pass/Fail
23,S.F. Normal Dynamic 9mA 35ms 3.75fr/s,57,54.15,59.85,2.525,3.416,Pass/Fail
24,S.F. Normal Dynamic 9mA 35ms 3.75fr/s,65,61.75,68.25,4.981,6.739,Pass/Fail
25,S.F. Normal Dynamic 9mA 35ms 3.75fr/s,100,95,105,7.497,10.143,Pass/Fail
26,S.F. Normal Dynamic 10.8mA 16ms 7.5fr/s,40,38,42,1.53,2.07,Pass/Fail
27,S.F. Normal Dynamic 10.8mA 16ms 7.5fr/s,48,45.6,50.4,1.828,2.473,Pass/Fail
28,S.F. Normal Dynamic 10.8mA 16ms 7.5fr/s,57,54.15,59.85,3.035,4.106,Pass/Fail
29,S.F. Normal Dynamic 10.8mA 16ms 7.5fr/s,65,61.75,68.25,5.976,8.085,Pass/Fail
30,S.F. Normal Dynamic 10.8mA 16ms 7.5fr/s,100,95,105,8.993,12.167,Pass/Fail
31,L.F. Normal Dynamic 16mA 14ms 3.75fr/s,40,38,42,2.27,3.071,Pass/Fail
32,L.F. Normal Dynamic 16mA 14ms 3.75fr/s,48,45.6,50.4,2.712,3.669,Pass/Fail
33,L.F. Normal Dynamic 16mA 14ms 3.75fr/s,57,54.15,59.85,4.488,6.072,Pass/Fail
34,L.F. Normal Dynamic 16mA 14ms 3.75fr/s,65,61.75,68.25,8.84,11.96,Pass/Fail
35,L.F. Normal Dynamic 16mA 14ms 3.75fr/s,100,95,105,13.32,18.021,Pass/Fail
36,L.F. Normal Dynamic 30mA 14ms 1.875fr/s,40,38,42,4.25,5.75,Pass/Fail
37,L.F. Normal Dynamic 30mA 14ms 1.875fr/s,48,45.6,50.4,5.083,6.877,Pass/Fail
38,L.F. Normal Dynamic 30mA 14ms 1.875fr/s,57,54.15,59.85,8.424,11.397,Pass/Fail
39,L.F. Normal Dynamic 30mA 14ms 1.875fr/s,65,61.75,68.25,16.592,22.448,Pass/Fail
40,L.F. Normal Dynamic 30mA 14ms 1.875fr/s,100,95,105,24.99,33.81,Pass/Fail
41,L.F. Normal Single 36mA 100ms,40,38,42,5.1,6.9,Pass/Fail
42,L.F. Normal Single 36mA 100ms,48,45.6,50.4,6.103,8.257,Pass/Fail
43,L.F. Normal Single 36mA 100ms,57,54.15,59.85,10.107,13.674,Pass/Fail
44,L.F. Normal Single 36mA 100ms,65,61.75,68.25,19.907,26.933,Pass/Fail
45,L.F. Normal Single 36mA 100ms,100,95,105,29.988,40.572,Pass/Fail
46,L.F. Normal Single 19.1mA 200ms,40,38,42,2.703,3.657,Pass/Fail
47,L.F. Normal Single 19.1mA 200ms,48,45.6,50.4,3.23,4.37,Pass/Fail
48,L.F. Normal Single 19.1mA 200ms,57,54.15,59.85,5.347,7.234,Pass/Fail
49,L.F. Normal Single 19.1mA 200ms,65,61.75,68.25,10.54,14.26,Pass/Fail
50,L.F. Normal Single 19.1mA 200ms,100,95,105,15.87,21.471,Pass/Fail
51,S.F. ISOWATT Dynamic 5.4mA 37ms 15fr/s,63,59.85,66.15,3.179,4.301,Pass/Fail
52,S.F. ISOWATT Dynamic 5.4mA 37ms 15fr/s,66,62.7,69.3,4.905,6.636,Pass/Fail
53,S.F. ISOWATT Dynamic 5.4mA 37ms 15fr/s,69,65.55,72.45,6.639,8.982,Pass/Fail
54,S.F. ISOWATT Dynamic 5.4mA 37ms 15fr/s,100,95,105,5.049,6.831,Pass/Fail
55,S.F. ISOWATT Dynamic 7.2mA 30ms 15fr/s,63,59.85,66.15,4.233,5.727,Pass/Fail
56,S.F. ISOWATT Dynamic 7.2mA 30ms 15fr/s,66,62.7,69.3,6.537,8.844,Pass/Fail
57,S.F. ISOWATT Dynamic 7.2mA 30ms 15fr/s,69,65.55,72.45,8.849,11.972,Pass/Fail
58,S.F. ISOWATT Dynamic 7.2mA 30ms 15fr/s,100,95,105,6.732,9.108,Pass/Fail
59,S.F. ISOWATT Dynamic 9mA 16ms 15fr/s,63,59.85,66.15,5.296,7.165,Pass/Fail
60,S.F. ISOWATT Dynamic 9mA 16ms 15fr/s,66,62.7,69.3,8.177,11.063,Pass/Fail
61,S.F. ISOWATT Dynamic 9mA 16ms 15fr/s,69,65.55,72.45,11.059,14.962,Pass/Fail
62,S.F. ISOWATT Dynamic 9mA 16ms 15fr/s,100,95,105,8.415,11.385,Pass/Fail
63,S.F. ISOWATT Dynamic 10.8mA 16ms 7.5fr/s,63,59.85,66.15,6.35,8.591,Pass/Fail
64,S.F. ISOWATT Dynamic 10.8mA 16ms 7.5fr/s,66,62.7,69.3,9.809,13.271,Pass/Fail
65,S.F. ISOWATT Dynamic 10.8mA 16ms 7.5fr/s,69,65.55,72.45,13.269,17.952,Pass/Fail
66,S.F. ISOWATT Dynamic 10.8mA 16ms 7.5fr/s,100,95,105,10.098,13.662,Pass/Fail
67,L.F. ISOWATT Dynamic 16mA 14ms 3.75fr/s,63,59.85,66.15,9.41,12.731,Pass/Fail
68,L.F. ISOWATT Dynamic 16mA 14ms 3.75fr/s,66,62.7,69.3,14.527,19.654,Pass/Fail
69,L.F. ISOWATT Dynamic 16mA 14ms 3.75fr/s,69,65.55,72.45,19.652,26.588,Pass/Fail
70,L.F. ISOWATT Dynamic 16mA 14ms 3.75fr/s,100,95,105,14.952,20.229,Pass/Fail"""

# --- CORE LOGIC FUNCTIONS ---

def extract_txt_data(uploaded_file):
    pattern = re.compile(r"^\s*(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(.*)$")
    raw_data = []
    start_reading = False
    
    content = uploaded_file.getvalue().decode("utf-8")
    for line in content.splitlines():
        if "Set kV" in line and "Filament" in line:
            start_reading = True
            continue
        if start_reading:
            match = pattern.match(line)
            if match:
                raw_data.append(match.groups())
            elif line.strip() == "" or "____" in line:
                break
    
    if not raw_data:
        return None

    columns = ["Set kV", "Set mA", "Act kV", "Act mA", "Filament(V)", "Mode"]
    df = pd.DataFrame(raw_data, columns=columns)
    numeric_cols = ["Set kV", "Set mA", "Act kV", "Act mA", "Filament(V)"]
    df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric)
    
    mask = df['Set mA'].shift(-1) != df['Set mA']
    return df.loc[mask].copy()

def create_pdf_bytes(dataframe):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    elements = []
    styles = getSampleStyleSheet()
    
    rows_per_page = 15
    total_rows = len(dataframe)

    left_style = ParagraphStyle('left', fontSize=9, leading=11, alignment=TA_LEFT)
    center_style = ParagraphStyle('center', fontSize=10, leading=12, alignment=TA_CENTER)
    
    for i in range(0, total_rows, rows_per_page):
        page_num = 37 + (i // rows_per_page)
        
        header_data = [
            [
                Paragraph("<b>PHILIPS<br/>Healthcare<br/>Imaging Systems</b><br/>HIC Pune India", center_style), 
                Paragraph("<b>Device History Record<br/>System Verification & &amp; AERB Zenition 30</b>", center_style),
                Paragraph(f"Doc Id: D001003021<br/>Rev No: U<br/>Page No: {page_num} of 45", left_style)
            ],
        ]
        h_table = Table(header_data, colWidths=[150, 240, 150])
        
        h_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
            ('LINEAFTER', (0, 0), (0, 0), 0.5, colors.black),
            ('LINEAFTER', (1, 0), (1, 0), 0.5, colors.black),
            ('LINEBELOW', (0, 0), (-1, -1), 0.5, colors.black),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        elements.append(h_table)
        elements.append(Spacer(1, 10))

        subset = dataframe.iloc[i : i + rows_per_page]
        t_header = ['S.no', 'Description', 'Tube kV', 'LSL kV', 'USL kV','LSL mA', 'USL mA', 'Set mA', 'Act kV', 'Status']
        t_data = [t_header]
        
        for _, row in subset.iterrows():
            t_data.append([
                row['S.no'], Paragraph(str(row['Test parameter/Description']), styles['Normal']), 
                row['Tube potential [kV]'], row['LSL [kV]'], row['USL [kV]'],
                row['LSL [mA]'], row['USL [mA]'], row['Set mA'], row['Act kV'], row['Status']
            ])

        main_table = Table(t_data, colWidths=[25, 140, 40, 40, 40, 40, 40, 40, 40, 40])
        main_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('FONTSIZE', (0, 0), (-1, -1), 6.5),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(main_table)
        
        if (i + rows_per_page) >= total_rows:
            elements.append(Spacer(1, 20))
            elements.append(Paragraph("<b>NOTE: $ These modes are available in 4 kW configuration only and rest modes are available in 2.1 kW and 4 kW configurations</b>", styles['Normal']))
            footer_table = Table([
                ["Testing Completion Details", "Technician 1", "Technician 2", "Technician 3"], 
                ["Name", "", "",""], 
                ["Points Completed", "", "",""], 
                ["Signature","","",""],
                ["Date","","",""]
            ], colWidths=[150, 100, 100, 100])
            footer_table.setStyle(TableStyle([('GRID', (0,0), (-1,-1), 0.5, colors.black)]))
            elements.append(footer_table)

        elements.append(PageBreak())

    doc.build(elements)
    return buffer.getvalue()

# --- STREAMLIT UI ---

st.set_page_config(page_title="Philips DHR Generator", layout="wide")
st.title("📄 X-Ray DHR Report Generator")

# Load dhr.csv from the embedded string automatically
dhr_base = pd.read_csv(io.StringIO(DHR_CSV_DATA))

txt_file = st.file_uploader("Upload System History (.txt)", type=["txt"])

if txt_file:
    try:
        # 1. Extract from TXT
        df_filtered = extract_txt_data(txt_file)
        
        if df_filtered is not None:
            # 2. Align and Validate
            min_rows = min(len(dhr_base), len(df_filtered))
            dhr = dhr_base.iloc[:min_rows].copy()
            df_filtered = df_filtered.iloc[:min_rows].copy()

            dhr['Set mA'] = df_filtered['Set mA'].values
            dhr['Act kV'] = df_filtered['Act kV'].values

            ma_criteria = (dhr['Set mA'] >= dhr['LSL [mA]']) & (dhr['Set mA'] <= dhr['USL [mA]'])
            kv_criteria = (dhr['Act kV'] >= dhr['LSL [kV]']) & (dhr['Act kV'] <= dhr['USL [kV]'])
            dhr['Status'] = 'Fail'
            dhr.loc[ma_criteria & kv_criteria, 'Status'] = 'Pass'

            st.success(f"Matched {min_rows} test points against internal template.")
            st.dataframe(dhr[['S.no', 'Set mA', 'Act kV', 'Status']].head(10))

            # 3. Generate PDF
            if st.button("Generate Final PDF Report"):
                with st.spinner("Building PDF..."):
                    pdf_data = create_pdf_bytes(dhr)
                    st.download_button(
                        label="📥 Download DHR_Testing_Report.pdf",
                        data=pdf_data,
                        file_name="DHR_Testing_Report.pdf",
                        mime="application/pdf"
                    )
        else:
            st.error("No valid data found in the uploaded text file. Check the file format.")

    except Exception as e:
        st.error(f"An error occurred: {e}")