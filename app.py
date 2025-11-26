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
      .arrow-display-small {
        font-size: 1.5rem;
        font-weight: 800;
        margin: 4px 0;
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
      .container-box {
        border: 2px solid #333;
        border-radius: 8px;
        padding: 12px;
        background: #EFE7E5;
        text-align: center;
      }
      .container-box h4 {
        margin: 0 0 4px 0;
        font-size: 1rem;
        font-weight: 700;
      }
      .container-box .desc {
        font-size: 0.8rem;
        color: #666;
        margin: 0 0 10px 0;
      }
      .container-box-pink {
        border: 2px solid #333;
        border-radius: 8px;
        padding: 12px;
        background: #FFF0EC;
        text-align: center;
      }
      .container-box-pink h4 {
        margin: 0 0 4px 0;
        font-size: 1rem;
        font-weight: 700;
      }
      .container-box-pink .desc {
        font-size: 0.8rem;
        color: #666;
        margin: 0 0 10px 0;
      }
      .inner-agent-box {
        border: 2px solid #333;
        border-radius: 6px;
        padding: 8px;
        background: white;
        text-align: center;
        margin-bottom: 6px;
      }
      .inner-agent-box h5 {
        margin: 0 0 4px 0;
        font-size: 0.85rem;
        font-weight: 600;
      }
      .stimulus-box {
        border: 2px solid #333;
        border-radius: 8px;
        padding: 10px;
        background: #FFF8DC;
        text-align: center;
        min-height: 80px;
      }
      .stimulus-box h5 {
        margin: 0 0 4px 0;
        font-size: 0.9rem;
        font-weight: 600;
        color: #333;
      }
      .stimulus-box .desc {
        font-size: 0.75rem;
        color: #666;
        margin: 0;
      }
      .response-box {
        border: 2px solid #333;
        border-radius: 8px;
        padding: 10px;
        background: #FFF8DC;
        text-align: center;
      }
      .response-box h5 {
        margin: 0 0 4px 0;
        font-size: 0.85rem;
        font-weight: 600;
        color: #333;
      }
      .result-box {
        border: 2px solid #333;
        border-radius: 8px;
        padding: 15px;
        background: #FFF8DC;
        text-align: center;
      }
      .result-box h4 {
        margin: 0 0 4px 0;
        font-size: 1.1rem;
        font-weight: 700;
      }
      .section-header {
        font-size: 0.9rem;
        font-weight: 600;
        color: #666;
        margin: 15px 0 10px 0;
        text-transform: uppercase;
        letter-spacing: 1px;
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

def compute_state_basic():
    hr0 = st.session_state.hr_baseline
    sv0 = st.session_state.sv_baseline
    HR_STEP = 0.12
    SV_STEP = 0.12
    net_chrono = st.session_state.chrono_pos_effect - st.session_state.chrono_neg_effect
    net_ino = st.session_state.ino_pos_effect - st.session_state.ino_neg_effect
    venous = st.session_state.venous_return_effect
    afterload = st.session_state.afterload_effect
    hr_direct = st.session_state.hr_direct_effect
    sv_direct = st.session_state.sv_direct_effect
    hr = hr0 * (1 + HR_STEP * (net_chrono + hr_direct))
    sv = sv0 * (1 + SV_STEP * (net_ino + venous - afterload + sv_direct))
    hr = max(30, min(180, hr))
    sv = max(30, min(140, sv))
    co = hr * sv / 1000.0
    return hr, sv, co

def compute_state_advanced():
    hr0 = st.session_state.hr_baseline
    sv0 = st.session_state.sv_baseline
    STEP = 0.12
    
    # Get stimuli
    exercise = st.session_state.exercise_effect
    bp = st.session_state.bp_effect  # Negative BP increases sympathetic, decreases parasympathetic
    
    # Exercise affects both pathways
    # BP affects sympathetic/parasympathetic (decreased BP -> increased sympathetic, decreased parasympathetic)
    sympathetic_effect = exercise - bp  # Decreased BP (negative) adds to sympathetic
    parasympathetic_effect = bp  # Decreased BP (negative) decreases parasympathetic (less slowing)
    
    # HR: increased by sympathetic, decreased by parasympathetic
    # So: sympathetic up -> HR up, parasympathetic down -> HR up
    hr_effect = sympathetic_effect - parasympathetic_effect
    
    hr = hr0 * (1 + STEP * hr_effect)
    sv = sv0 * (1 + STEP * exercise)  # SV still only from exercise via venous return -> EDV
    
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

def buttons_disabled():
    return st.session_state.phase != "select_box"

# ---------------------------
# Ensure session defaults
# ---------------------------
defaults = {
    "hr_baseline": 70.0,
    "sv_baseline": 70.0,
    "mode": "Basic",
    # Basic mode effects
    "chrono_pos_effect": 0,
    "chrono_neg_effect": 0,
    "ino_pos_effect": 0,
    "ino_neg_effect": 0,
    "venous_return_effect": 0,
    "afterload_effect": 0,
    "hr_direct_effect": 0,
    "sv_direct_effect": 0,
    # Advanced mode effects
    "exercise_effect": 0,
    "bp_effect": 0,
    # Phase tracking
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

# Mode toggle
mode = st.toggle("🔬 Advanced Mode", value=(st.session_state.mode == "Advanced"), key="mode_toggle")
if mode and st.session_state.mode != "Advanced":
    st.session_state.mode = "Advanced"
    st.session_state.phase = "select_box"
    st.session_state.selected_node = None
    st.rerun()
elif not mode and st.session_state.mode != "Basic":
    st.session_state.mode = "Basic"
    st.session_state.phase = "select_box"
    st.session_state.selected_node = None
    st.rerun()

disabled = buttons_disabled()

# ==================================================
# BASIC MODE
# ==================================================
if st.session_state.mode == "Basic":
    st.markdown(
        "<p class='subtitle'>Click ⬆️ Increase or ⬇️ Decrease in any box, predict the CO change, then see the flow chart update.</p>",
        unsafe_allow_html=True
    )
    
    # Compute state
    hr, sv, co = compute_state_basic()
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

    # ROW 1: Four main boxes
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            """
            <div class='container-box'>
                <h4>Chronotropic agents</h4>
                <div class='desc'>(alter SA node and AV node activity)</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        sub1, sub2 = st.columns(2)
        with sub1:
            st.markdown(f"<div class='inner-agent-box'><h5>Positive agents</h5><div style='font-size:0.75rem;color:#666;'>Amount:</div><div class='arrow-display'>{cp}</div></div>", unsafe_allow_html=True)
            if st.button("⬆️ Add more", key="chrono_pos_inc", use_container_width=True, disabled=disabled):
                st.session_state.selected_node = "chrono_pos"
                st.session_state.pending_direction = 1
                st.session_state.phase = "predict"
                st.rerun()
            if st.button("⬇️ Add less", key="chrono_pos_dec", use_container_width=True, disabled=disabled):
                st.session_state.selected_node = "chrono_pos"
                st.session_state.pending_direction = -1
                st.session_state.phase = "predict"
                st.rerun()
        with sub2:
            st.markdown(f"<div class='inner-agent-box'><h5>Negative agents</h5><div style='font-size:0.75rem;color:#666;'>Amount:</div><div class='arrow-display'>{cn}</div></div>", unsafe_allow_html=True)
            if st.button("⬆️ Add more", key="chrono_neg_inc", use_container_width=True, disabled=disabled):
                st.session_state.selected_node = "chrono_neg"
                st.session_state.pending_direction = 1
                st.session_state.phase = "predict"
                st.rerun()
            if st.button("⬇️ Add less", key="chrono_neg_dec", use_container_width=True, disabled=disabled):
                st.session_state.selected_node = "chrono_neg"
                st.session_state.pending_direction = -1
                st.session_state.phase = "predict"
                st.rerun()

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
            if st.button("⬆️ Increase", key="venous_inc", use_container_width=True, disabled=disabled):
                st.session_state.selected_node = "venous"
                st.session_state.pending_direction = 1
                st.session_state.phase = "predict"
                st.rerun()
        with c2:
            if st.button("⬇️ Decrease", key="venous_dec", use_container_width=True, disabled=disabled):
                st.session_state.selected_node = "venous"
                st.session_state.pending_direction = -1
                st.session_state.phase = "predict"
                st.rerun()
        st.markdown("<div class='arrow-down'>↓</div>", unsafe_allow_html=True)
        st.markdown("<div class='correlation-text'>is directly<br/>correlated with</div>", unsafe_allow_html=True)

    with col3:
        st.markdown(
            """
            <div class='container-box-pink'>
                <h4>Inotropic agents</h4>
                <div class='desc'>(substances that alter contractility of myocardium)</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        sub1, sub2 = st.columns(2)
        with sub1:
            st.markdown(f"<div class='inner-agent-box'><h5>Positive agents</h5><div style='font-size:0.75rem;color:#666;'>Amount:</div><div class='arrow-display'>{ip}</div></div>", unsafe_allow_html=True)
            if st.button("⬆️ Add more", key="ino_pos_inc", use_container_width=True, disabled=disabled):
                st.session_state.selected_node = "ino_pos"
                st.session_state.pending_direction = 1
                st.session_state.phase = "predict"
                st.rerun()
            if st.button("⬇️ Add less", key="ino_pos_dec", use_container_width=True, disabled=disabled):
                st.session_state.selected_node = "ino_pos"
                st.session_state.pending_direction = -1
                st.session_state.phase = "predict"
                st.rerun()
        with sub2:
            st.markdown(f"<div class='inner-agent-box'><h5>Negative agents</h5><div style='font-size:0.75rem;color:#666;'>Amount:</div><div class='arrow-display'>{inn}</div></div>", unsafe_allow_html=True)
            if st.button("⬆️ Add more", key="ino_neg_inc", use_container_width=True, disabled=disabled):
                st.session_state.selected_node = "ino_neg"
                st.session_state.pending_direction = 1
                st.session_state.phase = "predict"
                st.rerun()
            if st.button("⬇️ Add less", key="ino_neg_dec", use_container_width=True, disabled=disabled):
                st.session_state.selected_node = "ino_neg"
                st.session_state.pending_direction = -1
                st.session_state.phase = "predict"
                st.rerun()

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
            if st.button("⬆️ Increase", key="afterload_inc", use_container_width=True, disabled=disabled):
                st.session_state.selected_node = "afterload"
                st.session_state.pending_direction = 1
                st.session_state.phase = "predict"
                st.rerun()
        with c2:
            if st.button("⬇️ Decrease", key="afterload_dec", use_container_width=True, disabled=disabled):
                st.session_state.selected_node = "afterload"
                st.session_state.pending_direction = -1
                st.session_state.phase = "predict"
                st.rerun()
        st.markdown("<div class='arrow-down'>↓</div>", unsafe_allow_html=True)
        st.markdown("<div class='correlation-text'>is inversely<br/>correlated with</div>", unsafe_allow_html=True)

    # ROW 2: Arrows
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("<div class='arrow-down'>↓</div>", unsafe_allow_html=True)
    with col3:
        st.markdown("<div class='arrow-down'>↓</div>", unsafe_allow_html=True)

    # ROW 3: HR and SV
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
        c1, c2 = st.columns(2)
        with c1:
            if st.button("⬆️ Increase", key="hr_inc", use_container_width=True, disabled=disabled):
                st.session_state.selected_node = "hr"
                st.session_state.pending_direction = 1
                st.session_state.phase = "predict"
                st.rerun()
        with c2:
            if st.button("⬇️ Decrease", key="hr_dec", use_container_width=True, disabled=disabled):
                st.session_state.selected_node = "hr"
                st.session_state.pending_direction = -1
                st.session_state.phase = "predict"
                st.rerun()

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
        c1, c2 = st.columns(2)
        with c1:
            if st.button("⬆️ Increase", key="sv_inc", use_container_width=True, disabled=disabled):
                st.session_state.selected_node = "sv"
                st.session_state.pending_direction = 1
                st.session_state.phase = "predict"
                st.rerun()
        with c2:
            if st.button("⬇️ Decrease", key="sv_dec", use_container_width=True, disabled=disabled):
                st.session_state.selected_node = "sv"
                st.session_state.pending_direction = -1
                st.session_state.phase = "predict"
                st.rerun()

    # Arrows to CO
    col_arrow1, col_arrow2 = st.columns([1, 3])
    with col_arrow1:
        st.markdown("<div style='text-align: center; font-size: 2rem; margin: 10px 0;'>↘</div>", unsafe_allow_html=True)
    with col_arrow2:
        st.markdown("<div style='text-align: center; font-size: 2rem; margin: 10px 0;'>↙</div>", unsafe_allow_html=True)

    # CO
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
    reset_keys = ["chrono_pos_effect", "chrono_neg_effect", "ino_pos_effect", "ino_neg_effect",
                  "venous_return_effect", "afterload_effect", "hr_direct_effect", "sv_direct_effect"]
    compute_fn = compute_state_basic

# ==================================================
# ADVANCED MODE
# ==================================================
else:
    st.markdown(
        "<p class='subtitle'><b>Advanced Mode:</b> See how exercise triggers two pathways that both increase cardiac output.</p>",
        unsafe_allow_html=True
    )
    
    # Legend removed - using consistent box styling instead
    
    # Compute state
    exercise = st.session_state.exercise_effect
    bp = st.session_state.bp_effect
    exercise_arr = effect_arrow(exercise)
    bp_arr = effect_arrow(bp)
    
    # Derived values
    venous_return = exercise
    edv = venous_return
    # Sympathetic: increased by exercise, increased by decreased BP
    sympathetic = exercise - bp  # If BP decreases (negative), sympathetic increases
    # Parasympathetic: decreased by decreased BP
    parasympathetic = bp  # If BP decreases (negative), parasympathetic decreases
    # Ventricular filling is inverse of HR
    ventricular_filling = -(sympathetic - parasympathetic)
    
    hr, sv, co = compute_state_advanced()
    hr_dir = direction_vs_baseline(hr, st.session_state.hr_baseline)
    sv_dir = direction_vs_baseline(sv, st.session_state.sv_baseline)
    co_dir = direction_vs_baseline(co, (st.session_state.hr_baseline * st.session_state.sv_baseline / 1000.0))

    HR_arrow = effect_arrow(hr_dir)
    SV_arrow = effect_arrow(sv_dir)
    CO_arrow = effect_arrow(co_dir)
    venous_arr = effect_arrow(venous_return)
    edv_arr = effect_arrow(edv)
    sympathetic_arr = effect_arrow(sympathetic)
    parasympathetic_arr = effect_arrow(parasympathetic)
    filling_arr = effect_arrow(ventricular_filling)

    # ===== ROW 1: STIMULUS =====
    st.markdown("<div class='section-header'>Initial Stimulus</div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            f"""
            <div class='stimulus-box'>
                <h5>Exercise</h5>
                <div class='arrow-display-small'>{exercise_arr}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.button("🏃 Begin Exercise", key="exercise_inc", use_container_width=True, disabled=disabled):
            st.session_state.selected_node = "exercise"
            st.session_state.pending_direction = 1
            st.session_state.phase = "predict"
            st.rerun()
    
    with col2:
        st.markdown(
            f"""
            <div class='stimulus-box'>
                <h5>Blood Pressure</h5>
                <div class='arrow-display-small'>{bp_arr}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        c1, c2 = st.columns(2)
        with c1:
            if st.button("⬆️ Increase BP", key="bp_inc", use_container_width=True, disabled=disabled):
                st.session_state.selected_node = "bp"
                st.session_state.pending_direction = 1
                st.session_state.phase = "predict"
                st.rerun()
        with c2:
            if st.button("⬇️ Decrease BP", key="bp_dec", use_container_width=True, disabled=disabled):
                st.session_state.selected_node = "bp"
                st.session_state.pending_direction = -1
                st.session_state.phase = "predict"
                st.rerun()

    # Branching arrows
    st.markdown(
        """
        <div style="text-align: center; font-size: 1.5rem; margin: 10px 0;">
            <span style="margin-right: 80px;">↙</span>
            <span style="margin-left: 80px;">↘</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    # For boxes that show arrows only after stimulus is selected
    show_arrows = exercise != 0 or st.session_state.get("bp_effect", 0) != 0
    
    venous_display = venous_arr if show_arrows else ""
    edv_display = edv_arr if show_arrows else ""
    sympathetic_display = sympathetic_arr if show_arrows else ""
    parasympathetic_display = effect_arrow(-st.session_state.get("bp_effect", 0)) if show_arrows else ""
    HR_display = HR_arrow if show_arrows else ""
    filling_display = filling_arr if show_arrows else ""
    SV_display = SV_arrow if show_arrows else ""
    CO_display = CO_arrow if show_arrows else ""

    # Dynamic titles - remove arrows when no stimulus
    venous_title = "↑ Venous return" if venous_return > 0 else ("↓ Venous return" if venous_return < 0 else "Venous return")
    edv_title = "↑ EDV (preload)" if edv > 0 else ("↓ EDV (preload)" if edv < 0 else "EDV (preload)")
    sympathetic_title = "↑ Sympathetic activity" if sympathetic > 0 else ("↓ Sympathetic activity" if sympathetic < 0 else "Sympathetic activity")
    parasympathetic_val = -st.session_state.get("bp_effect", 0)
    parasympathetic_title = "↑ Parasympathetic activity" if parasympathetic_val > 0 else ("↓ Parasympathetic activity" if parasympathetic_val < 0 else "Parasympathetic activity")
    hr_title = "↑ Heart Rate" if hr_dir > 0 else ("↓ Heart Rate" if hr_dir < 0 else "Heart Rate")
    filling_title = "↑ Ventricular filling time" if ventricular_filling > 0 else ("↓ Ventricular filling time" if ventricular_filling < 0 else "Ventricular filling time")
    sv_title = "↑ Stroke Volume (SV)" if sv_dir > 0 else ("↓ Stroke Volume (SV)" if sv_dir < 0 else "Stroke Volume (SV)")
    co_title = "↑ Cardiac Output (CO = SV × HR)" if co_dir > 0 else ("↓ Cardiac Output (CO = SV × HR)" if co_dir < 0 else "Cardiac Output (CO = SV × HR)")

    # ===== ROW 2: FIRST RESPONSES =====
    st.markdown("<div class='section-header'>Physiological Responses</div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(
            f"""
            <div class='response-box'>
                <h5>{venous_title}</h5>
                <div style='font-size:0.75rem;color:#555;'>(blood returning to heart)</div>
                <div class='arrow-display-small'>{venous_display}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.markdown("<div class='arrow-down'>↓</div>", unsafe_allow_html=True)
        st.markdown(
            f"""
            <div class='response-box'>
                <h5>{edv_title}</h5>
                <div style='font-size:0.75rem;color:#555;'>(amount of blood in ventricle before contraction)</div>
                <div class='arrow-display-small'>{edv_display}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.markdown("<div class='arrow-down'>↓</div>", unsafe_allow_html=True)
    
    with col2:
        # Two sub-columns for sympathetic and parasympathetic
        sub1, sub2 = st.columns(2)
        with sub1:
            st.markdown(
                f"""
                <div class='response-box'>
                    <h5>{sympathetic_title}</h5>
                    <div class='arrow-display-small'>{sympathetic_display}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with sub2:
            st.markdown(
                f"""
                <div class='response-box'>
                    <h5>{parasympathetic_title}</h5>
                    <div class='arrow-display-small'>{parasympathetic_display}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        st.markdown("<div class='arrow-down'>↓</div>", unsafe_allow_html=True)
        st.markdown(
            f"""
            <div class='response-box'>
                <h5>{hr_title}</h5>
                <div style='font-size:0.75rem;color:#555;'>(beats per minute)</div>
                <div class='arrow-display-small'>{HR_display}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.markdown("<div class='arrow-down'>↓</div>", unsafe_allow_html=True)
        st.markdown(
            f"""
            <div class='response-box'>
                <h5>{filling_title}</h5>
                <div class='arrow-display-small'>{filling_display}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # ===== ROW 3: RESULTS - SV and HR =====
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(
            f"""
            <div class='result-box'>
                <h4>{sv_title}</h4>
                <div style='font-size:0.8rem;color:#555;'>(blood pumped per beat)</div>
                <div class='arrow-display'>{SV_display}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with col2:
        st.write("")  # Empty - HR is now in the chain above

    # Converging arrows
    st.markdown(
        """
        <div style="text-align: center; font-size: 2rem; margin: 10px 0;">
            <span style="margin-right: 100px;">↘</span>
            <span style="margin-left: 100px;">↙</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    # ===== ROW 4: CARDIAC OUTPUT =====
    st.markdown(
        f"""
        <div class='co-box'>
            <h4>{co_title}</h4>
            <div style='font-size:0.85rem;color:#555;'>(blood pumped per minute)</div>
            <div class='arrow-display'>{CO_display}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    key_map = {
        "exercise": "exercise_effect",
        "bp": "bp_effect",
    }
    reset_keys = ["exercise_effect", "bp_effect"]
    compute_fn = compute_state_advanced

# ---------------------------
# Handle phase transitions (shared by both modes)
# ---------------------------
if st.session_state.phase == "predict" and st.session_state.selected_node:
    node = st.session_state.selected_node
    _, _, CO_before = compute_fn()

    if have_dialog():
        @st.dialog("🔮 Predict the impact on cardiac output")
        def predict_dialog():
            st.write("**What will happen to cardiac output?**")
            st.write("")
            pred = st.radio("Your prediction:", ["Increase", "Decrease", "No change"], index=None)
            st.write("")
            if st.button("✅ Submit prediction", type="primary", disabled=(pred is None)):
                st.session_state.prediction = pred
                st.session_state[key_map[node]] = st.session_state.pending_direction
                st.session_state.graph_version += 1
                _, _, CO_after = compute_fn()
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

# Always show the reset button when in show_result phase
if st.session_state.phase == "show_result":
    st.write("")
    st.write("")
    if st.button("🔄 Start a new round", type="primary", use_container_width=True):
        for key in reset_keys:
            st.session_state[key] = 0
        st.session_state.graph_version += 1
        st.session_state.phase = "select_box"
        st.session_state.selected_node = None
        st.session_state.pending_direction = None
        st.session_state.prediction = None
        st.rerun()

st.write("")
st.caption("📝 Arrows show direction of change only. CO = HR × SV")
