import streamlit as st

# ---------------------------
# Page config + style
# ---------------------------
st.set_page_config(
    page_title="Cardiac Output Flow Chart",
    page_icon="🫀",
    layout="wide",
)

st.markdown(
    """
    <style>
      .big-title { font-size: 2.1rem; font-weight: 800; margin-bottom: 0.25rem; }
      .subtitle { color: #555; font-size: 1.05rem; margin-top: 0; }

      .cell {
        border: 1px solid #e9e9e9;
        border-radius: 14px;
        padding: 14px 14px 10px 14px;
        background: white;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        min-height: 180px;
      }
      .cell h4 {
        margin: 0 0 6px 0; font-size: 1.05rem;
      }
      .cell .desc {
        font-size: 0.92rem; color: #666; margin-bottom: 8px; min-height: 36px;
      }
      .arrow-big {
        font-size: 2.0rem; font-weight: 800; text-align:center; margin: 4px 0 8px 0;
      }
      .downstream {
        border: 1px dashed #eee;
        border-radius: 12px;
        padding: 10px;
        background: #fafafa;
        text-align:center;
        font-size: 1.05rem;
        font-weight: 700;
      }

      .tiny { font-size:0.9rem; color:#666; }
      .good { color: #0a7a2f; font-weight: 700; }
      .bad  { color: #b00020; font-weight: 700; }

      .stButton button {
        border-radius: 999px !important;
        padding: 0.4rem 0.9rem !important;
        font-weight: 700 !important;
      }
      .arrow-buttons .stButton button { width: 100%; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------
# Helpers
# ---------------------------
def effect_arrow(effect: int):
    return "↑" if effect > 0 else ("↓" if effect < 0 else "—")

def expected_direction(before, after, eps=1e-6):
    if abs(after - before) < eps:
        return "No change"
    return "Increase" if after > before else "Decrease"

def compute_state():
    """
    Discrete arrow-based teaching model.
    Outputs only direction + hidden numeric internal calc.
    """
    hr0 = st.session_state.hr_baseline
    sv0 = st.session_state.sv_baseline

    HR_STEP = 0.12
    SV_STEP = 0.12

    net_chrono = st.session_state.chrono_pos_effect - st.session_state.chrono_neg_effect
    net_ino    = st.session_state.ino_pos_effect    - st.session_state.ino_neg_effect
    venous     = st.session_state.venous_return_effect
    afterload  = st.session_state.afterload_effect

    hr = hr0 * (1 + HR_STEP * net_chrono)
    sv = sv0 * (1 + SV_STEP * (net_ino + venous - afterload))
    hr = max(30, min(180, hr))
    sv = max(30, min(140, sv))
    co = hr * sv / 1000.0
    return hr, sv, co

def direction_vs_baseline(value, baseline, eps=1e-6):
    if abs(value - baseline) < eps:
        return 0
    return 1 if value > baseline else -1

def control_cell(
    title,
    desc,
    key_effect,
    confusion_options,
    links=None,
):
    """
    Renders a squared flow-chart control cell with:
      - current arrow
      - prediction radio INSIDE the cell
      - ↑ / ↓ buttons INSIDE the cell
      - feedback INSIDE the cell
    """
    links = links or []

    # Current state before change
    HR_before, SV_before, CO_before = compute_state()

    effect = st.session_state[key_effect]
    arrow_text = effect_arrow(effect)

    st.markdown("<div class='cell'>", unsafe_allow_html=True)
    st.markdown(f"<h4>{title}</h4>", unsafe_allow_html=True)
    st.markdown(f"<div class='desc'>{desc}</div>", unsafe_allow_html=True)

    st.markdown(f"<div class='arrow-big'>{arrow_text}</div>", unsafe_allow_html=True)

    pred_key = f"pred_{key_effect}"
    if pred_key not in st.session_state:
        st.session_state[pred_key] = None

    st.session_state[pred_key] = st.radio(
        "Predict CO:",
        ["Increase", "Decrease", "No change"],
        index=None if st.session_state[pred_key] is None else ["Increase","Decrease","No change"].index(st.session_state[pred_key]),
        key=f"radio_{key_effect}",
        horizontal=True
    )

    bcol1, bcol2 = st.columns(2)
    with bcol1:
        inc = st.button("↑ Increase", key=f"inc_{key_effect}")
    with bcol2:
        dec = st.button("↓ Decrease", key=f"dec_{key_effect}")

    if inc or dec:
        if st.session_state[pred_key] is None:
            st.warning("Make a prediction first 🙂")
        else:
            st.session_state[key_effect] = 1 if inc else -1

            HR_after, SV_after, CO_after = compute_state()
            direction_CO = expected_direction(CO_before, CO_after)
            correct = (direction_CO == st.session_state[pred_key])

            st.markdown("**Result:**")
            st.write(f"CO will **{direction_CO}**.")

            if correct:
                st.markdown("<div class='good'>✅ Correct prediction!</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div class='bad'>❌ Not quite.</div>", unsafe_allow_html=True)
                confuse = st.selectbox(
                    "Where did you get confused?",
                    confusion_options,
                    index=None,
                    key=f"conf_{key_effect}"
                )
                if confuse:
                    st.info("Thanks — that point is worth reviewing.")

    if links:
        with st.expander("Learn more"):
            for text, url in links:
                st.markdown(f"- [{text}]({url})")

    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------
# Ensure session defaults (no missing-key errors)
# ---------------------------
defaults = {
    "hr_baseline": 70.0,
    "sv_baseline": 70.0,

    "chrono_pos_effect": 0,
    "chrono_neg_effect": 0,
    "ino_pos_effect": 0,
    "ino_neg_effect": 0,
    "venous_return_effect": 0,
    "afterload_effect": 0,
}
for k, v in defaults.items():
    st.session_state.setdefault(k, v)

# ---------------------------
# Header
# ---------------------------
st.markdown("<div class='big-title'>🫀 Cardiac Output Flow Chart</div>", unsafe_allow_html=True)
st.markdown(
    "<p class='subtitle'>Choose ↑ or ↓ inside any box. Downstream arrows update automatically.</p>",
    unsafe_allow_html=True
)

# ---------------------------
# Compute arrows for downstream boxes
# ---------------------------
hr, sv, co = compute_state()
hr_dir = direction_vs_baseline(hr, st.session_state.hr_baseline)
sv_dir = direction_vs_baseline(sv, st.session_state.sv_baseline)
co_dir = direction_vs_baseline(co, (st.session_state.hr_baseline * st.session_state.sv_baseline / 1000.0))

HR_arrow = effect_arrow(hr_dir)
SV_arrow = effect_arrow(sv_dir)
CO_arrow = effect_arrow(co_dir)

# ---------------------------
# Flow chart layout (squared / aligned)
# ---------------------------

# Row 1: four equal "agent" boxes, pos/neg aligned
r1c1, r1c2, r1c3, r1c4 = st.columns(4, gap="large")

with r1c1:
    control_cell(
        title="Positive chronotropic agents",
        desc="Increase SA/AV node activity.",
        key_effect="chrono_pos_effect",
        confusion_options=[
            "How positive chronotropes affect HR",
            "How HR affects CO",
            "How SV affects CO",
            "Not sure / other"
        ],
        links=[
            ("Cleveland Clinic: Cardiac output basics", "https://my.clevelandclinic.org/health/articles/17076-cardiac-output"),
            ("CDC: Heart failure overview", "https://www.cdc.gov/heartfailure/index.htm"),
        ],
    )

with r1c2:
    control_cell(
        title="Negative chronotropic agents",
        desc="Decrease SA/AV node activity.",
        key_effect="chrono_neg_effect",
        confusion_options=[
            "How negative chronotropes affect HR",
            "How HR affects CO",
            "How SV affects CO",
            "Not sure / other"
        ],
        links=[
            ("Cleveland Clinic: Heart rate & physiology", "https://my.clevelandclinic.org/health/articles/17076-cardiac-output"),
            ("CDC: Heart failure overview", "https://www.cdc.gov/heartfailure/index.htm"),
        ],
    )

with r1c3:
    control_cell(
        title="Positive inotropic agents",
        desc="Increase myocardial contractility.",
        key_effect="ino_pos_effect",
        confusion_options=[
            "How positive inotropes affect SV",
            "How SV affects CO",
            "Not sure / other"
        ],
        links=[
            ("Cleveland Clinic: Inotropes", "https://my.clevelandclinic.org/health/drugs/22633-inotropes"),
            ("CDC: Heart failure overview", "https://www.cdc.gov/heartfailure/index.htm"),
        ],
    )

with r1c4:
    control_cell(
        title="Negative inotropic agents",
        desc="Decrease myocardial contractility.",
        key_effect="ino_neg_effect",
        confusion_options=[
            "How negative inotropes affect SV",
            "How SV affects CO",
            "Not sure / other"
        ],
        links=[
            ("Cleveland Clinic: Inotropes", "https://my.clevelandclinic.org/health/drugs/22633-inotropes"),
            ("CDC: Heart failure overview", "https://www.cdc.gov/heartfailure/index.htm"),
        ],
    )

st.write("")  # spacing

# Row 2: venous return + afterload aligned equally
r2c1, r2c2 = st.columns(2, gap="large")
with r2c1:
    control_cell(
        title="Venous return (preload)",
        desc="More blood returning → more stretch → higher SV.",
        key_effect="venous_return_effect",
        confusion_options=[
            "Frank–Starling / preload → SV",
            "How SV affects CO",
            "Not sure / other"
        ],
        links=[
            ("OpenStax A&P: Stroke volume/preload", "https://openstax.org/books/anatomy-and-physiology/pages/19-4-cardiac-physiology"),
            ("CDC: Heart failure overview", "https://www.cdc.gov/heartfailure/index.htm"),
        ],
    )

with r2c2:
    control_cell(
        title="Afterload",
        desc="Higher arterial resistance makes ejection harder → lower SV.",
        key_effect="afterload_effect",
        confusion_options=[
            "Afterload → SV (inverse)",
            "How SV affects CO",
            "Not sure / other"
        ],
        links=[
            ("OpenStax A&P: Afterload", "https://openstax.org/books/anatomy-and-physiology/pages/19-4-cardiac-physiology"),
            ("CDC: Heart failure overview", "https://www.cdc.gov/heartfailure/index.htm"),
        ],
    )

st.write("")

# Row 3: downstream physiology (auto-filled arrows)
r3c1, r3c2 = st.columns(2, gap="large")
with r3c1:
    st.markdown(
        f"""
        <div class="cell">
          <h4>Heart rate (HR)</h4>
          <div class="desc">Beats per minute.</div>
          <div class="arrow-big">{HR_arrow}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with r3c2:
    st.markdown(
        f"""
        <div class="cell">
          <h4>Stroke volume (SV)</h4>
          <div class="desc">Blood pumped per beat.</div>
          <div class="arrow-big">{SV_arrow}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.write("")

# Row 4: cardiac output (auto-filled arrow)
st.markdown(
    f"""
    <div class="cell" style="max-width:520px; margin:auto;">
      <h4>Cardiac output (CO)</h4>
      <div class="desc">Blood pumped per minute.</div>
      <div class="arrow-big">{CO_arrow}</div>
    </div>
    """,
    unsafe_allow_html=True
)

st.write("")
with st.expander("Teacher controls (optional)"):
    st.session_state.hr_baseline = st.slider("Baseline HR (hidden from students)", 40, 120, int(st.session_state.hr_baseline))
    st.session_state.sv_baseline = st.slider("Baseline SV (hidden from students)", 40, 120, int(st.session_state.sv_baseline))
    if st.button("Reset all arrows to baseline (—)"):
        st.session_state.chrono_pos_effect = 0
        st.session_state.chrono_neg_effect = 0
        st.session_state.ino_pos_effect = 0
        st.session_state.ino_neg_effect = 0
        st.session_state.venous_return_effect = 0
        st.session_state.afterload_effect = 0
        st.rerun()

st.caption(
    "Simplified learning model: CO = HR × SV. Arrows represent direction of change only."
)
