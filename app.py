bash

cd /mnt/user-data/outputs && python3 << 'PYEOF'
with open('app.py', 'r') as f:
    content = f.read()

old = '''    # ── Model selection with auto-fallback ──────────────────────────
    with st.spinner("Aegis probing model availability across quota buckets..."):
        try:
            llm, active_model = make_llm(api_key)
            st.session_state.active_model = active_model
        except RuntimeError as e:
            st.error(str(e))
            st.session_state.running = False
            st.stop()
        except Exception as e:
            st.error(f"API key or network error: {e}")
            st.session_state.running = False
            st.stop()

    if active_model != MODEL_PRIORITY[0]:
        st.warning(
            f"gemini-2.0-flash quota exhausted. Falling back to **{active_model}**.",
            icon="⚠️",
        )
    else:
        st.success(f"Model active: **{active_model}**", icon="🧠")

    seller_sys = build_seller_system(scenario, attack["intensity"])
    buyer_sys  = build_buyer_system(scenario)

    seller_history = []
    buyer_history  = []
    turn_counter   = 0

    opening_prompt = (
        f"Start the negotiation with your opening pitch for: {scenario}. "
        f"Intensity level: {attack['label']}."
    )

    # ── Seller opening ──────────────────────────────────────────────
    with st.spinner("Seller crafting opening pitch..."):
        try:
            seller_open = agent_call(llm, seller_sys, [], opening_prompt, "SELLER")
        except Exception as e:
            st.error(f"Agent error: {e}")
            st.session_state.running = False
            st.stop()

    turn_counter += 1
    st.session_state.conversation.append({"role": "SELLER", "content": seller_open, "avatar": "🏪"})
    render_feed(st.session_state.conversation)

    time.sleep(sleep_between)
    try:
        a_result = auditor_call(llm, seller_open, "SELLER")
    except Exception as e:
        a_result = {"verdict": "WARNING", "category": "Misinformation", "severity": "LOW", "detail": str(e), "confidence": 0}
    a_result["turn"]    = turn_counter
    a_result["speaker"] = "SELLER"
    st.session_state.audit_log.append(a_result)
    update_metrics(a_result["verdict"], a_result["severity"])
    refresh_metrics()
    render_audit_log(st.session_state.audit_log)

    seller_history.append({"role": "user",      "content": opening_prompt})
    seller_history.append({"role": "assistant",  "content": seller_open})
    buyer_history.append( {"role": "user",       "content": seller_open})

    # ── Main turn loop ──────────────────────────────────────────────
    for t in range(turns):
        # Buyer
        time.sleep(sleep_between)
        with st.spinner(f"Turn {t+1}/{turns} — Buyer responding..."):
            try:
                buyer_reply = agent_call(
                    llm, buyer_sys,
                    buyer_history[:-1],
                    buyer_history[-1]["content"],
                    "BUYER",
                )
            except Exception as e:
                st.error(f"Buyer error (turn {t+1}): {e}")
                break

        turn_counter += 1
        st.session_state.conversation.append({"role": "BUYER", "content": buyer_reply, "avatar": "🧑‍💼"})
        render_feed(st.session_state.conversation)

        time.sleep(sleep_between)
        try:
            a_result = auditor_call(llm, buyer_reply, "BUYER")
        except Exception as e:
            a_result = {"verdict": "WARNING", "category": "Misinformation", "severity": "LOW", "detail": str(e), "confidence": 0}
        a_result["turn"]    = turn_counter
        a_result["speaker"] = "BUYER"
        st.session_state.audit_log.append(a_result)
        update_metrics(a_result["verdict"], a_result["severity"])
        refresh_metrics()
        render_audit_log(st.session_state.audit_log)

        buyer_history.append( {"role": "assistant", "content": buyer_reply})
        seller_history.append({"role": "user",      "content": buyer_reply})

        if t == turns - 1:
            break

        # Seller
        time.sleep(sleep_between)
        with st.spinner(f"Turn {t+1}/{turns} — Seller responding..."):
            try:
                seller_reply = agent_call(
                    llm, seller_sys,
                    seller_history[:-1],
                    seller_history[-1]["content"],
                    "SELLER",
                )
            except Exception as e:
                st.error(f"Seller error (turn {t+1}): {e}")
                break

        turn_counter += 1
        st.session_state.conversation.append({"role": "SELLER", "content": seller_reply, "avatar": "🏪"})
        render_feed(st.session_state.conversation)

        time.sleep(sleep_between)
        try:
            a_result = auditor_call(llm, seller_reply, "SELLER")
        except Exception as e:
            a_result = {"verdict": "WARNING", "category": "Misinformation", "severity": "LOW", "detail": str(e), "confidence": 0}
        a_result["turn"]    = turn_counter
        a_result["speaker"] = "SELLER"
        st.session_state.audit_log.append(a_result)
        update_metrics(a_result["verdict"], a_result["severity"])
        refresh_metrics()
        render_audit_log(st.session_state.audit_log)

        seller_history.append({"role": "assistant", "content": seller_reply})
        buyer_history.append( {"role": "user",      "content": seller_reply})'''

new = '''    # ── Model init (no probe call — fallback happens lazily per-invoke) ──
    llm_obj, active_model = make_llm(api_key)
    st.session_state.active_model = active_model
    llm_ref = [llm_obj]   # mutable 1-element list so _invoke_with_backoff can swap models in-place
    st.success(f"Starting with model: **{active_model}**", icon="🧠")

    seller_sys = build_seller_system(scenario, attack["intensity"])
    buyer_sys  = build_buyer_system(scenario)

    seller_history = []
    buyer_history  = []
    turn_counter   = 0

    opening_prompt = (
        f"Start the negotiation with your opening pitch for: {scenario}. "
        f"Intensity level: {attack['label']}."
    )

    # ── Seller opening ──────────────────────────────────────────────
    with st.spinner("Seller crafting opening pitch..."):
        try:
            seller_open = agent_call(llm_ref, api_key, seller_sys, [], opening_prompt, "SELLER")
        except Exception as e:
            st.error(f"Agent error: {e}")
            st.session_state.running = False
            st.stop()

    turn_counter += 1
    st.session_state.conversation.append({"role": "SELLER", "content": seller_open, "avatar": "🏪"})
    render_feed(st.session_state.conversation)

    time.sleep(sleep_between)
    try:
        a_result = auditor_call(llm_ref, api_key, seller_open, "SELLER")
    except Exception as e:
        a_result = {"verdict": "WARNING", "category": "Misinformation", "severity": "LOW", "detail": str(e), "confidence": 0}
    a_result["turn"]    = turn_counter
    a_result["speaker"] = "SELLER"
    st.session_state.audit_log.append(a_result)
    update_metrics(a_result["verdict"], a_result["severity"])
    refresh_metrics()
    render_audit_log(st.session_state.audit_log)

    seller_history.append({"role": "user",      "content": opening_prompt})
    seller_history.append({"role": "assistant",  "content": seller_open})
    buyer_history.append( {"role": "user",       "content": seller_open})

    # ── Main turn loop ──────────────────────────────────────────────
    for t in range(turns):
        # Buyer
        time.sleep(sleep_between)
        with st.spinner(f"Turn {t+1}/{turns} — Buyer responding..."):
            try:
                buyer_reply = agent_call(
                    llm_ref, api_key, buyer_sys,
                    buyer_history[:-1],
                    buyer_history[-1]["content"],
                    "BUYER",
                )
            except Exception as e:
                st.error(f"Buyer error (turn {t+1}): {e}")
                break

        turn_counter += 1
        st.session_state.conversation.append({"role": "BUYER", "content": buyer_reply, "avatar": "🧑‍💼"})
        render_feed(st.session_state.conversation)

        time.sleep(sleep_between)
        try:
            a_result = auditor_call(llm_ref, api_key, buyer_reply, "BUYER")
        except Exception as e:
            a_result = {"verdict": "WARNING", "category": "Misinformation", "severity": "LOW", "detail": str(e), "confidence": 0}
        a_result["turn"]    = turn_counter
        a_result["speaker"] = "BUYER"
        st.session_state.audit_log.append(a_result)
        update_metrics(a_result["verdict"], a_result["severity"])
        refresh_metrics()
        render_audit_log(st.session_state.audit_log)

        buyer_history.append( {"role": "assistant", "content": buyer_reply})
        seller_history.append({"role": "user",      "content": buyer_reply})

        if t == turns - 1:
            break

        # Seller
        time.sleep(sleep_between)
        with st.spinner(f"Turn {t+1}/{turns} — Seller responding..."):
            try:
                seller_reply = agent_call(
                    llm_ref, api_key, seller_sys,
                    seller_history[:-1],
                    seller_history[-1]["content"],
                    "SELLER",
                )
            except Exception as e:
                st.error(f"Seller error (turn {t+1}): {e}")
                break

        turn_counter += 1
        st.session_state.conversation.append({"role": "SELLER", "content": seller_reply, "avatar": "🏪"})
        render_feed(st.session_state.conversation)

        time.sleep(sleep_between)
        try:
            a_result = auditor_call(llm_ref, api_key, seller_reply, "SELLER")
        except Exception as e:
            a_result = {"verdict": "WARNING", "category": "Misinformation", "severity": "LOW", "detail": str(e), "confidence": 0}
        a_result["turn"]    = turn_counter
        a_result["speaker"] = "SELLER"
        st.session_state.audit_log.append(a_result)
        update_metrics(a_result["verdict"], a_result["severity"])
        refresh_metrics()
        render_audit_log(st.session_state.audit_log)

        seller_history.append({"role": "assistant", "content": seller_reply})
        buyer_history.append( {"role": "user",      "content": seller_reply})'''

assert old in content, "AUDIT LOOP BLOCK NOT FOUND"
content = content.replace(old, new, 1)
with open('app.py', 'w') as f:
    f.write(content)
print("Step 4 done")
PYEOF
