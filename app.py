import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config

# ---------------------------
# Page config + style
# ---------------------------
st.set_page_config(
    page_title="Cardiac Output Flow Explorer",
    page_icon="🫀",
    layout="wide",
)

st.markdown(
    """
    <style>
      .big-title { font-size: 2.1rem; font-weight: 800; margin-bottom: 0.25rem; }
      .subtitle { color: #555; font-size: 1.05rem; margin-top: 0; }
      .tiny { font-size:0.9rem; color:#666; }
      .node-card {
        border:1px solid #eee; border-radius:16px; padding:14px 16px;
        background: #fff; box-shadow: 0 2px 10px rgba(0,0,0,0.04);
      }
      .good { color: #0a7a2f; font-weight: 700; }
      .bad { color: #b00020; font-weight: 700; }
      .stButton button {
        border-radius: 999px !important;
        padding: 0.5rem 1rem !important;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------
# Helper functions
# ---------------------------
def effect_arrow(effect: int):
    """effect is -1, 0, +1"""
    return "↑" if effect > 0 else ("↓" if effect < 0 else "—")

def expected_direction(before, after, eps=1e-6):
    if abs(after - before) < eps:
        return "No change"
    return "Increase" if after > before else "Decrease"

def compute_state():
    """
    Discrete teaching model based on arrow choices:
    - HR baseline adjusted by net chronotropy (pos and neg agents)
    - SV baseline adjusted by venous return, inotropy, and afterload
    - CO = HR × SV

    We use step sizes so arrows produce meaningful but simple changes.
    """
    hr0 = st.session_state.hr_baseline
    sv0 = st.session_state.sv_baseline

    # Step sizes per arrow click (tweak if desired)
    HR_STEP = 0.12   # 12% per arrow unit
    SV_STEP = 0.12   # 12% per arrow unit

    # Chronotropy logic:
    # more positive chrono -> HR up
    # more negative chrono -> HR down
    net_chrono = (
        st.session_state.chrono_pos_effect
        - st.session_state.chrono_neg_effect
    )
    hr = hr0 * (1 + HR_STEP * net_chrono)

    # Inotropy logic (affects SV directly)
    net_ino = (
        st.session_state.ino_pos_effect
        - st.session_state.ino_neg_effect
    )

    # Venous return increases preload => SV up
    venous = st.session_state.venous_return_effect

    # Afterload opposes ejection => SV down when ↑
    afterload = st.session_state.afterload_effect

    sv = sv0 * (1 + SV_STEP * (net_ino + venous - afterload))

    # Clamp to keep things sensible for students
    hr = max(30, min(180, hr))
    sv = max(30, min(140, sv))

    co = hr * sv / 1000.0  # ml/min -> L/min
    return hr, sv, co

# ---------------------------
# Initialize session state
# ---------------------------
if "initialized" not in st.session_state:
    st.session_state.initialized = True

    # Baselines (teacher adjustable)
    st.session_state.hr_baseline = 70.0
    st.session_state.sv_baseline = 70.0

    # Discrete effects: -1 (↓), 0 (—), +1 (↑)
    st.session_state.chrono_pos_effect = 0
    st.session_state.chrono_neg_effect = 0
    st.session_state.ino_pos_effect = 0
    st.session_state.ino_neg_effect = 0
    st.session_state.venous_return_effect = 0
    st.session_state.afterload_effect = 0

    # UI memory
    st.session_state.show_quiz = False
    st.session_state.quiz_node = None
    st.session_state.prediction = None
    st.session_state.was_correct = None
    st.session_state.confusion_point = None

# ---------------------------
# Header
# ---------------------------
st.markdown("<div class='big-title'>🫀 Cardiac Output Flow Chart</div>", unsafe_allow_html=True)
st.markdown(
    "<p class='subtitle'>Click a control box, predict CO, then add ↑ or ↓. Downstream arrows update automatically.</p>",
    unsafe_allow_html=True
)

left, right = st.columns([1.9, 1.0], gap="large")

# Compute values
hr, sv, co = compute_state()
co0 = st.session_state.hr_baseline * st.session_state.sv_baseline / 1000.0

# ---------------------------
# LEFT: Fixed-layout flow chart
# ---------------------------
with left:
    st.markdown("### Interactive flow chart")

    # Display arrows in nodes
    cp = effect_arrow(st.session_state.chrono_pos_effect)
    cn = effect_arrow(st.session_state.chrono_neg_effect)
    ip = effect_arrow(st.session_state.ino_pos_effect)
    inn = effect_arrow(st.session_state.ino_neg_effect)
    vr = effect_arrow(st.session_state.venous_return_effect)
    al = effect_arrow(st.session_state.afterload_effect)

    # Fixed positions (grid-like)
    nodes = [
        # Top row controls
        Node(id="chrono_pos", label=f"Positive chronotropic agents\n{cp}", x=0,   y=0,   size=720, color="#FFE8A3", shape="box"),
        Node(id="venous",     label=f"Venous return (preload)\n{vr}", x=300, y=0,   size=720, color="#FFF6C8", shape="box"),
        Node(id="ino_pos",    label=f"Positive inotropic agents\n{ip}", x=600, y=0,   size=720, color="#FFD6CC", shape="box"),
        Node(id="afterload",  label=f"Afterload\n{al}", x=900, y=0,   size=720, color="#E1E8FF", shape="box"),

        # Second row sub-controls
        Node(id="chrono_neg", label=f"Negative chronotropic agents\n{cn}", x=0,   y=140, size=680, color="#FFE8A3", shape="box"),
        Node(id="ino_neg",    label=f"Negative inotropic agents\n{inn}", x=600, y=140, size=680, color="#FFD6CC", shape="box"),

        # Physiology row
        Node(id="hr", label=f"Heart rate (HR)\n{hr:.0f} bpm", x=90,  y=320, size=900, color="#FFFFFF", shape="box"),
        Node(id="sv", label=f"Stroke volume (SV)\n{sv:.0f} ml/beat", x=690, y=320, size=900, color="#FFFFFF", shape="box"),

        # Output
        Node(id="co", label=f"Cardiac output (CO)\n{co:.2f} L/min", x=390, y=520, size=1050, color="#F3D6DA", shape="box"),
    ]

    edges = [
        Edge(source="chrono_pos", target="hr", label="direct +"),
        Edge(source="chrono_neg", target="hr", label="direct −"),
        Edge(source="venous", target="sv", label="direct +"),
        Edge(source="ino_pos", target="sv", label="direct +"),
        Edge(source="ino_neg", target="sv", label="direct −"),
        Edge(source="afterload", target="sv", label="inverse −"),
        Edge(source="hr", target="co", label="CO = HR × SV"),
        Edge(source="sv", target="co", label="CO = HR × SV"),
    ]

    config = Config(
        width="100%",
        height=560,
        directed=True,
        physics=False,
        nodeHighlightBehavior=True,
        staticGraph=True,   # keep layout squared/locked
        fit=True
    )

    clicked = agraph(nodes=nodes, edges=edges, config=config)

    controllables = {
        "chrono_pos", "chrono_neg",
        "ino_pos", "ino_neg",
        "venous", "afterload"
    }

    if clicked in controllables:
        st.session_state.show_quiz = True
        st.session_state.quiz_node = clicked
        st.session_state.prediction = None
        st.session_state.was_correct = None
        st.session_state.confusion_point = None

# ---------------------------
# RIGHT: Quiz + controls
# ---------------------------
with right:
    st.markdown("### Your panel")

    st.markdown(
        f"""
        <div class="node-card">
          <div><b>HR:</b> {hr:.0f} bpm</div>
          <div><b>SV:</b> {sv:.0f} ml/beat</div>
          <div><b>CO:</b> {co:.2f} L/min</div>
          <div class="tiny" style="margin-top:6px;">
            Baseline CO ≈ {co0:.2f} L/min
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.write("")

    if st.session_state.show_quiz and st.session_state.quiz_node:
        node = st.session_state.quiz_node
        HR_before, SV_before, CO_before = compute_state()

        st.markdown("#### Step 1 — Predict first")
        st.session_state.prediction = st.radio(
            "What do you think will happen to Cardiac Output?",
            ["Increase", "Decrease", "No change"],
            index=None
        )

        st.markdown("#### Step 2 — Add an arrow to this box")

        col1, col2 = st.columns(2)
        with col1:
            inc = st.button("Add ↑", use_container_width=True)
        with col2:
            dec = st.button("Add ↓", use_container_width=True)

        # Map each controllable node to its session key
        key_map = {
            "chrono_pos": "chrono_pos_effect",
            "chrono_neg": "chrono_neg_effect",
            "ino_pos": "ino_pos_effect",
            "ino_neg": "ino_neg_effect",
            "venous": "venous_return_effect",
            "afterload": "afterload_effect",
        }

        if inc or dec:
            if st.session_state.prediction is None:
                st.warning("Please make a prediction before adding an arrow 🙂")
            else:
                eff_key = key_map[node]
                old_eff = st.session_state[eff_key]
                st.session_state[eff_key] = 1 if inc else -1

                HR_after, SV_after, CO_after = compute_state()
                direction_CO = expected_direction(CO_before, CO_after)

                st.session_state.was_correct = (direction_CO == st.session_state.prediction)

                st.success(
                    f"Arrow updated: {effect_arrow(old_eff)} → {effect_arrow(st.session_state[eff_key])}"
                )

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
                            "Effects of positive chronotropic agents",
                            "Effects of negative chronotropic agents",
                            "Effects of positive inotropic agents",
                            "Effects of negative inotropic agents",
                            "How venous return affects preload/SV",
                            "How afterload affects SV",
                            "How HR and SV combine to make CO",
                            "Something else / not sure"
                        ],
                        index=None
                    )
                    if st.session_state.confusion_point:
                        st.info("Thanks — that’s a great place to re-check your reasoning.")

        st.divider()

        st.markdown("#### Learn more about this step")
        if node in {"chrono_pos", "chrono_neg"}:
            st.write("Chronotropic agents alter **SA/AV node activity**, changing **heart rate**.")
            st.markdown("- Cleveland Clinic: Cardiac output basics (CO = HR × SV).")
        elif node in {"ino_pos", "ino_neg"}:
            st.write("Inotropic agents change **contractility**, affecting **stroke volume**.")
            st.markdown("- Cleveland Clinic: Inotropes and contractility.")
        elif node == "venous":
            st.write("Venous return increases preload → more stretch → higher SV (Frank–Starling).")
            st.markdown("- OpenStax A&P: Stroke volume and preload.")
        elif node == "afterload":
            st.write("Afterload opposes ejection → increased afterload lowers SV.")
            st.markdown("- OpenStax A&P: Afterload and SV.")
        st.markdown("- CDC: Heart failure overview and reduced pumping ability.")

    else:
        st.info("Click any yellow control box to start (top row).")

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
        if st.button("Reset all arrows to — (baseline)"):
            st.session_state.chrono_pos_effect = 0
            st.session_state.chrono_neg_effect = 0
            st.session_state.ino_pos_effect = 0
            st.session_state.ino_neg_effect = 0
            st.session_state.venous_return_effect = 0
            st.session_state.afterload_effect = 0
            st.session_state.show_quiz = False
            st.session_state.quiz_node = None
            st.experimental_rerun()

st.caption(
    "Note: This is a simplified causal model for learning. Real physiology includes reflexes, "
    "filling-time limits at high HR, vascular tone changes, and disease states."
)
