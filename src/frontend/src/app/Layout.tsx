import { Outlet, Link, useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { useAuth } from "@/shared/hooks/useAuth";
import { useTheme } from "@/shared/hooks/useTheme";
import { api } from "@/shared/api/client";
import styles from "./Layout.module.css";

export function Layout() {
  const { user, logout } = useAuth();
  const { theme, toggle: toggleTheme } = useTheme();
  const navigate = useNavigate();

  const { data: notifData } = useQuery<{ count: number }>({
    queryKey: ["notif-count"],
    queryFn: () => api.get("/notifications/unread/count"),
    refetchInterval: 10000,
  });

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
          <Link to="/notifications" className={styles.notifLink} aria-label="Notifications">
            Notifications
            {notifData && notifData.count > 0 && (
              <span className={styles.notifBadge}>{notifData.count}</span>
            )}
          </Link>
          <button onClick={toggleTheme} className={styles.themeBtn} aria-label="Changer le theme">
            {theme === "light" ? "Sombre" : "Clair"}
          </button>
          <span className={styles.user}>
            {user?.full_name} ({user?.role})
          </span>
          <button onClick={handleLogout} className={styles.logoutBtn} aria-label="Se deconnecter">
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
