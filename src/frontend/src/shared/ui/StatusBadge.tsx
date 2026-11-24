import styles from "./StatusBadge.module.css";

const LABELS: Record<string, string> = {
  DEPOSE: "Depose",
  EN_LECTURE: "Lecture OCR",
  EN_ANALYSE: "Analyse IA",
  PROPOSE_CONFORME: "Conforme (IA)",
  PROPOSE_REJET: "Rejet (IA)",
  A_REVOIR: "A revoir",
  CONFIRME: "Confirme",
  REJETE: "Rejete",
  INCOMPLET: "Incomplet",
  EN_COURS: "En cours",
  A_VALIDER: "A valider",
  VALIDE: "Valide",
};

const VARIANT: Record<string, string> = {
  DEPOSE: "neutral",
  EN_LECTURE: "info",
  EN_ANALYSE: "info",
  PROPOSE_CONFORME: "success",
  PROPOSE_REJET: "warning",
  A_REVOIR: "warning",
  CONFIRME: "success",
  REJETE: "danger",
  INCOMPLET: "warning",
  EN_COURS: "info",
  A_VALIDER: "warning",
  VALIDE: "success",
};

export function StatusBadge({ status }: { status: string }) {
  const label = LABELS[status] ?? status;
  const variant = VARIANT[status] ?? "neutral";
  return <span className={`${styles.badge} ${styles[variant]}`}>{label}</span>;
}
