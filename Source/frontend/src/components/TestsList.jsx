export default function TestsList({ tests, selectedId, canEdit, onSelect, onDelete }) {
  return (
    <section className="panel wide">
      <h2>Тесты</h2>
      <div className="items">
        {tests.map((test) => (
          <article className={selectedId === test.id ? 'item active' : 'item'} key={test.id}>
            <button type="button" className="item-main" onClick={() => onSelect(test)}>
              <strong>{test.title}</strong>
              <span>{test.subject}</span>
              <small>Проходной балл: {test.pass_percent}%</small>
            </button>
            {canEdit && (
              <button type="button" className="danger ghost" onClick={() => onDelete(test.id)}>
                Удалить
              </button>
            )}
          </article>
        ))}
      </div>
    </section>
  );
}
