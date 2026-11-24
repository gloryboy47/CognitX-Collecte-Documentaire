import { useState, type FormEvent } from "react";
import { Link } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/shared/api/client";
import { useAuth } from "@/shared/hooks/useAuth";
import { StatusBadge } from "@/shared/ui/StatusBadge";
import { useToast } from "@/shared/ui/Toast";
import { CardSkeleton } from "@/shared/ui/Skeleton";
import { StatsPanel } from "@/features/stats/StatsPanel";
import styles from "./Dashboard.module.css";

interface Case {
  id: number;
  name: string;
  description: string;
  state: string;
  owner_id: number;
  created_at: string;
}

export function DashboardPage() {
  const { user } = useAuth();
  const qc = useQueryClient();
  const [showForm, setShowForm] = useState(false);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [search, setSearch] = useState("");
  const [stateFilter, setStateFilter] = useState("all");
  const { toast } = useToast();

  const { data: cases = [], isLoading } = useQuery<Case[]>({
    queryKey: ["cases"],
    queryFn: () => api.get("/cases"),
  });

  const createCase = useMutation({
    mutationFn: (body: { name: string; description: string }) =>
      api.post("/cases", body),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["cases"] });
      setShowForm(false);
      setName("");
      setDescription("");
      toast("Dossier cree avec succes", "success");
    },
  });

  const handleCreate = (e: FormEvent) => {
    e.preventDefault();
    createCase.mutate({ name, description });
  };

  return (
    <div>
      <div className={styles.header}>
        <h1 className={styles.title}>Mes dossiers</h1>
        {user?.role === "client" && (
          <button
            className={styles.createBtn}
            onClick={() => setShowForm((v) => !v)}
          >
            + Nouveau dossier
          </button>
        )}
      </div>

      {showForm && (
        <form className={styles.form} onSubmit={handleCreate}>
          <input
            className={styles.input}
            placeholder="Nom du dossier"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />
          <input
            className={styles.input}
            placeholder="Description (optionnel)"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          />
          <button className={styles.submitBtn} type="submit">
            Creer
          </button>
        </form>
      )}

      <StatsPanel />

      <div className={styles.filters}>
        <input
          className={styles.searchInput}
          placeholder="Rechercher un dossier..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <select
          className={styles.filterSelect}
          value={stateFilter}
          onChange={(e) => setStateFilter(e.target.value)}
        >
          <option value="all">Tous les etats</option>
          <option value="INCOMPLET">Incomplet</option>
          <option value="EN_COURS">En cours</option>
          <option value="A_VALIDER">A valider</option>
          <option value="VALIDE">Valide</option>
        </select>
      </div>

      {isLoading && (
        <div className={styles.grid}>
          {[1, 2, 3].map((i) => <CardSkeleton key={i} />)}
        </div>
      )}

      {!isLoading && cases.length === 0 && (
        <p className={styles.muted}>Aucun dossier pour le moment.</p>
      )}

      <div className={styles.grid}>
        {cases
          .filter((c) => {
            const matchSearch = c.name.toLowerCase().includes(search.toLowerCase()) ||
              c.description.toLowerCase().includes(search.toLowerCase());
            const matchState = stateFilter === "all" || c.state === stateFilter;
            return matchSearch && matchState;
          })
          .map((c) => (
          <Link to={`/cases/${c.id}`} key={c.id} className={styles.card}>
            <div className={styles.cardHeader}>
              <span className={styles.ref}>#{c.id}</span>
              <StatusBadge status={c.state} />
            </div>
            <h3 className={styles.company}>{c.name}</h3>
            {c.description && (
              <span className={styles.year}>{c.description}</span>
            )}
          </Link>
        ))}
      </div>
    </div>
  );
}
