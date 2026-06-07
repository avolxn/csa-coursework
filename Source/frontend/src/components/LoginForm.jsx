import { useState } from 'react';

export default function LoginForm({ user, onLogin, onLogout }) {
  const [email, setEmail] = useState(() => localStorage.getItem('coursework.lastEmail') || 'admin@example.com');
  const [password, setPassword] = useState('password');

  if (user) {
    return (
      <section className="panel">
        <h2>Вход</h2>
        <p><strong>{user.name}</strong></p>
        <p className="muted">Роль: {user.role}</p>
        <button type="button" className="ghost" onClick={onLogout}>Выйти</button>
      </section>
    );
  }

  return (
    <section className="panel">
      <h2>Вход</h2>
      <form
        className="form"
        onSubmit={(event) => {
          event.preventDefault();
          localStorage.setItem('coursework.lastEmail', email);
          onLogin({ email, password });
        }}
      >
        <label>
          Email
          <input type="email" value={email} onChange={(event) => setEmail(event.target.value)} required />
        </label>
        <label>
          Пароль
          <input type="password" value={password} onChange={(event) => setPassword(event.target.value)} required />
        </label>
        <button type="submit">Войти</button>
      </form>
      <p className="muted">Демо: admin@example.com, maria.teacher@example.com, anna@example.com. Пароль: password.</p>
    </section>
  );
}
