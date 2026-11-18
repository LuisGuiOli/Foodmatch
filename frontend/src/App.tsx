// import { useState, type SyntheticEvent } from "react";

// type Prato = {
//   id: number;
//   prato: string;
//   restaurante: string;
//   preco: number;
//   score: number;
// };

// const moeda = new Intl.NumberFormat("pt-BR", {
//   style: "currency",
//   currency: "BRL",
// });

// function ListaDePratos({ pratos }: { pratos: Prato[] }) {
//   if (pratos.length === 0) {
//     return <p>Nenhum prato encontrado para essa busca.</p>;
//   }

//   return (
//     <section aria-labelledby="titulo-resultados">
//       <h2 id="titulo-resultados" className="mb-3 text-xl font-semibold">
//         Pratos recomendados
//       </h2>

//       <ol className="divide-y divide-stone-200">
//         {pratos.map((item) => (
//           <li key={item.id} className="flex items-start justify-between gap-4 py-4">
//             <div>
//               <h3 className="font-semibold">{item.prato}</h3>
//               <p className="text-sm text-stone-600">{item.restaurante}</p>
//             </div>
//             <span className="shrink-0 font-medium">{moeda.format(item.preco)}</span>
//           </li>
//         ))}
//       </ol>
//     </section>
//   );
// }

// export default function App() {
//   const [consulta, setConsulta] = useState("");
//   const [orcamento, setOrcamento] = useState("");
//   const [pratos, setPratos] = useState<Prato[] | null>(null);
//   const [carregando, setCarregando] = useState(false);
//   const [erro, setErro] = useState("");

//   async function buscar(evento: SyntheticEvent<HTMLFormElement>) {
//     evento.preventDefault();
//     const texto = consulta.trim();
//     if (!texto || carregando) return;

//     setErro("");
//     setPratos(null);
//     setCarregando(true);

//     const pedido = {
//       consulta: texto,
//       ...(orcamento !== "" && { orcamento: Number(orcamento) }),
//     };

//     try {
//       const resposta = await fetch("/api/recomendacoes", {
//         method: "POST",
//         headers: { "Content-Type": "application/json" },
//         body: JSON.stringify(pedido),
//       });

//       if (!resposta.ok) {
//         throw new Error(
//           resposta.status === 422
//             ? "Confira a consulta e o valor do orçamento."
//             : `A busca falhou (HTTP ${resposta.status}). Verifique a API.`,
//         );
//       }

//       const resultados: Prato[] = await resposta.json();
//       setPratos(resultados);
//     } catch (falha) {
//       setErro(falha instanceof Error ? falha.message : "Falha ao buscar os pratos.");
//     } finally {
//       setCarregando(false);
//     }
//   }

//   const estiloCampo =
//     "mt-1 w-full rounded-lg border border-stone-300 bg-white px-3 py-2.5 focus:outline-2 focus:outline-orange-700";

//   return (
//     <main className="min-h-screen bg-orange-50 px-5 py-12 text-stone-900">
//       <div className="mx-auto max-w-2xl">
//         <header className="mb-8">
//           <p className="mb-2 font-bold text-orange-800">FoodMatch</p>
//           <h1 className="text-3xl font-bold tracking-tight sm:text-4xl">
//             O que você quer comer?
//           </h1>
//         </header>

//         <form onSubmit={buscar} className="mb-8 grid gap-4">
//           <label className="font-medium">
//             Descreva seu pedido
//             <input
//               className={estiloCampo}
//               value={consulta}
//               onChange={(evento) => setConsulta(evento.target.value)}
//               placeholder="Quero frango com arroz e feijão"
//               maxLength={500}
//               required
//             />
//           </label>

//           <label className="font-medium sm:max-w-60">
//             Orçamento em R$ (opcional)
//             <input
//               className={estiloCampo}
//               type="number"
//               min="0.01"
//               step="0.01"
//               value={orcamento}
//               onChange={(evento) => setOrcamento(evento.target.value)}
//               placeholder="20,00"
//             />
//           </label>

//           <button
//             type="submit"
//             disabled={carregando || !consulta.trim()}
//             className="w-fit rounded-lg bg-orange-800 px-5 py-2.5 font-semibold text-white hover:bg-orange-900 disabled:opacity-50"
//           >
//             {carregando ? "Buscando..." : "Buscar pratos"}
//           </button>
//         </form>

//         {erro && <p role="alert" className="text-red-800">{erro}</p>}
//         <div aria-live="polite">
//           {pratos !== null && <ListaDePratos pratos={pratos} />}
//         </div>
//       </div>
//     </main>
//   );
// }
import { useRef, useState, type SyntheticEvent } from "react";
import {
  montarPedido,
  paraCard,
  vitrine,
  type Card,
  type Recomendacao,
} from "./foodmatch-data";
import "./foodmatch.css";

const moeda = new Intl.NumberFormat("pt-BR", {
  style: "currency",
  currency: "BRL",
});
const exemplos = [
  "Um almoço levinho",
  "Comida que abraça",
  "Frango com arroz e feijão",
];
const casas = [...new Set(vitrine.map((p) => p.casa))];

function Foto({ prato }: { prato: Card }) {
  return prato.foto ? (
    <img src={`/foodmatch/${prato.foto}.webp`} alt={prato.nome} />
  ) : (
    <div className="sem-foto" aria-hidden="true">
      <span>♨</span>
    </div>
  );
}

export default function App() {
  const [texto, setTexto] = useState("");
  const [orcamento, setOrcamento] = useState("");
  const [filtros, setFiltros] = useState(false);
  const [resultado, setResultado] = useState<Card[] | null>(null);
  const [grupo, setGrupo] = useState("Todos");
  const [buscando, setBuscando] = useState(false);
  const [erro, setErro] = useState("");
  const [ultima, setUltima] = useState("");
  const [salvos, setSalvos] = useState<Card[]>([]);
  const [painel, setPainel] = useState("");
  const dialog = useRef<HTMLDialogElement>(null);
  const input = useRef<HTMLInputElement>(null);

  const base = resultado ?? vitrine;
  const grupos = ["Todos", ...new Set(base.map((item) => item.grupo))];
  const visiveis =
    grupo === "Todos"
      ? (resultado ?? vitrine.slice(0, 4))
      : base.filter((p) => p.grupo === grupo);
  const detalhes =
    painel === "Salvos" ? salvos : vitrine.filter((p) => p.casa === painel);

  function abrir(titulo: string) {
    setPainel(titulo);
    dialog.current?.showModal();
  }
  function salvar(p: Card) {
    setSalvos((lista) =>
      lista.some((x) => x.chave === p.chave)
        ? lista.filter((x) => x.chave !== p.chave)
        : [...lista, p],
    );
  }

  async function buscar(e: SyntheticEvent<HTMLFormElement>) {
    e.preventDefault();
    if (buscando) return;
    const pedido = montarPedido(texto, orcamento);
    if (
      !pedido.consulta ||
      pedido.consulta.length > 500 ||
      (pedido.orcamento !== undefined &&
        (!Number.isFinite(pedido.orcamento) || pedido.orcamento <= 0))
    ) {
      setErro(
        "Descreva o prato e informe um orçamento maior que zero, se desejar.",
      );
      return;
    }
    setErro("");
    setBuscando(true);
    try {
      const res = await fetch("/api/recomendacoes", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(pedido),
      });
      if (!res.ok)
        throw new Error(
          `A API respondeu com HTTP ${res.status}. Tente novamente.`,
        );
      const pratos: Recomendacao[] = await res.json();
      setResultado(pratos.map(paraCard));
      setGrupo("Todos");
      setUltima(texto.trim());
    } catch (err) {
      setErro(
        err instanceof Error
          ? err.message
          : "Não foi possível concluir a busca.",
      );
    } finally {
      setBuscando(false);
    }
  }

  return (
    <div className="fm">
      <header>
        <div className="wrap top">
          <a className="marca" href="#descobrir">
            ✦ foodmatch
          </a>
          <nav>
            <a href="#descobrir">Descobrir</a>
            <a href="#casas">Restaurantes</a>
          </nav>
          <span className="local">
            Catálogo de demonstração<strong>Feira de Santana, BA</strong>
          </span>
          <button className="salvos" onClick={() => abrir("Salvos")}>
            ♡ Salvos ({salvos.length})
          </button>
        </div>
      </header>
      <main>
        <section className="hero" id="descobrir">
          <div className="wrap">
            <small>O seu próximo match tem sabor.</small>
            <div className="hero-titulo">
              <h1>Deu vontade de quê?</h1>
              <p>
                Descreva seu desejo. Encontre o prato certo,
                <br /> mesmo sem saber o nome dele.
              </p>
            </div>
            <form id="busca" className="busca" onSubmit={buscar}>
              <span className="lupa" aria-hidden="true"></span>
              <input
                ref={input}
                aria-label="Descreva o prato"
                value={texto}
                onChange={(e) => setTexto(e.target.value)}
                required
                maxLength={500}
                placeholder="Quero algo cremoso e bem temperado, até R$ 40"
              />
              <button className="primario" disabled={buscando}>
                {buscando ? "Buscando…" : "✧  Encontrar pratos"}
              </button>
            </form>
            <div className="sugestoes">
              <span>Experimente também:</span>
              {exemplos.map((x) => (
                <button
                  key={x}
                  onClick={() => {
                    setTexto(x);
                    input.current?.focus();
                  }}
                >
                  {x}
                </button>
              ))}
            </div>
            {erro && <p role="alert">{erro}</p>}
          </div>
        </section>
        <section className="wrap lista">
          <div className="barra">
            <div
              className="chips"
              aria-label={
                resultado ? "Filtrar por restaurante" : "Filtrar por categoria"
              }
            >
              {grupos.map((g) => (
                <button
                  key={g}
                  aria-pressed={g === grupo}
                  onClick={() => setGrupo(g)}
                >
                  {g}
                </button>
              ))}
            </div>
            <button
              className="filtro"
              aria-expanded={filtros}
              onClick={() => setFiltros(!filtros)}
            >
              ☷ Filtros{orcamento ? " •" : ""}
            </button>
          </div>
          {filtros && (
            <div className="opcoes">
              <label>
                Orçamento da próxima busca (R$){" "}
                <input
                  form="busca"
                  type="number"
                  min="0.01"
                  step=".01"
                  placeholder="Opcional"
                  value={orcamento}
                  onChange={(e) => setOrcamento(e.target.value)}
                />
              </label>
            </div>
          )}
          <div className="sec-titulo">
            <div>
              <h2>
                {resultado ? "Seu desejo, no prato." : "Para descobrir hoje."}
              </h2>
              <p>
                {resultado
                  ? `Resultados para “${ultima}”`
                  : "Uma seleção ilustrativa para inspirar sua próxima busca."}
              </p>
            </div>
            <span aria-live="polite">
              {visiveis.length} pratos ·{" "}
              {resultado ? "por relevância" : "vitrine"}
            </span>
          </div>
          <div className="grade">
            {visiveis.map((p) => (
              <article className="card" key={p.chave}>
                <div className="capa">
                  <Foto prato={p} />
                  <b className="tag">
                    {p.score === undefined
                      ? p.grupo
                      : `Score ${p.score.toFixed(3)}`}
                  </b>
                </div>
                <div className="corpo">
                  <h3>{p.nome}</h3>
                  {p.descricao && <p>{p.descricao}</p>}
                  <p>{p.casa}</p>
                  <div className="preco">
                    <strong>{moeda.format(p.preco)}</strong>
                    <button
                      aria-label={`Salvar ${p.nome}`}
                      aria-pressed={salvos.some((x) => x.chave === p.chave)}
                      onClick={() => salvar(p)}
                    >
                      {salvos.some((x) => x.chave === p.chave) ? "♥" : "♡"}
                    </button>
                  </div>
                </div>
              </article>
            ))}
          </div>
          {resultado && (
            <button
              className="link"
              onClick={() => {
                setResultado(null);
                setGrupo("Todos");
              }}
            >
              Voltar à vitrine
            </button>
          )}
        </section>
        <section id="casas" className="casas">
          <div className="wrap">
            <h2>Bons pratos. Boas descobertas.</h2>
            <p>Explore os cardápios ilustrativos da vitrine.</p>
            <div className="rest-grid">
              {casas.map((c, i) => (
                <article key={c} className="rest">
                  <div className="rest-head">
                    <b className={"monograma m" + i}>
                      {c
                        .split(" ")
                        .filter((x) => x !== "&")
                        .slice(0, 2)
                        .map((x) => x[0])
                        .join("")}
                    </b>
                    <h3>{c}</h3>
                  </div>
                  {vitrine
                    .filter((p) => p.casa === c)
                    .map((p) => (
                      <div className="mini" key={p.chave}>
                        <Foto prato={p} />
                        <div>
                          <h4>{p.nome}</h4>
                          <p>{p.descricao}</p>
                          <b>{moeda.format(p.preco)}</b>
                        </div>
                      </div>
                    ))}
                  <button className="link" onClick={() => abrir(c)}>
                    Ver cardápio →
                  </button>
                </article>
              ))}
            </div>
          </div>
        </section>
      </main>
      <footer>
        <div className="wrap">
          <a className="marca" href="#descobrir">
            foodmatch
          </a>
          <span>Seu próximo match tem sabor.</span>
        </div>
      </footer>
      <dialog ref={dialog}>
        <div className="dialog-head">
          <h2>{painel}</h2>
          <button onClick={() => dialog.current?.close()} aria-label="Fechar">
            ×
          </button>
        </div>
        {detalhes.length === 0 && (
          <p>Use o coração de um prato para salvá-lo nesta sessão.</p>
        )}
        {detalhes.map((p) => (
          <div className="linha" key={p.chave}>
            <div>
              <h3>{p.nome}</h3>
              <p>{p.casa}</p>
            </div>
            <b>{moeda.format(p.preco)}</b>
            {painel === "Salvos" && (
              <button
                aria-label={`Remover ${p.nome}`}
                onClick={() => salvar(p)}
              >
                ×
              </button>
            )}
          </div>
        ))}
      </dialog>
    </div>
  );
}
