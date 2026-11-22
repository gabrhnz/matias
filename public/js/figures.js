(function () {
  const INK = "#27455c";
  const FILL = "#3860be";
  const SOFT = "#d7e3f4";
  const PAPER = "#ffffff";
  const PEACH = "#f0b89a";
  const GREEN = "#29cc57";

  function esc(value) {
    return String(value)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;");
  }

  function svg(body, width, height) {
    return (
      '<svg viewBox="0 0 ' + width + " " + height + '" role="img" aria-hidden="true">' +
      body +
      "</svg>"
    );
  }

  function slice(cx, cy, radius, start, end, color) {
    const large = end - start > Math.PI ? 1 : 0;
    const x0 = cx + radius * Math.cos(start);
    const y0 = cy + radius * Math.sin(start);
    const x1 = cx + radius * Math.cos(end);
    const y1 = cy + radius * Math.sin(end);
    return (
      '<path d="M ' + cx + " " + cy +
      " L " + x0.toFixed(1) + " " + y0.toFixed(1) +
      " A " + radius + " " + radius + " 0 " + large + " 1 " +
      x1.toFixed(1) + " " + y1.toFixed(1) +
      ' Z" fill="' + color + '" stroke="' + PAPER + '" stroke-width="3"/>'
    );
  }

  function pie(parts, filled, cx, cy, radius) {
    if (parts <= 1) {
      return '<circle cx="' + cx + '" cy="' + cy + '" r="' + radius + '" fill="' + (filled ? FILL : PAPER) + '" stroke="' + INK + '" stroke-width="3"/>';
    }
    let body = '<circle cx="' + cx + '" cy="' + cy + '" r="' + radius + '" fill="' + PAPER + '" stroke="' + INK + '" stroke-width="3"/>';
    for (let index = 0; index < parts; index += 1) {
      const start = -Math.PI / 2 + (index * 2 * Math.PI) / parts;
      const end = start + (2 * Math.PI) / parts;
      body += slice(cx, cy, radius - 1.5, start, end, index < filled ? FILL : PAPER);
    }
    body += '<circle cx="' + cx + '" cy="' + cy + '" r="' + radius + '" fill="none" stroke="' + INK + '" stroke-width="3"/>';
    return body;
  }

  function bar(parts, filled, x, y, width, height, removed) {
    const gap = parts > 8 ? 3 : 6;
    const segment = (width - gap * (parts - 1)) / parts;
    let body = "";
    for (let index = 0; index < parts; index += 1) {
      let color = PAPER;
      if (index < filled - (removed || 0)) color = FILL;
      else if (removed && index < filled) color = PEACH;
      body +=
        '<rect x="' + (x + index * (segment + gap)).toFixed(1) +
        '" y="' + y + '" width="' + segment.toFixed(1) + '" height="' + height +
        '" rx="8" fill="' + color + '" stroke="' + INK + '" stroke-width="2.5"/>';
    }
    return body;
  }

  function caption(text, x, y) {
    return '<text x="' + x + '" y="' + y + '" text-anchor="middle" font-family="Inter, sans-serif" font-size="18" fill="#000">' + esc(text) + "</text>";
  }

  function drawPie(scene, width) {
    const height = scene.caption ? 250 : 220;
    return svg(pie(scene.parts, scene.filled, width / 2, 104, 78) + (scene.caption ? caption(scene.caption, width / 2, 220) : ""), width, height);
  }

  function drawBar(scene) {
    return svg(bar(scene.parts, scene.filled, 24, 78, 392, 64, 0), 440, 220);
  }

  function drawPair(scene) {
    const left = scene.items[0];
    const right = scene.items[1];
    return svg(
      pie(left.parts, left.filled, 110, 92, 68) +
      pie(right.parts, right.filled, 330, 92, 68) +
      caption(left.label || "", 110, 200) +
      caption(right.label || "", 330, 200),
      440,
      230
    );
  }

  function drawSum(scene) {
    const shape = scene.shape === "bar"
      ? bar(scene.parts, scene.left, 16, 78, 160, 52, 0) + bar(scene.parts, scene.right, 250, 78, 160, 52, 0)
      : pie(scene.parts, scene.left, 90, 100, 62) + pie(scene.parts, scene.right, 330, 100, 62);
    return svg(shape + caption("+", 210, 112), 440, 210);
  }

  function drawSubtract(scene) {
    return svg(
      bar(scene.parts, scene.filled, 16, 48, 250, 56, scene.remove) +
      caption("−", 292, 86) +
      bar(scene.parts, scene.remove, 316, 58, 108, 40, 0) +
      caption("se quitan", 370, 130),
      440,
      180
    );
  }

  function drawShare(scene) {
    const columns = scene.count > 12 ? 10 : Math.min(scene.count, 5);
    const gap = 14;
    const size = 28;
    let body = "";
    for (let index = 0; index < scene.count; index += 1) {
      const column = index % columns;
      const row = Math.floor(index / columns);
      body += '<circle cx="' + (36 + column * (size + gap)) + '" cy="' + (48 + row * (size + gap)) + '" r="13" fill="' + SOFT + '" stroke="' + INK + '" stroke-width="2.5"/>';
    }
    body += '<rect x="300" y="36" width="112" height="44" rx="22" fill="' + GREEN + '"/>';
    body += '<text x="356" y="65" text-anchor="middle" font-family="Inter, sans-serif" font-size="22" fill="#fff">' + esc(scene.label) + "</text>";
    return svg(body, 440, Math.ceil(scene.count / columns) * (size + gap) + 70);
  }

  function drawImproper(scene) {
    const wholes = Math.floor(scene.count / scene.parts);
    const rest = scene.count % scene.parts;
    const total = wholes + (rest ? 1 : 0);
    let body = "";
    for (let index = 0; index < total; index += 1) {
      const filled = index < wholes ? scene.parts : rest;
      body += pie(scene.parts, filled, 70 + index * 130, 100, 52);
    }
    return svg(body, Math.max(220, total * 130 + 20), 210);
  }

  function drawMixed(scene) {
    let body = "";
    for (let index = 0; index < scene.wholes; index += 1) {
      body += pie(1, 1, 70 + index * 120, 100, 52);
    }
    body += pie(scene.parts, scene.filled, 70 + scene.wholes * 120, 100, 52);
    return svg(body, 90 + (scene.wholes + 1) * 120, 210);
  }

  function drawNotation(scene) {
    const marked = scene.mark === "den";
    return svg(
      pie(scene.den, scene.num, 100, 110, 72) +
      '<text x="250" y="92" text-anchor="middle" font-family="Fraunces, Georgia, serif" font-size="42" fill="' + (marked ? INK : FILL) + '">' + scene.num + "</text>" +
      '<line x1="214" y1="108" x2="286" y2="108" stroke="' + INK + '" stroke-width="3"/>' +
      '<circle cx="250" cy="148" r="28" fill="' + (marked ? "#e7f8ec" : "none") + '" stroke="' + (marked ? GREEN : "none") + '" stroke-width="3"/>' +
      '<text x="250" y="158" text-anchor="middle" font-family="Fraunces, Georgia, serif" font-size="42" fill="' + FILL + '">' + scene.den + "</text>",
      420,
      230
    );
  }

  function polygon(sides, cx, cy, radius) {
    const points = [];
    for (let index = 0; index < sides; index += 1) {
      const angle = -Math.PI / 2 + (index * 2 * Math.PI) / sides;
      points.push((cx + radius * Math.cos(angle)).toFixed(1) + "," + (cy + radius * Math.sin(angle)).toFixed(1));
    }
    return points.join(" ");
  }

  function drawShape(scene) {
    const fill = scene.filled ? SOFT : PAPER;
    let body = "";
    if (scene.shape === "circle") {
      body = '<circle cx="210" cy="110" r="72" fill="' + fill + '" stroke="' + INK + '" stroke-width="4"/>';
    } else if (scene.shape === "square" || scene.shape === "rectangle") {
      const ratioW = scene.w || (scene.shape === "square" ? 4 : 6);
      const ratioH = scene.h || (scene.shape === "square" ? 4 : 3.2);
      const scale = Math.min(180 / ratioW, 120 / ratioH);
      const width = ratioW * scale;
      const height = ratioH * scale;
      const x = 210 - width / 2;
      const y = 108 - height / 2;
      body = '<rect x="' + x.toFixed(1) + '" y="' + y.toFixed(1) + '" width="' + width.toFixed(1) + '" height="' + height.toFixed(1) + '" rx="8" fill="' + fill + '" stroke="' + INK + '" stroke-width="4"/>';
      if (scene.w) {
        body += caption(scene.w + (scene.unit || ""), x + width / 2, y + height + 28);
        body += caption(scene.h + (scene.unit || ""), x + width + 28, y + height / 2);
      }
      if (scene.vertices) {
        [[x, y], [x + width, y], [x, y + height], [x + width, y + height]].forEach(function (point) {
          body += '<circle cx="' + point[0].toFixed(1) + '" cy="' + point[1].toFixed(1) + '" r="7" fill="' + GREEN + '"/>';
        });
      }
    } else if (scene.shape === "triangle") {
      body = '<polygon points="210,36 318,176 102,176" fill="' + fill + '" stroke="' + INK + '" stroke-width="4" stroke-linejoin="round"/>';
      if (scene.vertices) {
        [[210, 36], [318, 176], [102, 176]].forEach(function (point) {
          body += '<circle cx="' + point[0] + '" cy="' + point[1] + '" r="7" fill="' + GREEN + '"/>';
        });
      }
      if (scene.sides) {
        body += caption(scene.sides[0], 150, 100);
        body += caption(scene.sides[1], 276, 100);
        body += caption(scene.sides[2], 210, 198);
      }
    } else if (scene.shape === "pentagon") {
      body = '<polygon points="' + polygon(5, 210, 112, 78) + '" fill="' + fill + '" stroke="' + INK + '" stroke-width="4" stroke-linejoin="round"/>';
    } else if (scene.shape === "heart") {
      body = '<path d="M210 164 C210 164 150 124 150 92 C150 70 168 58 184 58 C198 58 210 68 210 80 C210 68 222 58 236 58 C252 58 270 70 270 92 C270 124 210 164 210 164 Z" fill="' + PEACH + '" stroke="' + INK + '" stroke-width="4" stroke-linejoin="round"/>';
    } else if (scene.shape === "letter-a") {
      body = '<path d="M210 42 L262 176 M210 42 L158 176 M178 124 H242" fill="none" stroke="' + INK + '" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"/>';
    }
    return svg(body, 420, 230);
  }

  function drawTriangleArea(scene) {
    const base = 220;
    const height = Math.max(48, Math.min(120, scene.height * 28));
    const x = 90;
    const y = 48;
    return svg(
      '<polygon points="' + (x + base / 2) + "," + y + " " + (x + base) + "," + (y + height) + " " + x + "," + (y + height) + '" fill="' + SOFT + '" stroke="' + INK + '" stroke-width="4" stroke-linejoin="round"/>' +
      '<line x1="' + (x + base / 2) + '" y1="' + y + '" x2="' + (x + base / 2) + '" y2="' + (y + height) + '" stroke="' + FILL + '" stroke-width="2.5" stroke-dasharray="6 6"/>' +
      caption(String(scene.base), x + base / 2, y + height + 28) +
      caption(String(scene.height), x + base / 2 + 36, y + height / 2),
      420,
      230
    );
  }

  function drawAngle(scene) {
    let body = "";
    if (scene.kind === "right" || scene.kind === "corner") {
      body =
        (scene.kind === "corner"
          ? '<path d="M70 40 H250 V190" fill="' + PAPER + '" stroke="' + INK + '" stroke-width="4"/>'
          : '<path d="M120 170 H300 M120 170 V40" fill="none" stroke="' + INK + '" stroke-width="6" stroke-linecap="round"/>') +
        '<rect x="' + (scene.kind === "corner" ? 214 : 120) + '" y="' + (scene.kind === "corner" ? 40 : 134) + '" width="28" height="28" fill="none" stroke="' + GREEN + '" stroke-width="3"/>';
    } else if (scene.kind === "acute") {
      body = '<path d="M110 180 L300 180 L210 62" fill="' + SOFT + '" stroke="' + INK + '" stroke-width="5" stroke-linejoin="round"/>';
    } else {
      body = '<path d="M70 150 L230 170 L320 70" fill="' + SOFT + '" stroke="' + INK + '" stroke-width="5" stroke-linejoin="round"/>';
    }
    return svg(body, 420, 220);
  }

  function drawPrism(scene) {
    const width = 36 + scene.w * 16;
    const height = 28 + scene.h * 16;
    const depth = 18 + scene.d * 10;
    const x = 90;
    const y = 70;
    return svg(
      '<polygon points="' + x + "," + y + " " + (x + depth) + "," + (y - depth * 0.55) + " " + (x + width + depth) + "," + (y - depth * 0.55) + " " + (x + width) + "," + y + '" fill="#edf3fb" stroke="' + INK + '" stroke-width="3"/>' +
      '<polygon points="' + (x + width) + "," + y + " " + (x + width + depth) + "," + (y - depth * 0.55) + " " + (x + width + depth) + "," + (y + height - depth * 0.55) + " " + (x + width) + "," + (y + height) + '" fill="' + SOFT + '" stroke="' + INK + '" stroke-width="3"/>' +
      '<rect x="' + x + '" y="' + y + '" width="' + width + '" height="' + height + '" fill="' + PAPER + '" stroke="' + INK + '" stroke-width="3"/>' +
      caption(String(scene.w), x + width / 2, y + height + 24) +
      caption(String(scene.h), x - 18, y + height / 2) +
      caption(String(scene.d), x + width + depth * 0.7, y - 8),
      420,
      250
    );
  }

  function draw(scene) {
    if (!scene) return "";
    if (scene.type === "pie") return drawPie(scene, 280);
    if (scene.type === "bar") return drawBar(scene);
    if (scene.type === "pair") return drawPair(scene);
    if (scene.type === "sum") return drawSum(scene);
    if (scene.type === "subtract") return drawSubtract(scene);
    if (scene.type === "share") return drawShare(scene);
    if (scene.type === "improper") return drawImproper(scene);
    if (scene.type === "mixed") return drawMixed(scene);
    if (scene.type === "notation") return drawNotation(scene);
    if (scene.type === "shape") return drawShape(scene);
    if (scene.type === "triangle-area") return drawTriangleArea(scene);
    if (scene.type === "angle") return drawAngle(scene);
    if (scene.type === "prism") return drawPrism(scene);
    return "";
  }

  function miniPie(label) {
    const match = /^(\d+)\s*\/\s*(\d+)$/.exec(label);
    if (!match) return "";
    const filled = Number(match[1]);
    const parts = Number(match[2]);
    if (!parts || filled < 0) return "";
    if (filled <= parts) {
      return '<svg viewBox="0 0 36 36" aria-hidden="true">' + pie(parts, filled, 18, 18, 14) + "</svg>";
    }
    const wholes = Math.floor(filled / parts);
    const rest = filled % parts;
    const count = wholes + (rest ? 1 : 0);
    const radius = count <= 2 ? 14 : 11;
    const step = radius * 2 + 6;
    const width = 4 + count * step - 6;
    let body = "";
    for (let index = 0; index < count; index += 1) {
      const cx = 2 + radius + index * step;
      body += index < wholes ? pie(1, 1, cx, 18, radius) : pie(parts, rest, cx, 18, radius);
    }
    return '<svg viewBox="0 0 ' + width + ' 36" aria-hidden="true">' + body + "</svg>";
  }

  window.MatiLabFigures = { draw: draw, miniPie: miniPie };
})();
