export type RiskLevel = "contest" | "review" | "gather";

export interface Recommendation {
  label: string;
  level: RiskLevel;
  reason: string;
}

export function getRecommendation(winProb: number | null | undefined): Recommendation {
  if (winProb === null || winProb === undefined) {
    return { label: "UNKNOWN", level: "gather", reason: "No win probability available." };
  }
  if (winProb >= 0.75) {
    return {
      label: "CONTEST",
      level: "contest",
      reason: "Strong evidence signal — good candidate to formally contest.",
    };
  }
  if (winProb >= 0.45) {
    return {
      label: "MANUAL REVIEW",
      level: "review",
      reason: "Evidence is currently insufficient for automatic contest submission.",
    };
  }
  return {
    label: "GATHER MORE EVIDENCE",
    level: "gather",
    reason: "Low win probability — consider strengthening evidence before contesting, or accept the loss.",
  };
}