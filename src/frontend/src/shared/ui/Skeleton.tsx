import styles from "./Skeleton.module.css";

interface Props {
  width?: string;
  height?: string;
  borderRadius?: string;
}

export function Skeleton({ width = "100%", height = "16px", borderRadius = "4px" }: Props) {
  return (
    <div
      className={styles.skeleton}
      style={{ width, height, borderRadius }}
    />
  );
}

export function CardSkeleton() {
  return (
    <div className={styles.card}>
      <div className={styles.cardRow}>
        <Skeleton width="60px" height="14px" />
        <Skeleton width="80px" height="22px" borderRadius="12px" />
      </div>
      <Skeleton width="70%" height="20px" />
      <Skeleton width="40%" height="14px" />
    </div>
  );
}

export function TableSkeleton({ rows = 4 }: { rows?: number }) {
  return (
    <div className={styles.tableWrap}>
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className={styles.tableRow}>
          <Skeleton width="40%" height="14px" />
          <Skeleton width="60px" height="14px" />
          <Skeleton width="80px" height="22px" borderRadius="12px" />
          <Skeleton width="50px" height="14px" />
        </div>
      ))}
    </div>
  );
}
