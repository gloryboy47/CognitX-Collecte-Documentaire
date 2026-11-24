import { useState } from "react";
import { useParams, Link } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/shared/api/client";
import { useAuth } from "@/shared/hooks/useAuth";
import { StatusBadge } from "@/shared/ui/StatusBadge";
import { useToast } from "@/shared/ui/Toast";
import styles from "./Review.module.css";

interface Prediction {
  id: number;
  predicted_class: string;
  confidence: number;
  probabilities: string | null;
  top_features: string | null;
  model_version: string | null;
  created_at: string;
}

interface Decision {
  id: number;
  actor: string;
  decision: string;
  comment: string;
  created_at: string;
}

interface ExtractedField {
  id: number;
  field_name: string;
  field_value: string | null;
  source: string;
}

interface ValidationCheck {
  id: number;
  rule_name: string;
  passed: boolean;
  message: string | null;
}

interface DocumentDetail {
  id: number;
  case_id: number;
  original_filename: string;
  file_size: number | null;
  state: string;
  ocr_text: string | null;
  ocr_confidence: number | null;
  predictions: Prediction[];
  decisions: Decision[];
  extracted_fields: ExtractedField[];
  validation_checks: ValidationCheck[];
}

const CLASS_LABELS: Record<string, string> = {
  facture: "Facture",
  fiche_de_paie: "Fiche de paie",
  contrat: "Contrat",
  compte_rendu_rd: "Compte-rendu R&D",
  autre: "Autre",
};

const FIELD_LABELS: Record<string, string> = {
  numero_facture: "N° facture",
  montant_ht: "Montant HT",
  montant_ttc: "Montant TTC",
  date_facture: "Date facture",
  tva: "TVA (%)",
  salaire_brut: "Salaire brut",
  salaire_net: "Salaire net",
  periode: "Periode",
  employeur: "Employeur",
  type_contrat: "Type contrat",
  date_debut: "Date debut",
  duree: "Duree",
  date_reunion: "Date reunion",
  projet: "Projet",
  participants: "Participants",
};

export function ReviewPage() {
  const { docId } = useParams<{ docId: string }>();
  const { user } = useAuth();
  const qc = useQueryClient();
  const [comment, setComment] = useState("");
  const { toast } = useToast();

  const { data: doc, isLoading } = useQuery<DocumentDetail>({
    queryKey: ["document", docId],
    queryFn: () => api.get(`/documents/${docId}`),
  });

  const decide = useMutation({
    mutationFn: (decision: string) =>
      api.post(`/documents/${docId}/decide`, { decision, comment }),
    onSuccess: (_data, decision) => {
      qc.invalidateQueries({ queryKey: ["document", docId] });
      qc.invalidateQueries({ queryKey: ["case"] });
      toast(
        decision === "confirme" ? "Document confirme" : "Document rejete",
        decision === "confirme" ? "success" : "info",
      );
    },
  });

  if (isLoading) return <p className={styles.muted}>Chargement...</p>;
  if (!doc) return <p className={styles.muted}>Document introuvable.</p>;

  const prediction = doc.predictions[doc.predictions.length - 1];
  const canDecide =
    user?.role === "consultant" &&
    ["PROPOSE_CONFORME", "PROPOSE_REJET", "A_REVOIR"].includes(doc.state);

  let probabilities: Record<string, number> = {};
  if (prediction?.probabilities) {
    try {
      probabilities = JSON.parse(prediction.probabilities);
    } catch {
      /* ignore */
    }
  }

  return (
    <div>
      <Link to={`/cases/${doc.case_id}`} className={styles.back}>
        &larr; Retour au dossier
      </Link>

      <div className={styles.header}>
        <h1 className={styles.title}>{doc.original_filename}</h1>
        <StatusBadge status={doc.state} />
      </div>

      {prediction && (
        <section className={styles.section}>
          <h2 className={styles.sectionTitle}>Classification IA</h2>
          <div className={styles.card}>
            <div className={styles.row}>
              <span className={styles.label}>Classe predite</span>
              <span className={styles.value}>
                {CLASS_LABELS[prediction.predicted_class] ??
                  prediction.predicted_class}
              </span>
            </div>
            <div className={styles.row}>
              <span className={styles.label}>Confiance</span>
              <span className={styles.value}>
                {(prediction.confidence * 100).toFixed(1)}%
              </span>
            </div>
            {prediction.top_features && (
              <div className={styles.row}>
                <span className={styles.label}>Mots-cles influents</span>
                <span className={styles.value}>{prediction.top_features}</span>
              </div>
            )}
            <div className={styles.row}>
              <span className={styles.label}>Modele</span>
              <span className={styles.valueMuted}>
                {prediction.model_version}
              </span>
            </div>

            {Object.keys(probabilities).length > 0 && (
              <div className={styles.probas}>
                <span className={styles.label}>Probabilites</span>
                {Object.entries(probabilities)
                  .sort(([, a], [, b]) => b - a)
                  .map(([cls, p]) => (
                    <div key={cls} className={styles.probaRow}>
                      <span className={styles.probaLabel}>
                        {CLASS_LABELS[cls] ?? cls}
                      </span>
                      <div className={styles.probaBar}>
                        <div
                          className={styles.probaFill}
                          style={{ width: `${(p * 100).toFixed(1)}%` }}
                        />
                      </div>
                      <span className={styles.probaVal}>
                        {(p * 100).toFixed(1)}%
                      </span>
                    </div>
                  ))}
              </div>
            )}
          </div>
        </section>
      )}

      {doc.extracted_fields && doc.extracted_fields.length > 0 && (
        <section className={styles.section}>
          <h2 className={styles.sectionTitle}>Champs extraits</h2>
          <div className={styles.card}>
            {doc.extracted_fields.map((f) => (
              <div key={f.id} className={styles.row}>
                <span className={styles.label}>{FIELD_LABELS[f.field_name] ?? f.field_name}</span>
                <span className={styles.value}>{f.field_value}</span>
              </div>
            ))}
          </div>
        </section>
      )}

      {doc.validation_checks && doc.validation_checks.length > 0 && (
        <section className={styles.section}>
          <h2 className={styles.sectionTitle}>Validation metier</h2>
          <div className={styles.card}>
            {doc.validation_checks.map((c) => (
              <div key={c.id} className={styles.checkRow}>
                <span className={c.passed ? styles.checkPass : styles.checkFail}>
                  {c.passed ? "✓" : "✗"}
                </span>
                <span className={styles.checkMessage}>{c.message}</span>
              </div>
            ))}
          </div>
        </section>
      )}

      {doc.ocr_text && (
        <section className={styles.section}>
          <h2 className={styles.sectionTitle}>
            Texte OCR
            {doc.ocr_confidence != null &&
              ` (confiance: ${(doc.ocr_confidence * 100).toFixed(0)}%)`}
          </h2>
          <pre className={styles.ocrText}>{doc.ocr_text.slice(0, 2000)}</pre>
        </section>
      )}

      {doc.decisions.length > 0 && (
        <section className={styles.section}>
          <h2 className={styles.sectionTitle}>Decisions</h2>
          {doc.decisions.map((d) => (
            <div key={d.id} className={styles.decisionCard}>
              <strong>{d.decision}</strong> par {d.actor}
              {d.comment && <p className={styles.decisionComment}>{d.comment}</p>}
            </div>
          ))}
        </section>
      )}

      {canDecide && (
        <section className={styles.section}>
          <h2 className={styles.sectionTitle}>Decision du consultant</h2>
          <p className={styles.hint}>
            L'IA propose, l'expert decide.
          </p>
          <textarea
            className={styles.textarea}
            placeholder="Commentaire (optionnel)"
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            rows={3}
          />
          <div className={styles.actions}>
            <button
              className={styles.confirmBtn}
              onClick={() => decide.mutate("confirme")}
              disabled={decide.isPending}
            >
              Confirmer
            </button>
            <button
              className={styles.rejectBtn}
              onClick={() => decide.mutate("rejete")}
              disabled={decide.isPending}
            >
              Rejeter
            </button>
          </div>
        </section>
      )}
    </div>
  );
}
