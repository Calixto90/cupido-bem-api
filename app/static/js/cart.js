const CARRINHO_KEY = "cupido_carrinho";

function lerCarrinho() {
  try {
    return JSON.parse(localStorage.getItem(CARRINHO_KEY)) || [];
  } catch (e) {
    return [];
  }
}

function salvarCarrinho(itens) {
  localStorage.setItem(CARRINHO_KEY, JSON.stringify(itens));
}

function adicionarAoCarrinho(item) {
  const itens = lerCarrinho();
  const existente = itens.find((i) => i.consignacao_id === item.consignacao_id);
  if (existente) {
    existente.quantidade += item.quantidade;
  } else {
    itens.push(item);
  }
  salvarCarrinho(itens);
  return itens;
}

function removerDoCarrinho(consignacaoId) {
  const itens = lerCarrinho().filter((i) => i.consignacao_id !== consignacaoId);
  salvarCarrinho(itens);
  return itens;
}

function limparCarrinho() {
  localStorage.removeItem(CARRINHO_KEY);
}

function totalCarrinho(itens) {
  return itens.reduce((soma, i) => soma + i.quantidade * parseFloat(i.preco_unitario), 0);
}
