/**
 * MCC profile photo cropper — drag + zoom, then export square JPEG.
 * openMccPhotoCrop(file).then(dataUrl => …)  |  null if cancelled
 */
(function (global) {
  const STYLE_ID = "mcc-photo-crop-style";

  function ensureStyles() {
    if (document.getElementById(STYLE_ID)) return;
    const s = document.createElement("style");
    s.id = STYLE_ID;
    s.textContent = `
      .mcc-crop-overlay {
        position: fixed; inset: 0; z-index: 9999;
        background: rgba(0,0,0,.82);
        display: flex; align-items: center; justify-content: center;
        padding: 1rem; box-sizing: border-box;
      }
      .mcc-crop-panel {
        width: min(26rem, 100%);
        background: #0a1f10; border: 1px solid rgba(245,197,24,.35);
        border-radius: 6px; padding: 1rem 1rem 1.1rem; color: #fff;
        font-family: "DM Sans", system-ui, sans-serif;
      }
      .mcc-crop-panel h3 {
        font-family: Oswald, sans-serif; letter-spacing: .1em; text-transform: uppercase;
        font-size: .95rem; color: #F5C518; margin: 0 0 .35rem;
      }
      .mcc-crop-panel .hint {
        font-size: .8rem; color: rgba(255,255,255,.5); margin: 0 0 .85rem; line-height: 1.4;
      }
      .mcc-crop-stage {
        position: relative; width: 100%; aspect-ratio: 1;
        max-height: min(70vw, 22rem); margin: 0 auto;
        overflow: hidden; background: #041108;
        border: 2px solid rgba(245,197,24,.55); border-radius: 4px;
        touch-action: none; cursor: grab; user-select: none;
      }
      .mcc-crop-stage:active { cursor: grabbing; }
      .mcc-crop-stage img {
        position: absolute; left: 50%; top: 50%;
        transform-origin: center center;
        max-width: none; pointer-events: none;
        -webkit-user-drag: none;
      }
      .mcc-crop-mask {
        position: absolute; inset: 0; pointer-events: none;
        box-shadow: inset 0 0 0 9999px rgba(0,0,0,.45);
      }
      .mcc-crop-circle {
        position: absolute; left: 50%; top: 50%;
        width: 78%; height: 78%;
        transform: translate(-50%, -50%);
        border-radius: 50%;
        box-shadow: 0 0 0 9999px rgba(0,0,0,.5);
        border: 2px solid #F5C518;
        pointer-events: none;
      }
      .mcc-crop-zoom {
        display: flex; align-items: center; gap: .65rem;
        margin: .9rem 0 .35rem; font-size: .75rem; color: rgba(255,255,255,.55);
        font-family: Oswald, sans-serif; letter-spacing: .08em; text-transform: uppercase;
      }
      .mcc-crop-zoom input[type=range] { flex: 1; accent-color: #F5C518; }
      .mcc-crop-actions {
        display: flex; gap: .6rem; margin-top: 1rem; flex-wrap: wrap;
      }
      .mcc-crop-actions button {
        flex: 1; min-width: 7rem; padding: .7rem .9rem; border: 0; border-radius: 3px;
        font-family: Oswald, sans-serif; letter-spacing: .1em; text-transform: uppercase;
        font-size: .8rem; cursor: pointer;
      }
      .mcc-crop-cancel { background: rgba(255,255,255,.1); color: #fff; }
      .mcc-crop-ok { background: #F5C518; color: #06140a; }
      .mcc-crop-ok:hover { background: #7CFF3A; }
    `;
    document.head.appendChild(s);
  }

  function openMccPhotoCrop(file) {
    ensureStyles();
    return new Promise((resolve) => {
      const reader = new FileReader();
      reader.onerror = () => resolve(null);
      reader.onload = () => {
        const img = new Image();
        img.onload = () => showModal(img, resolve);
        img.onerror = () => resolve(null);
        img.src = reader.result;
      };
      reader.readAsDataURL(file);
    });
  }

  function showModal(img, resolve) {
    const overlay = document.createElement("div");
    overlay.className = "mcc-crop-overlay";
    overlay.innerHTML = `
      <div class="mcc-crop-panel" role="dialog" aria-modal="true" aria-label="Set profile photo">
        <h3>Set profile photo</h3>
        <p class="hint">Drag to move · zoom se face center karo · phir Use Photo dabao</p>
        <div class="mcc-crop-stage" id="mcc-crop-stage">
          <img id="mcc-crop-img" alt="Crop" />
          <div class="mcc-crop-circle"></div>
        </div>
        <div class="mcc-crop-zoom">
          <span>Zoom</span>
          <input type="range" id="mcc-crop-zoom" min="100" max="300" value="100" />
        </div>
        <div class="mcc-crop-actions">
          <button type="button" class="mcc-crop-cancel" id="mcc-crop-cancel">Cancel</button>
          <button type="button" class="mcc-crop-ok" id="mcc-crop-ok">Use Photo</button>
        </div>
      </div>
    `;
    document.body.appendChild(overlay);

    const stage = overlay.querySelector("#mcc-crop-stage");
    const imgEl = overlay.querySelector("#mcc-crop-img");
    const zoomEl = overlay.querySelector("#mcc-crop-zoom");
    imgEl.src = img.src;

    let scale = 1;
    let tx = 0;
    let ty = 0;
    let dragging = false;
    let lastX = 0;
    let lastY = 0;
    let baseW = 0;
    let baseH = 0;

    function fit() {
      const sw = stage.clientWidth;
      const sh = stage.clientHeight;
      const cover = Math.max(sw / img.naturalWidth, sh / img.naturalHeight);
      baseW = img.naturalWidth * cover;
      baseH = img.naturalHeight * cover;
      scale = 1;
      tx = 0;
      ty = 0;
      zoomEl.value = "100";
      apply();
    }

    function apply() {
      const w = baseW * scale;
      const h = baseH * scale;
      imgEl.style.width = w + "px";
      imgEl.style.height = h + "px";
      imgEl.style.transform = `translate(calc(-50% + ${tx}px), calc(-50% + ${ty}px))`;
    }

    function onPointerDown(e) {
      dragging = true;
      lastX = e.clientX;
      lastY = e.clientY;
      stage.setPointerCapture(e.pointerId);
    }
    function onPointerMove(e) {
      if (!dragging) return;
      tx += e.clientX - lastX;
      ty += e.clientY - lastY;
      lastX = e.clientX;
      lastY = e.clientY;
      apply();
    }
    function onPointerUp() {
      dragging = false;
    }

    stage.addEventListener("pointerdown", onPointerDown);
    stage.addEventListener("pointermove", onPointerMove);
    stage.addEventListener("pointerup", onPointerUp);
    stage.addEventListener("pointercancel", onPointerUp);

    zoomEl.addEventListener("input", () => {
      scale = Number(zoomEl.value) / 100;
      apply();
    });

    function close(result) {
      overlay.remove();
      resolve(result);
    }

    overlay.querySelector("#mcc-crop-cancel").onclick = () => close(null);
    overlay.addEventListener("click", (e) => {
      if (e.target === overlay) close(null);
    });

    overlay.querySelector("#mcc-crop-ok").onclick = () => {
      const OUT = 512;
      const sw = stage.clientWidth;
      const sh = stage.clientHeight;
      // Circular crop area is 78% of stage, centered
      const cropSize = Math.min(sw, sh) * 0.78;
      const cropLeft = (sw - cropSize) / 2;
      const cropTop = (sh - cropSize) / 2;

      const dispW = baseW * scale;
      const dispH = baseH * scale;
      const imgLeft = sw / 2 + tx - dispW / 2;
      const imgTop = sh / 2 + ty - dispH / 2;

      const sx = ((cropLeft - imgLeft) / dispW) * img.naturalWidth;
      const sy = ((cropTop - imgTop) / dispH) * img.naturalHeight;
      const sSize = (cropSize / dispW) * img.naturalWidth;

      const canvas = document.createElement("canvas");
      canvas.width = OUT;
      canvas.height = OUT;
      const ctx = canvas.getContext("2d");
      ctx.fillStyle = "#0d3d18";
      ctx.fillRect(0, 0, OUT, OUT);
      ctx.drawImage(img, sx, sy, sSize, sSize, 0, 0, OUT, OUT);

      let quality = 0.82;
      let dataUrl = canvas.toDataURL("image/jpeg", quality);
      while (dataUrl.length > 800000 && quality > 0.45) {
        quality -= 0.08;
        dataUrl = canvas.toDataURL("image/jpeg", quality);
      }
      if (dataUrl.length > 850000) {
        close(null);
        return;
      }
      close(dataUrl);
    };

    // Fit after layout
    requestAnimationFrame(() => {
      fit();
      window.addEventListener("resize", fit, { once: true });
    });
  }

  global.openMccPhotoCrop = openMccPhotoCrop;
})(typeof window !== "undefined" ? window : globalThis);
