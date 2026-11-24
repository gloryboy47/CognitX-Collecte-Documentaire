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
  const [sortBy, setSortBy] = useState<"recent" | "name" | "state">("recent");
  const [page, setPage] = useState(0);
  const { toast } = useToast();
  const PAGE_SIZE = 9;

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
          aria-label="Rechercher un dossier"
        />
        <select
          className={styles.filterSelect}
          value={stateFilter}
          onChange={(e) => { setStateFilter(e.target.value); setPage(0); }}
          aria-label="Filtrer par etat"
        >
          <option value="all">Tous les etats</option>
          <option value="INCOMPLET">Incomplet</option>
          <option value="EN_COURS">En cours</option>
          <option value="A_VALIDER">A valider</option>
          <option value="VALIDE">Valide</option>
        </select>
        <select
          className={styles.filterSelect}
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value as "recent" | "name" | "state")}
          aria-label="Trier par"
        >
          <option value="recent">Plus recents</option>
          <option value="name">Nom (A-Z)</option>
          <option value="state">Etat</option>
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

      {(() => {
        const filtered = cases
          .filter((c) => {
            const matchSearch = c.name.toLowerCase().includes(search.toLowerCase()) ||
              c.description.toLowerCase().includes(search.toLowerCase());
            const matchState = stateFilter === "all" || c.state === stateFilter;
            return matchSearch && matchState;
          })
          .sort((a, b) => {
            if (sortBy === "name") return a.name.localeCompare(b.name);
            if (sortBy === "state") return a.state.localeCompare(b.state);
            return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
          });
        const totalPages = Math.ceil(filtered.length / PAGE_SIZE);
        const paginated = filtered.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE);

        return (
          <>
            <div className={styles.grid}>
              {paginated.map((c) => (
                <Link to={`/cases/${c.id}`} key={c.id} className={styles.card}>
                  <div className={styles.cardHeader}>
                    <span className={styles.ref}>#{c.id}</span>
                    <StatusBadge status={c.state} />
                  </div>
                  <h3 className={styles.company}>{c.name}</h3>
                  {c.description && (
                    <span className={styles.year}>{c.description}</span>
                  )}
                  <span className={styles.date}>
                    {new Date(c.created_at).toLocaleDateString("fr-FR", {
                      day: "numeric", month: "short", year: "numeric",
                    })}
                  </span>
                </Link>
              ))}
            </div>
            {totalPages > 1 && (
              <div className={styles.pagination}>
                <button
                  className={styles.pageBtn}
                  disabled={page === 0}
                  onClick={() => setPage((p) => p - 1)}
                >
                  Precedent
                </button>
                <span className={styles.pageInfo}>
                  {page + 1} / {totalPages}
                </span>
                <button
                  className={styles.pageBtn}
                  disabled={page >= totalPages - 1}
                  onClick={() => setPage((p) => p + 1)}
                >
                  Suivant
                </button>
              </div>
            )}
          </>
        );
      })()}
    </div>
  );
}
