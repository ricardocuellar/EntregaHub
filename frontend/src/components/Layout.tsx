import type { ReactNode } from 'react';
export function Layout({children, actions}: {children: ReactNode; actions?: ReactNode}) {
  return <><header><div><strong>EntregaPRO</strong><br/><small>Portal de entregables</small></div><nav aria-label="Principal">{actions}</nav></header><main>{children}</main></>;
}
