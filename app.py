import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config
import math

# ---------------------------
# Page config + style
# ---------------------------
st.set_page_config(
    page_title="Cardiac Output Explorer",
    page_icon="🫀",
    layout="wide",
)

st.markdown(
    """
    <style>
      .big-title {
        font-size: 2.2rem; font-weight: 800; margin-bottom: 0.25rem;
      }
      .subtitle {
        color: #555; font-size: 1.05rem; margin-top: 0;
      }
      .badge {
        display:inline-block; padding:0.2rem 0.6rem; border-radius:999px;
        background:#f2f2f2; font-size:0.85rem; margin-right:0.35rem;
      }
      .node-card {
        border:1px solid #eee; border-radius:16px; padding:14px 16px;
        background: #fff; box-shadow: 0 2px 10px rgba(0,0,0,0.04);
      }
      .tiny {
        font-size:0.9rem; color:#666;
      }
      .good {
        color: #0a7a2f; font-weight: 700;
      }
      .bad {
        color: #b00020; font-weight: 700;
      }
      .stButton button {
        border-radius: 999px !important;
        padding: 0.5rem 1rem !important;
      }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------------------------
# Helper functions
# ---------------------------
def clamp(x, lo, hi):
    return max(lo, min(hi, x))

def arrow(delta):
    if abs(delta) < 1e-6:
        return "→"
    return "⬆️" if delta > 0 else "⬇️"

def pretty_pct(x):
    return f"{x*100:.0f}%"

def compute_sv(baseline_sv, preload_factor, afterload_factor, contractility_factor):
    """
    Simple teaching model:
    SV ~ baseline * preload * contractility / afterload
    """
    return baseline_sv * preload_factor * contractility_factor / afterload_factor

def compute_state():
    hr = st.session_state.hr_baseline * st.session_state.chrono_factor
    contractility = st.session_state.contractility_baseline * st.session_state.ino_factor
    sv = compute_sv(
        st.session_state.sv_baseline,
        st.session_state.preload_factor,
        st.session_state.afterload_factor,
        contractility / st.session_state.contractility_baseline
    )
    co = hr * sv / 1000.0  # ml/min → L/min
    return hr, contractility, sv, co

def expected_direction(before, after):
    if abs(after - before) < 1e-6:
        return "No change"
    return "Increase" if after > before else "Decrease"

# ---------------------------
# Initialize session state
# ---------------------------
if "initialized" not in st.session_state:
    st.session_state.initialized = True

    # Baselines (modifiable if you want)
    st.session_state.hr_baseline = 70.0           # bpm
    st.session_state.sv_baseline = 70.0           # ml/beat
    st.session_state.contractility_baseline = 1.0 # normalized

    # Factors controlled in the flow chart
    st.session_state.chrono_factor = 1.0        # affects HR
    st.session_state.ino_factor = 1.0           # affects contractility
    st.session_state.preload_factor = 1.0       # affects SV
    st.session_state.afterload_factor = 1.0     # affects SV (inverse)

    # UI memory
    st.session_state.last_clicked = None
    st.session_state.show_quiz = False
    st.session_state.quiz_node = None
    st.session_state.prediction = None
    st.session_state.after_submit = False
    st.session_state.was_correct = None
    st.session_state.confusion_point = None

# ---------------------------
# Title
# ---------------------------
st.markdown("<div class='big-title'>🫀 Cardiac Output Explorer</div>", unsafe_allow_html=True)
st.markdown(
    "<p class='subtitle'>Click a control node, predict what happens, and watch the downstream physiology update.</p>",
    unsafe_allow_html=True
)

# ---------------------------
# Layout
# ---------------------------
left, right = st.columns([1.8, 1.0], gap="large")

# ---------------------------
# Compute current values
# ---------------------------
hr, contractility, sv, co = compute_state()

# ---------------------------
# LEFT: Interactive flow chart
# ---------------------------
with left:
    st.markdown("### Interactive flow chart")

    # deltas vs baseline for arrows
    hr0 = st.session_state.hr_baseline
    sv0 = st.session_state.sv_baseline
    co0 = hr0 * sv0 / 1000.0

    hr_delta = hr - hr0
    sv_delta = sv - sv0
    co_delta = co - co0

    # Nodes
    nodes = [
        Node(
            id="chrono",
            label=f"Chronotropic Agents\n(factor {pretty_pct(st.session_state.chrono_factor)})",
            size=850,
            color="#FFE8A3",
            shape="box"
        ),
        Node(
            id="ino",
            label=f"Inotropic Agents\n(factor {pretty_pct(st.session_state.ino_factor)})",
            size=850,
            color="#FFD6CC",
            shape="box"
        ),
        Node(
            id="preload",
            label=f"Preload\n(factor {pretty_pct(st.session_state.preload_factor)})",
            size=750,
            color="#D6F5E6",
            shape="box"
        ),
        Node(
            id="afterload",
            label=f"Afterload\n(factor {pretty_pct(st.session_state.afterload_factor)})",
            size=750,
            color="#E1E8FF",
            shape="box"
        ),
        Node(
            id="hr",
            label=f"Heart Rate (HR)\n{hr:.0f} bpm {arrow(hr_delta)}",
            size=900,
            color="#FFF",
            shape="ellipse"
        ),
        Node(
            id="contractility",
            label=f"Contractility\n{contractility:.2f} {arrow(contractility-1.0)}",
            size=850,
            color="#FFF",
            shape="ellipse"
        ),
        Node(
            id="sv",
            label=f"Stroke Volume (SV)\n{sv:.0f} ml/beat {arrow(sv_delta)}",
            size=900,
            color="#FFF",
            shape="ellipse"
        ),
        Node(
            id="co",
            label=f"Cardiac Output (CO)\n{co:.2f} L/min {arrow(co_delta)}",
            size=1100,
            color="#FFF",
            shape="ellipse"
        ),
    ]

    edges = [
        Edge(source="chrono", target="hr", label="+/− chronotropy"),
        Edge(source="ino", target="contractility", label="+/− inotropy"),
        Edge(source="contractility", target="sv", label="↑ force → ↑ SV"),
        Edge(source="preload", target="sv", label="↑ preload → ↑ SV"),
        Edge(source="afterload", target="sv", label="↑ afterload → ↓ SV"),
        Edge(source="hr", target="co", label="CO = HR × SV"),
        Edge(source="sv", target="co", label="CO = HR × SV"),
    ]

    config = Config(
        width="100%",
        height=520,
        directed=True,
        physics=False,
        hierarchical=True,
        levelSeparation=130,
        nodeSpacing=140,
        sortMethod="directed",
        borderWidth=1,
        font="Arial",
        collapsible=False
    )

    clicked = agraph(nodes=nodes, edges=edges, config=config)

    if clicked:
        st.session_state.last_clicked = clicked
        # Only open quiz for controllable nodes
        if clicked in {"chrono", "ino", "preload", "afterload"}:
            st.session_state.show_quiz = True
            st.session_state.quiz_node = clicked
            st.session_state.after_submit = False
            st.session_state.prediction = None

# ---------------------------
# RIGHT: Controls, quiz, resources
# ---------------------------
with right:
    st.markdown("### Your panel")

    # Quick readout card
    st.markdown(
        f"""
        <div class="node-card">
          <div><span class="badge">HR</span> <b>{hr:.0f} bpm</b></div>
          <div><span class="badge">SV</span> <b>{sv:.0f} ml/beat</b></div>
          <div><span class="badge">CO</span> <b>{co:.2f} L/min</b></div>
          <div class="tiny" style="margin-top:6px;">
            Teaching model: CO = HR × SV
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.write("")

    # Quiz/interaction panel
    if st.session_state.show_quiz and st.session_state.quiz_node:
        node = st.session_state.quiz_node
        HR_before, C_before, SV_before, CO_before = compute_state()

        st.markdown("#### Step 1 — Predict first")
        st.session_state.prediction = st.radio(
            "What do you think will happen to Cardiac Output?",
            ["Increase", "Decrease", "No change"],
            index=None,
            key="prediction_radio"
        )

        st.markdown("#### Step 2 — Make your change")

        colA, colB = st.columns(2)
        with colA:
            inc = st.button("Increase ⬆️", use_container_width=True)
        with colB:
            dec = st.button("Decrease ⬇️", use_container_width=True)

        change_map = {
            "chrono": ("Chronotropic Agents", "chrono_factor", 0.10),
            "ino": ("Inotropic Agents", "ino_factor", 0.10),
            "preload": ("Preload", "preload_factor", 0.10),
            "afterload": ("Afterload", "afterload_factor", 0.10),
        }

        label, factor_key, step = change_map[node]

        if inc or dec:
            if st.session_state.prediction is None:
                st.warning("Please make a prediction before changing anything 🙂")
            else:
                old = st.session_state[factor_key]
                new = old + step if inc else old - step

                # clamp factors to keep model reasonable
                new = clamp(new, 0.5, 1.8)
                st.session_state[factor_key] = new

                # recompute after
                HR_after, C_after, SV_after, CO_after = compute_state()

                direction_CO = expected_direction(CO_before, CO_after)
                st.session_state.was_correct = (direction_CO == st.session_state.prediction)
                st.session_state.after_submit = True

                st.success(f"Updated **{label}** from {pretty_pct(old)} to {pretty_pct(new)}.")

                # Show results
                st.markdown("#### Results")
                st.write(f"- HR: {HR_before:.0f} → {HR_after:.0f} bpm")
                st.write(f"- SV: {SV_before:.0f} → {SV_after:.0f} ml/beat")
                st.write(f"- CO: {CO_before:.2f} → {CO_after:.2f} L/min (**{direction_CO}**)")

                if st.session_state.was_correct:
                    st.markdown("<div class='good'>✅ Your prediction was correct!</div>", unsafe_allow_html=True)
                else:
                    st.markdown("<div class='bad'>❌ Not quite — let’s find the snag.</div>", unsafe_allow_html=True)
                    st.session_state.confusion_point = st.selectbox(
                        "Where do you think your reasoning went off?",
                        [
                            "How chronotropic agents affect HR",
                            "How inotropic agents affect contractility",
                            "How preload affects SV",
                            "How afterload affects SV",
                            "How SV and HR combine to make CO",
                            "Something else / not sure"
                        ],
                        index=None
                    )
                    if st.session_state.confusion_point:
                        st.info(
                            "Thanks! Discussing that step in class (or reviewing notes) will help lock it in."
                        )

        st.divider()

        # Context-specific resources
        st.markdown("#### Learn more about this step")

        if node == "chrono":
            st.write(
                "Chronotropic agents change **heart rate**, which directly changes CO."
            )
            st.markdown(
                "- Cardiac output basics (CO = HR × SV): Cleveland Clinic. :contentReference[oaicite:2]{index=2}"
            )

        if node == "ino":
            st.write(
                "Inotropic agents change **contractility**, affecting SV and then CO."
            )
            st.markdown(
                "- What inotropes do and why they raise/lower CO: Cleveland Clinic. :contentReference[oaicite:3]{index=3}"
            )

        if node in {"preload", "afterload"}:
            st.write(
                "Preload and afterload shift **stroke volume**, which then changes CO."
            )
            st.markdown(
                "- Stroke volume & cardiac physiology overview: OpenStax/OSU A&P OER. :contentReference[oaicite:4]{index=4}"
            )

        st.markdown(
            "- Heart failure & reduced pumping ability: CDC. :contentReference[oaicite:5]{index=5}"
        )

    else:
        st.info("Click a yellow/green/blue control box in the chart to begin.")

    st.write("")
    st.markdown("### Teacher controls (optional)")
    with st.expander("Adjust baselines"):
        st.session_state.hr_baseline = st.slider(
            "Baseline HR (bpm)", 40, 120, int(st.session_state.hr_baseline)
        )
        st.session_state.sv_baseline = st.slider(
            "Baseline SV (ml/beat)", 40, 120, int(st.session_state.sv_baseline)
        )

    with st.expander("Reset activity"):
        if st.button("Reset all factors to baseline"):
            st.session_state.chrono_factor = 1.0
            st.session_state.ino_factor = 1.0
            st.session_state.preload_factor = 1.0
            st.session_state.afterload_factor = 1.0
            st.session_state.show_quiz = False
            st.session_state.quiz_node = None
            st.experimental_rerun()

st.caption(
    "Teaching model note: this is a simplified causal map for learning. Real physiology includes reflexes, "
    "vascular tone, filling time, and pathologic states."
)
