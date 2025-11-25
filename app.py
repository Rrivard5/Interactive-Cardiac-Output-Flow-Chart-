import streamlit as st

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
      
      .flow-box {
        border: 2px solid #ddd;
        border-radius: 12px;
        padding: 20px;
        background: white;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        text-align: center;
        min-height: 160px;
      }
      
      .flow-box h4 {
        margin: 0 0 8px 0;
        font-size: 1.1rem;
        font-weight: 700;
      }
      
      .flow-box .desc {
        font-size: 0.85rem;
        color: #666;
        margin-bottom: 12px;
      }
      
      .arrow-display {
        font-size: 2.5rem;
        font-weight: 800;
        margin: 12px 0;
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
        padding: 0.5rem 1rem !important;
        font-weight: 600 !important;
      }
      
      .downstream-box {
        border: 3px solid #333;
        border-radius: 12px;
        padding: 20px;
        background: #ffffff;
        text-align: center;
        min-height: 140px;
      }
      
      .downstream-box h4 {
        margin: 0 0 8px 0;
        font-size: 1.2rem;
        font-weight: 700;
      }
      
      .co-box {
        border: 3px solid #333;
        border-radius: 12px;
        padding: 25px;
        background: #F3D6DA;
        text-align: center;
        max-width: 500px;
        margin: 0 auto;
      }
      
      .co-box h4 {
        margin: 0 0 8px 0;
        font-size: 1.3rem;
        font-weight: 700;
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
    hr_direct  = st.session_state.hr_direct_effect
    sv_direct  = st.session_state.sv_direct_effect

    hr = hr0 * (1 + HR_STEP * (net_chrono + hr_direct))
    sv = sv0 * (1 + SV_STEP * (net_ino + venous - afterload + sv_direct))

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
    "hr_direct_effect": 0,
    "sv_direct_effect": 0,

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
    "<p class='subtitle'>Click Increase ⬆️ or Decrease ⬇️ in any box, predict the CO change, then see the flow chart update.</p>",
    unsafe_allow_html=True
)

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

cp  = effect_arrow(st.session_state.chrono_pos_effect)
cn  = effect_arrow(st.session_state.chrono_neg_effect)
ip  = effect_arrow(st.session_state.ino_pos_effect)
inn = effect_arrow(st.session_state.ino_neg_effect)
vr  = effect_arrow(st.session_state.venous_return_effect)
al  = effect_arrow(st.session_state.afterload_effect)

# ---------------------------
# Flow chart using columns
# ---------------------------

# Row 1: Top level boxes
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(
        """
        <div class='flow-box' style='background: #EFE7E5;'>
            <h4>Chronotropic agents</h4>
            <div class='desc'>(alter SA node and AV node activity)</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        f"""
        <div class='flow-box' style='background: #FFF6C8;'>
            <h4>Venous return</h4>
            <div class='desc'>(volume of blood returning to heart alters stretch of heart wall or preload)</div>
            <div class='arrow-display'>{vr}</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    c1, c2 = st.columns(2)
    with c1:
        if st.button("⬆️ Increase", key="venous_inc", use_container_width=True):
            st.session_state.selected_node = "venous"
            st.session_state.pending_direction = 1
            st.session_state.phase = "predict"
            st.rerun()
    with c2:
        if st.button("⬇️ Decrease", key="venous_dec", use_container_width=True):
            st.session_state.selected_node = "venous"
            st.session_state.pending_direction = -1
            st.session_state.phase = "predict"
            st.rerun()

with col3:
    st.markdown(
        """
        <div class='flow-box' style='background: #FFF0EC;'>
            <h4>Inotropic agents</h4>
            <div class='desc'>(substances that alter contractility of myocardium)</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col4:
    st.markdown(
        f"""
        <div class='flow-box' style='background: #E1E8FF;'>
            <h4>Afterload</h4>
            <div class='desc'>(increased resistance in arteries)</div>
            <div class='arrow-display'>{al}</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    c1, c2 = st.columns(2)
    with c1:
        if st.button("⬆️ Increase", key="afterload_inc", use_container_width=True):
            st.session_state.selected_node = "afterload"
            st.session_state.pending_direction = 1
            st.session_state.phase = "predict"
            st.rerun()
    with c2:
        if st.button("⬇️ Decrease", key="afterload_dec", use_container_width=True):
            st.session_state.selected_node = "afterload"
            st.session_state.pending_direction = -1
            st.session_state.phase = "predict"
            st.rerun()

st.write("")

# Row 2: Agent boxes under headers
col1, col2, empty1, col3, col4, empty2 = st.columns([1, 1, 1, 1, 1, 1])

with col1:
    st.markdown(
        f"""
        <div class='flow-box' style='background: #FFE8A3;'>
            <h4>Positive agents</h4>
            <div class='arrow-display'>{cp}</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    c1, c2 = st.columns(2)
    with c1:
        if st.button("⬆️", key="chrono_pos_inc", use_container_width=True):
            st.session_state.selected_node = "chrono_pos"
            st.session_state.pending_direction = 1
            st.session_state.phase = "predict"
            st.rerun()
    with c2:
        if st.button("⬇️", key="chrono_pos_dec", use_container_width=True):
            st.session_state.selected_node = "chrono_pos"
            st.session_state.pending_direction = -1
            st.session_state.phase = "predict"
            st.rerun()

with col2:
    st.markdown(
        f"""
        <div class='flow-box' style='background: #FFE8A3;'>
            <h4>Negative agents</h4>
            <div class='arrow-display'>{cn}</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    c1, c2 = st.columns(2)
    with c1:
        if st.button("⬆️", key="chrono_neg_inc", use_container_width=True):
            st.session_state.selected_node = "chrono_neg"
            st.session_state.pending_direction = 1
            st.session_state.phase = "predict"
            st.rerun()
    with c2:
        if st.button("⬇️", key="chrono_neg_dec", use_container_width=True):
            st.session_state.selected_node = "chrono_neg"
            st.session_state.pending_direction = -1
            st.session_state.phase = "predict"
            st.rerun()

with col3:
    st.markdown(
        f"""
        <div class='flow-box' style='background: #FFD6CC;'>
            <h4>Positive agents</h4>
            <div class='arrow-display'>{ip}</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    c1, c2 = st.columns(2)
    with c1:
        if st.button("⬆️", key="ino_pos_inc", use_container_width=True):
            st.session_state.selected_node = "ino_pos"
            st.session_state.pending_direction = 1
            st.session_state.phase = "predict"
            st.rerun()
    with c2:
        if st.button("⬇️", key="ino_pos_dec", use_container_width=True):
            st.session_state.selected_node = "ino_pos"
            st.session_state.pending_direction = -1
            st.session_state.phase = "predict"
            st.rerun()

with col4:
    st.markdown(
        f"""
        <div class='flow-box' style='background: #FFD6CC;'>
            <h4>Negative agents</h4>
            <div class='arrow-display'>{inn}</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    c1, c2 = st.columns(2)
    with c1:
        if st.button("⬆️", key="ino_neg_inc", use_container_width=True):
            st.session_state.selected_node = "ino_neg"
            st.session_state.pending_direction = 1
            st.session_state.phase = "predict"
            st.rerun()
    with c2:
        if st.button("⬇️", key="ino_neg_dec", use_container_width=True):
            st.session_state.selected_node = "ino_neg"
            st.session_state.pending_direction = -1
            st.session_state.phase = "predict"
            st.rerun()

# SVG arrows between rows
st.markdown(
    """
    <svg width="100%" height="100" style="margin: 10px 0;">
        <defs>
            <marker id="arrowhead" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">
                <polygon points="0 0, 10 3, 0 6" fill="#666"/>
            </marker>
        </defs>
        <!-- Chronotropic agents to HR -->
        <line x1="12%" y1="10" x2="25%" y2="90" stroke="#666" stroke-width="2" marker-end="url(#arrowhead)"/>
        <line x1="20%" y1="10" x2="25%" y2="90" stroke="#666" stroke-width="2" marker-end="url(#arrowhead)"/>
        
        <!-- Venous to SV with label -->
        <line x1="37%" y1="5" x2="62%" y2="90" stroke="#666" stroke-width="2" marker-end="url(#arrowhead)"/>
        <text x="48%" y="45" font-size="11" fill="#666" font-style="italic" text-anchor="middle">is directly</text>
        <text x="48%" y="58" font-size="11" fill="#666" font-style="italic" text-anchor="middle">correlated with</text>
        
        <!-- Inotropic agents to SV -->
        <line x1="62%" y1="10" x2="62%" y2="90" stroke="#666" stroke-width="2" marker-end="url(#arrowhead)"/>
        <line x1="70%" y1="10" x2="62%" y2="90" stroke="#666" stroke-width="2" marker-end="url(#arrowhead)"/>
        
        <!-- Afterload to SV with label -->
        <line x1="88%" y1="5" x2="75%" y2="90" stroke="#666" stroke-width="2" marker-end="url(#arrowhead)"/>
        <text x="82%" y="45" font-size="11" fill="#666" font-style="italic" text-anchor="middle">is inversely</text>
        <text x="82%" y="58" font-size="11" fill="#666" font-style="italic" text-anchor="middle">correlated with</text>
    </svg>
    """,
    unsafe_allow_html=True
)

# Row 3: HR and SV
col1, col2 = st.columns(2)

with col1:
    st.markdown(
        f"""
        <div class='downstream-box'>
            <h4>Heart rate</h4>
            <div class='desc'>(beats per minute)</div>
            <div class='arrow-display'>{HR_arrow}</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    c1, c2 = st.columns(2)
    with c1:
        if st.button("⬆️ Increase", key="hr_inc", use_container_width=True):
            st.session_state.selected_node = "hr"
            st.session_state.pending_direction = 1
            st.session_state.phase = "predict"
            st.rerun()
    with c2:
        if st.button("⬇️ Decrease", key="hr_dec", use_container_width=True):
            st.session_state.selected_node = "hr"
            st.session_state.pending_direction = -1
            st.session_state.phase = "predict"
            st.rerun()

with col2:
    st.markdown(
        f"""
        <div class='downstream-box'>
            <h4>Stroke volume</h4>
            <div class='desc'>(blood pumped per beat)</div>
            <div class='arrow-display'>{SV_arrow}</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    c1, c2 = st.columns(2)
    with c1:
        if st.button("⬆️ Increase", key="sv_inc", use_container_width=True):
            st.session_state.selected_node = "sv"
            st.session_state.pending_direction = 1
            st.session_state.phase = "predict"
            st.rerun()
    with c2:
        if st.button("⬇️ Decrease", key="sv_dec", use_container_width=True):
            st.session_state.selected_node = "sv"
            st.session_state.pending_direction = -1
            st.session_state.phase = "predict"
            st.rerun()

# Final arrows to CO
st.markdown(
    """
    <svg width="100%" height="80" style="margin: 10px 0;">
        <defs>
            <marker id="arrowhead2" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">
                <polygon points="0 0, 10 3, 0 6" fill="#333"/>
            </marker>
        </defs>
        <line x1="25%" y1="10" x2="48%" y2="70" stroke="#333" stroke-width="3" marker-end="url(#arrowhead2)"/>
        <line x1="75%" y1="10" x2="52%" y2="70" stroke="#333" stroke-width="3" marker-end="url(#arrowhead2)"/>
    </svg>
    """,
    unsafe_allow_html=True
)

# Row 4: CO
st.markdown(
    f"""
    <div class='co-box'>
        <h4>Cardiac output</h4>
        <div class='desc'>(blood pumped per minute)</div>
        <div class='arrow-display'>{CO_arrow}</div>
    </div>
    """,
    unsafe_allow_html=True
)

# ---------------------------
# Handle phase transitions
# ---------------------------

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
                    "hr": "hr_direct_effect",
                    "sv": "sv_direct_effect",
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

# ---- PHASE: show_result ----
if st.session_state.phase == "show_result":
    @st.dialog("Results")
    def show_result_dialog():
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
        st.info("📊 Close this dialog to see the updated flow chart, then click 'Start a new round' below the chart.")
    
    if have_dialog():
        show_result_dialog()

    # Show reset button below the chart when in show_result phase
    st.write("")
    if st.button("🔄 Start a new round", type="primary", use_container_width=True):
        # reset arrows
        st.session_state.chrono_pos_effect = 0
        st.session_state.chrono_neg_effect = 0
        st.session_state.ino_pos_effect = 0
        st.session_state.ino_neg_effect = 0
        st.session_state.venous_return_effect = 0
        st.session_state.afterload_effect = 0
        st.session_state.hr_direct_effect = 0
        st.session_state.sv_direct_effect = 0

        st.session_state.graph_version += 1

        st.session_state.phase = "select_box"
        st.session_state.selected_node = None
        st.session_state.pending_direction = None
        st.session_state.prediction = None
        st.rerun()

st.write("")
st.caption("📝 Arrows show direction of change only. CO = HR × SV (simplified learning model).")
