"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
  type PropsWithChildren,
} from "react";

export interface User {
  username: string;
  displayName: string;
}

interface AuthContextValue {
  user: User | null;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<boolean>;
  signup: (username: string, password: string, displayName: string) => Promise<boolean>;
  logout: () => void;
}

const AuthCtx = createContext<AuthContextValue>({
  user: null,
  isLoading: true,
  login: async () => false,
  signup: async () => false,
  logout: () => {},
});

export function useAuth() {
  return useContext(AuthCtx);
}

const STORAGE_KEY = "companionhk_users";
const SESSION_KEY = "companionhk_session";

function getStoredUsers(): Record<string, { password: string; displayName: string }> {
  if (typeof window === "undefined") return {};
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY) || "{}");
  } catch {
    return {};
  }
}

function saveStoredUsers(users: Record<string, { password: string; displayName: string }>) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(users));
}

export function AuthProvider({ children }: PropsWithChildren) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const session = localStorage.getItem(SESSION_KEY);
    if (session) {
      try {
        setUser(JSON.parse(session));
      } catch {
        localStorage.removeItem(SESSION_KEY);
      }
    }
    setIsLoading(false);
  }, []);

  const login = useCallback(async (username: string, password: string): Promise<boolean> => {
    const users = getStoredUsers();
    const entry = users[username.toLowerCase()];
    if (!entry || entry.password !== password) return false;
    const u: User = { username: username.toLowerCase(), displayName: entry.displayName };
    setUser(u);
    localStorage.setItem(SESSION_KEY, JSON.stringify(u));
    return true;
  }, []);

  const signup = useCallback(
    async (username: string, password: string, displayName: string): Promise<boolean> => {
      const users = getStoredUsers();
      const key = username.toLowerCase();
      if (users[key]) return false;
      users[key] = { password, displayName };
      saveStoredUsers(users);
      const u: User = { username: key, displayName };
      setUser(u);
      localStorage.setItem(SESSION_KEY, JSON.stringify(u));
      return true;
    },
    [],
  );

  const logout = useCallback(() => {
    setUser(null);
    localStorage.removeItem(SESSION_KEY);
  }, []);

  return (
    <AuthCtx.Provider value={{ user, isLoading, login, signup, logout }}>
      {children}
    </AuthCtx.Provider>
  );
}
