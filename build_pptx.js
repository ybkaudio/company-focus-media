// 기업인집중탐구 에피소드 JSON -> 편집 가능한 PPTX (Canva에서 열어 글자 수정 가능)
// 사용법: node build_pptx.js episodes/01-apple.json out/01-apple.pptx
const fs = require("fs");
const pptxgen = require("pptxgenjs");

const [, , src, dst] = process.argv;
const ep = JSON.parse(fs.readFileSync(src, "utf8"));
const A = ep.accent.replace("#", "");
const FONT = "Noto Sans KR";
const PX = (v) => v / 144;            // 1080x1350px -> 7.5x9.375in
const PT = (v) => v * 0.5;            // px -> pt at 144dpi
const shade = "image/png;base64," + fs.readFileSync(__dirname + "/shade.png").toString("base64");

const pres = new pptxgen();
pres.defineLayout({ name: "IG45", width: 7.5, height: 9.375 });
pres.layout = "IG45";
pres.title = `기업인집중탐구 #${String(ep.no).padStart(2, "0")} ${ep.person}`;

const n = ep.slides.length;
const L = 80, R = 1000, BOTTOM = 1230;

function text(slide, t, x, y, w, h, o) {
  slide.addText(t, Object.assign({ x: PX(x), y: PX(y), w: PX(w), h: PX(h), fontFace: FONT,
    color: "FFFFFF", margin: 0, valign: "top", isTextBox: true }, o));
}
function bar(slide, x, y) {
  slide.addShape(pres.shapes.RECTANGLE, { x: PX(x), y: PX(y), w: PX(84), h: PX(5), fill: { color: A }, line: { color: A, width: 0 }, objectName: "accent" });
}

ep.slides.forEach((s, i) => {
  const slide = pres.addSlide();
  slide.background = { color: "0B0B0D" };
  // 사진 자리: 이 사각형을 지우고 사진을 넣은 뒤 맨 뒤로 보내기
  slide.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 7.5, h: PX(1053), fill: { color: "17171B" }, line: { color: "17171B", width: 0 }, objectName: "사진 자리" });
  text(slide, "사진 자리 (이 상자를 사진으로 바꾸기)", 0, 250, 1080, 50, { fontSize: 14, color: "4A4A52", align: "center", objectName: "사진 안내" });
  slide.addImage({ data: shade, x: 0, y: 0, w: 7.5, h: 9.375, objectName: "그라데이션" });
  // 페이지 표시
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: PX(R - 120), y: PX(84), w: PX(128), h: PX(62), rectRadius: 0.2, fill: { color: "000000", transparency: 45 }, line: { color: "000000", width: 0 } });
  text(slide, `${i + 1}/${n}`, R - 120, 84, 128, 62, { fontSize: 16, align: "center", valign: "middle" });

  const t = s.type || "text";
  if (t !== "cover") { text(slide, s.index, L, 96, 700, 44, { fontSize: 16, bold: true, charSpacing: 2 }); bar(slide, L, 162); }

  const titleLines = s.title.split("\n").length;
  const titleSize = t === "cover" ? 90 : 88;
  const titleH = titleLines * titleSize * 1.22;

  // 아래에서 위로 쌓기: 본문 -> 구분선 -> 제목
  let bodyBlockH, drawBody;
  if (t === "stats") {
    bodyBlockH = s.stats.length * 230 + s.body.length * 56;
    drawBody = (y) => {
      s.stats.forEach((st) => {
        text(slide, st.cap, L, y, 920, 44, { fontSize: 16, color: "CFCFD6" }); y += 50;
        text(slide, [{ text: st.num, options: { fontSize: 72, bold: true } }, { text: "  " + st.unit, options: { fontSize: 22, color: "CFCFD6" } }], L, y, 920, 160, { valign: "bottom" });
        y += 180;
      });
      text(slide, s.body.join("\n"), L, y, 920, s.body.length * 56, { fontSize: 18, color: "E6E6EA", lineSpacingMultiple: 1.3 });
    };
  } else if (t === "outro") {
    bodyBlockH = s.points.length * 58 + 70 + 50 + 70 + 90;
    drawBody = (y) => {
      text(slide, s.points.map((p, k) => ({ text: p, options: { bullet: true, breakLine: k < s.points.length - 1 } })), L, y, 920, s.points.length * 58, { fontSize: 17, color: "E6E6EA", paraSpaceAfter: 6 });
      y += s.points.length * 58 + 20;
      text(slide, s.question, L, y, 920, 56, { fontSize: 22, bold: true }); y += 60;
      text(slide, s.ask, L, y, 920, 44, { fontSize: 16, color: "CFCFD6" }); y += 70;
      text(slide, ep.handle.toUpperCase(), L, y, 600, 40, { fontSize: 14, bold: true, charSpacing: 3 }); y += 46;
      slide.addShape(pres.shapes.RECTANGLE, { x: PX(L), y: PX(y), w: PX(330), h: PX(84), fill: { color: "FFFFFF" }, line: { color: "FFFFFF", width: 0 } });
      text(slide, s.button, L, y, 330, 84, { fontSize: 17, bold: true, color: "000000", align: "center", valign: "middle" });
    };
  } else {
    const lh = 36 * 1.55;
    bodyBlockH = s.body.length * lh;
    drawBody = (y) => text(slide, s.body.join("\n"), L, y, 920, bodyBlockH + 10, { fontSize: 18, color: "E6E6EA", lineSpacingMultiple: 1.3 });
  }
  const bodyY = BOTTOM - bodyBlockH;
  const divY = bodyY - 45;
  const titleY = divY - 44 - titleH;
  if (t === "cover") text(slide, ep.handle.toUpperCase(), L, titleY - 64, 800, 40, { fontSize: 15, bold: true, charSpacing: 4 });
  text(slide, s.title, L, titleY, 940, titleH, { fontSize: PT(titleSize), bold: true, lineSpacingMultiple: 1.05, valign: "bottom", objectName: "제목" });
  bar(slide, L, divY);
  drawBody(bodyY);
});

pres.writeFile({ fileName: dst }).then(() => console.log("wrote", dst));
