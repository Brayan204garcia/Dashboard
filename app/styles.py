import streamlit as st

from app.config import COLORS


def inject_css():
    st.markdown(
        f"""
        <style>
        .stApp {{
            background: {COLORS["bg"]};
            color: {COLORS["text"]};
        }}
        div[data-testid="stDecoration"],
        div[data-testid="stStatusWidget"],
        div[data-testid="stToolbar"] [data-testid="stMainMenu"],
        div[data-testid="stToolbar"] [data-testid="stMainMenuButton"],
        div[data-testid="stToolbar"] [data-testid="stDeployButton"],
        div[data-testid="stToolbar"] [data-testid="stAppDeployButton"],
        div[data-testid="stToolbar"] [aria-label="Deploy"],
        div[data-testid="stToolbar"] button[title="Deploy"],
        #MainMenu,
        footer {{
            display: none !important;
            visibility: hidden !important;
            height: 0 !important;
        }}
        header[data-testid="stHeader"] {{
            background: transparent !important;
            box-shadow: none !important;
            overflow: visible !important;
            pointer-events: none !important;
        }}
        div[data-testid="stToolbar"] {{
            display: flex !important;
            visibility: visible !important;
            opacity: 1 !important;
            pointer-events: none !important;
            background: transparent !important;
        }}
        button[data-testid="stExpandSidebarButton"],
        div[data-testid="collapsedControl"] {{
            display: flex !important;
            visibility: visible !important;
            opacity: 1 !important;
            position: fixed !important;
            top: .65rem !important;
            left: .75rem !important;
            z-index: 999999 !important;
            pointer-events: auto !important;
        }}
        button[data-testid="stExpandSidebarButton"] {{
            align-items: center !important;
            justify-content: center !important;
            width: 2.35rem !important;
            height: 2.35rem !important;
            color: #8b5cf6 !important;
            background: transparent !important;
            border: 0 !important;
            border-radius: 10px !important;
            box-shadow: none !important;
        }}
        .stApp > div:first-child {{
            padding-top: 0 !important;
        }}
        section[data-testid="stSidebar"] {{
            background: #1f2937;
            border-right: 1px solid rgba(255,255,255,.08);
        }}
        section[data-testid="stSidebar"] * {{
            color: #e5e7eb !important;
        }}
        section[data-testid="stSidebar"] > div {{
            padding: 0 .85rem 1.05rem;
        }}
        .sidebar-brand {{
            display: flex;
            align-items: center;
            gap: .85rem;
            margin-top: -.35rem;
            padding: 0 .45rem 2.3rem .45rem;
        }}
        .sidebar-logo {{
            width: 40px;
            height: 40px;
            color: #8b5cf6;
            flex: 0 0 auto;
        }}
        .sidebar-title {{
            color: #ffffff !important;
            font-size: 1.05rem;
            line-height: 1;
            font-weight: 800;
            letter-spacing: 0;
            white-space: nowrap;
        }}
        .sidebar-pages {{
            padding: 0 .45rem .75rem .45rem;
            color: #7c8799 !important;
            font-size: .82rem;
            font-weight: 800;
            text-transform: uppercase;
        }}
        section[data-testid="stSidebar"] hr {{
            display: none;
        }}
        section[data-testid="stSidebar"] [data-testid="stRadio"] > label {{
            display: none;
        }}
        section[data-testid="stSidebar"] [role="radiogroup"] {{
            display: flex;
            flex-direction: column;
            gap: .35rem;
        }}
        section[data-testid="stSidebar"] [role="radiogroup"] label {{
            min-height: 46px;
            border-radius: 9px;
            padding: 0 .95rem !important;
            margin: 0 !important;
            display: flex !important;
            align-items: center;
            background: transparent;
            transition: background .15s ease, color .15s ease;
        }}
        section[data-testid="stSidebar"] [role="radiogroup"] label:hover {{
            background: rgba(255,255,255,.045);
        }}
        section[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {{
            background: rgba(139,92,246,.16);
        }}
        section[data-testid="stSidebar"] [role="radiogroup"] label > div:first-child {{
            display: none !important;
        }}
        section[data-testid="stSidebar"] [role="radiogroup"] label p {{
            display: flex;
            align-items: center;
            gap: .9rem;
            margin: 0 !important;
            color: #ffffff !important;
            font-size: 1.02rem;
            font-weight: 800;
            line-height: 1;
        }}
        section[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) p {{
            color: #8b5cf6 !important;
        }}
        section[data-testid="stSidebar"] [role="radiogroup"] label p::before {{
            width: 24px;
            color: #6b7280;
            font-size: 1.15rem;
            font-weight: 800;
            text-align: center;
        }}
        section[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) p::before {{
            color: #8b5cf6;
        }}
        section[data-testid="stSidebar"] [role="radiogroup"] label:nth-child(1) p::before {{ content: "◔"; }}
        section[data-testid="stSidebar"] [role="radiogroup"] label:nth-child(2) p::before {{ content: "♟"; }}
        section[data-testid="stSidebar"] [role="radiogroup"] label:nth-child(3) p::before {{ content: "⬡"; }}
        section[data-testid="stSidebar"] [role="radiogroup"] label:nth-child(4) p::before {{ content: "▣"; }}
        section[data-testid="stSidebar"] [role="radiogroup"] label:nth-child(5) p::before {{ content: "⌁"; }}
        section[data-testid="stSidebar"] [role="radiogroup"] label:nth-child(6) p::before {{ content: "♣"; }}
        section[data-testid="stSidebar"] [role="radiogroup"] label:nth-child(1) p::before {{ content: "\\25D4"; }}
        section[data-testid="stSidebar"] [role="radiogroup"] label:nth-child(2) p::before {{ content: "\\25CF"; }}
        section[data-testid="stSidebar"] [role="radiogroup"] label:nth-child(3) p::before {{ content: "\\2B22"; }}
        section[data-testid="stSidebar"] [role="radiogroup"] label:nth-child(4) p::before {{ content: "\\25A3"; }}
        section[data-testid="stSidebar"] [role="radiogroup"] label:nth-child(5) p::before {{ content: "\\2301"; }}
        section[data-testid="stSidebar"] [role="radiogroup"] label:nth-child(6) p::before {{ content: "\\2663"; }}
        section[data-testid="stSidebar"] [role="radiogroup"] label p::before {{
            content: "" !important;
            display: inline-block;
            width: 22px;
            height: 22px;
            flex: 0 0 22px;
            background: currentColor;
            color: #6b7280;
            -webkit-mask-repeat: no-repeat;
            mask-repeat: no-repeat;
            -webkit-mask-position: center;
            mask-position: center;
            -webkit-mask-size: 21px 21px;
            mask-size: 21px 21px;
        }}
        section[data-testid="stSidebar"] [role="radiogroup"] label:nth-child(1) p::before {{
            -webkit-mask-image: url("data:image/svg+xml,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%20viewBox='0%200%2024%2024'%20fill='none'%20stroke='black'%20stroke-width='2'%20stroke-linecap='round'%20stroke-linejoin='round'%3E%3Cpath%20d='M12%2014l4-4'/%3E%3Cpath%20d='M3.34%2019a10%2010%200%201%201%2017.32%200'/%3E%3C/svg%3E");
            mask-image: url("data:image/svg+xml,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%20viewBox='0%200%2024%2024'%20fill='none'%20stroke='black'%20stroke-width='2'%20stroke-linecap='round'%20stroke-linejoin='round'%3E%3Cpath%20d='M12%2014l4-4'/%3E%3Cpath%20d='M3.34%2019a10%2010%200%201%201%2017.32%200'/%3E%3C/svg%3E");
        }}
        section[data-testid="stSidebar"] [role="radiogroup"] label:nth-child(2) p::before {{
            -webkit-mask-image: url("data:image/svg+xml,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%20viewBox='0%200%2024%2024'%20fill='none'%20stroke='black'%20stroke-width='2'%20stroke-linecap='round'%20stroke-linejoin='round'%3E%3Cpath%20d='M20%2021a8%208%200%200%200-16%200'/%3E%3Ccircle%20cx='12'%20cy='7'%20r='4'/%3E%3C/svg%3E");
            mask-image: url("data:image/svg+xml,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%20viewBox='0%200%2024%2024'%20fill='none'%20stroke='black'%20stroke-width='2'%20stroke-linecap='round'%20stroke-linejoin='round'%3E%3Cpath%20d='M20%2021a8%208%200%200%200-16%200'/%3E%3Ccircle%20cx='12'%20cy='7'%20r='4'/%3E%3C/svg%3E");
        }}
        section[data-testid="stSidebar"] [role="radiogroup"] label:nth-child(3) p::before {{
            -webkit-mask-image: url("data:image/svg+xml,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%20viewBox='0%200%2024%2024'%20fill='none'%20stroke='black'%20stroke-width='2'%20stroke-linecap='round'%20stroke-linejoin='round'%3E%3Cpath%20d='M21%208a2%202%200%200%200-1-1.73l-7-4a2%202%200%200%200-2%200l-7%204A2%202%200%200%200%203%208v8a2%202%200%200%200%201%201.73l7%204a2%202%200%200%200%202%200l7-4A2%202%200%200%200%2021%2016Z'/%3E%3Cpath%20d='M3.3%207L12%2012l8.7-5'/%3E%3Cpath%20d='M12%2022V12'/%3E%3C/svg%3E");
            mask-image: url("data:image/svg+xml,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%20viewBox='0%200%2024%2024'%20fill='none'%20stroke='black'%20stroke-width='2'%20stroke-linecap='round'%20stroke-linejoin='round'%3E%3Cpath%20d='M21%208a2%202%200%200%200-1-1.73l-7-4a2%202%200%200%200-2%200l-7%204A2%202%200%200%200%203%208v8a2%202%200%200%200%201%201.73l7%204a2%202%200%200%200%202%200l7-4A2%202%200%200%200%2021%2016Z'/%3E%3Cpath%20d='M3.3%207L12%2012l8.7-5'/%3E%3Cpath%20d='M12%2022V12'/%3E%3C/svg%3E");
        }}
        section[data-testid="stSidebar"] [role="radiogroup"] label:nth-child(4) p::before {{
            -webkit-mask-image: url("data:image/svg+xml,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%20viewBox='0%200%2024%2024'%20fill='none'%20stroke='black'%20stroke-width='2'%20stroke-linecap='round'%20stroke-linejoin='round'%3E%3Cpath%20d='M21%208v13H3V8'/%3E%3Cpath%20d='M1%203h22v5H1z'/%3E%3Cpath%20d='M10%2012h4'/%3E%3C/svg%3E");
            mask-image: url("data:image/svg+xml,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%20viewBox='0%200%2024%2024'%20fill='none'%20stroke='black'%20stroke-width='2'%20stroke-linecap='round'%20stroke-linejoin='round'%3E%3Cpath%20d='M21%208v13H3V8'/%3E%3Cpath%20d='M1%203h22v5H1z'/%3E%3Cpath%20d='M10%2012h4'/%3E%3C/svg%3E");
        }}
        section[data-testid="stSidebar"] [role="radiogroup"] label:nth-child(5) p::before {{
            -webkit-mask-image: url("data:image/svg+xml,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%20viewBox='0%200%2024%2024'%20fill='none'%20stroke='black'%20stroke-width='2'%20stroke-linecap='round'%20stroke-linejoin='round'%3E%3Cpath%20d='M3%2019h18'/%3E%3Cpath%20d='M5%2015l4-4%204%204%206-8'/%3E%3C/svg%3E");
            mask-image: url("data:image/svg+xml,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%20viewBox='0%200%2024%2024'%20fill='none'%20stroke='black'%20stroke-width='2'%20stroke-linecap='round'%20stroke-linejoin='round'%3E%3Cpath%20d='M3%2019h18'/%3E%3Cpath%20d='M5%2015l4-4%204%204%206-8'/%3E%3C/svg%3E");
        }}
        section[data-testid="stSidebar"] [role="radiogroup"] label:nth-child(6) p::before {{
            -webkit-mask-image: url("data:image/svg+xml,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%20viewBox='0%200%2024%2024'%20fill='none'%20stroke='black'%20stroke-width='2'%20stroke-linecap='round'%20stroke-linejoin='round'%3E%3Cpath%20d='M16%2021v-2a4%204%200%200%200-4-4H6a4%204%200%200%200-4%204v2'/%3E%3Ccircle%20cx='9'%20cy='7'%20r='4'/%3E%3Cpath%20d='M22%2021v-2a4%204%200%200%200-3-3.87'/%3E%3Cpath%20d='M16%203.13a4%204%200%200%201%200%207.75'/%3E%3C/svg%3E");
            mask-image: url("data:image/svg+xml,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%20viewBox='0%200%2024%2024'%20fill='none'%20stroke='black'%20stroke-width='2'%20stroke-linecap='round'%20stroke-linejoin='round'%3E%3Cpath%20d='M16%2021v-2a4%204%200%200%200-4-4H6a4%204%200%200%200-4%204v2'/%3E%3Ccircle%20cx='9'%20cy='7'%20r='4'/%3E%3Cpath%20d='M22%2021v-2a4%204%200%200%200-3-3.87'/%3E%3Cpath%20d='M16%203.13a4%204%200%200%201%200%207.75'/%3E%3C/svg%3E");
        }}
        .block-container {{
            padding-top: .65rem;
            padding-bottom: 2.4rem;
            max-width: 1560px;
        }}
        h1, h2, h3 {{
            letter-spacing: 0;
        }}
        .topbar {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            min-height: 56px;
            padding: 0 0 .75rem 0;
            border-bottom: 1px solid #e5e7eb;
            margin-bottom: 1.25rem;
        }}
        .brand {{
            font-size: 1.15rem;
            font-weight: 700;
            color: #111827;
        }}
        .card {{
            background: {COLORS["card"]};
            border-radius: 12px;
            box-shadow: 0 1px 2px rgba(15,23,42,.06);
            border: 1px solid rgba(15,23,42,.04);
            padding: 1.15rem;
            min-height: 100%;
        }}
        .kpi-card {{
            position: relative;
            overflow: hidden;
            min-height: 154px;
            background: {COLORS["dark_card"]};
            color: white;
            border-radius: 12px;
            box-shadow: 0 1px 2px rgba(15,23,42,.08);
            padding: 1.05rem;
        }}
        .section-gap {{
            height: 1.35rem;
        }}
        .kpi-title {{
            font-size: 1.04rem;
            font-weight: 700;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}
        .kpi-meta {{
            margin-top: 1rem;
            color: #9ca3af;
            font-size: .7rem;
            font-weight: 700;
            text-transform: uppercase;
        }}
        .kpi-value {{
            margin-top: .55rem;
            font-size: 2.05rem;
            line-height: 1;
            font-weight: 800;
        }}
        .pill {{
            display: inline-flex;
            align-items: center;
            padding: .25rem .55rem;
            border-radius: 999px;
            font-size: .8rem;
            font-weight: 700;
            white-space: nowrap;
        }}
        .pill-green {{ color: #86efac; background: rgba(34,197,94,.16); }}
        .pill-red {{ color: #fda4af; background: rgba(244,63,94,.16); }}
        .pill-yellow {{ color: #fde68a; background: rgba(234,179,8,.16); }}
        .pill-sky {{ color: #7dd3fc; background: rgba(56,189,248,.16); }}
        .soft-green {{ color: #15803d; background: rgba(34,197,94,.14); }}
        .soft-red {{ color: #be123c; background: rgba(244,63,94,.14); }}
        .soft-yellow {{ color: #a16207; background: rgba(234,179,8,.16); }}
        .soft-violet {{ color: #6d28d9; background: rgba(139,92,246,.14); }}
        .section-title {{
            color: #111827;
            font-size: 1.05rem;
            font-weight: 700;
            margin: 0 0 .2rem 0;
        }}
        .eyebrow {{
            color: #9ca3af;
            font-size: .72rem;
            font-weight: 800;
            text-transform: uppercase;
        }}
        .muted {{
            color: #6b7280;
            font-size: .9rem;
        }}
        .metric-row {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: .75rem;
            padding: .7rem .8rem;
            background: #f9fafb;
            border-radius: 10px;
            margin-bottom: .65rem;
        }}
        .dot {{
            width: .65rem;
            height: .65rem;
            border-radius: 999px;
            display: inline-block;
            margin-right: .45rem;
        }}
        .dot-green {{ background: {COLORS["green"]}; }}
        .dot-yellow {{ background: {COLORS["yellow"]}; }}
        .dot-red {{ background: {COLORS["red"]}; }}
        .dot-sky {{ background: {COLORS["sky"]}; }}
        div[data-testid="stMetricValue"] {{
            font-size: 1.65rem;
        }}
        .stPlotlyChart {{
            width: 100%;
        }}
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.client-chart-head) {{
            background: #ffffff;
            border-color: rgba(139,92,246,.28);
            box-shadow: 0 10px 26px rgba(139,92,246,.08), 0 1px 2px rgba(15,23,42,.05);
            transition: border-color .16s ease, box-shadow .16s ease;
        }}
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.client-chart-head):hover {{
            border-color: rgba(14,165,233,.46);
            box-shadow: 0 14px 32px rgba(14,165,233,.12), 0 1px 2px rgba(15,23,42,.06);
        }}
        .client-chart-head {{
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            gap: 1rem;
            margin: .1rem 0 .85rem 0;
            padding-bottom: .75rem;
            border-bottom: 1px solid #eef2f7;
        }}
        .client-chart-title {{
            color: #0f172a;
            font-size: 1rem;
            line-height: 1.2;
            font-weight: 800;
            letter-spacing: 0;
        }}
        .client-chart-subtitle {{
            margin-top: .22rem;
            color: #475569;
            font-size: .82rem;
            line-height: 1.25;
            font-weight: 750;
        }}
        .client-chart-badges {{
            display: flex;
            align-items: center;
            justify-content: flex-end;
            flex-wrap: wrap;
            gap: .35rem;
            min-width: fit-content;
        }}
        .client-chart-badge {{
            display: inline-flex;
            align-items: center;
            min-height: 26px;
            padding: .28rem .58rem;
            border-radius: 999px;
            border: 1px solid #cbd5e1;
            background: #f1f5f9;
            color: #334155;
            font-size: .72rem;
            font-weight: 800;
            white-space: nowrap;
        }}
        .rfm-card {{
            min-height: 174px;
            border-radius: 12px;
            padding: 1.15rem;
            margin: .35rem .18rem .15rem .18rem;
            border: 0;
            background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
            box-shadow: none;
        }}
        .rfm-card-top {{
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            gap: .75rem;
        }}
        .rfm-title {{
            color: #0f172a;
            font-size: .96rem;
            line-height: 1.12;
            font-weight: 850;
        }}
        .rfm-count {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            min-width: 34px;
            height: 30px;
            border-radius: 999px;
            color: #ffffff;
            font-size: .9rem;
            font-weight: 900;
        }}
        .rfm-customers {{
            margin-top: .9rem;
            color: #334155;
            font-size: .86rem;
            line-height: 1.35;
            font-weight: 700;
        }}
        .rfm-action {{
            margin-top: .9rem;
            color: #475569;
            font-size: .78rem;
            line-height: 1.25;
            font-weight: 850;
            text-transform: uppercase;
        }}
        .rfm-green,
        .rfm-sky,
        .rfm-yellow,
        .rfm-red {{ box-shadow: none; }}
        .rfm-green .rfm-count {{ background: #16a34a; }}
        .rfm-sky .rfm-count {{ background: #0284c7; }}
        .rfm-yellow .rfm-count {{ background: #ca8a04; }}
        .rfm-red .rfm-count {{ background: #e11d48; }}
        .client-profile {{
            border-radius: 12px;
            border: 1px solid rgba(139,92,246,.25);
            background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
            padding: 1rem;
        }}
        .profile-title {{
            color: #0f172a;
            font-size: 1.18rem;
            font-weight: 900;
            padding-bottom: .7rem;
            border-bottom: 1px solid #e2e8f0;
            margin-bottom: .85rem;
        }}
        .profile-grid {{
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: .55rem .9rem;
        }}
        .profile-stack {{
            display: flex;
            flex-direction: column;
            gap: .55rem;
        }}
        .profile-line {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: .75rem;
            padding: .55rem .65rem;
            border-radius: 9px;
            background: #f1f5f9;
            color: #475569;
            font-size: .84rem;
            font-weight: 750;
        }}
        .profile-line strong {{
            color: #0f172a;
            font-weight: 900;
            text-align: right;
        }}
        .profile-subtitle {{
            margin: 1rem 0 .45rem 0;
            color: #334155;
            font-size: .82rem;
            font-weight: 900;
            text-transform: uppercase;
        }}
        .profile-reco {{
            margin-top: 1rem;
            border-radius: 10px;
            padding: .75rem .85rem;
            color: #7f1d1d;
            background: #fee2e2;
            border: 1px solid #fecaca;
            font-weight: 900;
        }}
        @media (max-width: 780px) {{
            .client-chart-head {{
                flex-direction: column;
                gap: .55rem;
            }}
            .client-chart-badges {{
                justify-content: flex-start;
            }}
            .profile-grid {{
                grid-template-columns: 1fr;
            }}
        }}
        .team-grid {{
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 1rem;
        }}
        .team-member-card {{
            display: grid;
            align-content: space-between;
            min-height: 150px;
            padding: 1.25rem;
            border-radius: 14px;
            background: #1f2937;
            color: #ffffff;
            border: 1px solid rgba(255,255,255,.08);
            box-shadow: 0 1px 2px rgba(15,23,42,.08);
        }}
        .team-member-name {{
            color: #ffffff;
            font-size: 1.18rem;
            line-height: 1.18;
            font-weight: 850;
        }}
        .team-member-place {{
            margin-top: .75rem;
            color: #9ca3af;
            font-size: .92rem;
            font-weight: 700;
        }}
        @media (max-width: 1100px) {{
            .team-grid {{
                grid-template-columns: repeat(2, minmax(0, 1fr));
            }}
        }}
        @media (max-width: 680px) {{
            .team-grid {{
                grid-template-columns: 1fr;
            }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
