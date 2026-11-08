import streamlit as st
from openai import OpenAI
import concurrent.futures
from docx import Document
import io
import re

st.set_page_config(page_title="Orchestratore IA Parallelo", page_icon="⚡", layout="centered")

st.title("⚡ Orchestratore Multi-Agente in Parallelo")
st.write("Esecuzione simultanea di agenti specializzati con sintesi coordinata e generazione documento Word.")

# --- SIDEBAR CONFIGURAZIONE ---
with st.sidebar:
    st.header("⚙️ Configurazione")
    api_key = st.text_input("OpenRouter API Key", type="password")
    modello = st.selectbox(
        "Modello OpenRouter",
        ["openrouter/auto", "anthropic/claude-3.5-haiku", "deepseek/deepseek-chat", "google/gemini-flash-1.5"],
        index=0
    )

tema = st.text_input("🎯 Inserisci il tema centrale:", "L'uso degli Agenti IA nella didattica inclusiva")

# --- FUNZIONE AUSILIARIA PER CHIAMARE OPENROUTER ---
def chiama_agente(prompt_sistema, prompt_utente, api_key_val, modello_val):
    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key_val)
    try:
        response = client.chat.completions.create(
            model=modello_val,
            messages=[
                {"role": "system", "content": prompt_sistema},
                {"role": "user", "content": prompt_utente}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Errore nell'agente: {e}"

# --- FUNZIONE PER CONVERTIRE IL MARKDOWN IN STILI WORD REALI ---
def append_markdown_to_docx(doc, text):
    for line in text.split('\n'):
        line_str = line.strip()
        if not line_str:
            continue
        if line_str.startswith('### '):
            doc.add_heading(line_str.replace('### ', ''), level=3)
        elif line_str.startswith('## '):
            doc.add_heading(line_str.replace('## ', ''), level=2)
        elif line_str.startswith('# '):
            doc.add_heading(line_str.replace('# ', ''), level=1)
        else:
            p = doc.add_paragraph()
            parts = re.split(r'(\*\*.*?\*\*)', line)
            for part in parts:
                if part.startswith('**') and part.endswith('**'):
                    p.add_run(part[2:-2]).bold = True
                else:
                    p.add_run(part)

# --- AVVIO DELL'ORCHESTRATORE PARALLELO ---
if st.button("🚀 Avvia Orchestratore in Parallelo", type="primary"):
    if not api_key or not tema:
        st.error("⚠️ Inserisci la tua API Key di OpenRouter e il tema.")
    else:
        with st.spinner("⚡ L'orchestratore ha avviato i processi in parallelo (Pedagogico, Normativo, Operativo)..."):
            
            # 1. DEFINIZIONE DEI TASK PER I 3 AGENTI IN CONTEMPORANEA
            task_pedagogico = (
                "Sei un Esperto di Pedagogia.",
                f"Analizza il tema '{tema}' individuando i benefici e l'impatto sull'apprendimento. Usa il grassetto per i concetti chiave."
            )
            task_normativo = (
                "Sei un Esperto di Normativa Scolastica e inclusione (BES/DSA).",
                f"Analizza il tema '{tema}' dal punto di vista normativo, dei diritti e dell'inclusione nella scuola italiana. Usa il grassetto."
            )
            task_pratico = (
                "Sei un Docente Innovatore.",
                f"Proponi 2 esempi pratici e operativi per applicare '{tema}' direttamente in classe. Usa il grassetto."
            )

            # 2. ESECUZIONE IN PARALLELO REALE CON ThreadPoolExecutor
            with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                future_pedagogico = executor.submit(chiama_agente, task_pedagogico[0], task_pedagogico[1], api_key, modello)
                future_normativo = executor.submit(chiama_agente, task_normativo[0], task_normativo[1], api_key, modello)
                future_pratico = executor.submit(chiama_agente, task_pratico[0], task_pratico[1], api_key, modello)

                # Raccolta dei risultati non appena completati
                res_pedagogico = future_pedagogico.result()
                res_normativo = future_normativo.result()
                res_pratico = future_pratico.result()

            st.session_state['res_pedagogico'] = res_pedagogico
            st.session_state['res_normativo'] = res_normativo
            st.session_state['res_pratico'] = res_pratico

            # 3. FASE DI CONVERGENZA: L'AGENTE EDITOR COORDINATORE
            prompt_editor = f"""
            Sei il Caporedattore e un saggista esperto in educazione. 
            Hai ricevuto tre contributi paralleli sul tema: "{tema}".
            
            Contributo Pedagogico:
            {res_pedagogico}
            
            Contributo Normativo/Inclusivo:
            {res_normativo}
            
            Contributo Operativo/Pratico:
            {res_pratico}
            
            Fondi insieme questi tre sguardi e scrivi un ARTICOLO DI SINTESI COMPLETO E ORGANICO (circa 500 parole). 
            Struttura l'articolo con un titolo principale (#), sottotitoli preceduti da tre cancelletti (###) ed evidenzia i termini importanti con il **grassetto**.
            """
            
            articolo_finale = chiama_agente(
                "Sei un editor editoriale di altissimo livello.", 
                prompt_editor, 
                api_key, 
                modello
            )
            st.session_state['articolo_finale'] = articolo_finale
            st.success("🎉 Analisi parallele completate e sintetizzate con successo dall'Editor!")

# --- VISUALIZZAZIONE DEI RISULTATI NELL'APP ---
if 'articolo_finale' in st.session_state:
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        with st.expander("🧠 Vista Pedagogica"):
            st.write(st.session_state['res_pedagogico'])
    with col2:
        with st.expander("⚖️ Vista Normativa"):
            st.write(st.session_state['res_normativo'])
    with col3:
        with st.expander("🛠️ Vista Operativa"):
            st.write(st.session_state['res_pratico'])

    st.markdown("---")
    st.subheader("📰 Articolo di Sintesi Coordinato (Editor)")
    st.markdown(st.session_state['articolo_finale'])

    # --- GENERAZIONE FILE WORD (.docx) STRUTTURATO ---
    doc = Document()
    doc.add_heading(f"Report Integrato: {tema}", level=0)
    
    doc.add_heading("1. Sintesi Coordinata (Editor)", level=1)
    append_markdown_to_docx(doc, st.session_state['articolo_finale'])
    
    doc.add_heading("2. Contributi di Analisi Parallela", level=1)
    doc.add_heading("Prospettiva Pedagogica", level=2)
    append_markdown_to_docx(doc, st.session_state['res_pedagogico'])
    doc.add_heading("Prospettiva Normativa", level=2)
    append_markdown_to_docx(doc, st.session_state['res_normativo'])
    doc.add_heading("Prospettiva Operativa", level=2)
    append_markdown_to_docx(doc, st.session_state['res_pratico'])

    bio = io.BytesIO()
    doc.save(bio)
    
    st.download_button(
        label="📄 Scarica Report Completo in Word (.docx)",
        data=bio.getvalue(),
        file_name=f"Report_Parallelo_{tema.replace(' ', '_')}.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
