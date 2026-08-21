import { useCallback, useEffect, useRef, useState } from "react";

const SIDE_LABEL = {
  for: "Agree",
  against: "Disagree",
  depends: "It depends",
};

/**
 * Native shareable card — canvas PNG of question + stance + BarathX mark.
 */
export default function ShareCard({
  question,
  side,
  sideLabel,
  open = false,
  onClose,
}) {
  const canvasRef = useRef(null);
  const [ready, setReady] = useState(false);
  const [busy, setBusy] = useState(false);
  const label = sideLabel || SIDE_LABEL[side] || side || "My take";

  const draw = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const w = 1080;
    const h = 1350;
    canvas.width = w;
    canvas.height = h;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const grad = ctx.createLinearGradient(0, 0, w, h);
    grad.addColorStop(0, "#0c1a24");
    grad.addColorStop(0.55, "#132a36");
    grad.addColorStop(1, "#1a3a2a");
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, w, h);

    ctx.fillStyle = "rgba(255,153,51,0.18)";
    ctx.beginPath();
    ctx.arc(w * 0.85, h * 0.12, 220, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = "rgba(19,136,8,0.14)";
    ctx.beginPath();
    ctx.arc(w * 0.12, h * 0.88, 260, 0, Math.PI * 2);
    ctx.fill();

    ctx.fillStyle = "#f4f7f5";
    ctx.font = "700 52px Georgia, 'Times New Roman', serif";
    ctx.fillText("BarathX", 72, 120);
    ctx.font = "400 28px system-ui, sans-serif";
    ctx.fillStyle = "rgba(244,247,245,0.72)";
    ctx.fillText("India's conversation network", 72, 168);

    ctx.fillStyle = "#ff9933";
    ctx.font = "700 36px system-ui, sans-serif";
    ctx.fillText(String(label).toUpperCase(), 72, 280);

    const q = String(question || "Today's question").trim();
    ctx.fillStyle = "#f4f7f5";
    ctx.font = "600 54px Georgia, 'Times New Roman', serif";
    const lines = wrapText(ctx, q, w - 144);
    let y = 380;
    for (const line of lines.slice(0, 6)) {
      ctx.fillText(line, 72, y);
      y += 72;
    }

    ctx.fillStyle = "rgba(244,247,245,0.8)";
    ctx.font = "500 30px system-ui, sans-serif";
    ctx.fillText("Take a side. Meet your people.", 72, h - 160);
    ctx.font = "400 26px system-ui, sans-serif";
    ctx.fillStyle = "rgba(244,247,245,0.55)";
    ctx.fillText("barathx.com", 72, h - 110);

    setReady(true);
  }, [question, label]);

  useEffect(() => {
    if (open) draw();
  }, [open, draw]);

  async function download() {
    const canvas = canvasRef.current;
    if (!canvas) return;
    setBusy(true);
    try {
      const blob = await new Promise((resolve) => canvas.toBlob(resolve, "image/png"));
      if (!blob) return;
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "barathx-take.png";
      a.click();
      URL.revokeObjectURL(url);
    } finally {
      setBusy(false);
    }
  }

  async function shareNative() {
    const canvas = canvasRef.current;
    if (!canvas || !navigator.share) {
      await download();
      return;
    }
    setBusy(true);
    try {
      const blob = await new Promise((resolve) => canvas.toBlob(resolve, "image/png"));
      if (!blob) return;
      const file = new File([blob], "barathx-take.png", { type: "image/png" });
      if (navigator.canShare?.({ files: [file] })) {
        await navigator.share({
          files: [file],
          title: "My BarathX take",
          text: `${label} — ${question}\nbarathx.com`,
        });
      } else {
        await download();
      }
    } catch {
      /* user cancelled */
    } finally {
      setBusy(false);
    }
  }

  if (!open) return null;

  return (
    <div className="share-card-overlay" role="dialog" aria-modal="true" aria-label="Share your take">
      <div className="share-card-panel">
        <h3 className="share-card-title">Share your side</h3>
        <p className="hint">A simple card for WhatsApp, Instagram, or X — no login wall in the image.</p>
        <canvas ref={canvasRef} className="share-card-canvas" aria-hidden="true" />
        <div className="share-card-actions">
          <button type="button" className="btn btn-primary" disabled={!ready || busy} onClick={shareNative}>
            {busy ? "Preparing…" : "Share card"}
          </button>
          <button type="button" className="btn btn-secondary" disabled={!ready || busy} onClick={download}>
            Download PNG
          </button>
          <button type="button" className="btn btn-secondary" onClick={onClose}>
            Close
          </button>
        </div>
      </div>
    </div>
  );
}

function wrapText(ctx, text, maxWidth) {
  const words = text.split(/\s+/);
  const lines = [];
  let line = "";
  for (const word of words) {
    const next = line ? `${line} ${word}` : word;
    if (ctx.measureText(next).width > maxWidth && line) {
      lines.push(line);
      line = word;
    } else {
      line = next;
    }
  }
  if (line) lines.push(line);
  return lines;
}
