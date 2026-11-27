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
  const [inviteCode, setInviteCode] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const passwordStrength = (() => {
    if (password.length === 0) return { label: "", color: "", width: "0%" };
    if (password.length < 6) return { label: "Faible", color: "var(--color-danger)", width: "33%" };
    if (password.length < 10 || !/[0-9]/.test(password)) return { label: "Moyen", color: "var(--color-warning)", width: "66%" };
    return { label: "Fort", color: "var(--color-success)", width: "100%" };
  })();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await register(email, password, fullName, role, inviteCode);
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
          {password.length > 0 && (
            <div className={styles.strengthWrap}>
              <div className={styles.strengthBar}>
                <div
                  className={styles.strengthFill}
                  style={{ width: passwordStrength.width, background: passwordStrength.color }}
                />
              </div>
              <span className={styles.strengthLabel} style={{ color: passwordStrength.color }}>
                {passwordStrength.label}
              </span>
            </div>
          )}
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

        {role === "consultant" && (
          <div className={styles.field}>
            <label className={styles.label}>Code d'invitation consultant</label>
            <input
              className={styles.input}
              type="password"
              value={inviteCode}
              onChange={(e) => setInviteCode(e.target.value)}
              required
            />
          </div>
        )}

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
