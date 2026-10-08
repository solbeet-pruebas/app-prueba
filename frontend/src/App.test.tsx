import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import App from "./App";

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

describe("App", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("muestra los items que devuelve la API", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        jsonResponse([{ id: 1, name: "Primero", description: null, created_at: "" }]),
      ),
    );
    render(<App />);
    expect(await screen.findByText("Primero")).toBeInTheDocument();
  });

  it("agrega un item nuevo", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse([]))
      .mockResolvedValueOnce(
        jsonResponse({ id: 2, name: "Nuevo", description: null, created_at: "" }, 201),
      );
    vi.stubGlobal("fetch", fetchMock);
    render(<App />);

    await userEvent.type(screen.getByLabelText("Nuevo item"), "Nuevo");
    await userEvent.click(screen.getByRole("button", { name: "Agregar" }));

    expect(await screen.findByText("Nuevo")).toBeInTheDocument();
    expect(fetchMock).toHaveBeenLastCalledWith("/api/items", expect.objectContaining({ method: "POST" }));
  });

  it("muestra un error si la API falla", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(jsonResponse({}, 500)));
    render(<App />);
    expect(await screen.findByRole("alert")).toHaveTextContent("No se pudo cargar la lista");
  });
});
