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
      .big-title { 
        font-size: 2.3rem; 
        font-weight: 800; 
        margin-bottom: 0.5rem;
        color: #1f1f1f;
      }
      .subtitle { 
        color: #555; 
        font-size: 1.1rem; 
        margin-top: 0;
        margin-bottom: 1.5rem;
      }

      .node-card {
        border: 2px solid #e0e0e0;
        border-radius: 12px;
        padding: 16px 18px;
        background: #fafafa;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        margin-bottom: 1rem;
      }
      .good { 
        color: #0a7a2f; 
        font-weight: 800;
        font-size: 1.1rem;
      }
      .bad { 
        color: #b00020; 
        font-weight: 800;
        font-size: 1.1rem;
      }

      .stButton button {
        border-radius: 8px !important;
        padding: 0.6rem 1.2rem !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
      }
      
      .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
      }
      
      /* Make the graph container more prominent */
      .graph-container {
        border: 2px solid #e0e0e0;
        border-radius: 12px;
        padding: 20px;
        background: #ffffff;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
      }
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

    "chrono_pos_effect": 0,
    "chrono_neg_effect": 0,
    "ino_pos_effect": 0,
    "ino_neg_effect": 0,
    "venous_return_effect": 0,
    "afterload_effect": 0,

    "phase": "select_box",
    "selected_node": None,
    "pending_direction": None,
    "prediction": None,
    "last_feedback": None,
    "last_correct": None,

    "graph_version": 0,
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

left, right = st.columns([2.3, 1.0], gap="large")

# ---------------------------
# Compute downstream arrows
# ---------------------------
hr, sv, co = compute_state()
hr_dir = direction_vs_baseline(hr, st.session_state.hr_baseline)
sv_dir = direction_vs_baseline(sv, st.session_state.sv_baseline)
co_dir = direction_vs_baseline(co, (st.session_state.hr_baseline * st.session_state.sv_baseline / 1000.0))

HR_arrow = effect_arrow(hr_dir)
SV_arrow = effect_arrow(sv_dir)
CO_arrow = effect_arrow(co_dir)

# ---------------------------
# LEFT: flow chart
# ---------------------------
with left:
    st.markdown("### 📊 Interactive Flow Chart")
    st.markdown("<div class='graph-container'>", unsafe_allow_html=True)

    cp  = effect_arrow(st.session_state.chrono_pos_effect)
    cn  = effect_arrow(st.session_state.chrono_neg_effect)
    ip  = effect_arrow(st.session_state.ino_pos_effect)
    inn = effect_arrow(st.session_state.ino_neg_effect)
    vr  = effect_arrow(st.session_state.venous_return_effect)
    al  = effect_arrow(st.session_state.afterload_effect)

    # Adjusted node positions for better centering
    nodes = [
        Node(id="chrono_header",
             label="Chronotropic agents\n(alter SA node and\nAV node activity)",
             x=200,   y=100, size=1200, color="#EFE7E5", shape="box", font={"size": 22}),
        Node(id="venous",
             label=f"Venous return\n(preload)\n{vr}",
             x=520, y=100, size=1100, color="#FFF6C8", shape="box", font={"size": 22}),
        Node(id="ino_header",
             label="Inotropic agents\n(alter contractility)",
             x=840, y=100, size=1200, color="#FFF0EC", shape="box", font={"size": 22}),
        Node(id="afterload",
             label=f"Afterload\n{al}",
             x=1160, y=100, size=1100, color="#E1E8FF", shape="box", font={"size": 22}),

        Node(id="chrono_pos", label=f"Positive agents\n{cp}",
             x=80, y=300, size=950, color="#FFE8A3", shape="box", font={"size": 20}),
        Node(id="chrono_neg", label=f"Negative agents\n{cn}",
             x=320,  y=300, size=950, color="#FFE8A3", shape="box", font={"size": 20}),

        Node(id="ino_pos", label=f"Positive agents\n{ip}",
             x=760, y=300, size=950, color="#FFD6CC", shape="box", font={"size": 20}),
        Node(id="ino_neg", label=f"Negative agents\n{inn}",
             x=920, y=300, size=950, color="#FFD6CC", shape="box", font={"size": 20}),

        Node(id="hr", label=f"Heart rate (HR)\n{HR_arrow}",
             x=200,   y=520, size=1350, color="#E8F5E9", shape="box", font={"size": 24, "bold": True}),
        Node(id="sv", label=f"Stroke volume (SV)\n{SV_arrow}",
             x=840, y=520, size=1350, color="#FFF3E0", shape="box", font={"size": 24, "bold": True}),

        Node(id="co", label=f"Cardiac output (CO)\n{CO_arrow}",
             x=520, y=720, size=1500, color="#F3D6DA", shape="box", font={"size": 26, "bold": True}),
    ]

    # Invisible redraw node
    nodes.append(
        Node(
            id=f"_force_{st.session_state.graph_version}",
            label="",
            x=-9999, y=-9999,
            size=1,
            color="#FFFFFF",
            shape="dot",
            font={"size": 1}
        )
    )

    edges = [
        Edge(source="chrono_pos", target="hr", color="#666"),
        Edge(source="chrono_neg", target="hr", color="#666"),
        Edge(source="venous", target="sv", color="#666"),
        Edge(source="ino_pos", target="sv", color="#666"),
        Edge(source="ino_neg", target="sv", color="#666"),
        Edge(source="afterload", target="sv", color="#666"),
        Edge(source="hr", target="co", color="#333"),
        Edge(source="sv", target="co", color="#333"),
    ]

    config = Config(
        width="100%",
        height=820,
        directed=True,
        physics=False,
        staticGraph=True,
        nodeHighlightBehavior=True,
        interaction={
            "dragNodes": False,
            "dragView": True,
            "zoomView": True
        },
        # Center the graph on the main flow
        initialZoom=1.0,
        minZoom=0.5,
        maxZoom=2.0,
    )

    clicked = agraph(nodes=nodes, edges=edges, config=config)
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------
# AFTER graph: handle click → phase transitions
# ---------------------------
controllables = {"chrono_pos", "chrono_neg", "ino_pos", "ino_neg", "venous", "afterload"}

if st.session_state.phase == "select_box" and clicked in controllables:
    st.session_state.selected_node = clicked
    st.session_state.phase = "choose_dir"
    st.rerun()

# ---------------------------
# RIGHT: student dialogs + results
# ---------------------------
with right:
    st.markdown("### 🎯 Student Interaction")

    # ---- PHASE: choose_dir ----
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
            @st.dialog(f"📍 {node_title}")
            def choose_dir_dialog():
                st.write("**Do you want to increase or decrease this factor?**")
                st.write("")
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("⬆️ Increase", use_container_width=True, type="primary"):
                        st.session_state.pending_direction = 1
                        st.session_state.phase = "predict"
                        st.rerun()
                with c2:
                    if st.button("⬇️ Decrease", use_container_width=True):
                        st.session_state.pending_direction = -1
                        st.session_state.phase = "predict"
                        st.rerun()
            choose_dir_dialog()
        else:
            st.markdown(f"**📍 {node_title}**")
            st.write("Do you want to increase or decrease this factor?")
            st.write("")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("⬆️ Increase", use_container_width=True, type="primary"):
                    st.session_state.pending_direction = 1
                    st.session_state.phase = "predict"
                    st.rerun()
            with c2:
                if st.button("⬇️ Decrease", use_container_width=True):
                    st.session_state.pending_direction = -1
                    st.session_state.phase = "predict"
                    st.rerun()

    # ---- PHASE: predict ----
    if st.session_state.phase == "predict" and st.session_state.selected_node:
        node = st.session_state.selected_node
        _, _, CO_before = compute_state()

        if have_dialog():
            @st.dialog("🔮 Predict the impact on cardiac output")
            def predict_dialog():
                st.write("**What will happen to cardiac output?**")
                st.write("")
                pred = st.radio("Your prediction:",
                                ["Increase", "Decrease", "No change"],
                                index=None)
                st.write("")
                if st.button("✅ Submit prediction", type="primary", disabled=(pred is None)):
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

                    st.session_state.graph_version += 1

                    _, _, CO_after = compute_state()
                    dir_CO = expected_direction(CO_before, CO_after)
                    correct = (dir_CO == pred)

                    st.session_state.last_feedback = dir_CO
                    st.session_state.last_correct = correct
                    st.session_state.phase = "show_result"
                    st.rerun()
            predict_dialog()
        else:
            st.write("**🔮 What will happen to cardiac output?**")
            st.write("")
            pred = st.radio("Your prediction:",
                            ["Increase", "Decrease", "No change"],
                            index=None)
            st.write("")
            if st.button("✅ Submit prediction", type="primary", disabled=(pred is None)):
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

                st.session_state.graph_version += 1

                _, _, CO_after = compute_state()
                dir_CO = expected_direction(CO_before, CO_after)
                correct = (dir_CO == pred)

                st.session_state.last_feedback = dir_CO
                st.session_state.last_correct = correct
                st.session_state.phase = "show_result"
                st.rerun()

    # ---- PHASE: show_result ----
    if st.session_state.phase == "show_result":
        st.markdown(
            f"""
            <div class="node-card">
              <div style="margin-bottom: 10px;"><b>Your prediction:</b> {st.session_state.prediction}</div>
              <div><b>Correct CO change:</b> {st.session_state.last_feedback}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        if st.session_state.last_correct:
            st.markdown("<div class='good'>✅ Your prediction was correct!</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='bad'>❌ Your prediction was not correct.</div>", unsafe_allow_html=True)
            st.write("")
            st.selectbox(
                "Where did you get confused?",
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

        st.write("")
        if st.button("🔄 Start a new round", type="primary", use_container_width=True):
            # reset arrows
            st.session_state.chrono_pos_effect = 0
            st.session_state.chrono_neg_effect = 0
            st.session_state.ino_pos_effect = 0
            st.session_state.ino_neg_effect = 0
            st.session_state.venous_return_effect = 0
            st.session_state.afterload_effect = 0

            st.session_state.graph_version += 1

            st.session_state.phase = "select_box"
            st.session_state.selected_node = None
            st.session_state.pending_direction = None
            st.session_state.prediction = None
            st.rerun()
    else:
        st.info("👈 Click a box in the flow chart to begin.")

st.write("")
st.caption("📝 Arrows show direction of change only. CO = HR × SV (simplified learning model).")
