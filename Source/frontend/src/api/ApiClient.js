async function request(path, options = {}) {
  const response = await fetch(path, {
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    },
    ...options,
  });

  const body = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(body.message || 'Ошибка запроса');
  }

  return body.data;
}

export const ApiClient = {
  auth: {
    me() {
      return request('/me');
    },

    login(payload) {
      return request('/login', {
        method: 'POST',
        body: JSON.stringify(payload),
      });
    },

    logout() {
      return request('/logout', { method: 'POST' });
    },
  },

  users: {
    all() {
      return request('/users');
    },

    create(payload) {
      return request('/users', {
        method: 'POST',
        body: JSON.stringify({
          ...payload,
          age: payload.age === '' ? null : Number(payload.age),
        }),
      });
    },
  },

  tests: {
    all() {
      return request('/tests');
    },

    create(payload) {
      return request('/tests', {
        method: 'POST',
        body: JSON.stringify(payload),
      });
    },

    update(id, payload) {
      return request(`/tests/${id}`, {
        method: 'PUT',
        body: JSON.stringify(payload),
      });
    },

    delete(id) {
      return request(`/tests/${id}`, {
        method: 'DELETE',
      });
    },
  },

  results: {
    all() {
      return request('/results');
    },

    create(payload) {
      return request('/results', {
        method: 'POST',
        body: JSON.stringify(payload),
      });
    },

    update(id, payload) {
      return request(`/results/${id}`, {
        method: 'PUT',
        body: JSON.stringify(payload),
      });
    },

    delete(id) {
      return request(`/results/${id}`, {
        method: 'DELETE',
      });
    },
  },
};
