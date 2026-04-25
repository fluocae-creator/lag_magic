const cards = [
  {
    id: "card01",
    name: "店長款名片",
    image: "images/card01.png",
    businessCard: "店長款個人名片",
    theme: "溫柔可靠",
    description: "今天的小鳥推薦是溫柔可靠的店長款。"
  },
  {
    id: "card02",
    name: "店員款名片",
    image: "images/card02.png",
    businessCard: "店員款個人名片",
    theme: "活潑親切",
    description: "今天的小鳥推薦是活潑親切的店員款。"
  },
  {
    id: "card03",
    name: "旅人款名片",
    image: "images/card03.png",
    businessCard: "旅人款個人名片",
    theme: "神祕溫暖",
    description: "今天的小鳥推薦是神祕溫暖的旅人款。"
  }
];

const IMAGE_FALLBACK = "images/placeholder.png";
const CARD_BACK = "images/card-back.png";

const landing = document.getElementById("landing");
const gacha = document.getElementById("gacha");
const heroImage = document.getElementById("heroImage");
const cardImage = document.getElementById("cardImage");
const cardStage = document.getElementById("cardStage");
const drawBtn = document.getElementById("drawBtn");
const retryBtn = document.getElementById("retryBtn");
const resultCard = document.getElementById("resultCard");

const resultName = document.getElementById("resultName");
const resultBusinessCard = document.getElementById("resultBusinessCard");
const resultTheme = document.getElementById("resultTheme");
const resultDescription = document.getElementById("resultDescription");

function setSafeImage(imgElement, src, altText) {
  imgElement.onerror = () => {
    imgElement.onerror = null;
    imgElement.src = IMAGE_FALLBACK;
  };
  imgElement.src = src;
  imgElement.alt = altText;
}

function showLanding() {
  gacha.classList.add("hidden");
  landing.classList.remove("hidden");
}

function showGacha() {
  landing.classList.add("hidden");
  gacha.classList.remove("hidden");
}

function getRandomCard(list) {
  const randomIndex = Math.floor(Math.random() * list.length);
  return list[randomIndex];
}

function renderCard(card) {
  setSafeImage(cardImage, card.image, `${card.name} 圖片`);
  resultName.textContent = card.name;
  resultBusinessCard.textContent = card.businessCard;
  resultTheme.textContent = card.theme;
  resultDescription.textContent = card.description;
  resultCard.classList.remove("hidden");
}

function playFlipThenDraw() {
  if (cards.length === 0) {
    resultName.textContent = "目前尚無卡片資料";
    resultDescription.textContent = "請先到 script.js 新增 cards 資料。";
    resultCard.classList.remove("hidden");
    return;
  }

  drawBtn.disabled = true;
  retryBtn.disabled = true;

  cardStage.classList.remove("card-flip");
  void cardStage.offsetWidth;
  cardStage.classList.add("card-flip");

  window.setTimeout(() => {
    const picked = getRandomCard(cards);
    renderCard(picked);
    drawBtn.disabled = false;
    retryBtn.disabled = false;
  }, 650);
}

setSafeImage(heroImage, "images/hero-bird.png", "羅雀鎮主視覺小鳥");
setSafeImage(cardImage, CARD_BACK, "名片卡背");

document.getElementById("enterBtn").addEventListener("click", showGacha);
document.getElementById("backBtn").addEventListener("click", () => {
  showLanding();
  resultCard.classList.add("hidden");
  setSafeImage(cardImage, CARD_BACK, "名片卡背");
});

drawBtn.addEventListener("click", playFlipThenDraw);
retryBtn.addEventListener("click", playFlipThenDraw);
