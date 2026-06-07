import { useEffect, useState } from 'react';

const emptyTest = {
  title: '',
  subject: '',
  description: '',
  pass_percent: 60,
};

export default function TestEditor({ test, onSave, onClear }) {
  const [form, setForm] = useState(emptyTest);
  const [message, setMessage] = useState('');

  useEffect(() => {
    setForm(test || emptyTest);
    setMessage('');
  }, [test]);

  function update(field, value) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setMessage('');

    try {
      await onSave(form, test?.id || null);
      setMessage('Сохранено');
      if (!test) {
        setForm(emptyTest);
      }
    } catch (err) {
      setMessage(err.message);
    }
  }

  return (
    <section className="panel">
      <h2>{test ? 'Редактирование теста' : 'Новый тест'}</h2>
      <form onSubmit={handleSubmit} className="form">
        <label>
          Название
          <input value={form.title} onChange={(event) => update('title', event.target.value)} required />
        </label>
        <label>
          Предмет
          <input value={form.subject} onChange={(event) => update('subject', event.target.value)} required />
        </label>
        <label>
          Описание
          <textarea value={form.description || ''} onChange={(event) => update('description', event.target.value)} />
        </label>
        <label>
          Проходной процент
          <input
            type="number"
            min="1"
            max="100"
            value={form.pass_percent}
            onChange={(event) => update('pass_percent', Number(event.target.value))}
          />
        </label>
        <div className="actions">
          <button type="submit">Сохранить</button>
          {test && <button type="button" className="ghost" onClick={onClear}>Новый</button>}
        </div>
      </form>
      {message && <p className="muted">{message}</p>}
    </section>
  );
}
