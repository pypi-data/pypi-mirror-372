from numpy import extract
from .myfuncs import generate_report2, import_file, count_pupils, dialog_stats, count_teacher_impulses, llm_analysis_groq, llm_analysis_openai

from pathlib import Path
import sys
import os
import webbrowser
from shiny import App, render, ui, reactive, req
from shiny._main import run_app

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from faicons import icon_svg
from groq import Groq
from openai import OpenAI, api_key
import json
from datetime import date
import tempfile
import pickle
import keyring
import keyring.errors


# Path Helper for css-files
def resource_path(relative_path: str) -> Path:
    if hasattr(sys, '_MEIPASS'):
        return Path(sys._MEIPASS) / relative_path
    return Path(__file__).parent / relative_path

# Open the App in a Web Browser
url = "http://127.0.0.1:8000"
webbrowser.open_new_tab(url)

# Define the Layout

# Sidebar Menu with Model Selection, Analysis, Report Download and Session Management
app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.output_ui("dynamic_select"),
        ui.input_switch("llm_switch", "Analyse per LLM", True),  
        ui.input_action_button("button_analysis", "Analyse starten", icon = icon_svg("magnifying-glass-chart")),
        ui.output_text("start_analysis"),
        ui.output_ui("show_report_download_button"),
        ui.input_file("button_import_session", "Sitzung importieren", accept=[".pkl"], multiple=False),
        ui.download_button("button_export_session", "Sitzung exportieren", icon = icon_svg("file-export")),
        ui.input_action_button("button_reset", "Sitzung zurücksetzen", icon = icon_svg("arrow-rotate-left")),
        title="Sidebar",
    ),

    # Main Content Area with Tabs for Analysis, Results, and Options
    ui.navset_tab(  
        ui.nav_panel("Analyse",
            ui.card(     
            ui.layout_columns(
                # Group and Transcript Metadata
                ui.card(
                ui.card_header("Allgemeine Informationen"),
                ui.input_text("name_group", "ID der Gruppe", "B1"),
                ui.input_numeric("num_pupils", "Anzahl Schüler:innen", 25, min=1, max=100),
                ui.input_text("name_teacher", "Name der Lehrperson im Transkript", "LEHRER"),              
                ),
                # Document Upload for Transcript and Codebook
                ui.card(
                    ui.card_header("Dokumenteneingabe"),
                    ui.input_file(
                        "transcript",
                        "Transkript hochladen",
                        multiple=False,
                        accept=[".txt", ".docx", ".pdf"],
                        button_label='Browse...',
                        placeholder='Keine Datei ausgewählt',
                    ),
                     ui.input_file(
                        "codebook",
                        "Codebuch hochladen",
                        multiple=False,
                        accept=[".txt", ".docx", ".pdf"],
                        button_label='Browse...',
                        placeholder='Keine Datei ausgewählt',
                    )

                ),
            ),     
            ),
            # Preview of Codebook and Transcript
            ui.card(
                ui.card_header("Vorschau Codebuch"),
                ui.output_ui("show_codebook_preview"),   
                full_screen=True,
            ),
            ui.card(
                ui.card_header("Vorschau Transkript"),
                ui.output_ui("show_transcript_preview"),   
                full_screen=True,
            ),
            icon=icon_svg("brain")
        ),
        # Results Tab with Quantitative and Qualitative Analysis
        ui.nav_panel("Ergebnisse",
            ui.card(
                ui.card_header(ui.h3("Quantitative Verteilung der Gesprächsanteile")),
                # General group satistics 
                ui.layout_column_wrap(
                    ui.value_box(
                        "ID der Gruppe ",
                        ui.output_text("nameGroup"),
                        showcase=icon_svg("id-card"),
                    ),
                    ui.value_box(
                        "Klassengröße",
                        ui.output_text("numPupils"),
                        showcase=icon_svg("user-group"),
                    ),
                    ui.value_box(
                        "Anzahl beteiligter Schüler:innen",
                        ui.output_text("numParticipants"),
                        showcase=icon_svg("user-check"),
                    ),
                    ui.value_box(
                        "Beteiligungsquote",
                        ui.output_text("participationRate"),
                        showcase=icon_svg("square-poll-vertical"),
                    ),
                    fill=False,
                ),
                ),
                # Quantitative Stats for Conversation Distribution
                ui.layout_columns(
                    # Conversation Distribution Plot
                    ui.card(
                        ui.card_header("Gesprächsverteilung"),
                        ui.output_plot("sim_stats_plot"),
                        full_screen=True,
                    ),
                    # Conversation Statistics for Teacher and Pupils
                    ui.card(
                        ui.card_header("Gesprächsbeiträge"),
                        ui.layout_column_wrap(
                            ui.card(
                            ui.card_header("Lehrperson"),
                            ui.markdown("**Anzahl Beiträge**"),
                            ui.output_text("teacher_turns"),
                            ui.markdown("**Länge in Wörtern M (SD)**"),
                            ui.output_text("teacher_turns_length"),

                            ),
                            ui.card(
                            ui.card_header("Schüler:innen"),
                            ui.markdown("**Anzahl Beiträge:**"),
                            ui.output_text("pupils_turns"),
                            ui.markdown("**Länge in Wörtern M (SD)**"),
                            ui.output_text("pupils_turns_length"),
                            ),
                        ),
                        full_screen=True,
                    ),
                    col_widths=[4, 8]
                ),
            # Qualitative Analysis of Teacher's Impulses
            # Quick Stats for Teacher's Impulses
            ui.card(
                ui.card_header(ui.h3("Qualitative Codierung der Impulse der Lehrperson")),
                ui.layout_columns(
                    ui.value_box(
                        "Anzahl der Gesprächsimpulse",
                        ui.output_text("teacher_impulses"),
                        showcase=icon_svg("square-poll-vertical")
                    ),
                    ui.value_box(
                        "Codierte Impulse",
                        ui.output_text("teacher_impulses_coded"),
                        showcase=icon_svg("hashtag")
                    ),
                    ui.value_box(
                        "Häufigster Code",
                        ui.output_text("code_most_used"),
                        showcase=icon_svg("ranking-star")
                    ),
                    ui.value_box(
                        "Gesprächsanteil der Lehrperson",
                        ui.output_text("teacher_share"),
                        showcase=icon_svg("user-tie")
                    ),
                    col_widths=[3]
                ),   
                ui.layout_columns(
                    # Qualitative Statistics Plot for Coded Impulses
                    ui.card(
                        ui.card_header("Verteilung der Impulse"),
                        ui.row(
                            ui.output_plot("qualitative_stats_plot"),
                        ),
                        # Explanation of Codes
                        ui.row(
                            ui.output_ui("code_legend"),
                        ),
                        full_screen=True,
                    ),
                    # DataFrame of Coded Impulses
                    ui.card(
                        ui.card_header("Codierung der Impulse"),
                        ui.output_ui("quali_stats_df"),
                        full_screen=True,
                    ),
                ),          
            ),
        ),
        # Options Tab for API Configuration and Custom Prompts
        ui.nav_panel("Optionen",
            # API Configuration 
            ui.card(
                ui.card_header("API-Konfiguration"),
                ui.layout_columns(
                    # Select between OpenAI and Groq API    
                    ui.card(
                        "API-Auswahl",
                        ui.input_switch("api_select", "OpenAI nutzen", True)
                    ),
                    # Api Key Management
                    ui.card(
                        ui.output_text("api_key_exists"),
                        ui.layout_columns( 
                        ui.input_action_button("button_change_api_key", "Ändern"),
                        ui.input_action_button("button_delete_api_key", "Löschen"),
                        ),
                    ),
                ),
                # Prompt Management for System and User Prompt
            ui.card(
                ui.card_header("Benutzerdefinierte Prompts"),
                "System-Prompt",
                ui.output_text_verbatim("system_prompt_output"),
                ui.input_action_button("button_change_system_prompt", "Ändern", width="20%"),
                "User-Prompt",
                ui.output_text_verbatim("user_prompt_output"),
                ui.input_action_button("button_change_user_prompt", "Ändern", width="20%"),              
                ),                
            ),
            icon=icon_svg("gear")  
        ),
        # Tab Identifier to Actively Switch Between Tabs
        id="main_tabs",  
    ),  

    # Incluse CSS Stylesheet
    ui.include_css(str(resource_path("static/styles.css"))),
    # Set the Title of the App-Window
    title="LLM Teaching Simulation Evaluation",
    fillable=True,
    )


def server(input, output, session):
    # Define helper variables
    transcript_data = reactive.value(None)
    codebook_data = reactive.value(None)
    api_key_groq = reactive.value()
    api_key_openai = reactive.value()
    num_participants = reactive.value(None)
    participation_rate = reactive.value(None)
    t_turns = reactive.value(None)
    t_turns_length = reactive.value(None)
    t_turns_length_mean_sd = reactive.value(None)
    p_turns = reactive.value(None)
    p_turns_length = reactive.value(None)
    p_turns_length_mean_sd = reactive.value(None)
    stats = reactive.value(None)
    llm_analysis_data = reactive.value([])
    model = reactive.value("llama-3.3-70b-versatile")
    teacher_impulses_count = reactive.value(None)
    analysis_state = reactive.value(False)
    analysis_llm_state = reactive.value(False)
    sim_plot = reactive.value(None)
    qual_plot = reactive.value()
    qual_stats_df = reactive.value(None)
    placeholder_plot = reactive.value()


    # Define Baseline System Prompt
    system_prompt = reactive.value('''
    Sie sind jetzt ein Forschungsexperte für qualitative Analyse von Unterrichtsgesprächen.
    Das Ziel besteht darin, die Äußerungen der Lehrperson aus dem Unterricht basierend auf einem vordefinierten Codebuch zu codieren, um die Qualität der sprachlichen Impulse der Lehrkraft zu verstehen.
    Die Daten stammen aus einer Unterrichtsstunde in Deutschland.
    Bitte führe die Analyse durch und codiere ausschließlich mit dem Codebuch die übereinstimmenden sprachlichen Impulse der Lehrperson.
    Gibt die Zuordnung der Codes zu den Lehrerimpulsen (in Kurzform) als strukturierte Daten in JSON aus. Zitiere die Lehreräußerung wörtlich und fasse sie nicht zusammen! Das JSON-Schema sollte enthalten:
    {
        "#": "int (aufsteigend nummeriert)",
        "Shortcode": "string (kategorisch: der zugeordnete Shortcode aus dem Codebuch)",
        "Lehreräußerung (kurz)": "string (Die jeweilige Lehreräußerung)"
    }
    '''
    )


    # Define Baseline User Prompt
    user_prompt = reactive.value('''
    Ich stelle dir nun das Transkript zur Verfügung. Eine Leerzeile markiert einen Sprecherwechsel. Die Lehrperson wird, wenn Sie spricht, als ‚Lehrperson‘
    oder ‚Lehrer‘ gefolgt von einem Doppelpunkt dargestellt. Äußerungen der Schüler werden mit S01, S02, S03… gefolgt von einem Doppelpunkt dargestellt. Die gleiche Nummer bedeutet, dass derselbe Schüler spricht.

    {transcript}

    Und hier ist das Codebuch: {codebook}

    Bitte führe damit die Analyse des Transkripts durch und codiere ausschließlich mit dem Codebuch die übereinstimmenden sprachlichen Impulse der Lehrperson. Erfinde keine eigenen Codes. Denke daran, die Analyse als formatiertes JSON auszugeben.
    '''
    )


    # Load API keys from keyring if they exist
    try:
        api_key_openai.set(keyring.get_password("teach_sim_eval", "api_key_openai"))
    except keyring.errors.PasswordDeleteError:
        pass

    try: 
        api_key_groq.set(keyring.get_password("teach_sim_eval", "api_key_groq"))
    except keyring.errors.PasswordDeleteError:
        pass

 
    ##### Testing Teil #####
    # Session Export
    @render.download(filename=lambda: f"{date.today().isoformat()} - llm_tse_session.pkl")
    def button_export_session():
        session_data = {
            "transcript_data": transcript_data.get(),
            "num_participants": num_participants.get(),
            "participation_rate": participation_rate.get(),
            "stats": stats.get(),
            "llm_analysis_data": llm_analysis_data.get(),
            "analysis_llm_state": analysis_llm_state.get(),
        }
        
        # serialize the dictionary to a pickle file
        with open("session_dump.pkl", "wb") as f:
            pickle.dump(session_data, f)
        return "session_dump.pkl"
    

    # Session Import
    @reactive.effect
    def imported_session():
        file = input.button_import_session()
        if not file:
            return
        
        with open(file[0]["datapath"], "rb") as f:
            session_data = pickle.load(f)
        
        # Set the reactive values
        transcript_data.set(session_data.get("transcript_data"))
        num_participants.set(session_data.get("num_participants"))
        participation_rate.set(session_data.get("participation_rate"))
        stats.set(session_data.get("stats"))
        llm_analysis_data.set(session_data.get("llm_analysis_data"))
        analysis_llm_state.set(session_data.get("analysis_llm_state"))
        placeholder_plot.set(session_data.get("placeholder_plot"))

        ui.update_switch("llm_switch", value=False)
        m = ui.modal(  
                "Bitte Analyse erneut starten (ohne LLM)!",  
                title="Hinweis",  
                easy_close=True,  
            )  
        ui.modal_show(m)  


    # Reset Session
    @reactive.effect
    @reactive.event(input.button_reset)
    def reset_session():
        # Reset all reactive values to their initial state
        transcript_data.set(None)
        codebook_data.set(None)
        num_participants.set(None)
        participation_rate.set(None)
        stats.set(None)
        llm_analysis_data.set([])
        teacher_impulses_count.set(None)
        analysis_state.set(False)
        analysis_llm_state.set(False)
        sim_plot.set(None)
        qual_plot.set(None)
        qual_stats_df.set(None)
        placeholder_plot.set(None)
        # Go back to Analysis Pane
        ui.update_navs("main_tabs", selected="Analyse")

    # Create a bar plot for quantitative statistics
    @reactive.calc
    def make_sim_stats_plot():
        req(input.button_analysis(), transcript_data.get() != None)

        distribution = stats.get().plot(kind='bar', x='Sprecher', y='Gesamt_Woerter', alpha=1, rot=0)
        plt.gca().set_xlabel('Wörter insgesamt')
        plt.gca().set_ylabel('Anzahl')
        distribution.set_axisbelow(True)
        distribution.grid(color='gray', axis = 'y')
        distribution.get_legend().remove()
        total = stats.get()['Gesamt_Woerter'].sum()
        for container in distribution.containers:
            perc_labels = [f"{(bar.get_height() / total * 100):.1f}%" for bar in container]

            distribution.bar_label(container, label_type='center')
            distribution.bar_label(container, labels=perc_labels, label_type='edge') 
            
        sim_plot.set(distribution)
        return distribution


    # Create a bar plot for qualitative statistics
    @reactive.calc
    def make_qualitative_stats_plot():
        req(llm_analysis_data.get())
        analysis_plot = llm_analysis_data.get()[-1].groupby('Shortcode').agg(
            Anzahl=('Shortcode', 'count'),
            ).reset_index().plot(kind='bar', x='Shortcode', y='Anzahl', alpha=1, rot=0)
        plt.gca().set_xlabel('Shortcode')
        plt.xticks(rotation=45, ha='right')
        plt.gca().set_ylabel('Anzahl')
        analysis_plot.set_axisbelow(True)
        analysis_plot.grid(color='gray', axis = 'y')
        analysis_plot.get_legend().remove()
        for container in analysis_plot.containers:
            analysis_plot.bar_label(container, label_type='edge')
        qual_plot.set(analysis_plot)
        return analysis_plot


    # Create a DataFrame for qualitative statistics
    @reactive.calc
    def make_qualitative_stats_df():
        req(llm_analysis_data.get())
        analysis_df = llm_analysis_data.get()[-1]
        analysis_df['#'] = analysis_df.reset_index().index+1
        analysis_df = analysis_df[['#', 'Lehreräußerung (kurz)', 'Shortcode']]
        qual_stats_df.set(analysis_df)
        return analysis_df        


    # Display the number of teacher turns
    @render.text
    def teacher_impulses():
        req(teacher_impulses_count.get() != None)
        return teacher_impulses_count.get()
    

    # Display the number of impulses coded
    @render.text
    def teacher_impulses_coded():
        req(analysis_llm_state.get(), analysis_state.get())
        # Count number of rows in the dataframe
        num_impulses = qual_stats_df.get().shape[0] if qual_stats_df.get() is not None else "0"
        return num_impulses
    
    
    # Display the most used code
    @render.text
    def code_most_used():
        req(analysis_llm_state.get(), analysis_state.get())
        # Find the most used code
        try:
            most_used_codes = qual_stats_df.get()['Shortcode'].mode().to_list() if not qual_stats_df.get().empty else "Kein Code verwendet"
            return ', '.join(most_used_codes)
        except:
            pass

    # Display the share of words spoken by the teacher
    @render.text
    def teacher_share():
        req(stats.get().empty == False)
        # Calculate the share of words spoken by the teacher
        total_words = stats.get()['Gesamt_Woerter'].sum()
        teacher_words = stats.get().loc[stats.get()['Sprecher'] == input.name_teacher(), 'Gesamt_Woerter'].values[0]
        share = (teacher_words / total_words * 100) if total_words > 0 else 0
        return f"{round(share, 2)} %"


    # Model Selection
    @render.ui
    def dynamic_select():
        return ui.input_select("model_select", "Wähle ein Modell", choices=select_api_choices(), selected="o1")

    # Change Model Selection
    @reactive.effect
    @reactive.event(input.model_select)
    def change_model():
        # Dictionary to map model names to their identifiers
        model_map = {
        "Llama 3": "llama3-8b-8192",
        "Llama Versatile": "llama-3.3-70b-versatile",
        "DeepSeek": "deepseek-r1-distill-llama-70b",
        "GPT-4.1 nano": "gpt-4.1-nano",
        "GPT-4.1 mini": "gpt-4.1-mini",
        "o3": "o3",
        "o1": "o1",
        "o3-mini": "o3-mini",
        "o4-mini": "o4-mini",
        "GPT-4o": "gpt-4o",
        "GPT-4o-mini": "gpt-4o-mini"
        }


        # Check if the selected model is in the model_map
        selected = input.model_select()
        if selected in model_map:
            model.set(model_map[selected])
            print(f"Model changed to: {model.get()}")


    # Analyse
    # Shared analysis function
    async def run_analysis():
        req(transcript_data.get() != None)
        # Progress bar to indicate the analysis steps
        with ui.Progress(min=1, max=4) as p:
            p.set(message="Analyse läuft", detail="Dies kann eine Weile dauern...")
            # Generate Quantitative Stats without LLM 
            num_participants.set(count_pupils(transcript_data.get())) 
            p.set(1, message="Rechnet")
            
            stats.set(dialog_stats(transcript_data.get(), input.name_teacher()))
            teacher_impulses_count.set(count_teacher_impulses(stats.get(), input.name_teacher()))
            p.set(2, message="Warte auf ChatGPT")

            # Perform LLM-Request, if Activated
            if input.llm_switch():
                req(input.codebook())
                # Call either Groq or OpenAI API based on User Selection
                if not input.api_select():
                    req(api_key_groq.get() != None)
                    llm_response = llm_analysis_groq(system_prompt.get(), user_prompt.get(), model.get(), transcript_data.get(), codebook_data.get(), Groq(api_key=api_key_groq.get()))
                else:
                    req(api_key_openai.get() != None)
                    llm_response = llm_analysis_openai(system_prompt.get(), user_prompt.get(), model.get(), transcript_data.get(), codebook_data.get(), OpenAI(api_key=api_key_openai.get()))
                
                if '"error":' in llm_response:
                    return f"❗️Fehler bei LLM-Analyse: {json.loads(llm_response)['error']}. Bitte versuche es erneut!"
                
                existing_data = llm_analysis_data.get()
                new_data = json.loads(llm_response)
                new_data_df = pd.DataFrame(new_data['analysis'], columns=['#', 'Shortcode', 'Lehreräußerung (kurz)'])
                existing_data.append(new_data_df)
                llm_analysis_data.set(list(existing_data)) # Important to Set as a List to Avoid Reactivity Issues, Due to Immutability Logic of Python!!!
                analysis_llm_state.set(True)
            p.set(4, message="Analyse abgeschlossen")
            # Mark Analysis as Completed
            analysis_state.set(True)
        # Automatically Switch to Results Tab
        ui.update_navs("main_tabs", selected="Ergebnisse")
        return "Analyse abgeschlossen!"

    # Start Analysis Button
    @render.text
    @reactive.event(input.button_analysis)
    async def start_analysis():
        return await run_analysis()

    # Update Quantiative Statistics Values
    @reactive.effect
    @reactive.event(input.button_analysis)
    def stats_values():
        req(transcript_data.get() != None)
        t_turns.set(stats.get().loc[stats.get()['Sprecher'] == input.name_teacher(), 'Anzahl_Beitraege'].values[0])
        t_turns_length.set(round(stats.get().loc[stats.get()['Sprecher'] == input.name_teacher(), 'Durchschnitt_Woerter'].values[0], 1))
        t_turns_length_mean_sd.set(round(stats.get().loc[stats.get()['Sprecher'] == input.name_teacher(), 'Median_Woerter'].values[0], 1))
        p_turns.set(stats.get().loc[stats.get()['Sprecher'] == "Schüler:innen", 'Anzahl_Beitraege'].values[0])
        p_turns_length.set(round(stats.get().loc[stats.get()['Sprecher'] == "Schüler:innen", 'Durchschnitt_Woerter'].values[0], 1))
        p_turns_length_mean_sd.set(stats.get().loc[stats.get()['Sprecher'] == "Schüler:innen", 'Median_Woerter'].values[0])


    @render.ui
    def show_report_download_button():
        req(analysis_state.get())
        return ui.download_button("download_report", "Report herunterladen", icon = icon_svg("download")),


    @render.download(filename=lambda: f"{date.today().isoformat()} - Ergebnisse Gruppe {input.name_group.get()}.docx")
    def download_report():
        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".docx")
        tmp_file.close()
        if llm_analysis_data.get():
            generate_report2(tmp_file.name, input.name_group(), input.num_pupils(), num_participants.get(), participation_rate.get(), {"num": t_turns.get(), "words": t_turns_length.get(), "mean_sd": t_turns_length_mean_sd.get()}, {"num": p_turns.get(), "words": p_turns_length.get(), "mean_sd": p_turns_length_mean_sd.get()}, sim_plot.get(), teacher_impulses_count.get(), True, qual_plot.get(), qual_stats_df.get())

        else:
            generate_report2(tmp_file.name, input.name_group(), input.num_pupils(), num_participants.get(), participation_rate.get(), {"num": t_turns.get(), "words": t_turns_length.get(), "mean_sd": t_turns_length_mean_sd.get()}, {"num": p_turns.get(), "words": p_turns_length.get(), "mean_sd": p_turns_length_mean_sd.get()}, sim_plot.get(), teacher_impulses_count.get(), llm_analysis=False)

        return tmp_file.name
    

    @reactive.effect
    @reactive.event(input.codebook)
    def process_codebook():
        file = input.codebook()
        if file is not None:
            codebook_data.set(import_file(file[0]))


    @reactive.effect
    @reactive.event(input.transcript)
    def process_transcript():
        file = input.transcript()
        if file is not None:
            transcript_data.set(import_file(file[0]))
    

    # Warnung bei fehlendem Transkript   
    @reactive.effect
    @reactive.event(input.button_analysis)
    def _():
        if transcript_data.get() == None:
            m = ui.modal(  
                "Bitte zuerst Transkript hochladen!",  
                title="Fehler",  
                easy_close=True,  
            )  
            ui.modal_show(m)  
    

    # Warnung bei fehlendem Codebuch
    @reactive.effect
    @reactive.event(input.button_analysis)
    def _():
        req(input.llm_switch())
        if codebook_data.get() == None:
            m = ui.modal(  
                "Bitte zuerst Codebuch hochladen!",  
                title="Fehler",  
                easy_close=True,  
            )  
            ui.modal_show(m)  

    # Codebuch-Vorschau anzeigen
    @render.ui
    def show_codebook_preview():
        if codebook_data.get() == None:
            return "Noch kein Codebuch hochgeladen..."
        else: 
            return ui.output_table("codebook_preview")


    # Transkript-Vorschau ausgeben
    @render.ui
    def show_transcript_preview():
        if transcript_data.get() == None:
            return "Noch kein Transkript hochgeladen..."
        else: 
            return transcript_data.get()

    # Codebook Vorschau ausgeben
    @render.table
    def codebook_preview():
        req(codebook_data.get() != None)
        return pd.DataFrame(codebook_data.get()).iloc[1:] # Erste Zeile entfernen, da sie nur die Überschriften enthält


    # ERGEBNISSE
    @reactive.effect
    @reactive.event(input.main_tabs)
    def warn_if_results_tab_clicked():
        if input.main_tabs() == "Ergebnisse" and not analysis_state.get():
            m = ui.modal(
                "Bitte zuerst die Analyse durchführen!",
                title="Noch keine Ergebnisse",
                easy_close=True,
                footer=None,
                size="2"
            )
            ui.modal_show(m)
            ui.update_navs("main_tabs", selected="Analyse")


    # Anzeige der Gruppen-ID
    @render.text
    def nameGroup():
        return input.name_group()


    # Anzeige der Klassengröße
    @render.text
    def numPupils():
        return input.num_pupils()
    

    # Anzeige der Anzahl beteiligter Schüler:innen
    @render.text
    def numParticipants():
        req(num_participants.get() != None)
        return num_participants.get()
    

    
    @render.text
    @reactive.calc
    def participationRate():
        req(num_participants.get() != None) 
        participation_rate.set(num_participants.get() / input.num_pupils() * 100)
        return f"{round(participation_rate.get(), 2)} %" 
  

    # Plot für Gesprächsverteilung
    @render.plot(alt="Gesprächsverteilung")
    def sim_stats_plot():
        if analysis_state.get() == False:
            fig, ax = plt.subplots()
            ax.text(0.5, 0.5, "Noch keine Daten", ha='center', va='center', fontsize=12)
            ax.axis('off')
            return fig
        else:
            return make_sim_stats_plot()  
    

    # Gesprächsbeiträge Lehrperson
    @render.text
    def teacher_turns():
        req(input.button_analysis(), transcript_data.get() != None)
        return stats.get().loc[stats.get()['Sprecher'] == input.name_teacher(), 'Anzahl_Beitraege'].values[0]
    

    # Länge der Gesprächsbeiträge Lehrperson
    @render.text
    def teacher_turns_length():
        req(input.button_analysis(), transcript_data.get() != None)
        return f"{round(stats.get().loc[stats.get()['Sprecher'] == input.name_teacher(), 'Durchschnitt_Woerter'].values[0], 1)} ({round(stats.get().loc[stats.get()['Sprecher'] == input.name_teacher(), 'Median_Woerter'].values[0], 1)})"
    

    # Gesprächsbeiträge Schüler:innen
    @render.text
    def pupils_turns():
        req(input.button_analysis(), transcript_data.get() != None)
        return stats.get().loc[stats.get()['Sprecher'] == "Schüler:innen", 'Anzahl_Beitraege'].values[0]
    

    # Länge der Gesprächsbeiträge Schüler:innen
    @render.text
    def pupils_turns_length():
        req(input.button_analysis(), transcript_data.get() != None)
        return f"{round(stats.get().loc[stats.get()['Sprecher'] == "Schüler:innen", 'Durchschnitt_Woerter'].values[0], 1)} ({stats.get().loc[stats.get()['Sprecher'] == "Schüler:innen", 'Median_Woerter'].values[0]
        })"


    # Plot für qualitative Statistik
    @render.plot(alt="Noch keine Daten")
    def qualitative_stats_plot():
        if not llm_analysis_data.get():
            fig, ax = plt.subplots()
            ax.text(0.5, 0.5, "Noch keine Daten", ha='center', va='center', fontsize=12)
            ax.axis('off')
            return fig
        else:
            return make_qualitative_stats_plot() 


    # Code-Legende aus Codebuch extrahieren
    @reactive.calc
    def extract_code_legend():
        req(codebook_data.get() != None)
        df = pd.DataFrame(codebook_data.get())
        legend = []
        for code in df[df.columns[0]].unique():
            legend.append(f"{code}")
        return "; ".join(legend)
    

    # Code-Legende anzeigen
    @render.ui
    def code_legend():
        return ui.markdown(f"**Legende:** {extract_code_legend()}")


    # DataFrame für qualitative Statistik
    @render.ui
    def quali_stats_df():
        if not llm_analysis_data.get():
            return ui.output_plot("placeholder")
        else:
            return ui.output_table("qualitative_stats_df")

    # Placeholder Plot, wenn noch keine Daten vorhanden sind
    @render.plot(alt="Noch keine Daten")
    def placeholder():
        fig, ax = plt.subplots()
        ax.text(0.5, 0.5, "Noch keine Daten", ha='center', va='center', fontsize=12)
        ax.axis('off')
        placeholder_plot.set(fig)
        return fig

    
    @render.plot(alt="Noch keine Daten")
    def placeholder2():
        return placeholder_plot.get()


    # DataFrame für qualitative Statistik generieren
    @render.table()
    def qualitative_stats_df():
        return make_qualitative_stats_df()


    # OPTIONEN
    # API-Key-Verwaltung
    @render.text
    def api_key_exists():
        if not input.api_select():
            a = api_key_groq.get() # for reactivity/invalidation
            return "API-Key für Groq vorhanden" if api_key_groq.get() else "Kein API-Key für Groq vorhanden. Bitte konfigurieren."
        else:
            a = api_key_openai.get() # for reactivity/invalidation
            return "API-Key für openAI vorhanden" if api_key_openai.get() else "Kein API-Key für openAI vorhanden. Bitte konfigurieren."


    # Button zum Ändern des API-Keys
    @reactive.effect
    @reactive.event(input.button_change_api_key)
    def change_api_key():
        m = ui.modal(
            ui.input_password("api_key", label=None, placeholder="API-Key eingeben"),
            ui.input_action_button("button_save_api_key", "Speichern"),
            title="API-Key ändern",
            easy_close=True,
        )
        ui.modal_show(m)

    # Speichern des API-Keys
    @reactive.effect
    @reactive.event(input.button_save_api_key)
    def save_api_key():
        req(input.api_key())
        if input.api_select():
            keyring.set_password("teach_sim_eval", "api_key_openai", input.api_key())
            api_key_openai.set(input.api_key())
        else:
            keyring.set_password("teach_sim_eval", "api_key_groq", input.api_key())
            api_key_groq.set(input.api_key())
        ui.modal_remove()   

    # Button zum Löschen des API-Keys
    @reactive.effect
    @reactive.event(input.button_delete_api_key)
    def delete_api_key():
        m = ui.modal(
            "Möchten Sie den API-Key wirklich löschen?",
            ui.input_action_button("button_confirm_delete_api_key", "Ja, löschen"),
            ui.input_action_button("button_cancel_delete_api_key", "Abbrechen"),
            title="API-Key löschen",
            easy_close=True,
        )
        ui.modal_show(m)

    # Löschens des API-Keys bestätigen
    @reactive.effect
    @reactive.event(input.button_confirm_delete_api_key)
    def confirm_delete_api_key():
        keyring.delete_password("teach_sim_eval", "api_key_openai") if input.api_select() else keyring.delete_password("teach_sim_eval", "api_key_groq")
        api_key_openai.set(None) if input.api_select() else api_key_groq.set(None)
        ui.modal_remove()

    # Löschens des API-Keys abbrechen
    @reactive.effect
    @reactive.event(input.button_cancel_delete_api_key)
    def cancel_delete_api_key():
        ui.modal_remove()


    # API-Auswahl
    @reactive.calc
    def select_api_choices():
        if input.api_select():
            return ["GPT-4.1 nano", "GPT-4.1 mini", "o3", "o1", "o3-mini", "o4-mini", "GPT-4o"]
        else:
            return ["Llama 3", "Llama Versatile", "DeepSeek"]
        

    # Warnung bei fehlendem API-Key   
    @reactive.effect
    @reactive.event(input.button_analysis)
    def _():
        req(input.llm_switch(), input.button_analysis(), transcript_data.get() != None, codebook_data.get() != None)
        if api_key_openai.get() == None and input.api_select() or api_key_groq.get() == None and not input.api_select():
            m = ui.modal(  
                "Kein API-Key vorhanden. Bitte konfigurieren!",  
                    title="Fehler",  
                    easy_close=True,  
                )
            ui.modal_show(m)
            ui.update_navs("main_tabs", selected="Optionen")  


    # System Prompt anzeigen
    @render.text()
    def system_prompt_output():
        return system_prompt.get()
    
    # Button zum Ändern des System Prompts
    @reactive.effect
    @reactive.event(input.button_change_system_prompt)
    def change_system_prompt():
        m = ui.modal(
            ui.input_text_area("system_prompt", "System-Prompt ändern", system_prompt.get(), rows=10),
            ui.input_action_button("button_save_system_prompt", "Speichern"),
            title="System-Prompt ändern",
            easy_close=True,
        )
        ui.modal_show(m)

    # Speichern des System Prompts
    @reactive.effect
    @reactive.event(input.button_save_system_prompt)
    def save_system_prompt():
        req(input.system_prompt())
        system_prompt.set(input.system_prompt())
        ui.modal_remove()   

    
    # User Prompt anzeigen
    @render.text()
    def user_prompt_output():
        return user_prompt.get()
    
    # Button zum Ändern des User Prompts
    @reactive.effect
    @reactive.event(input.button_change_user_prompt)
    def change_user_prompt():
        m = ui.modal(
            ui.input_text_area("user_prompt", "User-Prompt ändern", user_prompt.get(), rows=10),
            ui.input_action_button("button_save_user_prompt", "Speichern"),
            title="User-Prompt ändern",
            easy_close=True,
        )
        ui.modal_show(m)

    # Speichern des User Prompts
    @reactive.effect
    @reactive.event(input.button_save_user_prompt)
    def save_user_prompt():
        req(input.user_prompt())
        user_prompt.set(input.user_prompt())
        ui.modal_remove()   

# App als globales Objekt initiasieren, damit der server zugreifen kann
app = App(app_ui, server)

# Get the directory containing the current file
current_dir = Path(__file__).parent

def main():
    run_app(app)
