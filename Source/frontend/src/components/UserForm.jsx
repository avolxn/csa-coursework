import { useState } from 'react';

const initialForm = {
  name: '',
  email: '',
  password: 'password',
  age: '',
  role: 'student',
};

export default function UserForm({ onCreate }) {
  const [form, setForm] = useState(initialForm);
  const [message, setMessage] = useState('');

  function update(field, value) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setMessage('');

    try {
      await onCreate(form);
      setForm(initialForm);
      setMessage('Пользователь создан');
    } catch (err) {
      setMessage(err.message);
    }
  }

  return (
    <section className="panel full">
      <h2>Новый пользователь</h2>
      <form onSubmit={handleSubmit} className="form grid-form">
        <label>
          Имя
          <input value={form.name} onChange={(event) => update('name', event.target.value)} required />
        </label>
        <label>
          Email
          <input type="email" value={form.email} onChange={(event) => update('email', event.target.value)} required />
        </label>
        <label>
          Пароль
          <input type="password" value={form.password} onChange={(event) => update('password', event.target.value)} required />
        </label>
        <label>
          Возраст
          <input type="number" min="6" max="100" value={form.age} onChange={(event) => update('age', event.target.value)} />
        </label>
        <label>
          Роль
          <select value={form.role} onChange={(event) => update('role', event.target.value)}>
            <option value="student">student</option>
            <option value="teacher">teacher</option>
            <option value="admin">admin</option>
          </select>
        </label>
        <button type="submit">Создать</button>
      </form>
      {message && <p className="muted">{message}</p>}
    </section>
  );
}
