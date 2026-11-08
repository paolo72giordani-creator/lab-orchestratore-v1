import streamlit as st
from openai import OpenAI
import concurrent.futures
from docx import Document
import io
import re

st.set_page_config(page_title="Orchestratore IA Personalizzabile", page_icon="⚡", layout="centered")

st.title("⚡ Orchestratore Multi-Agente con Aree di Indagine Scelte")
st.write("Personalizza i ruoli dei tre agenti in parallelo e lascia che l'Editor crei un articolo ampio ed esaustivo.")

# --- SIDEBAR CONFIGURAZIONE ---
with st.sidebar:
    st.header("⚙️ Configurazione")
    api_key = st.text_input("OpenRouter API Key", type="password")
    modello = st.selectbox(
        "Modello OpenRouter",
        ["openrouter/auto", "anthropic/claude-3.5-haiku", "deepseek/deepseek-chat", "google/gemini-flash-1.5"],
        index=0
    )

tema = st.text_input("🎯 Tema centrale dell'indagine:", "L'uso degli Agenti IA nella didattica inclusiva")

st.markdown("---")
st.subheader("🕵️‍♂️ Personalizza le 3 Aree di Indagine in Parallelo")
st.write("Definisci cosa deve approfondire ciascun agente:")

focus_1 = st.text_input("Angolazione Agente 1", "Impatto pedagogico e metacognitivo sugli studenti")
focus_2 = st.text_input("Angolazione Agente 2", "Riferimenti normativi, privacy e inclusione (BES/DSA)")
focus_3 = st.text_input("Angolazione Agente 3", "Esempi pratici, operativi e laboratoriali per la classe")

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
if st.button("🚀 Avvia Orchestratore su Misura", type="primary"):
    if not api_key or not tema:
        st.error("⚠️ Inserisci la tua API Key di OpenRouter e il tema centrale.")
    else:
        with st.spinner("⚡ I tre agenti stanno lavorando in parallelo sulle angolazioni scelte..."):
            
            # 1. COSTRUZIONE DINAMICA DEI TASK USANDO LE SCELTE DELL'UTENTE
            task_1 = (
                f"Sei un esperto focalizzato su: {focus_1}.",
                f"Analizza il tema '{tema}' approfondendo rigorosamente questo aspetto: {focus_1}. Usa il grassetto per i concetti chiave."
            )
            task_2 = (
                f"Sei un esperto focalizzato su: {focus_2}.",
                f"Analizza il tema '{tema}' approfondendo rigorosamente questo aspetto: {focus_2}. Usa il grassetto per i concetti chiave."
            )
            task_3 = (
                f"Sei un esperto focalizzato su: {focus_3}.",
                f"Analizza il tema '{tema}' approfondendo rigorosamente questo aspetto: {focus_3}. Usa il grassetto per i concetti chiave."
            )

            # 2. ESECUZIONE IN PARALLELO REALE
            with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                future_1 = executor.submit(chiama_agente, task_1[0], task_1[1], api_key, modello)
                future_2 = executor.submit(chiama_agente, task_2[0], task_2[1], api_key, modello)
                future_3 = executor.submit(chiama_agente, task_3[0], task_3[1], api_key, modello)

                res_1 = future_1.result()
                res_2 = future_2.result()
                res_3 = future_3.result()

            st.session_state['res_1'] = res_1
            st.session_state['res_2'] = res_2
            st.session_state['res_3'] = res_3

            # 3. FASE DI CONVERGENZA: L'EDITOR SCRIVE L'ARTICOLO AMPIO ED ESAUSTIVO
            prompt_editor = f"""
            Sei un Caporedattore e un saggista di altissimo livello.
            Hai ricevuto tre ampi contributi specialistici sul tema centrale: "{tema}".
            
            Contributo 1 ({focus_1}):
            {res_1}
            
            Contributo 2 ({focus_2}):
            {res_2}
            
            Contributo 3 ({focus_3}):
            {res_3}
            
            Sintetizza, amalgama e sviluppa questi tre contributi in un ARTICOLO AMPIO, ESAUSTIVO E APPROFONDITO (circa 700-800 parole).
            L'articolo deve essere strutturato professionalmente con:
            - Un titolo principale (# [Titolo incisivo])
            - Sottotitoli di sezione preceduti da tre cancelletti (### [Sottotitolo])
            - Un flusso narrativo coerente che integri perfettamente i tre punti di vista scelti dall'utente.
            - Termini chiave evidenziati in **grassetto**.
            """
            
            articolo_ampio = chiama_agente(
                "Sei un editor editoriale d'eccellenza.", 
                prompt_editor, 
                api_key, 
                modello
            )
            st.session_state['articolo_ampio'] = articolo_ampio
            st.success("🎉 Analisi parallele completate e fuse nell'articolo esaustivo dall'Editor!")

# --- VISUALIZZAZIONE DEI RISULTATI NELL'APP ---
if 'articolo_ampio' in st.session_state:
    st.markdown("---")
    
    # Mostriamo le tre prospettive scelte dall'utente nei rispettivi expander
    col1, col2, col3 = st.columns(3)
    with col1:
        with st.expander(f"📌 {focus_1[:25]}..."):
            st.write(st.session_state['res_1'])
    with col2:
        with st.expander(f"📌 {focus_2[:25]}..."):
            st.write(st.session_state['res_2'])
    with col3:
        with st.expander(f"📌 {focus_3[:25]}..."):
            st.write(st.session_state['res_3'])

    st.markdown("---")
    st.subheader("📰 Articolo Saggistico Ampio e Coordinato (Editor)")
    st.markdown(st.session_state['articolo_ampio'])

    # --- GENERAZIONE FILE WORD (.docx) STRUTTURATO ---
    doc = Document()
    doc.add_heading(f"Report ed Analisi Integrata: {tema}", level=0)
    
    doc.add_heading("Articolo Saggistico Coordinato", level=1)
    append_markdown_to_docx(doc, st.session_state['articolo_ampio'])
    
    doc.add_heading("Contributi Specialistici di Partenza", level=1)
    
    doc.add_heading(f"1. {focus_1}", level=2)
    append_markdown_to_docx(doc, st.session_state['res_1'])
    
    doc.add_heading(f"2. {focus_2}", level=2)
    append_markdown_to_docx(doc, st.session_state['res_2'])
    
    doc.add_heading(f"3. {focus_3}", level=2)
    append_markdown_to_docx(doc, st.session_state['res_3'])

    bio = io.BytesIO()
    doc.save(bio)
    
    st.download_button(
        label="📄 Scarica Articolo e Report in Word (.docx)",
        data=bio.getvalue(),
        file_name=f"Articolo_Esaustivo_{tema.replace(' ', '_')}.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
