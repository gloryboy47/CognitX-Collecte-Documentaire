import { Outlet, Link, useNavigate } from "react-router-dom";
import { useAuth } from "@/shared/hooks/useAuth";
import styles from "./Layout.module.css";

export function Layout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <div className={styles.layout}>
      <header className={styles.header}>
        <Link to="/" className={styles.logo}>
          CognitX
        </Link>
        <nav className={styles.nav}>
          <span className={styles.user}>
            {user?.full_name} ({user?.role})
          </span>
          <button onClick={handleLogout} className={styles.logoutBtn}>
            Deconnexion
          </button>
        </nav>
      </header>
      <main className={styles.main}>
        <Outlet />
      </main>
    </div>
  );
}
