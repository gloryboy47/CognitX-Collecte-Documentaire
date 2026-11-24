import { Routes, Route, Navigate } from "react-router-dom";
import { useAuth } from "@/shared/hooks/useAuth";
import { Layout } from "@/app/Layout";
import { LoginPage } from "@/features/auth/LoginPage";
import { RegisterPage } from "@/features/auth/RegisterPage";
import { DashboardPage } from "@/features/cases/DashboardPage";
import { CaseDetailPage } from "@/features/cases/CaseDetailPage";
import { ReviewPage } from "@/features/review/ReviewPage";
import { NotificationsPage } from "@/features/notifications/NotificationsPage";

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { user } = useAuth();
  if (!user) return <Navigate to="/login" replace />;
  return <>{children}</>;
}

export function App() {
  const { user } = useAuth();

  return (
    <Routes>
      <Route
        path="/login"
        element={user ? <Navigate to="/" replace /> : <LoginPage />}
      />
      <Route
        path="/register"
        element={user ? <Navigate to="/" replace /> : <RegisterPage />}
      />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        <Route index element={<DashboardPage />} />
        <Route path="cases/:caseId" element={<CaseDetailPage />} />
        <Route path="documents/:docId/review" element={<ReviewPage />} />
        <Route path="notifications" element={<NotificationsPage />} />
      </Route>
    </Routes>
  );
}
