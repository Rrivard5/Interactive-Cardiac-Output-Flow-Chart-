import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config

# ---------------------------
# Page config + style
# ---------------------------
st.set_page_config(
    page_title="Interactive Cardiac Output Flow Chart",
    page_icon="🫀",
    layout="wide",
)

st.markdown(
    """
    <style>
      .big-title { font-size: 2.1rem; font-weight: 800; margin-bottom: 0.25rem; }
      .subtitle  { color: #555; font-size: 1.05rem; margin-top: 0; }

      .node-card {
        border:1px solid #eee; border-radius:14px; padding:12px 14px;
        background:#fff; box-shadow:0 2px 10px rgba(0,0,0,0.04);
      }
      .good { color:#0a7a2f; font-weight:800; }
      .bad  { color:#b00020; font-weight:800; }

      .stButton button {
        border-radius: 999px !important;
        padding: 0.45rem 1rem !important;
        font-weight: 700 !important;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------
# Helpers
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
    Discrete arrow-based teaching model.
    Internal numbers are hidden from students;
    nodes display arrows only.
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

def have_dialog():
    return hasattr(st, "dialog")

# ---------------------------
# Ensure session defaults
# ---------------------------
defaults = {
    "hr_baseline": 70.0,
    "sv_baseline": 70.0,

    # controllable arrows
    "chrono_pos_effect": 0,
    "chrono_neg_effect": 0,
    "ino_pos_effect": 0,
    "ino_neg_effect": 0,
    "venous_return_effect": 0,
    "afterload_effect": 0,

    # learning cycle state machine
    "phase": "select_box",  # select_box → choose_dir → predict → show_result
    "selected_node": None,
    "pending_direction": None,  # +1 or -1
    "prediction": None,
    "last_feedback": None,
    "last_correct": None,
}
for k, v in defaults.items():
    st.session_state.setdefault(k, v)

# ---------------------------
# Header
# ---------------------------
st.markdown("<div class='big-title'>🫀 Cardiac Output Flow Chart</div>", unsafe_allow_html=True)
st.markdown(
    "<p class='subtitle'>Click ONE box to change. Lock ↑ or ↓, predict CO, then see the flow chart update.</p>",
    unsafe_allow_html=True
)

left, right = st.columns([2.1, 1.0], gap="large")

# ---------------------------
# Compute current downstream arrows
# ---------------------------
hr, sv, co = compute_state()
hr_dir = direction_vs_baseline(hr, st.session_state.hr_baseline)
sv_dir = direction_vs_baseline(sv, st.session_state.sv_baseline)
co_dir = direction_vs_baseline(co, (st.session_state.hr_baseline * st.session_state.sv_baseline / 1000.0))

HR_arrow = effect_arrow(hr_dir)
SV_arrow = effect_arrow(sv_dir)
CO_arrow = effect_arrow(co_dir)

# ---------------------------
# LEFT: flow chart (fixed layout like your image)
# ---------------------------
with left:
    st.markdown("### Flow chart")

    cp = effect_arrow(st.session_state.chrono_pos_effect)
    cn = effect_arrow(st.session_state.chrono_neg_effect)
    ip = effect_arrow(st.session_state.ino_pos_effect)
    inn= effect_arrow(st.session_state.ino_neg_effect)
    vr = effect_arrow(st.session_state.venous_return_effect)
    al = effect_arrow(st.session_state.afterload_effect)

    nodes = [
        # Top big headers
        Node(id="chrono_header", label="Chronotropic agents\n(alter SA/AV node activity)", x=0, y=0,
             size=900, color="#EFE7E5", shape="box", font={"size": 16}),
        Node(id="venous", label=f"Venous return\n(preload)\n{vr}", x=360, y=0,
             size=850, color="#FFF6C8", shape="box", font={"size": 16}),
        Node(id="ino_header", label="Inotropic agents\n(alter contractility)", x=720, y=0,
             size=900, color="#FFF0EC", shape="box", font={"size": 16}),
        Node(id="afterload", label=f"Afterload\n{al}", x=1080, y=0,
             size=850, color="#E1E8FF", shape="box", font={"size": 16}),

        # Sub-boxes under chrono/inotropy
        Node(id="chrono_pos", label=f"Positive agents\n{cp}", x=-120, y=160,
             size=650, color="#FFE8A3", shape="box", font={"size": 15}),
        Node(id="chrono_neg", label=f"Negative agents\n{cn}", x=120, y=160,
             size=650, color="#FFE8A3", shape="box", font={"size": 15}),

        Node(id="ino_pos", label=f"Positive agents\n{ip}", x=600, y=160,
             size=650, color="#FFD6CC", shape="box", font={"size": 15}),
        Node(id="ino_neg", label=f"Negative agents\n{inn}", x=840, y=160,
             size=650, color="#FFD6CC", shape="box", font={"size": 15}),

        # Middle physiology
        Node(id="hr", label=f"Heart rate (HR)\n{HR_arrow}", x=0, y=360,
             size=950, color="#FFFFFF", shape="box", font={"size": 18}),
        Node(id="sv", label=f"Stroke volume (SV)\n{SV_arrow}", x=720, y=360,
             size=950, color="#FFFFFF", shape="box", font={"size": 18}),

        # Bottom output
        Node(id="co", label=f"Cardiac output (CO)\n{CO_arrow}", x=360, y=560,
             size=1050, color="#F3D6DA", shape="box", font={"size": 18}),
    ]

    edges = [
        Edge(source="chrono_pos", target="hr"),
        Edge(source="chrono_neg", target="hr"),
        Edge(source="venous", target="sv"),
        Edge(source="ino_pos", target="sv"),
        Edge(source="ino_neg", target="sv"),
        Edge(source="afterload", target="sv"),
        Edge(source="hr", target="co"),
        Edge(source="sv", target="co"),
    ]

    config = Config(
        width="100%",
        height=640,
        directed=True,
        physics=False,
        staticGraph=True,
        nodeHighlightBehavior=True,
        fit=True
    )

    clicked = agraph(nodes=nodes, edges=edges, config=config)

    controllables = {"chrono_pos", "chrono_neg", "ino_pos", "ino_neg", "venous", "afterload"}

    # Phase 1: selecting one box
    if st.session_state.phase == "select_box" and clicked in controllables:
        st.session_state.selected_node = clicked
        st.session_state.phase = "choose_dir"
        st.rerun()

# ---------------------------
# RIGHT: learning-cycle popups + teacher panel
# ---------------------------
with right:
    st.markdown("### Student step")

    # ---- PHASE: choose_dir (increase/decrease) ----
    if st.session_state.phase == "choose_dir" and st.session_state.selected_node:
        node = st.session_state.selected_node

        title_map = {
            "chrono_pos": "Positive chronotropic agents",
            "chrono_neg": "Negative chronotropic agents",
            "ino_pos": "Positive inotropic agents",
            "ino_neg": "Negative inotropic agents",
            "venous": "Venous return (preload)",
            "afterload": "Afterload",
        }
        node_title = title_map[node]

        if have_dialog():
            @st.dialog(f"{node_title}: choose a direction")
            def choose_dir_dialog():
                st.write("Do you want to increase or decrease this factor?")
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("Increase ↑", use_container_width=True):
                        st.session_state.pending_direction = 1
                        st.session_state.phase = "predict"
                        st.rerun()
                with c2:
                    if st.button("Decrease ↓", use_container_width=True):
                        st.session_state.pending_direction = -1
                        st.session_state.phase = "predict"
                        st.rerun()
                st.caption("You can only change one box per round.")
            choose_dir_dialog()
        else:
            st.markdown(f"**{node_title}**")
            st.write("Increase or decrease this factor?")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("Increase ↑", use_container_width=True):
                    st.session_state.pending_direction = 1
                    st.session_state.phase = "predict"
                    st.rerun()
            with c2:
                if st.button("Decrease ↓", use_container_width=True):
                    st.session_state.pending_direction = -1
                    st.session_state.phase = "predict"
                    st.rerun()

    # ---- PHASE: predict CO ----
    if st.session_state.phase == "predict" and st.session_state.selected_node:
        node = st.session_state.selected_node

        # snapshot before applying change
        _, _, CO_before = compute_state()

        if have_dialog():
            @st.dialog("Predict the impact on cardiac output")
            def predict_dialog():
                st.write("Based on your change, what will happen to CO?")
                pred = st.radio(
                    "Your prediction:",
                    ["Increase", "Decrease", "No change"],
                    index=None
                )
                if st.button("Submit prediction"):
                    st.session_state.prediction = pred

                    # apply the change NOW
                    key_map = {
                        "chrono_pos": "chrono_pos_effect",
                        "chrono_neg": "chrono_neg_effect",
                        "ino_pos": "ino_pos_effect",
                        "ino_neg": "ino_neg_effect",
                        "venous": "venous_return_effect",
                        "afterload": "afterload_effect",
                    }
                    eff_key = key_map[node]
                    st.session_state[eff_key] = st.session_state.pending_direction

                    # compute after
                    _, _, CO_after = compute_state()
                    dir_CO = expected_direction(CO_before, CO_after)
                    correct = (dir_CO == pred)

                    st.session_state.last_feedback = dir_CO
                    st.session_state.last_correct = correct
                    st.session_state.phase = "show_result"
                    st.rerun()
            predict_dialog()
        else:
            st.write("Predict the impact on CO:")
            pred = st.radio(
                "Your prediction:",
                ["Increase", "Decrease", "No change"],
                index=None
            )
            if st.button("Submit prediction"):
                st.session_state.prediction = pred

                key_map = {
                    "chrono_pos": "chrono_pos_effect",
                    "chrono_neg": "chrono_neg_effect",
                    "ino_pos": "ino_pos_effect",
                    "ino_neg": "ino_neg_effect",
                    "venous": "venous_return_effect",
                    "afterload": "afterload_effect",
                }
                eff_key = key_map[node]
                st.session_state[eff_key] = st.session_state.pending_direction

                _, _, CO_after = compute_state()
                dir_CO = expected_direction(CO_before, CO_after)
                correct = (dir_CO == pred)

                st.session_state.last_feedback = dir_CO
                st.session_state.last_correct = correct
                st.session_state.phase = "show_result"
                st.rerun()

    # ---- PHASE: show_result (then reset to allow next round) ----
    if st.session_state.phase == "show_result":
        st.markdown(
            f"""
            <div class="node-card">
              <div><b>Actual CO change:</b> {st.session_state.last_feedback}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.session_state.last_correct:
            st.markdown("<div class='good'>✅ Your prediction was correct!</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='bad'>❌ Not quite.</div>", unsafe_allow_html=True)
            st.write("Where did you get confused?")
            st.selectbox(
                "Pick the step:",
                [
                    "Chronotropic agents → HR",
                    "Inotropic agents → SV",
                    "Venous return (preload) → SV",
                    "Afterload → SV (inverse)",
                    "Combining HR and SV to get CO",
                    "Not sure / other"
                ],
                index=None
            )

        if st.button("Start a new round"):
            st.session_state.phase = "select_box"
            st.session_state.selected_node = None
            st.session_state.pending_direction = None
            st.session_state.prediction = None
            st.rerun()

    st.divider()

    st.markdown("### Teacher controls (optional)")
    with st.expander("Hidden baselines"):
        st.session_state.hr_baseline = st.slider("Baseline HR (hidden)", 40, 120, int(st.session_state.hr_baseline))
        st.session_state.sv_baseline = st.slider("Baseline SV (hidden)", 40, 120, int(st.session_state.sv_baseline))
        if st.button("Reset all arrows to baseline (—)"):
            st.session_state.chrono_pos_effect = 0
            st.session_state.chrono_neg_effect = 0
            st.session_state.ino_pos_effect = 0
            st.session_state.ino_neg_effect = 0
            st.session_state.venous_return_effect = 0
            st.session_state.afterload_effect = 0
            st.session_state.phase = "select_box"
            st.session_state.selected_node = None
            st.session_state.pending_direction = None
            st.session_state.prediction = None
            st.rerun()

st.caption("Arrows show direction of change only. CO = HR × SV (simplified learning model).")
