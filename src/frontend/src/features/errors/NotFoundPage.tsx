import { Link } from "react-router-dom";

export function NotFoundPage() {
  return (
    <div style={{ textAlign: "center", padding: "80px 24px" }}>
      <h1 style={{ fontSize: "3rem", fontWeight: 800, marginBottom: 8 }}>404</h1>
      <p style={{ color: "var(--color-text-muted)", marginBottom: 24 }}>
        Page introuvable.
      </p>
      <Link
        to="/"
        style={{
          padding: "10px 24px",
          background: "var(--color-primary)",
          color: "#fff",
          borderRadius: "var(--radius)",
          fontWeight: 600,
        }}
      >
        Retour au tableau de bord
      </Link>
    </div>
  );
}
