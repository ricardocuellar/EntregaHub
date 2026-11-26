import { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from 'react';
import { api, ApiError } from '../lib/http';

type User = { id: number; username: string; name: string; role: string };
type SessionState =
  | { status: 'checking' | 'error'; user: null }
  | { status: 'ready'; user: User | null };
type Session = SessionState & {
  retry: () => void;
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
};
const SessionContext = createContext<Session | null>(null);

export function SessionProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<SessionState>({ status: 'checking', user: null });
  const checkSession = useCallback(async () => {
    setState({ status: 'checking', user: null });
    try {
      const { user } = await api<{ user: User }>('/api/auth/me/');
      setState({ status: 'ready', user });
    } catch (error) {
      if (error instanceof ApiError && [401, 403].includes(error.status)) {
        setState({ status: 'ready', user: null });
      } else {
        setState({ status: 'error', user: null });
      }
    }
  }, []);

  useEffect(() => { void checkSession(); }, [checkSession]);

  async function login(username: string, password: string) {
    const { user } = await api<{ user: User }>('/api/auth/login/', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    });
    setState({ status: 'ready', user });
  }

  async function logout() {
    await api('/api/auth/logout/', { method: 'POST' });
    setState({ status: 'ready', user: null });
  }

  return <SessionContext.Provider value={{ ...state, retry: () => { void checkSession(); }, login, logout }}>
    {children}
  </SessionContext.Provider>;
}

export function useSession() {
  const session = useContext(SessionContext);
  if (!session) throw new Error('Falta SessionProvider.');
  return session;
}
