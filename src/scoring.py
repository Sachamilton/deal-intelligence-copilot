import re
from dataclasses import dataclass

from src.pitch_analysis import PitchAnalysis
from src.web_research import WebsiteAnalysis


@dataclass
class CriterionScore:
    label: str
    points: int
    maximum: int
    explanation: str
    sources: list[str]
    matched_terms: list[str]


@dataclass
class ScoreResult:
    total: int
    maximum: int
    criteria: list[CriterionScore]


def matching_terms(text: str, keywords: list[str]) -> list[str]:
    normalized_text = text.lower()
    matches = []

    for keyword in keywords:
        pattern = rf"(?<!\w){re.escape(keyword.lower())}(?!\w)"

        if re.search(pattern, normalized_text):
            matches.append(keyword)

    return matches


def score_thesis_fit(
    analysis: PitchAnalysis,
    thesis: dict,
    website_analysis: WebsiteAnalysis | None = None,
) -> ScoreResult:
    pitch_text = " ".join(
        [
            analysis.business_model,
            analysis.sector,
            analysis.problem,
            analysis.product,
            analysis.customer_target,
            analysis.geography,
            analysis.international_ambition,
            analysis.network_leverage,
        ]
    ).lower()

    website_text = ""

    if website_analysis:
        website_text = " ".join(
            f"{fact.field} {fact.value} {fact.quote}"
            for fact in website_analysis.facts
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
            "global",
            "global-first",
            "europe",
            "européen",
            "allemagne",
            "royaume-uni",
            "uk",
            "london",
        ],
        "priority_theme": [
            "intelligence artificielle",
            "ai",
            "ia",
            "énergie",
            "energy",
            "climat",
            "climate",
            "carbone",
            "carbon",
            "esg",
            "fintech",
            "longevity",
            "digital",
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

    criterion_scores = []

    for criterion in thesis["criteria"]:
        criterion_id = criterion["id"]
        label = criterion["label"]
        maximum = criterion["weight"]
        keywords = keyword_map.get(criterion_id, [])

        pitch_terms = matching_terms(pitch_text, keywords)
        website_terms = matching_terms(website_text, keywords)

        pitch_has_evidence = bool(pitch_terms)
        website_has_evidence = bool(website_terms)

        if criterion_id == "network_leverage":
            network_declared = (
                analysis.network_leverage.strip().lower() != "non renseigné"
            )

            if network_declared:
                pitch_has_evidence = True

                if not pitch_terms:
                    pitch_terms = ["besoin de soutien du réseau déclaré"]

        sources = []

        if pitch_has_evidence:
            sources.append("Pitch")

        if website_has_evidence:
            sources.append("Site officiel")

        matched_terms = list(dict.fromkeys(pitch_terms + website_terms))

        if sources:
            points = maximum
            explanation = (
                "Points attribués car le critère est documenté dans : "
                + ", ".join(sources)
                + "."
            )
        else:
            points = 0
            explanation = (
                "Aucun élément explicite correspondant à ce critère "
                "n'a été détecté dans le pitch ou le site officiel."
            )

        criterion_scores.append(
            CriterionScore(
                label=label,
                points=points,
                maximum=maximum,
                explanation=explanation,
                sources=sources,
                matched_terms=matched_terms,
            )
        )

    return ScoreResult(
        total=sum(item.points for item in criterion_scores),
        maximum=sum(item.maximum for item in criterion_scores),
        criteria=criterion_scores,
    )