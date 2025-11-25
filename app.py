import streamlit as st
import streamlit.components.v1 as components

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
    "<p class='subtitle'>Click ONE box to change. Lock ↑ or ↓, predict CO, then see the flow chart update.</p>",
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

# ---------------------------
# Flow chart with custom HTML/SVG
# ---------------------------
cp  = effect_arrow(st.session_state.chrono_pos_effect)
cn  = effect_arrow(st.session_state.chrono_neg_effect)
ip  = effect_arrow(st.session_state.ino_pos_effect)
inn = effect_arrow(st.session_state.ino_neg_effect)
vr  = effect_arrow(st.session_state.venous_return_effect)
al  = effect_arrow(st.session_state.afterload_effect)

# Create custom HTML flowchart
flowchart_html = f"""
<div id="flowchart" style="width: 100%; height: 650px; border: 1px solid #ddd; border-radius: 8px; background: white; position: relative;">
    <svg width="100%" height="100%" viewBox="0 0 1200 800" preserveAspectRatio="xMidYMid meet">
        <!-- Arrows/Lines -->
        <line x1="150" y1="200" x2="150" y2="380" stroke="#999" stroke-width="2" marker-end="url(#arrowhead)"/>
        <line x1="350" y1="200" x2="350" y2="380" stroke="#999" stroke-width="2" marker-end="url(#arrowhead)"/>
        <line x1="600" y1="150" x2="600" y2="380" stroke="#999" stroke-width="2" marker-end="url(#arrowhead)"/>
        <line x1="750" y1="200" x2="750" y2="380" stroke="#999" stroke-width="2" marker-end="url(#arrowhead)"/>
        <line x1="950" y1="200" x2="950" y2="380" stroke="#999" stroke-width="2" marker-end="url(#arrowhead)"/>
        <line x1="1050" y1="150" x2="900" y2="350" stroke="#999" stroke-width="2" marker-end="url(#arrowhead)"/>
        
        <line x1="250" y1="450" x2="600" y2="650" stroke="#999" stroke-width="3" marker-end="url(#arrowhead)"/>
        <line x1="850" y1="450" x2="600" y2="650" stroke="#999" stroke-width="3" marker-end="url(#arrowhead)"/>
        
        <!-- Arrow marker definition -->
        <defs>
            <marker id="arrowhead" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">
                <polygon points="0 0, 10 3, 0 6" fill="#999"/>
            </marker>
        </defs>
        
        <!-- Top Row -->
        <rect id="chrono_header" x="50" y="50" width="250" height="80" rx="8" fill="#EFE7E5" stroke="#999" stroke-width="2" style="cursor: pointer;"/>
        <text x="175" y="85" text-anchor="middle" font-size="14" font-weight="bold">Chronotropic agents</text>
        <text x="175" y="105" text-anchor="middle" font-size="12">(alter SA node and</text>
        <text x="175" y="120" text-anchor="middle" font-size="12">AV node activity)</text>
        
        <rect id="venous" x="475" y="50" width="250" height="80" rx="8" fill="#FFF6C8" stroke="#999" stroke-width="2" style="cursor: pointer;"/>
        <text x="600" y="80" text-anchor="middle" font-size="14" font-weight="bold">Venous return</text>
        <text x="600" y="100" text-anchor="middle" font-size="12">(preload)</text>
        <text x="600" y="120" text-anchor="middle" font-size="16" font-weight="bold">{vr}</text>
        
        <rect id="ino_header" x="750" y="50" width="200" height="80" rx="8" fill="#FFF0EC" stroke="#999" stroke-width="2" style="cursor: pointer;"/>
        <text x="850" y="80" text-anchor="middle" font-size="14" font-weight="bold">Inotropic agents</text>
        <text x="850" y="100" text-anchor="middle" font-size="12">(alter</text>
        <text x="850" y="115" text-anchor="middle" font-size="12">contractility)</text>
        
        <rect id="afterload" x="975" y="50" width="200" height="80" rx="8" fill="#E1E8FF" stroke="#999" stroke-width="2" style="cursor: pointer;"/>
        <text x="1075" y="80" text-anchor="middle" font-size="14" font-weight="bold">Afterload</text>
        <text x="1075" y="110" text-anchor="middle" font-size="16" font-weight="bold">{al}</text>
        
        <!-- Second Row -->
        <rect id="chrono_pos" x="50" y="150" width="200" height="60" rx="8" fill="#FFE8A3" stroke="#999" stroke-width="2" style="cursor: pointer;"/>
        <text x="150" y="175" text-anchor="middle" font-size="13">Positive agents</text>
        <text x="150" y="195" text-anchor="middle" font-size="16" font-weight="bold">{cp}</text>
        
        <rect id="chrono_neg" x="275" y="150" width="200" height="60" rx="8" fill="#FFE8A3" stroke="#999" stroke-width="2" style="cursor: pointer;"/>
        <text x="375" y="175" text-anchor="middle" font-size="13">Negative agents</text>
        <text x="375" y="195" text-anchor="middle" font-size="16" font-weight="bold">{cn}</text>
        
        <rect id="ino_pos" x="650" y="150" width="200" height="60" rx="8" fill="#FFD6CC" stroke="#999" stroke-width="2" style="cursor: pointer;"/>
        <text x="750" y="175" text-anchor="middle" font-size="13">Positive agents</text>
        <text x="750" y="195" text-anchor="middle" font-size="16" font-weight="bold">{ip}</text>
        
        <rect id="ino_neg" x="875" y="150" width="200" height="60" rx="8" fill="#FFD6CC" stroke="#999" stroke-width="2" style="cursor: pointer;"/>
        <text x="975" y="175" text-anchor="middle" font-size="13">Negative agents</text>
        <text x="975" y="195" text-anchor="middle" font-size="16" font-weight="bold">{inn}</text>
        
        <!-- Third Row -->
        <rect id="hr" x="50" y="380" width="400" height="80" rx="8" fill="#FFFFFF" stroke="#333" stroke-width="3" style="cursor: pointer;"/>
        <text x="250" y="415" text-anchor="middle" font-size="18" font-weight="bold">Heart rate (HR)</text>
        <text x="250" y="445" text-anchor="middle" font-size="22" font-weight="bold">{HR_arrow}</text>
        
        <rect id="sv" x="650" y="380" width="400" height="80" rx="8" fill="#FFFFFF" stroke="#333" stroke-width="3" style="cursor: pointer;"/>
        <text x="850" y="415" text-anchor="middle" font-size="18" font-weight="bold">Stroke volume (SV)</text>
        <text x="850" y="445" text-anchor="middle" font-size="22" font-weight="bold">{SV_arrow}</text>
        
        <!-- Bottom -->
        <rect id="co" x="400" y="650" width="400" height="100" rx="8" fill="#F3D6DA" stroke="#333" stroke-width="3" style="cursor: pointer;"/>
        <text x="600" y="690" text-anchor="middle" font-size="20" font-weight="bold">Cardiac output (CO)</text>
        <text x="600" y="725" text-anchor="middle" font-size="26" font-weight="bold">{CO_arrow}</text>
    </svg>
</div>

<script>
    const clickableIds = ['chrono_header', 'chrono_pos', 'chrono_neg', 'venous', 'ino_header', 'ino_pos', 'ino_neg', 'afterload', 'hr', 'sv'];
    
    clickableIds.forEach(id => {{
        const elem = document.getElementById(id);
        if (elem) {{
            elem.addEventListener('click', () => {{
                window.parent.postMessage({{
                    type: 'streamlit:setComponentValue',
                    value: id
                }}, '*');
            }});
            
            elem.addEventListener('mouseenter', () => {{
                elem.style.opacity = '0.8';
            }});
            
            elem.addEventListener('mouseleave', () => {{
                elem.style.opacity = '1';
            }});
        }}
    }});
</script>
"""

clicked = components.html(flowchart_html, height=650, scrolling=False)

# ---------------------------
# Handle click → phase transitions
# ---------------------------
controllables = {"chrono_pos", "chrono_neg", "ino_pos", "ino_neg", "venous", "afterload", "hr", "sv"}

if st.session_state.phase == "select_box" and clicked in controllables:
    st.session_state.selected_node = clicked
    st.session_state.phase = "choose_dir"
    st.rerun()

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
        "hr": "Heart Rate (HR)",
        "sv": "Stroke Volume (SV)",
    }
    node_title = title_map[node]

    if have_dialog():
        @st.dialog(f"📍 {node_title}")
        def choose_dir_dialog():
            st.write("**Do you want to increase or decrease this factor?**")
            st.write("")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("⬆️ Increase", use_container_width=True):
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
            if st.button("⬆️ Increase", use_container_width=True):
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
    else:
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
        st.info("📊 Review the updated flow chart above, then click 'Start a new round' below.")

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
