import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/shared/api/client";
import styles from "./Notifications.module.css";

interface Notification {
  id: number;
  type: string;
  title: string;
  message: string;
  is_read: boolean;
  created_at: string;
}

export function NotificationsPage() {
  const qc = useQueryClient();

  const { data: notifications, isLoading } = useQuery<Notification[]>({
    queryKey: ["notifications"],
    queryFn: () => api.get("/notifications"),
  });

  const markRead = useMutation({
    mutationFn: (id: number) => api.post(`/notifications/${id}/read`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["notifications"] });
      qc.invalidateQueries({ queryKey: ["notif-count"] });
    },
  });

  const markAllRead = useMutation({
    mutationFn: () => api.post("/notifications/read-all"),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["notifications"] });
      qc.invalidateQueries({ queryKey: ["notif-count"] });
    },
  });

  if (isLoading) return <p className={styles.muted}>Chargement...</p>;

  const unread = notifications?.filter((n) => !n.is_read).length ?? 0;

  return (
    <div>
      <div className={styles.header}>
        <h1 className={styles.title}>Notifications</h1>
        {unread > 0 && (
          <button
            className={styles.markAllBtn}
            onClick={() => markAllRead.mutate()}
            disabled={markAllRead.isPending}
          >
            Tout marquer comme lu
          </button>
        )}
      </div>

      {!notifications || notifications.length === 0 ? (
        <p className={styles.muted}>Aucune notification.</p>
      ) : (
        <div className={styles.list}>
          {notifications.map((n) => (
            <div
              key={n.id}
              className={`${styles.card} ${n.is_read ? "" : styles.unread}`}
            >
              <div className={styles.cardHeader}>
                <span className={styles.cardTitle}>{n.title}</span>
                <span className={styles.date}>
                  {new Date(n.created_at).toLocaleDateString("fr-FR", {
                    day: "numeric",
                    month: "short",
                    hour: "2-digit",
                    minute: "2-digit",
                  })}
                </span>
              </div>
              <p className={styles.message}>{n.message}</p>
              {!n.is_read && (
                <button
                  className={styles.readBtn}
                  onClick={() => markRead.mutate(n.id)}
                  disabled={markRead.isPending}
                >
                  Marquer comme lu
                </button>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
