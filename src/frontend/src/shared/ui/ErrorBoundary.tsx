import { Component, type ReactNode, type ErrorInfo } from "react";

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false, error: null };

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error("ErrorBoundary caught:", error, info.componentStack);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{
          textAlign: "center",
          padding: "60px 24px",
          maxWidth: 500,
          margin: "0 auto",
        }}>
          <h1 style={{ fontSize: "1.5rem", fontWeight: 700, marginBottom: 8 }}>
            Une erreur est survenue
          </h1>
          <p style={{ color: "var(--color-text-muted)", marginBottom: 16 }}>
            {this.state.error?.message || "Erreur inattendue"}
          </p>
          <button
            onClick={() => {
              this.setState({ hasError: false, error: null });
              window.location.href = "/";
            }}
            style={{
              padding: "10px 24px",
              background: "var(--color-primary)",
              color: "#fff",
              border: "none",
              borderRadius: "var(--radius)",
              fontWeight: 600,
              cursor: "pointer",
            }}
          >
            Retour a l'accueil
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}
