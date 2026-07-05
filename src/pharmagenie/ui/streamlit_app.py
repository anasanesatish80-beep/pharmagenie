"""Streamlit frontend for PharmaGenie."""

import asyncio
import tempfile
import time
from pathlib import Path

import streamlit as st

from pharmagenie.agents import CoordinatorAgent
from pharmagenie.reports.markdown import render_markdown
from pharmagenie.reports.pdf import write_pdf
from pharmagenie.safety import ResearchRequest


st.set_page_config(page_title="PharmaGenie", page_icon="PG", layout="wide")

st.markdown(
    """
    <style>
    :root {
        --pg-bg: #03070b;
        --pg-panel: rgba(3, 14, 22, 0.86);
        --pg-panel-2: rgba(16, 20, 38, 0.78);
        --pg-cyan: #5ef5ff;
        --pg-blue: #7aa7ff;
        --pg-lime: #b7ff5e;
        --pg-amber: #ffcc66;
        --pg-rose: #ff6f91;
        --pg-text: #eafcff;
        --pg-muted: #99b9c1;
    }

    .stApp {
        background:
            radial-gradient(circle at 14% 12%, rgba(94, 245, 255, 0.22), transparent 18rem),
            radial-gradient(circle at 88% 5%, rgba(122, 167, 255, 0.18), transparent 24rem),
            radial-gradient(circle at 74% 78%, rgba(183, 255, 94, 0.10), transparent 24rem),
            linear-gradient(135deg, #02060b 0%, #07121f 42%, #11091d 100%);
        color: var(--pg-text);
    }

    .stApp:before {
        content: "";
        position: fixed;
        inset: 0;
        background-image:
            linear-gradient(rgba(94,245,255,0.035) 1px, transparent 1px),
            linear-gradient(90deg, rgba(94,245,255,0.035) 1px, transparent 1px),
            radial-gradient(circle, rgba(255,255,255,0.16) 1px, transparent 1px);
        background-size: 48px 48px, 48px 48px, 140px 140px;
        background-position: center, center, 12px 19px;
        pointer-events: none;
    }

    .stApp:after {
        content: "";
        position: fixed;
        inset: 0;
        background: repeating-linear-gradient(
            0deg,
            rgba(255,255,255,0.025) 0,
            rgba(255,255,255,0.025) 1px,
            transparent 1px,
            transparent 5px
        );
        mix-blend-mode: screen;
        opacity: 0.35;
        pointer-events: none;
    }

    [data-testid="stHeader"] { background: rgba(0, 0, 0, 0); }
    [data-testid="stSidebar"] { background: rgba(4, 8, 15, 0.96); }
    .block-container { padding-top: 1.2rem; max-width: 1400px; }

    .pg-hero {
        position: relative;
        display: grid;
        grid-template-columns: minmax(0, 1.08fr) minmax(360px, 0.92fr);
        gap: 1.1rem;
        padding: 1.15rem;
        border: 1px solid rgba(94, 245, 255, 0.28);
        background:
            linear-gradient(135deg, rgba(94, 245, 255, 0.15), rgba(122, 167, 255, 0.08) 45%, rgba(183, 255, 94, 0.07)),
            rgba(2, 9, 16, 0.78);
        border-radius: 8px;
        overflow: hidden;
        box-shadow:
            0 0 55px rgba(94, 245, 255, 0.14),
            inset 0 0 40px rgba(94, 245, 255, 0.05);
        margin-bottom: 1rem;
    }

    .pg-hero:before {
        content: "";
        position: absolute;
        inset: 0;
        background:
            linear-gradient(120deg, rgba(94,245,255,0.10), transparent 36%),
            repeating-linear-gradient(90deg, rgba(94,245,255,0.06) 0 1px, transparent 1px 42px);
        mask-image: linear-gradient(90deg, black, transparent 88%);
        pointer-events: none;
    }

    .pg-hero-copy {
        position: relative;
        padding: 1rem 1rem 0.8rem 1rem;
        z-index: 1;
    }

    .pg-kicker {
        color: var(--pg-lime);
        font-size: 0.78rem;
        letter-spacing: 0;
        text-transform: uppercase;
        font-weight: 700;
        margin-bottom: 0.4rem;
        position: relative;
    }

    .pg-title {
        color: var(--pg-text);
        font-size: 3.35rem;
        line-height: 1.02;
        font-weight: 800;
        letter-spacing: 0;
        margin: 0;
        position: relative;
        text-shadow: 0 0 28px rgba(94,245,255,0.22);
    }

    .pg-subtitle {
        color: var(--pg-muted);
        max-width: 760px;
        font-size: 1.02rem;
        line-height: 1.55;
        margin-top: 0.75rem;
        position: relative;
    }

    .pg-visual {
        position: relative;
        min-height: 320px;
        border: 1px solid rgba(94,245,255,0.18);
        border-radius: 8px;
        background:
            radial-gradient(circle at 50% 44%, rgba(94,245,255,0.18), transparent 10rem),
            linear-gradient(145deg, rgba(6, 18, 30, 0.80), rgba(12, 8, 28, 0.84));
        overflow: hidden;
        box-shadow: inset 0 0 45px rgba(94,245,255,0.08);
    }

    .pg-visual:before {
        content: "";
        position: absolute;
        width: 260px;
        height: 260px;
        left: 50%;
        top: 50%;
        transform: translate(-50%, -50%);
        border: 1px solid rgba(94,245,255,0.34);
        border-radius: 50%;
        box-shadow:
            0 0 28px rgba(94,245,255,0.24),
            inset 0 0 28px rgba(122,167,255,0.10);
    }

    .pg-orbit {
        position: absolute;
        left: 50%;
        top: 50%;
        width: 285px;
        height: 92px;
        border: 1px solid rgba(183,255,94,0.32);
        border-radius: 50%;
        transform: translate(-50%, -50%) rotate(-18deg);
        animation: pgSpin 9s linear infinite;
    }

    .pg-orbit.two {
        transform: translate(-50%, -50%) rotate(42deg);
        border-color: rgba(122,167,255,0.32);
        width: 300px;
        height: 102px;
        animation: pgSpinReverse 12s linear infinite;
    }

    .pg-core {
        position: absolute;
        left: 50%;
        top: 50%;
        width: 84px;
        height: 84px;
        transform: translate(-50%, -50%);
        border-radius: 50%;
        background:
            radial-gradient(circle, rgba(234,252,255,0.95), rgba(94,245,255,0.72) 32%, rgba(94,245,255,0.12) 66%, transparent 70%);
        box-shadow: 0 0 55px rgba(94,245,255,0.70);
        animation: pgPulse 2.4s ease-in-out infinite;
    }

    .pg-node {
        position: absolute;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        background: var(--pg-lime);
        box-shadow: 0 0 18px rgba(183,255,94,0.85);
    }

    .pg-node.n1 { left: 20%; top: 33%; }
    .pg-node.n2 { right: 22%; top: 23%; background: var(--pg-cyan); box-shadow: 0 0 18px rgba(94,245,255,0.85); }
    .pg-node.n3 { right: 18%; bottom: 28%; background: var(--pg-rose); box-shadow: 0 0 18px rgba(255,111,145,0.75); }
    .pg-node.n4 { left: 27%; bottom: 20%; background: var(--pg-blue); box-shadow: 0 0 18px rgba(122,167,255,0.80); }

    @keyframes pgPulse {
        0%, 100% { transform: translate(-50%, -50%) scale(0.96); opacity: 0.82; }
        50% { transform: translate(-50%, -50%) scale(1.08); opacity: 1; }
    }

    @keyframes pgSpin {
        from { transform: translate(-50%, -50%) rotate(-18deg); }
        to { transform: translate(-50%, -50%) rotate(342deg); }
    }

    @keyframes pgSpinReverse {
        from { transform: translate(-50%, -50%) rotate(42deg); }
        to { transform: translate(-50%, -50%) rotate(-318deg); }
    }

    .pg-dna {
        position: absolute;
        left: 7%;
        top: 12%;
        color: rgba(94,245,255,0.68);
        font-family: Consolas, monospace;
        font-size: 0.78rem;
        line-height: 1.6;
        white-space: pre;
    }

    .pg-telemetry {
        position: absolute;
        right: 1rem;
        bottom: 1rem;
        width: min(260px, 70%);
        border: 1px solid rgba(94,245,255,0.20);
        background: rgba(2, 8, 14, 0.72);
        border-radius: 8px;
        padding: 0.75rem;
        color: var(--pg-muted);
        font-size: 0.76rem;
    }

    .pg-telemetry strong {
        color: var(--pg-cyan);
        display: block;
        font-size: 0.88rem;
        margin-bottom: 0.25rem;
    }

    .pg-status-row {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 0.75rem;
        margin: 1rem 0 1.4rem 0;
    }

    .pg-status {
        border: 1px solid rgba(255, 255, 255, 0.12);
        background:
            linear-gradient(135deg, rgba(94,245,255,0.08), transparent),
            rgba(5, 17, 24, 0.76);
        border-radius: 8px;
        padding: 0.8rem 0.9rem;
        box-shadow: inset 0 0 24px rgba(94,245,255,0.04);
    }

    .pg-status small {
        color: var(--pg-muted);
        display: block;
        font-size: 0.72rem;
        margin-bottom: 0.2rem;
    }

    .pg-status strong {
        color: var(--pg-text);
        font-size: 0.95rem;
    }

    .pg-panel {
        border: 1px solid rgba(94, 245, 255, 0.26);
        background:
            linear-gradient(135deg, rgba(94,245,255,0.09), rgba(122,167,255,0.05) 40%, transparent),
            var(--pg-panel);
        border-radius: 8px;
        padding: 1.1rem;
        margin-bottom: 1rem;
        box-shadow: 0 0 30px rgba(94,245,255,0.08);
    }

    .pg-section-title {
        color: var(--pg-cyan);
        font-size: 1.15rem;
        font-weight: 750;
        margin-bottom: 0.35rem;
    }

    .pg-muted { color: var(--pg-muted); }

    .pg-input-grid {
        display: grid;
        grid-template-columns: 1fr;
        gap: 0.65rem;
        margin-top: 0.8rem;
    }

    .pg-input-callout {
        border: 1px solid rgba(183,255,94,0.24);
        border-radius: 8px;
        padding: 0.75rem;
        color: #dfffce;
        background: rgba(183,255,94,0.07);
        margin-bottom: 0.8rem;
    }

    .pg-agent-grid {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 0.7rem;
        margin: 1rem 0;
    }

    .pg-agent {
        border: 1px solid rgba(94,245,255,0.20);
        background:
            radial-gradient(circle at 15% 15%, rgba(94,245,255,0.13), transparent 45%),
            rgba(4, 12, 20, 0.88);
        border-radius: 8px;
        padding: 0.75rem;
        min-height: 92px;
        position: relative;
        overflow: hidden;
    }

    .pg-agent:after {
        content: "";
        position: absolute;
        left: -45%;
        top: 0;
        width: 35%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(94,245,255,0.20), transparent);
        animation: pgSweep 2.8s linear infinite;
    }

    @keyframes pgSweep {
        from { left: -45%; }
        to { left: 120%; }
    }

    .pg-agent small {
        display: block;
        color: var(--pg-muted);
        font-size: 0.68rem;
        text-transform: uppercase;
        margin-bottom: 0.25rem;
    }

    .pg-agent strong {
        display: block;
        color: var(--pg-text);
        font-size: 0.92rem;
        margin-bottom: 0.35rem;
    }

    .pg-agent span {
        color: var(--pg-lime);
        font-size: 0.76rem;
        font-family: Consolas, monospace;
    }

    .pg-console {
        border: 1px solid rgba(94,245,255,0.20);
        background: rgba(1, 7, 12, 0.92);
        border-radius: 8px;
        padding: 0.85rem;
        font-family: Consolas, monospace;
        color: #bffaff;
        min-height: 150px;
        box-shadow: inset 0 0 24px rgba(94,245,255,0.07);
    }

    .pg-console-line {
        border-bottom: 1px solid rgba(94,245,255,0.08);
        padding: 0.18rem 0;
        font-size: 0.82rem;
    }

    div[data-testid="stTextInput"] input,
    div[data-testid="stTextArea"] textarea {
        background: rgba(1, 7, 12, 0.96);
        color: #eafffb;
        border: 1px solid rgba(94, 245, 255, 0.50);
        border-radius: 6px;
        box-shadow: inset 0 0 18px rgba(94,245,255,0.05);
    }

    div[data-testid="stButton"] button {
        border-radius: 6px;
        border: 1px solid rgba(94, 245, 255, 0.56);
        background:
            linear-gradient(90deg, rgba(28,107,114,0.95), rgba(83,107,36,0.95));
        color: #f4fff8;
        font-weight: 750;
        box-shadow: 0 0 18px rgba(94,245,255,0.12);
    }

    .pg-hypothesis {
        border: 1px solid rgba(94, 245, 255, 0.30);
        background:
            linear-gradient(135deg, rgba(94,245,255,0.10), rgba(255,111,145,0.07)),
            rgba(4, 12, 22, 0.92);
        border-radius: 8px;
        padding: 1rem;
        margin: 0.75rem 0;
        box-shadow: 0 0 28px rgba(94,245,255,0.08);
    }

    .pg-pill {
        display: inline-block;
        margin: 0.15rem 0.35rem 0.15rem 0;
        padding: 0.22rem 0.5rem;
        border: 1px solid rgba(183, 255, 94, 0.32);
        border-radius: 999px;
        color: #ddffc0;
        background: rgba(183, 255, 94, 0.08);
        font-size: 0.78rem;
    }

    .pg-risk {
        border-left: 3px solid var(--pg-amber);
        background: rgba(255, 204, 102, 0.09);
        padding: 0.65rem 0.8rem;
        border-radius: 6px;
        color: #fff3d2;
    }

    @media (max-width: 900px) {
        .pg-title { font-size: 2.15rem; }
        .pg-status-row { grid-template-columns: repeat(2, minmax(0, 1fr)); }
        .pg-agent-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
        .pg-hero { grid-template-columns: 1fr; }
        .pg-visual { min-height: 260px; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if "dossier" not in st.session_state:
    st.session_state.dossier = None
if "markdown" not in st.session_state:
    st.session_state.markdown = None
if "disease_value" not in st.session_state:
    st.session_state.disease_value = "glioblastoma"
if "goal_value" not in st.session_state:
    st.session_state.goal_value = (
        "Generate and prioritize in silico target and candidate hypotheses from biomedical evidence."
    )


def apply_example(disease: str, goal: str) -> None:
    """Apply a preset query before keyed widgets are rendered."""

    st.session_state.disease_value = disease
    st.session_state.goal_value = goal


st.markdown(
    """
    <div class="pg-hero">
      <div class="pg-hero-copy">
        <div class="pg-kicker">PHARMAGENIE // AI DISCOVERY ENGINE</div>
        <h1 class="pg-title">In Silico Drug Discovery Console</h1>
        <div class="pg-subtitle">
          A high-signal discovery cockpit for exploring disease biology, target hypotheses,
          compound strategy, and translational risk before wet-lab validation.
        </div>
      </div>
      <div class="pg-visual">
        <div class="pg-dna">A-T  C-G  G-C
T-A  G-C  A-T
C-G  A-T  T-A
G-C  T-A  C-G</div>
        <div class="pg-orbit"></div>
        <div class="pg-orbit two"></div>
        <div class="pg-core"></div>
        <div class="pg-node n1"></div>
        <div class="pg-node n2"></div>
        <div class="pg-node n3"></div>
        <div class="pg-node n4"></div>
        <div class="pg-telemetry">
          <strong>Target Acquisition Online</strong>
          Evidence graph: active<br>
          Hypothesis engine: Gemini-ready<br>
          Validation mode: in silico
        </div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="pg-status-row">
      <div class="pg-status"><small>Source Mesh</small><strong>PubMed / UniProt / PubChem / Trials</strong></div>
      <div class="pg-status"><small>Reasoning Layer</small><strong>Gemini synthesis when configured</strong></div>
      <div class="pg-status"><small>Output</small><strong>Target + candidate hypotheses</strong></div>
      <div class="pg-status"><small>Safety</small><strong>In silico only, lab validation required</strong></div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="pg-panel">
      <div class="pg-section-title">Agent Swarm Status</div>
      <div class="pg-agent-grid">
        <div class="pg-agent"><small>Coordinator</small><strong>Mission Control</strong><span>STANDBY // routing</span></div>
        <div class="pg-agent"><small>Planner</small><strong>Protocol Designer</strong><span>STANDBY // decomposition</span></div>
        <div class="pg-agent"><small>Literature</small><strong>PubMed Scanner</strong><span>STANDBY // papers</span></div>
        <div class="pg-agent"><small>Protein</small><strong>UniProt Mapper</strong><span>STANDBY // targets</span></div>
        <div class="pg-agent"><small>Compound</small><strong>PubChem Probe</strong><span>STANDBY // molecules</span></div>
        <div class="pg-agent"><small>Trials</small><strong>Clinical Radar</strong><span>STANDBY // translation</span></div>
        <div class="pg-agent"><small>Evidence</small><strong>Signal Ranker</strong><span>STANDBY // scoring</span></div>
        <div class="pg-agent"><small>Report</small><strong>Dossier Forge</strong><span>STANDBY // synthesis</span></div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.container():
    st.markdown('<div class="pg-panel">', unsafe_allow_html=True)
    st.markdown('<div class="pg-section-title">Primary Discovery Input</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="pg-input-callout">Type directly below. This is the launch panel for the discovery workflow.</div>',
        unsafe_allow_html=True,
    )

    input_cols = st.columns([0.85, 1.55])
    with input_cols[0]:
        disease = st.text_input(
            "Disease or biomedical topic",
            key="disease_value",
            placeholder="glioblastoma, NSCLC, Alzheimer disease",
        )
    with input_cols[1]:
        research_goal = st.text_area(
            "Discovery objective",
            key="goal_value",
            placeholder="Example: Identify evidence-linked targets and candidate strategies for early discovery.",
            height=116,
        )

    example_cols = st.columns(4)
    examples = {
        "Glioblastoma": (
            "glioblastoma",
            "Generate and prioritize in silico target and candidate hypotheses from biomedical evidence.",
        ),
        "EGFR NSCLC": (
            "non-small cell lung cancer EGFR",
            "Prioritize target and compound strategies related to EGFR-driven disease biology.",
        ),
        "Alzheimer": (
            "Alzheimer disease",
            "Generate target hypotheses from protein, literature, compound, and trial evidence.",
        ),
        "TNBC": (
            "triple-negative breast cancer",
            "Identify candidate mechanisms and target strategies for experimental follow-up.",
        ),
    }
    for column, (label, values) in zip(example_cols, examples.items(), strict=True):
        column.button(
            label,
            use_container_width=True,
            on_click=apply_example,
            args=(values[0], values[1]),
        )

    run = st.button("Run Discovery Workflow", type="primary", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

if run:
    progress = st.progress(0, text="Initializing discovery engine")
    console = st.empty()
    live_lines: list[str] = []
    staged_agents = [
        ("Coordinator Agent", "mission control handshake"),
        ("Planner Agent", "research protocol decomposition"),
        ("Literature Agent", "PubMed evidence scan"),
        ("Protein Agent", "UniProt target mapping"),
        ("Compound Agent", "PubChem molecular probe"),
        ("Clinical Trial Agent", "translation landscape radar"),
        ("Evidence Ranking Agent", "signal scoring and conflict check"),
        ("Target Discovery Agent", "hypothesis generation"),
        ("Candidate Prioritization Agent", "candidate strategy ranking"),
        ("Report Agent", "dossier assembly"),
    ]

    for index, (agent_name, action) in enumerate(staged_agents, start=1):
        progress.progress(
            min(index / (len(staged_agents) + 1), 0.92),
            text=f"{agent_name}: {action}",
        )
        live_lines.append(f"> {agent_name.upper()} :: {action} ... ONLINE")
        console.markdown(
            '<div class="pg-console">'
            + "".join(f'<div class="pg-console-line">{line}</div>' for line in live_lines[-8:])
            + "</div>",
            unsafe_allow_html=True,
        )
        time.sleep(0.16)

    with st.status("Executing source retrieval and Gemini synthesis", expanded=True) as status:
        request = ResearchRequest(disease=disease, research_goal=research_goal)
        dossier = asyncio.run(CoordinatorAgent().run(request))
        for step in dossier.agent_steps:
            st.write(f"{step.name}: {step.status} - {step.detail}")
        status.update(label="Discovery dossier ready", state="complete")

    progress.progress(1.0, text="Discovery dossier ready")
    live_lines.append("> DISCOVERY DOSSIER :: generated and ranked")
    console.markdown(
        '<div class="pg-console">'
        + "".join(f'<div class="pg-console-line">{line}</div>' for line in live_lines[-8:])
        + "</div>",
        unsafe_allow_html=True,
    )

    st.session_state.dossier = dossier
    st.session_state.markdown = render_markdown(dossier)

dossier = st.session_state.dossier
markdown = st.session_state.markdown

if dossier and markdown:
    tabs = st.tabs(["Hypotheses", "Evidence Matrix", "Dossier", "Downloads"])

    with tabs[0]:
        st.markdown('<div class="pg-section-title">Ranked Discovery Hypotheses</div>', unsafe_allow_html=True)
        for index, hypothesis in enumerate(dossier.discovery_hypotheses, start=1):
            st.markdown('<div class="pg-hypothesis">', unsafe_allow_html=True)
            st.markdown(f"#### {index}. {hypothesis.target}")
            metric_cols = st.columns(4)
            metric_cols[0].metric("Overall", f"{hypothesis.overall_score:.3f}")
            metric_cols[1].metric("Evidence", f"{hypothesis.evidence_score:.2f}")
            metric_cols[2].metric("Feasibility", f"{hypothesis.feasibility_score:.2f}")
            metric_cols[3].metric("Novelty", f"{hypothesis.novelty_score:.2f}")
            st.markdown(f"**Mechanism:** {hypothesis.mechanism}")
            st.markdown(f"**Candidate strategy:** {hypothesis.candidate_strategy}")
            st.markdown(f"**Rationale:** {hypothesis.rationale}")
            st.markdown("".join(f'<span class="pg-pill">{source}</span>' for source in hypothesis.evidence_sources), unsafe_allow_html=True)
            if hypothesis.risk_flags:
                st.markdown(
                    f'<div class="pg-risk">{" | ".join(hypothesis.risk_flags)}</div>',
                    unsafe_allow_html=True,
                )
            st.markdown("</div>", unsafe_allow_html=True)

    with tabs[1]:
        st.markdown('<div class="pg-section-title">Evidence Matrix</div>', unsafe_allow_html=True)
        st.dataframe(
            [
                {
                    "source": item.source,
                    "title": item.title,
                    "confidence": item.confidence,
                    "mode": item.metadata.get("client", "unknown"),
                    "url": item.url,
                    "summary": item.summary,
                }
                for item in dossier.evidence
            ],
            use_container_width=True,
            hide_index=True,
        )

    with tabs[2]:
        st.markdown(markdown)

    with tabs[3]:
        with tempfile.TemporaryDirectory() as tmpdir:
            pdf_path = write_pdf(dossier, Path(tmpdir) / "pharmagenie-dossier.pdf")
            pdf_bytes = pdf_path.read_bytes()

        download_cols = st.columns(2)
        download_cols[0].download_button(
            "Download Markdown",
            markdown,
            "pharmagenie-dossier.md",
            "text/markdown",
            use_container_width=True,
        )
        download_cols[1].download_button(
            "Download PDF",
            pdf_bytes,
            "pharmagenie-dossier.pdf",
            "application/pdf",
            use_container_width=True,
        )
else:
    st.markdown(
        """
        <div class="pg-panel">
          <div class="pg-section-title">Awaiting discovery run</div>
          <div class="pg-muted">
            Fill the visible input fields above and launch the workflow. Results will appear as
            ranked hypothesis cards, a source evidence matrix, and a downloadable dossier.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
