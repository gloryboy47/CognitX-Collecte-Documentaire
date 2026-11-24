import {
  createContext,
  useContext,
  useState,
  useCallback,
  type ReactNode,
} from "react";
import { api } from "@/shared/api/client";

interface User {
  id: number;
  email: string;
  full_name: string;
  role: "client" | "consultant";
}

interface AuthCtx {
  user: User | null;
  token: string | null;
  login: (email: string, password: string) => Promise<void>;
  register: (
    email: string,
    password: string,
    full_name: string,
    role: "client" | "consultant",
  ) => Promise<void>;
  logout: () => void;
}

const Ctx = createContext<AuthCtx | null>(null);

interface TokenResponse {
  access_token: string;
  token_type: string;
  user: { id: number; email: string; full_name: string; role: string };
}

function restoreUser(): User | null {
  try {
    const raw = localStorage.getItem("user");
    if (raw) return JSON.parse(raw);
  } catch {
    /* ignore */
  }
  return null;
}

function saveSession(data: TokenResponse) {
  localStorage.setItem("token", data.access_token);
  const user: User = {
    id: data.user.id,
    email: data.user.email,
    full_name: data.user.full_name,
    role: data.user.role as "client" | "consultant",
  };
  localStorage.setItem("user", JSON.stringify(user));
  return user;
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(() =>
    localStorage.getItem("token"),
  );
  const [user, setUser] = useState<User | null>(restoreUser);

  const login = useCallback(async (email: string, password: string) => {
    const data = await api.post<TokenResponse>("/auth/login", {
      email,
      password,
    });
    const u = saveSession(data);
    setToken(data.access_token);
    setUser(u);
  }, []);

  const register = useCallback(
    async (
      email: string,
      password: string,
      full_name: string,
      role: "client" | "consultant",
    ) => {
      const data = await api.post<TokenResponse>("/auth/register", {
        email,
        password,
        full_name,
        role,
      });
      const u = saveSession(data);
      setToken(data.access_token);
      setUser(u);
    },
    [],
  );

  const logout = useCallback(() => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    setToken(null);
    setUser(null);
  }, []);

  return (
    <Ctx.Provider value={{ user, token, login, register, logout }}>
      {children}
    </Ctx.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(Ctx);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
