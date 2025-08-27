# EmpowerNow SDK – Python & React packages

EmpowerNow provides a **secure‐by‐default** toolkit for building apps on top of the EmpowerNow Platform.  The SDK is split into two families:

| Package | Runtime | Purpose |
|---------|---------|---------|
| `empowernow-common` | Python 3.10 – 3.12 | Shared cryptography, OAuth helpers, AuthZEN PDP client, Redis/metrics utilities. |
| `@empowernow/bff-auth-react` | React 18 | Hooks & components for the **Backend-for-Frontend** (BFF) cookie-based auth model. |
| `@empowernow/ui` | React 18 | Headless UI-component library used by all EmpowerNow SPAs. (Depends on either `@empowernow/bff-auth-react` *or* the legacy shim `@empowernow/react`.) |

> **Why no browser-side OAuth client?**  EmpowerNow moved to a BFF architecture to comply with FAPI 2.0 Baseline / Advanced and to keep tokens **out of the browser**.  The legacy `@empowernow/react` library now acts as a thin re-export of `@empowernow/bff-auth-react` for backward compatibility.  It no longer handles tokens.

---

## Installation

### Python (server-side services)
```bash
pip install "empowernow-common>=2.3,<3"
```

Optional extras:
* `empowernow-common[fips]` – Use when running under an OpenSSL FIPS provider.
* `empowernow-common[redis]`, `empowernow-common[kafka]`, etc. – Feature-scoped extras, see *pyproject.toml*.

### React (front-end SPAs)
```bash
npm install @empowernow/bff-auth-react @empowernow/ui
```

If you still have code importing `@empowernow/react`, update it at your own pace – the alias re-exports the new package so nothing breaks at runtime.

---

## Quick start

### Using the Python OAuthClient
```python
from empowernow_common.oauth import OAuthClient

oauth = OAuthClient(
    issuer="https://idp.example.com",
    client_id="python-client",
    client_secret="…",  # confidential client
    redirect_uri="https://bff.example.com/auth/callback",
    scopes=["openid", "profile"]
)

auth_url = oauth.create_authorization_url(state="xyz")
print("Open browser to", auth_url)
```

### React – wrap your SPA in the AuthProvider
```tsx
import { AuthProvider } from '@empowernow/bff-auth-react';
import { createRoot } from 'react-dom/client';
import App from './App';

createRoot(document.getElementById('root')!).render(
  <AuthProvider baseUrl={import.meta.env.VITE_BFF_BASE_URL}>
    <App />
  </AuthProvider>
);
```

`useAuth()` gives you `isAuthenticated`, `user`, `session` and convenience helpers like `login()` and `logout()`; `apiClient` is a fetch wrapper that automatically adds CSRF headers and `credentials:"include"`.

---

## Security & Compliance
* **FAPI 2.0 ready** – private-key-JWT, PAR, JARM, DPoP and SameSite cookie model supported at the BFF layer.
* **FIPS option** – When the host OpenSSL runs in FIPS 140-3 mode, `empowernow-common` can validate algorithms at start-up and periodically (opt-in via env `FIPS_CONTINUOUS_VALIDATION=1`).
* **No browser tokens** – SPAs never see access- or refresh-tokens; they use HttpOnly cookies issued by the BFF.
* **Structured logging & Prometheus metrics** built in.

---

## Repository layout
```
client_sdk/empowernow-packages/
 ├── packages/
 │   ├── empowernow-common/            # Python package
 │   ├── @empowernow/bff-auth-react/   # React auth kit
 │   ├── @empowernow/ui/               # UI kit (optional peer)
 │   └── empowernow-react/             # Shim – re-exports BFF kit
```

---

## Contributing
Pull requests are welcome.  Please run `pre-commit run -a` and ensure `pytest -q` / `pnpm test` are green before opening a PR.

---

© 2025 EmpowerNow – Apache 2.0 licence.
