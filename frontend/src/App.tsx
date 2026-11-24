import { useEffect, useState } from 'react';
import { Layout } from './components/Layout';
import { api } from './lib/http';
export function App() {
  const [status, setStatus] = useState('Conectando con la API…');
  useEffect(() => {
    api<{ status: string; service: string }>('/api/health/')
      .then(data => setStatus(`${data.service}: ${data.status}`))
      .catch(() => setStatus('No se pudo conectar con la API. Revisa los servicios.'));
  }, []);
  return <Layout><span className="tag">Base del proyecto</span><h1>Una base para construir EntregaPRO</h1><section className="card"><h2>Conexión al servicio</h2><p role="status">{status}</p><p className="muted">El acceso, los proyectos y las entregas se incorporan en los siguientes bloques.</p></section></Layout>;
}
