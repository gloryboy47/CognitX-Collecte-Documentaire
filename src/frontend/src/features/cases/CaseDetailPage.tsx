import { useState } from "react";
import { useParams, Link } from "react-router-dom";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/shared/api/client";
import { useAuth } from "@/shared/hooks/useAuth";
import { StatusBadge } from "@/shared/ui/StatusBadge";
import { TableSkeleton } from "@/shared/ui/Skeleton";
import { UploadZone } from "@/features/documents/UploadZone";
import styles from "./CaseDetail.module.css";

interface Document {
  id: number;
  case_id: number;
  original_filename: string;
  file_size: number | null;
  state: string;
  created_at: string;
}

interface CaseDetail {
  id: number;
  name: string;
  description: string;
  state: string;
  owner_id: number;
  created_at: string;
  documents: Document[];
  checklist: Requirement[];
}

interface Requirement {
  code: string;
  label: string;
  status: "FOURNI" | "A_VALIDER" | "A_REVOIR" | "REJETE" | "MANQUANT";
}

export function CaseDetailPage() {
  const { caseId } = useParams<{ caseId: string }>();
  const { user } = useAuth();
  const qc = useQueryClient();
  const [exportError, setExportError] = useState("");

  const { data: caseData, isLoading } = useQuery<CaseDetail>({
    queryKey: ["case", caseId],
    queryFn: () => api.get(`/cases/${caseId}`),
    refetchInterval: 5000,
  });

  const handleExport = async () => {
    setExportError("");
    try {
      await api.download(`/export/cases/${caseId}/csv`, `dossier_${caseId}.csv`);
    } catch (e) {
      setExportError(e instanceof Error ? e.message : "Export impossible");
    }
  };

  if (isLoading) return <TableSkeleton rows={5} />;
  if (!caseData) return <p className={styles.muted}>Dossier introuvable.</p>;

  const canUpload = user?.role === "client" || user?.role === "consultant";

  return (
    <div>
      <Link to="/" className={styles.back}>
        &larr; Retour aux dossiers
      </Link>

      <div className={styles.header}>
        <div>
          <h1 className={styles.title}>{caseData.name}</h1>
          {caseData.description && (
            <p className={styles.desc}>{caseData.description}</p>
          )}
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
          <StatusBadge status={caseData.state} />
          {caseData.documents.length > 0 && (
            <button
              type="button"
              className={styles.exportBtn}
              onClick={handleExport}
            >
              Export CSV
            </button>
          )}
        </div>
      </div>

      {exportError && <p className={styles.errorText}>{exportError}</p>}

      <h2 className={styles.sectionTitle}>
        Pieces attendues (
        {caseData.checklist.filter((r) => r.status === "FOURNI").length}/
        {caseData.checklist.length} validees)
      </h2>
      <ul className={styles.checklist}>
        {caseData.checklist.map((r) => (
          <li key={r.code} className={styles.checkItem}>
            <span>{r.label}</span>
            <StatusBadge status={r.status} />
          </li>
        ))}
      </ul>

      {canUpload && (
        <UploadZone
          caseId={Number(caseId)}
          onUploaded={() =>
            qc.invalidateQueries({ queryKey: ["case", caseId] })
          }
        />
      )}

      <h2 className={styles.sectionTitle}>
        Documents ({caseData.documents.length})
      </h2>

      {caseData.documents.length > 0 && (
        <div className={styles.docStats}>
          {(() => {
            const counts: Record<string, number> = {};
            for (const d of caseData.documents) {
              counts[d.state] = (counts[d.state] || 0) + 1;
            }
            return Object.entries(counts).map(([state, count]) => (
              <span key={state} className={styles.docStatBadge}>
                <StatusBadge status={state} /> {count}
              </span>
            ));
          })()}
        </div>
      )}

      {caseData.documents.length === 0 ? (
        <p className={styles.muted}>Aucun document depose.</p>
      ) : (
        <div className={styles.tableWrap}>
        <table className={styles.table}>
          <thead>
            <tr>
              <th>Fichier</th>
              <th>Taille</th>
              <th>Statut</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {caseData.documents.map((doc) => (
              <tr key={doc.id}>
                <td className={styles.filename}>{doc.original_filename}</td>
                <td className={styles.size}>
                  {doc.file_size
                    ? `${(doc.file_size / 1024).toFixed(0)} Ko`
                    : "-"}
                </td>
                <td>
                  <StatusBadge status={doc.state} />
                </td>
                <td>
                  {["PROPOSE_CONFORME", "PROPOSE_REJET", "A_REVOIR"].includes(
                    doc.state,
                  ) ? (
                    user?.role === "consultant" ? (
                      <Link
                        to={`/documents/${doc.id}/review`}
                        className={styles.reviewLink}
                      >
                        Revoir
                      </Link>
                    ) : (
                      <Link
                        to={`/documents/${doc.id}/review`}
                        className={styles.viewLink}
                      >
                        Voir
                      </Link>
                    )
                  ) : ["CONFIRME", "REJETE"].includes(doc.state) ? (
                    <Link
                      to={`/documents/${doc.id}/review`}
                      className={styles.viewLink}
                    >
                      Voir
                    </Link>
                  ) : (
                    <span className={styles.muted}>En cours...</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        </div>
      )}
    </div>
  );
}
