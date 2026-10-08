import { type FormEvent, useEffect, useState } from "react";

import { createItem, type Item, listItems } from "./api";

/** Página de ejemplo: lista items del backend y permite crear uno nuevo. */
export default function App() {
  const [items, setItems] = useState<Item[]>([]);
  const [name, setName] = useState("");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    listItems()
      .then(setItems)
      .catch(() => setError("No se pudo cargar la lista"));
  }, []);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    if (!name.trim()) return;
    try {
      const created = await createItem(name.trim());
      setItems((current) => [...current, created]);
      setName("");
      setError(null);
    } catch {
      setError("No se pudo crear el item");
    }
  }

  return (
    <main>
      <h1>App de prueba</h1>
      <form onSubmit={handleSubmit}>
        <label htmlFor="item-name">Nuevo item</label>
        <input id="item-name" value={name} onChange={(e) => setName(e.target.value)} />
        <button type="submit">Agregar</button>
      </form>
      {error && <p role="alert">{error}</p>}
      <ul>
        {items.map((item) => (
          <li key={item.id}>{item.name}</li>
        ))}
      </ul>
    </main>
  );
}
