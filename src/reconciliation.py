from dataclasses import dataclass

from src.pitch_analysis import PitchAnalysis
from src.public_research import PublicSourceAnalysis
from src.web_research import WebsiteAnalysis


@dataclass
class EvidenceStatus:
    label: str
    status: str
    explanation: str


def contains_any(text: str, keywords: list[str]) -> bool:
    text = text.lower()
    return any(keyword in text for keyword in keywords)


def reconcile_thesis_evidence(
    pitch_analysis: PitchAnalysis,
    website_analysis: WebsiteAnalysis | None,
    supporting_source_analyses: list[PublicSourceAnalysis],
    thesis: dict,
) -> list[EvidenceStatus]:
    pitch_text = " ".join(
        [
            pitch_analysis.business_model,
            pitch_analysis.sector,
            pitch_analysis.problem,
            pitch_analysis.product,
            pitch_analysis.customer_target,
            pitch_analysis.geography,
            pitch_analysis.international_ambition,
            pitch_analysis.network_leverage,
        ]
    ).lower()

    website_text = ""

    if website_analysis:
        website_text = " ".join(
            f"{fact.field} {fact.value} {fact.quote}"
            for fact in website_analysis.facts
        ).lower()

    supporting_text = " ".join(
        f"{fact.field} {fact.value} {fact.quote}"
        for source_analysis in supporting_source_analyses
        for fact in source_analysis.facts
    ).lower()

    keyword_map = {
        "b2b_relevance": [
            "b2b",
            "entreprise",
            "entreprises",
            "industriel",
            "industriels",
            "immobilier",
            "construction",
            "promoteur",
            "bailleur",
        ],
        "international_ambition": [
            "international",
            "europe",
            "européen",
            "france",
            "allemagne",
            "royaume-uni",
            "uk",
            "london",
        ],
        "priority_theme": [
            "énergie",
            "energy",
            "climat",
            "climate",
            "carbone",
            "carbon",
            "esg",
            "ia",
            "intelligence artificielle",
            "fintech",
            "longevity",
        ],
        "industrial_transformation": [
            "industrie",
            "industriel",
            "construction",
            "immobilier",
            "opérations",
            "infrastructure",
            "décarbonation",
            "circularité",
        ],
        "network_leverage": [
            "partenariat",
            "partenariats",
            "réseau",
            "commercial",
            "go-to-market",
        ],
    }

    results = []

    for criterion in thesis["criteria"]:
        criterion_id = criterion["id"]
        label = criterion["label"]
        keywords = keyword_map.get(criterion_id, [])

        pitch_has_evidence = contains_any(pitch_text, keywords)
        website_has_evidence = contains_any(website_text, keywords)
        supporting_has_evidence = contains_any(supporting_text, keywords)

        if criterion_id == "network_leverage":
            pitch_has_evidence = (
                pitch_analysis.network_leverage.strip().lower()
                != "non renseigné"
            )

        if pitch_has_evidence and website_has_evidence and supporting_has_evidence:
            status = "Triangulé"
            explanation = (
                "Le critère est documenté dans le pitch, sur le site officiel "
                "et dans au moins une source publique complémentaire."
            )
        elif supporting_has_evidence and (
            pitch_has_evidence or website_has_evidence
        ):
            status = "Corroboré par une source complémentaire"
            explanation = (
                "Le critère est documenté par l'entreprise et retrouvé dans "
                "au moins une source publique complémentaire."
            )
        elif pitch_has_evidence and website_has_evidence:
            status = "Corroboré par le site officiel"
            explanation = (
                "Le critère apparaît dans le pitch et sur le site officiel. "
                "Ces deux sources restent liées à l'entreprise."
            )
        elif supporting_has_evidence:
            status = "Trouvé dans une source complémentaire"
            explanation = (
                "Le critère est mentionné dans une source publique "
                "complémentaire, mais n'est pas clairement documenté ailleurs."
            )
        elif pitch_has_evidence:
            status = "Déclaré dans le pitch"
            explanation = (
                "Le critère apparaît dans le pitch, mais n'a pas été "
                "corroboré par une autre source."
            )
        elif website_has_evidence:
            status = "Trouvé sur le site officiel"
            explanation = (
                "Le critère apparaît sur le site officiel, mais pas "
                "explicitement dans le pitch."
            )
        else:
            status = "Non documenté"
            explanation = (
                "Aucune preuve explicite n'a été identifiée dans les "
                "sources analysées."
            )

        results.append(
            EvidenceStatus(
                label=label,
                status=status,
                explanation=explanation,
            )
        )

    return results