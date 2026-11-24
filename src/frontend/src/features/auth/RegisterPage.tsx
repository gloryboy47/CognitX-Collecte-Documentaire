import { useState, type FormEvent } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "@/shared/hooks/useAuth";
import styles from "./AuthForm.module.css";

export function RegisterPage() {
  const { register } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [role, setRole] = useState<"client" | "consultant">("client");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await register(email, password, fullName, role);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Erreur d'inscription");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.page}>
      <form className={styles.card} onSubmit={handleSubmit}>
        <h1 className={styles.title}>Inscription</h1>
        <p className={styles.subtitle}>Creer un compte CognitX</p>

        <div className={styles.field}>
          <label className={styles.label}>Nom complet</label>
          <input
            className={styles.input}
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            required
          />
        </div>

        <div className={styles.field}>
          <label className={styles.label}>Email</label>
          <input
            className={styles.input}
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </div>

        <div className={styles.field}>
          <label className={styles.label}>Mot de passe</label>
          <input
            className={styles.input}
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            minLength={6}
          />
        </div>

        <div className={styles.field}>
          <label className={styles.label}>Role</label>
          <select
            className={styles.select}
            value={role}
            onChange={(e) => setRole(e.target.value as "client" | "consultant")}
          >
            <option value="client">Client</option>
            <option value="consultant">Consultant</option>
          </select>
        </div>

        {error && <p className={styles.error}>{error}</p>}

        <button className={styles.btn} type="submit" disabled={loading}>
          {loading ? "Inscription..." : "S'inscrire"}
        </button>

        <Link to="/login" className={styles.link}>
          Deja un compte ? Se connecter
        </Link>
      </form>
    </div>
  );
}
