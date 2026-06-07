import { useEffect, useState } from 'react';
import { ApiClient } from './api/ApiClient.js';
import LoginForm from './components/LoginForm.jsx';
import TestsList from './components/TestsList.jsx';
import TestEditor from './components/TestEditor.jsx';
import ResultsTable from './components/ResultsTable.jsx';
import UserForm from './components/UserForm.jsx';

export default function App() {
  const [users, setUsers] = useState([]);
  const [tests, setTests] = useState([]);
  const [results, setResults] = useState([]);
  const [currentUser, setCurrentUser] = useState(null);
  const [selectedTest, setSelectedTest] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const canEdit = currentUser && ['admin', 'teacher'].includes(currentUser.role);

  const passedCount = results.filter((item) => item.passed === true || item.passed === '1').length;
  const averagePercent = results.length === 0
    ? 0
    : Math.round(results.reduce((sum, item) => sum + Number(item.percent || 0), 0) / results.length);

  useEffect(() => {
    init();
  }, []);

  async function init() {
    setLoading(true);
    setError('');

    try {
      const user = await ApiClient.auth.me();
      if (!user) {
        setCurrentUser(null);
        clearData();
        return;
      }

      setCurrentUser(user);
      await refreshData();
    } catch (err) {
      setError(err.message || 'Ошибка загрузки данных');
    } finally {
      setLoading(false);
    }
  }

  function clearData() {
    setUsers([]);
    setTests([]);
    setResults([]);
    setSelectedTest(null);
  }

  async function refreshData() {
    const [nextUsers, nextTests, nextResults] = await Promise.all([
      ApiClient.users.all(),
      ApiClient.tests.all(),
      ApiClient.results.all(),
    ]);
    setUsers(nextUsers);
    setTests(nextTests);
    setResults(nextResults);
  }

  async function handleLogin(payload) {
    setLoading(true);
    setError('');

    try {
      const user = await ApiClient.auth.login(payload);
      setCurrentUser(user);
      await refreshData();
    } catch (err) {
      setError(err.message || 'Ошибка входа');
    } finally {
      setLoading(false);
    }
  }

  async function handleLogout() {
    try {
      await ApiClient.auth.logout();
    } catch {
      // Сессию могли уже очистить на сервере, интерфейс все равно сбрасываем.
    }

    setCurrentUser(null);
    clearData();
  }

  async function handleCreateUser(payload) {
    const user = await ApiClient.users.create(payload);
    setUsers((current) => [...current, user]);
  }

  async function handleSaveTest(payload, id = null) {
    const saved = id ? await ApiClient.tests.update(id, payload) : await ApiClient.tests.create(payload);
    setTests((current) => (id ? current.map((item) => (item.id === id ? saved : item)) : [...current, saved]));
  }

  async function handleDeleteTest(id) {
    await ApiClient.tests.delete(id);
    setTests((current) => current.filter((item) => item.id !== id));
    setSelectedTest(null);
  }

  async function handleSaveResult(payload, id = null) {
    const saved = id ? await ApiClient.results.update(id, payload) : await ApiClient.results.create(payload);
    await refreshData();
    return saved;
  }

  async function handleDeleteResult(id) {
    await ApiClient.results.delete(id);
    setResults((current) => current.filter((item) => item.id !== id));
  }

  return (
    <main className="app">
      <header className="topbar">
        <div>
          <h1>Результаты тестов</h1>
          <p>Учет тестов, студентов и итоговых баллов</p>
        </div>
      </header>

      {loading && <p className="notice">Загрузка...</p>}
      {error && <p className="error">Ошибка загрузки данных: {error}</p>}

      {!loading && !currentUser && (
        <LoginForm onLogin={handleLogin} />
      )}

      {!loading && currentUser && (
        <>
          <section className="layout">
            <LoginForm user={currentUser} onLogout={handleLogout} />
            <div className="summary">
              <span>Тестов: {tests.length}</span>
              <span>Результатов: {results.length}</span>
              <span>Средний процент: {averagePercent}%</span>
              <span>Зачтено: {passedCount}</span>
            </div>
          </section>

          <section className="layout">
            <TestsList
              tests={tests}
              selectedId={selectedTest?.id}
              canEdit={canEdit}
              onSelect={setSelectedTest}
              onDelete={handleDeleteTest}
            />
            {canEdit && <TestEditor test={selectedTest} onSave={handleSaveTest} onClear={() => setSelectedTest(null)} />}
          </section>

          <ResultsTable
            users={users}
            tests={tests}
            results={results}
            canEdit={canEdit}
            currentUser={currentUser}
            onSave={handleSaveResult}
            onDelete={handleDeleteResult}
          />

          {currentUser?.role === 'admin' && <UserForm onCreate={handleCreateUser} />}
        </>
      )}
    </main>
  );
}
