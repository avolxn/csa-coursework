import { useEffect, useState } from 'react';

export default function ResultsTable({ users, tests, results, canEdit, currentUser, onSave, onDelete }) {
  const students = users.filter((user) => user.role === 'student');
  const [form, setForm] = useState(emptyForm);
  const [message, setMessage] = useState('');

  const visibleResults = currentUser?.role === 'student'
    ? results.filter((result) => Number(result.user_id) === Number(currentUser.id))
    : results;

  useEffect(() => {
    setForm((current) => ({
      ...current,
      user_id: current.user_id || String(students[0]?.id || ''),
      test_id: current.test_id || String(tests[0]?.id || ''),
    }));
  }, [students, tests]);

  function update(field, value) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setMessage('');

    try {
      await onSave({
        ...form,
        user_id: Number(form.user_id),
        test_id: Number(form.test_id),
      });
      setForm(emptyForm());
      setMessage('Результат добавлен');
    } catch (err) {
      setMessage(err.message);
    }
  }

  return (
    <section className="panel full">
      <div className="section-title">
        <h2>Результаты</h2>
        <span>{currentUser?.role === 'student' ? 'Показаны только свои результаты' : 'Показаны все результаты'}</span>
      </div>

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Студент</th>
              <th>Тест</th>
              <th>Балл</th>
              <th>%</th>
              <th>Оценка</th>
              <th>Статус</th>
              <th>Комментарий</th>
              {canEdit && <th></th>}
            </tr>
          </thead>
          <tbody>
            {visibleResults.map((result) => (
              <tr key={result.id}>
                <td>{result.student_name || nameById(users, result.user_id)}</td>
                <td>{result.test_title || nameById(tests, result.test_id, 'title')}</td>
                <td>{result.score}/{result.max_score}</td>
                <td>{Number(result.percent).toFixed(0)}%</td>
                <td>{result.grade}</td>
                <td>{result.passed === true || result.passed === '1' ? 'зачтено' : 'не зачтено'}</td>
                <td>{result.comment}</td>
                {canEdit && (
                  <td>
                    <button type="button" className="danger ghost" onClick={() => onDelete(result.id)}>
                      Удалить
                    </button>
                  </td>
                )}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {canEdit && (
        <form onSubmit={handleSubmit} className="form grid-form">
          <label>
            Студент
            <select value={form.user_id} onChange={(event) => update('user_id', event.target.value)}>
              {students.map((user) => (
                <option key={user.id} value={user.id}>{user.name}</option>
              ))}
            </select>
          </label>
          <label>
            Тест
            <select value={form.test_id} onChange={(event) => update('test_id', event.target.value)}>
              {tests.map((test) => (
                <option key={test.id} value={test.id}>{test.title}</option>
              ))}
            </select>
          </label>
          <label>
            Балл
            <input type="number" min="0" value={form.score} onChange={(event) => update('score', Number(event.target.value))} />
          </label>
          <label>
            Максимум
            <input type="number" min="1" value={form.max_score} onChange={(event) => update('max_score', Number(event.target.value))} />
          </label>
          <label className="stretch">
            Комментарий
            <input value={form.comment} onChange={(event) => update('comment', event.target.value)} />
          </label>
          <button type="submit">Добавить результат</button>
        </form>
      )}
      {message && <p className="muted">{message}</p>}
    </section>
  );
}

function nameById(rows, id, field = 'name') {
  return rows.find((row) => Number(row.id) === Number(id))?.[field] || 'Не найдено';
}

function emptyForm() {
  return {
    user_id: '',
    test_id: '',
    score: 0,
    max_score: 1,
    comment: '',
  };
}
