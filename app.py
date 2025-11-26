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
      
      .header-box {
        border: 2px solid #333;
        border-radius: 8px;
        padding: 12px;
        background: #EFE7E5;
        text-align: center;
        margin-bottom: 0px;
      }
      
      .header-box h4 {
        margin: 0 0 4px 0;
        font-size: 1rem;
        font-weight: 700;
      }
      
      .header-box .desc {
        font-size: 0.8rem;
        color: #666;
        margin: 0;
      }
      
      .header-box-yellow {
        border: 2px solid #333;
        border-radius: 8px;
        padding: 12px;
        background: #FFF8DC;
        text-align: center;
        margin-bottom: 8px;
      }
      
      .header-box-yellow h4 {
        margin: 0 0 4px 0;
        font-size: 1rem;
        font-weight: 700;
      }
      
      .header-box-yellow .desc {
        font-size: 0.8rem;
        color: #666;
        margin: 0;
      }
      
      .arrow-display {
        font-size: 2rem;
        font-weight: 800;
        margin: 8px 0;
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
        padding: 0.4rem 0.8rem !important;
        font-weight: 600 !important;
      }
      
      .agent-box {
        border: 2px solid #333;
        border-radius: 8px;
        padding: 10px;
        background: white;
        text-align: center;
        margin-bottom: 8px;
      }
      
      .agent-box h5 {
        margin: 0 0 4px 0;
        font-size: 0.9rem;
        font-weight: 600;
      }
      
      .downstream-box {
        border: 2px solid #333;
        border-radius: 8px;
        padding: 15px;
        background: #EFE7E5;
        text-align: center;
      }
      
      .downstream-box h4 {
        margin: 0 0 4px 0;
        font-size: 1.1rem;
        font-weight: 700;
      }
      
      .downstream-box-yellow {
        border: 2px solid #333;
        border-radius: 8px;
        padding: 15px;
        background: #FFF8DC;
        text-align: center;
      }
      
      .downstream-box-yellow h4 {
        margin: 0 0 4px 0;
        font-size: 1.1rem;
        font-weight: 700;
      }
      
      .co-box {
        border: 2px solid #333;
        border-radius: 8px;
        padding: 20px;
        background: #F3D6DA;
        text-align: center;
      }
      
      .co-box h4 {
        margin: 0 0 4px 0;
        font-size: 1.2rem;
        font-weight: 700;
      }
      
      .arrow-down {
        text-align: center;
        font-size: 1.5rem;
        color: #333;
        margin: 5px 0;
      }
      
      .correlation-text {
        font-style: italic;
        font-size: 0.85rem;
        color: #555;
        text-align: center;
        margin: 5px 0;
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
    net_ino = st.session_state.ino_pos_effect - st.session_state.ino_neg_effect
    venous = st.session_state.venous_return_effect
    afterload = st.session_state.afterload_effect
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
    "<p class='subtitle'>Click ⬆️ Increase or ⬇️ Decrease in any box, predict the CO change, then see the flow chart update.</p>",
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

cp = effect_arrow(st.session_state.chrono_pos_effect)
cn = effect_arrow(st.session_state.chrono_neg_effect)
ip = effect_arrow(st.session_state.ino_pos_effect)
inn = effect_arrow(st.session_state.ino_neg_effect)
vr = effect_arrow(st.session_state.venous_return_effect)
al = effect_arrow(st.session_state.afterload_effect)

# ---------------------------
# ROW 1: Four header boxes
# ---------------------------
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(
        """
        <div class='header-box'>
            <h4>Chronotropic agents</h4>
            <div class='desc'>(alter SA node and AV node activity)</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        f"""
        <div class='header-box-yellow'>
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
        <div class='header-box' style='background: #FFF0EC;'>
            <h4>Inotropic agents</h4>
            <div class='desc'>(substances that alter contractility of myocardium)</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col4:
    st.markdown(
        f"""
        <div class='header-box-yellow'>
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

# ---------------------------
# ROW 2: Agent sub-boxes and correlation text
# ---------------------------
col1, col2, col3, col4 = st.columns(4)

with col1:
    # Positive/Negative agents under Chronotropic
    sub1, sub2 = st.columns(2)
    with sub1:
        st.markdown(f"<div class='agent-box'><h5>Positive agents</h5><div class='arrow-display'>{cp}</div></div>", unsafe_allow_html=True)
        if st.button("⬆️ Increase", key="chrono_pos_inc", use_container_width=True):
            st.session_state.selected_node = "chrono_pos"
            st.session_state.pending_direction = 1
            st.session_state.phase = "predict"
            st.rerun()
        if st.button("⬇️ Decrease", key="chrono_pos_dec", use_container_width=True):
            st.session_state.selected_node = "chrono_pos"
            st.session_state.pending_direction = -1
            st.session_state.phase = "predict"
            st.rerun()
    with sub2:
        st.markdown(f"<div class='agent-box'><h5>Negative agents</h5><div class='arrow-display'>{cn}</div></div>", unsafe_allow_html=True)
        if st.button("⬆️ Increase", key="chrono_neg_inc", use_container_width=True):
            st.session_state.selected_node = "chrono_neg"
            st.session_state.pending_direction = 1
            st.session_state.phase = "predict"
            st.rerun()
        if st.button("⬇️ Decrease", key="chrono_neg_dec", use_container_width=True):
            st.session_state.selected_node = "chrono_neg"
            st.session_state.pending_direction = -1
            st.session_state.phase = "predict"
            st.rerun()

with col2:
    # Arrow from venous return
    st.markdown("<div class='arrow-down'>↓</div>", unsafe_allow_html=True)
    st.markdown("<div class='correlation-text'>is directly<br/>correlated with</div>", unsafe_allow_html=True)

with col3:
    # Positive/Negative agents under Inotropic
    sub1, sub2 = st.columns(2)
    with sub1:
        st.markdown(f"<div class='agent-box'><h5>Positive agents</h5><div class='arrow-display'>{ip}</div></div>", unsafe_allow_html=True)
        if st.button("⬆️ Increase", key="ino_pos_inc", use_container_width=True):
            st.session_state.selected_node = "ino_pos"
            st.session_state.pending_direction = 1
            st.session_state.phase = "predict"
            st.rerun()
        if st.button("⬇️ Decrease", key="ino_pos_dec", use_container_width=True):
            st.session_state.selected_node = "ino_pos"
            st.session_state.pending_direction = -1
            st.session_state.phase = "predict"
            st.rerun()
    with sub2:
        st.markdown(f"<div class='agent-box'><h5>Negative agents</h5><div class='arrow-display'>{inn}</div></div>", unsafe_allow_html=True)
        if st.button("⬆️ Increase", key="ino_neg_inc", use_container_width=True):
            st.session_state.selected_node = "ino_neg"
            st.session_state.pending_direction = 1
            st.session_state.phase = "predict"
            st.rerun()
        if st.button("⬇️ Decrease", key="ino_neg_dec", use_container_width=True):
            st.session_state.selected_node = "ino_neg"
            st.session_state.pending_direction = -1
            st.session_state.phase = "predict"
            st.rerun()

with col4:
    # Arrow from afterload
    st.markdown("<div class='arrow-down'>↓</div>", unsafe_allow_html=True)
    st.markdown("<div class='correlation-text'>is inversely<br/>correlated with</div>", unsafe_allow_html=True)

# ---------------------------
# ROW 3: Arrows down (positioned under each section)
# ---------------------------
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("<div class='arrow-down'>↓</div>", unsafe_allow_html=True)

with col2:
    st.write("")  # Empty - venous return arrow already shown above

with col3:
    st.markdown("<div class='arrow-down'>↓</div>", unsafe_allow_html=True)

with col4:
    st.write("")  # Empty - afterload arrow already shown above

# ---------------------------
# ROW 4: Heart Rate (col 1) and Stroke Volume (cols 2-4)
# ---------------------------
col_hr, col_sv = st.columns([1, 3])

with col_hr:
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

with col_sv:
    st.markdown(
        f"""
        <div class='downstream-box-yellow'>
            <h4>Stroke volume</h4>
            <div class='desc'>(blood pumped per beat)</div>
            <div class='arrow-display'>{SV_arrow}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

# ---------------------------
# ROW 5: Arrows to Cardiac Output
# ---------------------------
col_arrow1, col_arrow2 = st.columns([1, 3])

with col_arrow1:
    st.markdown("<div style='text-align: center; font-size: 2rem; margin: 10px 0;'>↘</div>", unsafe_allow_html=True)

with col_arrow2:
    st.markdown("<div style='text-align: center; font-size: 2rem; margin: 10px 0;'>↙</div>", unsafe_allow_html=True)

# ---------------------------
# ROW 6: Cardiac Output (full width)
# ---------------------------
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
if st.session_state.phase == "predict" and st.session_state.selected_node:
    node = st.session_state.selected_node
    _, _, CO_before = compute_state()

    if have_dialog():
        @st.dialog("🔮 Predict the impact on cardiac output")
        def predict_dialog():
            st.write("**What will happen to cardiac output?**")
            st.write("")
            pred = st.radio("Your prediction:", ["Increase", "Decrease", "No change"], index=None)
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
                st.session_state[key_map[node]] = st.session_state.pending_direction
                st.session_state.graph_version += 1
                _, _, CO_after = compute_state()
                dir_CO = expected_direction(CO_before, CO_after)
                st.session_state.last_feedback = dir_CO
                st.session_state.last_correct = (dir_CO == pred)
                st.session_state.phase = "show_result"
                st.rerun()
        predict_dialog()

if st.session_state.phase == "show_result":
    if have_dialog():
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
            st.info("📊 Close this dialog to see the updated flow chart, then click 'Start a new round' below.")
        show_result_dialog()

    st.write("")
    if st.button("🔄 Start a new round", type="primary", use_container_width=True):
        for key in ["chrono_pos_effect", "chrono_neg_effect", "ino_pos_effect", "ino_neg_effect",
                    "venous_return_effect", "afterload_effect"]:
            st.session_state[key] = 0
        st.session_state.graph_version += 1
        st.session_state.phase = "select_box"
        st.session_state.selected_node = None
        st.session_state.pending_direction = None
        st.session_state.prediction = None
        st.rerun()

st.write("")
st.caption("📝 Arrows show direction of change only. CO = HR × SV (simplified learning model).")
