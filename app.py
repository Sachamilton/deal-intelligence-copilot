import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import streamlit as st

from src.pitch_analysis import analyse_pitch
from src.scoring import score_thesis_fit
from src.web_research import analyse_website
from src.reconciliation import reconcile_thesis_evidence
from src.public_research import analyse_public_sources

BASE_DIR = Path(__file__).parent
THESIS_PATH = BASE_DIR / "config" / "thesis.json"
EXAMPLE_PITCH_PATH = BASE_DIR / "fixtures" / "pitch_greenledger.txt"


def load_json(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def load_text(path):
    with open(path, "r", encoding="utf-8") as file:
        return file.read()


def show_list(items):
    if not items:
        st.write("Non renseigné")
        return

    for item in items:
        st.write(f"- {item}")


st.set_page_config(
    page_title="Deal Intelligence Copilot",
    page_icon="🔎",
    layout="wide",
)

thesis = load_json(THESIS_PATH)
example_pitch = load_text(EXAMPLE_PITCH_PATH)

st.title("Deal Intelligence Copilot")
st.caption(
    "Pré-analyse VC assistée par IA - validation humaine obligatoire."
)

st.info(
    "Ce prototype analyse des informations publiques ou synthétiques. "
    "Il ne prend aucune décision d'investissement."
)

left_column, right_column = st.columns([2, 1])

with left_column:
    st.subheader("Nouvelle opportunité")

    with st.form("deal_form"):
        company_name = st.text_input(
            "Nom de la startup",
            value="GreenLedger",
        )

        website = st.text_input(
            "Site officiel (recommandé)",
            placeholder="https://www.example.com",
        )

        supporting_urls = st.text_area(
            "Sources publiques complémentaires (facultatif)",
            placeholder=(
                "Une URL par ligne : article de presse, communiqué, fiche de base "
                "de données publique, etc. Maximum 3 sources."
            ),
            help=(
                "Ces sources seront distinguées du site officiel et serviront à "
                "corroborer ou contredire les informations déclarées."
            ),
        )

        founder_name = st.text_input(
            "Nom du ou de la fondatrice (facultatif)",
            value="Clara Martin",
        )

        pitch = st.text_area(
            "E-mail ou pitch entrant",
            value=example_pitch,
            height=350,
        )

        submitted = st.form_submit_button("Créer le deal brief")

    if submitted:
        if not pitch.strip():
            st.error("Merci de renseigner un pitch avant de lancer l'analyse.")

        else:
            try:
                with st.spinner("Le copilot analyse le pitch et fait une recherche web..."):
                    analysis = analyse_pitch(pitch)

                    website_analysis = None
                    supporting_source_analyses = []
                    research_warnings = []

                    with ThreadPoolExecutor(max_workers=2) as executor:
                        website_future = None
                        sources_future = None

                        if website.strip():
                            website_future = executor.submit(analyse_website, website)

                        if supporting_urls.strip():
                            sources_future = executor.submit(
                                analyse_public_sources,
                                supporting_urls,
                            )

                    if website_future:
                        try:
                            website_analysis = website_future.result()
                        except Exception as error:
                            research_warnings.append(
                                f"Le site officiel n'a pas pu être analysé : {error}"
                            )

                    if sources_future:
                        try:
                            supporting_source_analyses = sources_future.result()
                        except Exception as error:
                            research_warnings.append(
                                f"Les sources complémentaires n'ont pas pu être analysées : {error}"
                            )

                    score_result = score_thesis_fit(
                        analysis,
                        thesis,
                        website_analysis,
                    )
                    
                    evidence_statuses = reconcile_thesis_evidence(
                        analysis,
                        website_analysis,
                        supporting_source_analyses,
                        thesis,
                    )

            except Exception as error:
                st.error(
                    "L'analyse n'a pas pu être réalisée. "
                    f"Détail technique : {error}"
                )

            else:
                if website_analysis:
                    st.success(
                        "Pitch analysé. Le score et le niveau de confiance intègrent toutes les sources ayant pu être analysées : pitch, site officiel et sources publiques complémentaires."
                    )
                else:
                    st.success("Pitch analysé. Tous les faits ci-dessous proviennent du pitch.")

                for warning in research_warnings:
                    st.warning(warning)
                
                st.subheader("Adéquation préliminaire à la thèse")

                score_column, explanation_column = st.columns([1, 2])

                with score_column:
                    st.metric(
                        "Thesis fit score",
                        f"{score_result.total} / {score_result.maximum}",
                    )

                with explanation_column:
                    st.caption(
                        "Ce score mesure uniquement la correspondance avec "
                        "la thèse configurée. Il ne constitue pas une "
                        "recommandation d'investissement."
                    )

                st.subheader("Justification du score")

                score_rows = []

                for criterion_score in score_result.criteria:
                    score_rows.append(
                        {
                            "Critère": criterion_score.label,
                            "Score": (  
                                f"{criterion_score.points}"
                                f"/{criterion_score.maximum}"
                            ),
                            "Justification": criterion_score.explanation,
                            "Sources utilisées": (
                                ", ".join(criterion_score.sources)
                                if criterion_score.sources
                                else "Aucune"
                            ),
                            "Éléments détectés": (
                                ", ".join(criterion_score.matched_terms)
                                if criterion_score.matched_terms
                                else "Aucun"
                            ),
                        }
                    )

                st.dataframe(
                    score_rows,
                    hide_index=True,
                    width="stretch",
                )
                st.subheader("Niveau de confiance des critères")

                for evidence_status in evidence_statuses:
                    st.write(
                        f"**{evidence_status.label} : "
                        f"{evidence_status.status}**"
                    )
                    st.caption(evidence_status.explanation)

                st.subheader("Fiche de pré-qualification")

                first_column, second_column = st.columns(2)

                with first_column:
                    st.write(f"**Startup :** {analysis.company_name}")
                    st.write(f"**Fondatrice / fondateur :** {analysis.founder_name}")
                    st.write(f"**Modèle :** {analysis.business_model}")
                    st.write(f"**Secteur :** {analysis.sector}")
                    st.write(f"**Client cible :** {analysis.customer_target}")
                    st.write(f"**Géographie :** {analysis.geography}")
                    st.write(f"**Stade :** {analysis.funding_stage}")
                    st.write(f"**Montant recherché :** {analysis.fundraising_amount}")

                with second_column:
                    st.write("**Problème identifié**")
                    st.write(analysis.problem)

                    st.write("**Produit**")
                    st.write(analysis.product)

                    st.write("**Ambition internationale**")
                    st.write(analysis.international_ambition)

                    st.write("**Valeur potentielle du réseau**")
                    st.write(analysis.network_leverage)

                st.write("**Traction déclarée**")
                show_list(analysis.traction)

                st.write("**Équipe déclarée**")
                show_list(analysis.team)

                st.write("**Informations à demander**")
                show_list(analysis.missing_information)

                st.subheader("Preuves dans le pitch")
                st.caption(
                    "Chaque élément ci-dessous est une déclaration du ou de la fondatrice. "
                    "Aucune vérification web n'a encore été effectuée."
                )

                evidence_rows = [
                    {
                        "Champ": evidence.field,
                        "Extrait du pitch": evidence.quote,
                        "Type de source": "Déclaration du fondateur",
                    }
                    for evidence in analysis.evidence
                ]

                if evidence_rows:
                    st.dataframe(
                        evidence_rows,
                        hide_index=True,
                        use_container_width=True,
                    )
                else:
                    st.write("Aucune citation n'a été extraite.")
                    st.subheader("Enrichissement web public")

                if website_analysis is None:
                    st.caption(
                        "Aucun site officiel n'a été renseigné : "
                        "la recherche web a été ignorée."
                    )

                else:
                    st.caption(
                        "Les faits ci-dessous proviennent du site officiel. "
                        "Ils restent des déclarations de l'entreprise et "
                        "doivent être vérifiés."
                    )

                    st.markdown(
                        f"[Ouvrir la source analysée]({website_analysis.source_url})"
                    )

                    web_rows = [
                        {
                            "Champ": fact.field,
                            "Information publique": fact.value,
                            "Extrait du site": fact.quote,
                        }
                        for fact in website_analysis.facts
                    ]

                    if web_rows:
                        st.dataframe(
                            web_rows,
                            hide_index=True,
                            width="stretch",
                        )
                    else:
                        st.write(
                            "Aucun fait pertinent n'a été identifié sur cette page."
                        )

                    if website_analysis.limitations:
                        st.write("**Limites de cette recherche**")
                        show_list(website_analysis.limitations)

                    if supporting_source_analyses:
                        st.subheader("Sources publiques complémentaires")
                        st.caption(
                            "Ces sources sont distinctes du site officiel. "
                            "Elles servent à compléter ou à nuancer les informations déclarées."
                        )

                        for source_analysis in supporting_source_analyses:
                            with st.expander(
                                f"{source_analysis.source_type} — {source_analysis.source_url}"
                            ):
                                source_rows = [
                                    {
                                        "Champ": fact.field,
                                        "Valeur": fact.value,
                                        "Extrait cité": fact.quote,
                                    }
                                    for fact in source_analysis.facts
                                ]

                                if source_rows:
                                    st.dataframe(
                                        source_rows,
                                        hide_index=True,
                                        width="stretch",
                                    )
                                else:
                                    st.write("Aucun fait pertinent n'a été extrait de cette source.")

                                if source_analysis.limitations:
                                    st.write("**Limites de cette source**")

                                    for limitation in source_analysis.limitations:
                                        st.write(f"- {limitation}")

with right_column:
    st.subheader("Thèse utilisée")
    st.write(thesis["name"])
    st.caption(thesis["source_note"])

    st.write("**Critères d'adéquation**")
    for criterion in thesis["criteria"]:
        st.write(
            f"- **{criterion['label']}** "
            f"({criterion['weight']} points)"
        )

    st.caption("Score maximal : 10 points")
