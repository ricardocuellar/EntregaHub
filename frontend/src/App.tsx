import { useState, type FormEvent } from 'react';
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import { Layout } from './components/Layout';
import { ApiError } from './lib/http';
import { SessionProvider, useSession } from './session/SessionProvider';

function Login() {
  const session = useSession();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [fieldErrors, setFieldErrors] = useState<{ username: string[]; password: string[] }>({
    username: [], password: [],
  });
  if (session.user) return <Navigate to="/" replace />;

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (busy) return;
    setBusy(true);
    setError('');
    setFieldErrors({ username: [], password: [] });
    try {
      await session.login(username, password);
    } catch (error) {
      if (error instanceof ApiError && error.status === 400) {
        const data = error.data;
        const messages = (field: 'username' | 'password'): string[] => {
          if (!data || typeof data !== 'object') return [];
          const value = (data as Record<string, unknown>)[field];
          return Array.isArray(value)
            ? value.filter((message): message is string => typeof message === 'string' && message.trim().length > 0)
            : [];
        };
        const fields = { username: messages('username'), password: messages('password') };
        setFieldErrors(fields);
        if (!fields.username.length && !fields.password.length) {
          setError('Usuario o contraseña incorrectos.');
        }
      } else {
        setError('No se pudo iniciar sesión. Inténtalo de nuevo.');
      }
    } finally {
      setPassword('');
      setBusy(false);
    }
  }

  return <Layout><h1>Iniciar sesión</h1><section className="card">
    <form onSubmit={submit} aria-busy={busy}>
      <label htmlFor="username">Usuario
        <input id="username" name="username" autoComplete="username" required maxLength={150}
          aria-invalid={fieldErrors.username.length > 0 || undefined}
          aria-describedby={fieldErrors.username.length ? 'username-errors' : undefined}
          value={username} onChange={event => setUsername(event.target.value)} disabled={busy} />
      </label>
      {fieldErrors.username.length > 0 && <div id="username-errors" role="alert">
        {fieldErrors.username.map((message, index) => <p key={index}>{message}</p>)}
      </div>}
      <label htmlFor="password">Contraseña
        <input id="password" name="password" type="password" autoComplete="current-password" required
          aria-invalid={fieldErrors.password.length > 0 || undefined}
          aria-describedby={fieldErrors.password.length ? 'password-errors' : undefined}
          value={password} onChange={event => setPassword(event.target.value)} disabled={busy} />
      </label>
      {fieldErrors.password.length > 0 && <div id="password-errors" role="alert">
        {fieldErrors.password.map((message, index) => <p key={index}>{message}</p>)}
      </div>}
      {error && <p role="alert">{error}</p>}
      <button type="submit" disabled={busy}>{busy ? 'Entrando…' : 'Entrar'}</button>
    </form>
  </section></Layout>;
}

function Home() {
  const session = useSession();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  if (!session.user) return <Navigate to="/login" replace />;

  async function logout() {
    if (busy) return;
    setBusy(true);
    setError('');
    try {
      await session.logout();
    } catch {
      setError('No se pudo confirmar el cierre de sesión. Inténtalo de nuevo.');
    } finally {
      setBusy(false);
    }
  }

  return <Layout actions={<button onClick={logout} disabled={busy}>
    {busy ? 'Saliendo…' : 'Cerrar sesión'}
  </button>}><h1>Tu sesión</h1><section className="card">
    <span className="tag">Sesión activa</span>
    <p>Has iniciado sesión correctamente.</p>
    <p><strong>Usuario:</strong> {session.user.username}</p>
    <p><strong>Rol:</strong> {session.user.role}</p>
    {error && <p role="alert">{error}</p>}
  </section></Layout>;
}

function SessionRoutes() {
  const session = useSession();
  if (session.status === 'checking') {
    return <Layout><section className="card"><p role="status">Comprobando sesión…</p></section></Layout>;
  }
  if (session.status === 'error') {
    return <Layout><section className="card">
      <p role="alert">No se pudo comprobar la sesión. Revisa tu conexión e inténtalo de nuevo.</p>
      <button onClick={session.retry}>Reintentar</button>
    </section></Layout>;
  }
  return <Routes>
    <Route path="/login" element={<Login />} />
    <Route path="/" element={<Home />} />
    <Route path="*" element={<Navigate to="/" replace />} />
  </Routes>;
}

export function App() {
  return <BrowserRouter><SessionProvider><SessionRoutes /></SessionProvider></BrowserRouter>;
}
