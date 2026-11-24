import { useQuery } from "@tanstack/react-query";
import { api } from "@/shared/api/client";
import styles from "./Stats.module.css";

interface Stats {
  total_documents: number;
  total_cases: number;
  documents_par_statut: Record<string, number>;
  predictions_par_classe: Record<string, number>;
  confiance_moyenne: number;
  haute_confiance: number;
  basse_confiance: number;
  confirmes: number;
  rejetes: number;
  en_attente: number;
}

const CLASS_LABELS: Record<string, string> = {
  facture: "Factures",
  fiche_de_paie: "Fiches de paie",
  contrat: "Contrats",
  compte_rendu_rd: "CR R&D",
  autre: "Autres",
};

export function StatsPanel() {
  const { data: stats } = useQuery<Stats>({
    queryKey: ["stats"],
    queryFn: () => api.get("/stats"),
    refetchInterval: 10000,
  });

  if (!stats || stats.total_documents === 0) return null;

  const pctConfiance = Math.round(stats.confiance_moyenne * 100);
  const totalDecided = stats.confirmes + stats.rejetes;
  const tauxConformite = totalDecided > 0 ? Math.round((stats.confirmes / totalDecided) * 100) : 0;

  return (
    <div className={styles.panel}>
      <h2 className={styles.title}>Metriques IA</h2>

      <div className={styles.tiles}>
        <div className={styles.tile}>
          <span className={styles.tileValue}>{stats.total_documents}</span>
          <span className={styles.tileLabel}>Documents</span>
        </div>
        <div className={styles.tile}>
          <span className={styles.tileValue}>{stats.total_cases}</span>
          <span className={styles.tileLabel}>Dossiers</span>
        </div>
        <div className={styles.tile}>
          <span className={styles.tileValue}>{pctConfiance}%</span>
          <span className={styles.tileLabel}>Confiance moy.</span>
        </div>
        <div className={styles.tile}>
          <span className={styles.tileValue}>{stats.haute_confiance}</span>
          <span className={styles.tileLabel}>Haute conf.</span>
        </div>
      </div>

      <div className={styles.tiles}>
        <div className={styles.tile}>
          <span className={styles.tileValue}>{stats.en_attente}</span>
          <span className={styles.tileLabel}>En attente</span>
        </div>
        <div className={styles.tile}>
          <span className={styles.tileValue}>{stats.confirmes}</span>
          <span className={styles.tileLabel}>Confirmes</span>
        </div>
        <div className={styles.tile}>
          <span className={styles.tileValue}>{stats.rejetes}</span>
          <span className={styles.tileLabel}>Rejetes</span>
        </div>
        <div className={styles.tile}>
          <span className={styles.tileValue}>{totalDecided > 0 ? `${tauxConformite}%` : "-"}</span>
          <span className={styles.tileLabel}>Taux conformite</span>
        </div>
      </div>

      {Object.keys(stats.predictions_par_classe).length > 0 && (
        <div className={styles.section}>
          <h3 className={styles.sectionTitle}>Classification IA</h3>
          <div className={styles.bars}>
            {Object.entries(stats.predictions_par_classe).map(([cls, count]) => {
              const max = Math.max(...Object.values(stats.predictions_par_classe));
              const pct = max > 0 ? (count / max) * 100 : 0;
              return (
                <div key={cls} className={styles.barRow}>
                  <span className={styles.barLabel}>
                    {CLASS_LABELS[cls] || cls}
                  </span>
                  <div className={styles.barTrack}>
                    <div
                      className={styles.barFill}
                      style={{ width: `${pct}%` }}
                    />
                  </div>
                  <span className={styles.barCount}>{count}</span>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {totalDecided > 0 && (
        <div className={styles.section}>
          <h3 className={styles.sectionTitle}>Taux de conformite</h3>
          <div className={styles.barTrack}>
            <div
              className={styles.barFillSuccess}
              style={{ width: `${tauxConformite}%` }}
            />
          </div>
          <div className={styles.decisions}>
            <span className={styles.decisionConfirme}>
              {stats.confirmes} confirmes ({tauxConformite}%)
            </span>
            <span className={styles.decisionRejete}>
              {stats.rejetes} rejetes ({100 - tauxConformite}%)
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
