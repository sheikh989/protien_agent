# -*- coding: utf-8 -*-
"""
AfDesign Peptide Binder Design — Streamlit App
Converted from ColabDesign notebook (binder_design.py)
"""

import os
import re
import warnings
import tempfile
import streamlit as st
import numpy as np
import requests
import plotly.express as px

warnings.simplefilter(action='ignore', category=FutureWarning)

# ───────────────────────────────────────────────────────────────────────
# Page config & custom CSS
# ───────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AfDesign · Peptide Binder Designer",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

:root {
    --bg-primary: #0d1117;
    --bg-secondary: #161b22;
    --bg-card: rgba(22, 27, 34, 0.85);
    --border-color: rgba(48, 54, 61, 0.7);
    --accent: #58a6ff;
    --accent-glow: rgba(88, 166, 255, 0.25);
    --accent-secondary: #7ee787;
    --text-primary: #e6edf3;
    --text-secondary: #8b949e;
    --gradient-1: linear-gradient(135deg, #58a6ff 0%, #bc8cff 50%, #f778ba 100%);
    --gradient-2: linear-gradient(135deg, #1a1f35 0%, #0d1117 100%);
}

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

.stApp {
    background: var(--gradient-2);
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: var(--bg-secondary) !important;
    border-right: 1px solid var(--border-color);
}

section[data-testid="stSidebar"] .stMarkdown h3 {
    background: var(--gradient-1);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 700;
    letter-spacing: -0.02em;
    margin-top: 1.2rem;
}

/* Hero header */
.hero-title {
    font-size: 2.4rem;
    font-weight: 700;
    background: var(--gradient-1);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0;
    letter-spacing: -0.03em;
    animation: fadeInUp 0.8s ease-out;
}

.hero-sub {
    color: var(--text-secondary);
    font-size: 1.05rem;
    margin-top: 0.3rem;
    animation: fadeInUp 1s ease-out;
}

/* Glass cards */
.glass-card {
    background: var(--bg-card);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid var(--border-color);
    border-radius: 16px;
    padding: 1.5rem 1.8rem;
    margin-bottom: 1.2rem;
    transition: transform 0.25s ease, box-shadow 0.25s ease;
}
.glass-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.35);
}

.card-title {
    font-size: 1.15rem;
    font-weight: 600;
    color: var(--accent);
    margin-bottom: 0.8rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

/* Metric pills */
.metric-row {
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
    margin-bottom: 1rem;
}
.metric-pill {
    background: rgba(88, 166, 255, 0.08);
    border: 1px solid rgba(88, 166, 255, 0.2);
    border-radius: 12px;
    padding: 0.9rem 1.4rem;
    min-width: 150px;
    flex: 1;
    text-align: center;
    transition: border-color 0.3s ease;
}
.metric-pill:hover {
    border-color: var(--accent);
}
.metric-pill .label {
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--text-secondary);
    margin-bottom: 0.3rem;
}
.metric-pill .value {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--text-primary);
}

/* Sequence display */
.seq-box {
    font-family: 'Courier New', monospace;
    font-size: 1.15rem;
    letter-spacing: 0.15em;
    word-break: break-all;
    background: rgba(88,166,255,0.06);
    border: 1px solid rgba(88,166,255,0.15);
    border-radius: 12px;
    padding: 1rem 1.2rem;
    color: var(--accent-secondary);
    line-height: 1.8;
}

/* Buttons */
.stButton > button {
    background: var(--gradient-1) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.75rem 2rem !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    letter-spacing: 0.02em;
    transition: opacity 0.3s ease, transform 0.2s ease !important;
}
.stButton > button:hover {
    opacity: 0.9 !important;
    transform: translateY(-1px) !important;
}

/* Download button */
.stDownloadButton > button {
    background: rgba(126, 231, 135, 0.12) !important;
    border: 1px solid rgba(126, 231, 135, 0.35) !important;
    color: var(--accent-secondary) !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    transition: background 0.3s ease !important;
}
.stDownloadButton > button:hover {
    background: rgba(126, 231, 135, 0.22) !important;
}

/* Animations */
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(20px); }
    to   { opacity: 1; transform: translateY(0); }
}

/* Status indicator */
.status-dot {
    display: inline-block;
    width: 8px; height: 8px;
    border-radius: 50%;
    margin-right: 6px;
    animation: pulse 2s infinite;
}
.status-dot.ready   { background: var(--accent-secondary); }
.status-dot.running { background: #f0883e; }

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50%      { opacity: 0.4; }
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ───────────────────────────────────────────────────────────────────────
# Helper: fetch PDB file
# ───────────────────────────────────────────────────────────────────────
PARAMS_DIR = "params"

@st.cache_data(show_spinner=False)
def fetch_pdb(pdb_code: str) -> str:
    """Download a PDB from RCSB or AlphaFoldDB and return the local path."""
    if os.path.isfile(pdb_code):
        return pdb_code
    if len(pdb_code) == 4:
        url = f"https://files.rcsb.org/view/{pdb_code}.pdb"
        out_path = f"{pdb_code}.pdb"
    else:
        url = f"https://alphafold.ebi.ac.uk/files/AF-{pdb_code}-F1-model_v3.pdb"
        out_path = f"AF-{pdb_code}-F1-model_v3.pdb"
    if not os.path.isfile(out_path):
        resp = requests.get(url, timeout=60)
        resp.raise_for_status()
        with open(out_path, "w") as f:
            f.write(resp.text)
    return out_path


def ensure_params():
    """Check if AlphaFold parameters are downloaded."""
    return os.path.isdir(PARAMS_DIR)


# ───────────────────────────────────────────────────────────────────────
# Hero header
# ───────────────────────────────────────────────────────────────────────
st.markdown('<p class="hero-title">🧬 AfDesign · Peptide Binder Designer</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="hero-sub">'
    'Generate / hallucinate a protein binder sequence that AlphaFold predicts will bind your target structure. '
    'Maximises interface contacts and binder pLDDT.'
    '</p>',
    unsafe_allow_html=True,
)

# ───────────────────────────────────────────────────────────────────────
# Sidebar — Inputs
# ───────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🎯 Target Info")
    pdb_code = st.text_input(
        "PDB / UniProt Code",
        value="5F9R",
        help="Enter a 4-letter PDB code (e.g. 5F9R), a UniProt code (to fetch from AlphaFoldDB), or leave blank and upload a file below.",
    )
    uploaded_pdb = st.file_uploader("Or upload a PDB file", type=["pdb"])
    target_chain = st.text_input("Target Chain", value="B", help="Chain identifier for the target protein.")
    target_hotspot = st.text_input(
        "Target Hotspot",
        value="",
        help='Restrict loss to specific positions on the target (e.g. "1-10,12,15"). Leave blank for no restriction.',
    )
    target_flexible = st.toggle("Flexible Target Backbone", value=False, help="Allow backbone of target to be flexible during design.")

    st.markdown("---")
    st.markdown("### 🔗 Binder Info")
    binder_len = st.slider("Binder Length", min_value=10, max_value=200, value=25, step=1, help="Length of the binder peptide to hallucinate.")
    binder_seq_input = st.text_input(
        "Initial Binder Sequence",
        value="",
        help="Optional amino acid sequence to initialize the design. If provided, binder length is set to its length.",
    )
    binder_chain_input = st.text_input(
        "Binder Chain (supervised)",
        value="",
        help="If defined, supervised loss is used and binder length is ignored.",
    )

    st.markdown("---")
    st.markdown("### ⚙️ Model Configuration")
    use_multimer = st.toggle("Use AlphaFold-Multimer", value=False, help="Use the multimer model for design.")
    num_recycles = st.select_slider("Number of Recycles", options=[0, 1, 3, 6], value=1)
    num_models_sel = st.selectbox("Number of Models", options=["1", "2", "3", "4", "5", "all"], index=0, help="Number of trained models to use during optimization.")

    st.markdown("---")
    st.markdown("### 🚀 Optimization")
    optimizer = st.selectbox(
        "Optimizer",
        options=["pssm_semigreedy", "3stage", "semigreedy", "pssm", "logits", "soft", "hard"],
        index=0,
        help=(
            "• pssm_semigreedy — uses designed PSSM to bias semigreedy opt (recommended)\n"
            "• 3stage — gradient descent: logits → soft → hard\n"
            "• semigreedy — random mutations, accepts if loss decreases\n"
            "• pssm — GD logits→soft for a sequence profile\n"
            "• logits / soft / hard — raw GD optimization"
        ),
    )

    with st.expander("Advanced GD Settings", expanded=False):
        gd_method = st.selectbox(
            "GD Method",
            options=[
                "sgd", "adam", "adamw", "adabelief", "adafactor", "adagrad",
                "fromage", "lamb", "lars", "noisy_sgd", "dpsgd", "radam",
                "rmsprop", "sm3", "yogi",
            ],
            index=0,
        )
        learning_rate = st.number_input("Learning Rate", min_value=0.0001, max_value=10.0, value=0.1, step=0.01, format="%.4f")
        norm_seq_grad = st.toggle("Normalize Sequence Gradient", value=True)
        dropout = st.toggle("Dropout", value=True)

    st.markdown("---")
    st.markdown("### 🎨 Visualization")
    color_mode = st.selectbox("Color Scheme", options=["pLDDT", "chain", "rainbow"], index=0)
    show_sidechains = st.toggle("Show Sidechains", value=False)
    show_mainchains = st.toggle("Show Mainchains", value=False)

# ───────────────────────────────────────────────────────────────────────
# Process inputs
# ───────────────────────────────────────────────────────────────────────
binder_seq = re.sub("[^A-Z]", "", binder_seq_input.upper()) if binder_seq_input else ""
if len(binder_seq) > 0:
    binder_len_final = len(binder_seq)
else:
    binder_seq = None
    binder_len_final = binder_len

binder_chain = binder_chain_input if binder_chain_input.strip() else None
hotspot = target_hotspot if target_hotspot.strip() else None
num_models_int = 5 if num_models_sel == "all" else int(num_models_sel)

# ───────────────────────────────────────────────────────────────────────
# Summary cards
# ───────────────────────────────────────────────────────────────────────
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(
        f"""<div class="glass-card">
            <div class="card-title">🎯 Target</div>
            <div class="metric-row">
                <div class="metric-pill"><div class="label">PDB</div><div class="value">{pdb_code or "Upload"}</div></div>
                <div class="metric-pill"><div class="label">Chain</div><div class="value">{target_chain}</div></div>
            </div>
        </div>""",
        unsafe_allow_html=True,
    )
with col2:
    st.markdown(
        f"""<div class="glass-card">
            <div class="card-title">🔗 Binder</div>
            <div class="metric-row">
                <div class="metric-pill"><div class="label">Length</div><div class="value">{binder_len_final}</div></div>
                <div class="metric-pill"><div class="label">Mode</div><div class="value">{"Supervised" if binder_chain else "Hallucinate"}</div></div>
            </div>
        </div>""",
        unsafe_allow_html=True,
    )
with col3:
    st.markdown(
        f"""<div class="glass-card">
            <div class="card-title">⚙️ Model</div>
            <div class="metric-row">
                <div class="metric-pill"><div class="label">Optimizer</div><div class="value" style="font-size:1rem;">{optimizer}</div></div>
                <div class="metric-pill"><div class="label">Models</div><div class="value">{num_models_sel}</div></div>
            </div>
        </div>""",
        unsafe_allow_html=True,
    )

# ───────────────────────────────────────────────────────────────────────
# Run button & pipeline
# ───────────────────────────────────────────────────────────────────────
st.markdown("---")
run_clicked = st.button("▶  Run Binder Design", use_container_width=True, type="primary")

if run_clicked:
    # ── 1. Resolve PDB file ──────────────────────────────────────────
    with st.status("🔬 Running AfDesign Pipeline...", expanded=True) as status:
        try:
            st.write("📥 Resolving PDB structure...")
            if uploaded_pdb is not None:
                tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdb")
                tmp.write(uploaded_pdb.read())
                tmp.close()
                pdb_path = tmp.name
            else:
                pdb_path = fetch_pdb(pdb_code)

            # ── 2. Check params ──────────────────────────────────────
            if not ensure_params():
                st.warning(
                    "⚠️ AlphaFold parameters not found in `./params/`. "
                    "Please download them first:\n\n"
                    "```bash\n"
                    "mkdir params\n"
                    "wget https://storage.googleapis.com/alphafold/alphafold_params_2022-12-06.tar\n"
                    "tar -xf alphafold_params_2022-12-06.tar -C params\n"
                    "```"
                )
                status.update(label="❌ Missing AlphaFold params", state="error")
                st.stop()

            # ── 3. Build model ───────────────────────────────────────
            st.write("🏗️ Building AfDesign model...")
            from colabdesign import mk_afdesign_model, clear_mem
            from colabdesign.shared.utils import copy_dict
            from colabdesign.af.alphafold.common import residue_constants
            from scipy.special import softmax

            clear_mem()
            model = mk_afdesign_model(
                protocol="binder",
                use_multimer=use_multimer,
                num_recycles=num_recycles,
                recycle_mode="sample",
            )

            prep_kwargs = {
                "pdb_filename": pdb_path,
                "chain": target_chain,
                "binder_len": binder_len_final,
                "binder_chain": binder_chain,
                "hotspot": hotspot,
                "use_multimer": use_multimer,
                "rm_target_seq": target_flexible,
            }
            model.prep_inputs(**prep_kwargs, ignore_missing=False)
            st.write(f"  ↳ Target length: **{model._target_len}** · Binder length: **{model._binder_len}**")

            # ── 4. Optimize ──────────────────────────────────────────
            st.write(f"🧪 Running optimization ({optimizer})...")
            model.restart(seq=binder_seq)
            model.set_optimizer(
                optimizer=gd_method,
                learning_rate=learning_rate,
                norm_seq_grad=norm_seq_grad,
            )
            models_list = model._model_names[:num_models_int]
            flags = {"num_recycles": num_recycles, "models": models_list, "dropout": dropout}

            pssm = None

            if optimizer == "3stage":
                model.design_3stage(120, 60, 10, **flags)
                pssm = softmax(model._tmp["seq_logits"], -1)

            elif optimizer == "pssm_semigreedy":
                model.design_pssm_semigreedy(120, 32, **flags)
                pssm = softmax(model._tmp["seq_logits"], 1)

            elif optimizer == "semigreedy":
                model.design_pssm_semigreedy(0, 32, **flags)
                pssm = None

            elif optimizer == "pssm":
                model.design_logits(120, e_soft=1.0, num_models=1, ramp_recycles=True, **flags)
                model.design_soft(32, num_models=1, **flags)
                flags.update({"dropout": False, "save_best": True})
                model.design_soft(10, num_models=num_models_int, **flags)
                pssm = softmax(model.aux["seq"]["logits"], -1)

            else:
                opt_map = {
                    "logits": model.design_logits,
                    "soft": model.design_soft,
                    "hard": model.design_hard,
                }
                if optimizer in opt_map:
                    opt_map[optimizer](120, num_models=1, ramp_recycles=True, **flags)
                    flags.update({"dropout": False, "save_best": True})
                    opt_map[optimizer](10, num_models=num_models_int, **flags)
                    pssm = softmax(model.aux["seq"]["logits"], -1)

            st.write("✅ Optimization complete!")

            # ── 5. Save PDB ──────────────────────────────────────────
            out_pdb = f"{model.protocol}.pdb"
            model.save_pdb(out_pdb)

            status.update(label="✅ Design Complete!", state="complete")

        except Exception as e:
            status.update(label="❌ Error", state="error")
            st.error(f"**Error:** {e}")
            st.stop()

    # ── Results ──────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown('<p class="hero-title" style="font-size:1.6rem;">📊 Results</p>', unsafe_allow_html=True)

    # Metrics
    log = model._tmp.get("best", {}).get("aux", {}).get("log", {})
    metric_cols = st.columns(4)
    metrics_to_show = [
        ("pLDDT (binder)", log.get("plddt", None)),
        ("pAE", log.get("pae", None)),
        ("i_pAE", log.get("i_pae", None)),
        ("i_con", log.get("i_con", None)),
    ]
    for col, (label, val) in zip(metric_cols, metrics_to_show):
        with col:
            display_val = f"{val:.3f}" if val is not None else "—"
            st.markdown(
                f"""<div class="metric-pill" style="text-align:center;">
                    <div class="label">{label}</div>
                    <div class="value">{display_val}</div>
                </div>""",
                unsafe_allow_html=True,
            )

    # Designed sequence
    st.markdown('<div class="glass-card"><div class="card-title">🧬 Designed Sequence</div>', unsafe_allow_html=True)
    seqs = model.get_seqs()
    if seqs:
        seq_str = seqs[0] if isinstance(seqs, list) else str(seqs)
        st.markdown(f'<div class="seq-box">{seq_str}</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Download PDB
    res_col1, res_col2 = st.columns([1, 1])
    with res_col1:
        if os.path.isfile(out_pdb):
            with open(out_pdb, "r") as f:
                pdb_data = f.read()
            st.download_button(
                label="⬇️ Download Designed PDB",
                data=pdb_data,
                file_name=out_pdb,
                mime="chemical/x-pdb",
                use_container_width=True,
            )

    # PSSM heatmap
    if pssm is not None:
        st.markdown(
            '<div class="glass-card"><div class="card-title">📈 Amino Acid Probability (PSSM)</div>',
            unsafe_allow_html=True,
        )
        pssm_2d = pssm.mean(0) if pssm.ndim == 3 else pssm
        fig = px.imshow(
            pssm_2d.T,
            labels=dict(x="Position", y="Amino Acid", color="Probability"),
            y=list(residue_constants.restypes),
            zmin=0,
            zmax=1,
            color_continuous_scale="Viridis",
            template="plotly_dark",
            aspect="auto",
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter", color="#e6edf3"),
            margin=dict(l=50, r=20, t=30, b=40),
            height=400,
        )
        fig.update_xaxes(side="top")
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Log details
    with st.expander("📋 Full Design Log", expanded=False):
        st.json(log)

else:
    # ── Landing / idle state ─────────────────────────────────────────
    st.markdown(
        """
        <div class="glass-card" style="text-align:center; padding:3rem 2rem;">
            <div style="font-size:3rem; margin-bottom:0.8rem;">🧬</div>
            <div style="font-size:1.2rem; font-weight:600; color:#e6edf3; margin-bottom:0.5rem;">
                Ready to Design
            </div>
            <div style="color:#8b949e; max-width:500px; margin:0 auto;">
                Configure your target protein and binder parameters in the sidebar,
                then click <strong style="color:#58a6ff;">Run Binder Design</strong> to begin.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="glass-card">
            <div class="card-title">📖 How It Works</div>
            <div style="color:#8b949e; line-height:1.75;">
                <strong style="color:#e6edf3;">1. Provide a target</strong> — Enter a PDB code, UniProt ID, or upload a PDB file.<br/>
                <strong style="color:#e6edf3;">2. Set binder parameters</strong> — Choose length, optional initial sequence, and chain info.<br/>
                <strong style="color:#e6edf3;">3. Configure model</strong> — Select recycles, model count, and optimizer strategy.<br/>
                <strong style="color:#e6edf3;">4. Run design</strong> — AfDesign hallucinate a binder sequence and optimizes for interface contacts & pLDDT.<br/>
                <strong style="color:#e6edf3;">5. Analyze results</strong> — View metrics, designed sequence, PSSM heatmap, and download the PDB.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div style="text-align:center; color:#484f58; font-size:0.8rem; margin-top:2rem;">
            Powered by <a href="https://github.com/sokrypton/ColabDesign" target="_blank" style="color:#58a6ff; text-decoration:none;">ColabDesign</a>
            &nbsp;·&nbsp; AlphaFold Parameters © DeepMind
        </div>
        """,
        unsafe_allow_html=True,
    )
