export type Recomendacao = {
  id: number;
  prato: string;
  restaurante: string;
  preco: number;
  score: number;
};
export type Card = {
  chave: string;
  nome: string;
  casa: string;
  preco: number;
  grupo: string;
  foto?: string;
  descricao?: string;
  score?: number;
};

export const vitrine: Card[] = [
  {
    chave: "v1",
    nome: "Fettuccine ao molho de parmesão",
    casa: "Massa Mia",
    preco: 36.9,
    grupo: "Massas",
    foto: "massa",
    descricao: "Massa fresca, creme de queijo e um toque de pimenta-do-reino.",
  },
  {
    chave: "v2",
    nome: "Strogonoff de frango da casa",
    casa: "Dona Ana Cozinha",
    preco: 32.9,
    grupo: "Brasileira",
    foto: "frango",
    descricao: "Frango bem temperado, arroz soltinho e batata palha crocante.",
  },
  {
    chave: "v3",
    nome: "Risoto de cogumelos",
    casa: "Massa Mia",
    preco: 39.9,
    grupo: "Risotos",
    foto: "risoto",
    descricao: "Arroz arbóreo cremoso com cogumelos e parmesão.",
  },
  {
    chave: "v4",
    nome: "Curry de grão-de-bico",
    casa: "Verde & Grão",
    preco: 34.9,
    grupo: "Vegetais",
    foto: "grao",
    descricao:
      "Leite de coco, especiarias e legumes. Cremoso e cheio de sabor.",
  },
  {
    chave: "v5",
    nome: "Frango grelhado da Ana",
    casa: "Dona Ana Cozinha",
    preco: 29.9,
    grupo: "Brasileira",
    foto: "grelhado",
    descricao: "Arroz, feijão e tempero de casa.",
  },
  {
    chave: "v6",
    nome: "Bowl da horta",
    casa: "Verde & Grão",
    preco: 31.9,
    grupo: "Vegetais",
    foto: "bowl",
    descricao: "Grãos, folhas frescas e legumes.",
  },
];

// A API atual não fornece foto, descrição nem categoria dos pratos.
export function paraCard(item: Recomendacao): Card {
  return {
    chave: String(item.id),
    nome: item.prato,
    casa: item.restaurante,
    preco: item.preco,
    score: item.score,
    grupo: item.restaurante,
  };
}

export function montarPedido(texto: string, limite: string) {
  const trecho = texto.match(
    /(?:[,;]?\s*até\s*R\$\s*(\d+(?:[.,]\d{1,2})?))\s*[.!]?$/i,
  );
  const consulta = (trecho ? texto.slice(0, trecho.index) : texto).trim();
  const valor = limite.trim() || trecho?.[1];
  return {
    consulta,
    ...(valor ? { orcamento: Number(valor.replace(",", ".")) } : {}),
  };
}
