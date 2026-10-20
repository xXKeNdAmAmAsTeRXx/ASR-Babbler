import {
  getRandomExercise,
  uploadAudio,
  getScore,
  getCerVisualization,
  getTranscription,
  getAudio,
  getScoresHistory,
  healthCheck,
} from "./api.js";
import { AudioRecorder } from "./recorder.js";
import { saveAudioId, getAudioId, clearAudioId } from "./storage.js";
import { blobToWav } from "./wav.js";
import { apiAudioToObjectUrl } from "./playback.js";

const $ = (sel) => document.querySelector(sel);

const els = {
  difficulty: $("#difficulty"),
  btnNewExercise: $("#btn-new-exercise"),
  exercisePanel: $("#exercise-panel"),
  exerciseName: $("#exercise-name"),
  exerciseMeta: $("#exercise-meta"),
  exerciseText: $("#exercise-text"),
  exerciseHint: $("#exercise-hint"),
  recordPanel: $("#record-panel"),
  recordIndicator: $("#record-indicator"),
  recordTimer: $("#record-timer"),
  btnRecord: $("#btn-record"),
  btnStop: $("#btn-stop"),
  btnSubmit: $("#btn-submit"),
  status: $("#status"),
  resultsPanel: $("#results-panel"),
  scoresGrid: $("#scores-grid"),
  transcriptionRef: $("#transcription-ref"),
  transcriptionHyp: $("#transcription-hyp"),
  cerViz: $("#cer-viz"),
  playbackAudio: $("#playback-audio"),
  playbackMeta: $("#playback-meta"),
  btnReloadResults: $("#btn-reload-results"),
  btnClearSession: $("#btn-clear-session"),
  historyTbody: $("#history-tbody"),
  historyEmpty: $("#history-empty"),
  historyTable: $("#history-table"),
  btnRefreshHistory: $("#btn-refresh-history"),
  loading: $("#loading"),
  loadingMessage: $("#loading-message"),
};

let scoresHistory = [];

let currentExercise = null;
let recordedBlob = null;
const recorder = new AudioRecorder();
let timerInterval = null;
let playbackObjectUrl = null;

function setStatus(message, type = "") {
  els.status.textContent = message;
  els.status.className = `status${type ? ` ${type}` : ""}`;
}

function showLoading(message = "Przetwarzanie…") {
  els.loadingMessage.textContent = message;
  els.loading.classList.add("visible");
}

function hideLoading() {
  els.loading.classList.remove("visible");
}

function exerciseListIndex(exercise) {
  return exercise.id - 1;
}

function formatPercent(value) {
  if (value == null || Number.isNaN(value)) return "—";
  return `${(Number(value) * 100).toFixed(1)}%`;
}

function formatNumber(value, digits = 2) {
  if (value == null || Number.isNaN(value)) return "—";
  return Number(value).toFixed(digits);
}

function renderExercise(exercise) {
  currentExercise = exercise;
  recordedBlob = null;
  els.btnSubmit.disabled = true;
  els.btnStop.disabled = true;
  els.btnRecord.disabled = false;

  els.exerciseName.textContent = exercise.nazwa;
  els.exerciseText.textContent = exercise.tekst;
  els.exerciseHint.textContent = exercise.wskazowka;

  els.exerciseMeta.innerHTML = [
    `<span class="badge">${escapeHtml(exercise.typ)}</span>`,
    `<span class="badge">${escapeHtml(exercise.trudnosc)}</span>`,
    ...(exercise.fokus || []).map(
      (f) => `<span class="badge">${escapeHtml(f)}</span>`
    ),
  ].join("");

  els.exercisePanel.classList.remove("hidden");
  els.recordPanel.classList.remove("hidden");
  resetTimer();
  setStatus("Przeczytaj tekst na głos, potem nagraj i wyślij.");
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

function resetTimer() {
  clearInterval(timerInterval);
  els.recordTimer.textContent = "0:00";
  els.recordTimer.classList.remove("recording");
  els.recordIndicator.classList.remove("active");
}

function startTimer() {
  const start = Date.now();
  els.recordTimer.classList.add("recording");
  els.recordIndicator.classList.add("active");
  timerInterval = setInterval(() => {
    const sec = Math.floor((Date.now() - start) / 1000);
    const m = Math.floor(sec / 60);
    const s = sec % 60;
    els.recordTimer.textContent = `${m}:${String(s).padStart(2, "0")}`;
  }, 200);
}

async function loadRandomExercise() {
  const trudnosc = els.difficulty.value || null;
  showLoading("Ładowanie ćwiczenia…");
  try {
    const exercise = await getRandomExercise(trudnosc);
    renderExercise(exercise);
    els.resultsPanel.classList.add("hidden");
    setStatus("Nowe ćwiczenie załadowane.", "success");
  } catch (err) {
    setStatus(err.message || "Nie udało się pobrać ćwiczenia.", "error");
  } finally {
    hideLoading();
  }
}

async function onRecordStart() {
  try {
    await recorder.start();
    els.btnRecord.disabled = true;
    els.btnStop.disabled = false;
    startTimer();
    setStatus("Nagrywanie… Kliknij Zatrzymaj, gdy skończysz.");
  } catch (err) {
    setStatus(
      err.message ||
        "Brak dostępu do mikrofonu. Zezwól na nagrywanie w przeglądarce.",
      "error"
    );
  }
}

async function onRecordStop() {
  try {
    const { blob } = await recorder.stop();
    recordedBlob = blob;
    clearInterval(timerInterval);
    els.recordIndicator.classList.remove("active");
    els.recordTimer.classList.remove("recording");
    els.btnRecord.disabled = false;
    els.btnStop.disabled = true;
    els.btnSubmit.disabled = false;
    setStatus("Nagranie gotowe. Wyślij do analizy.", "success");
  } catch (err) {
    setStatus(err.message, "error");
  }
}

async function onSubmit() {
  if (!currentExercise || !recordedBlob) {
    setStatus("Najpierw nagraj wypowiedź.", "error");
    return;
  }

  const index = exerciseListIndex(currentExercise);
  showLoading("Konwersja nagrania do WAV 16 kHz…");
  els.btnSubmit.disabled = true;

  try {
    const wavBlob = await blobToWav(recordedBlob);
    showLoading("Wysyłanie i transkrypcja (może potrwać)…");
    const { audio_id } = await uploadAudio(wavBlob, index);
    saveAudioId(audio_id);
    setStatus(`Zapisano. ID nagrania: ${audio_id}`, "success");
    await loadResults(audio_id);
  } catch (err) {
    setStatus(err.message || "Błąd wysyłania.", "error");
    els.btnSubmit.disabled = false;
  } finally {
    hideLoading();
  }
}

function renderScoresHistory(history, selectedId = null) {
  scoresHistory = history;
  const items = [...history].reverse();

  if (items.length === 0) {
    els.historyTbody.innerHTML = "";
    els.historyTable.classList.add("hidden");
    els.historyEmpty.classList.remove("hidden");
    return;
  }

  els.historyTable.classList.remove("hidden");
  els.historyEmpty.classList.add("hidden");

  els.historyTbody.innerHTML = items
    .map((score, index) => {
      const attemptNum = items.length - index;
      const accuracy = 1 - Number(score.cer_score);
      const isSelected = selectedId && score.id === selectedId;
      return `
    <tr class="history-row${isSelected ? " is-selected" : ""}" data-audio-id="${escapeHtml(score.id)}" tabindex="0" role="button" title="${escapeHtml(score.id)}">
      <td class="history-num">${attemptNum}</td>
      <td>${escapeHtml(formatPercent(accuracy))}</td>
      <td>${escapeHtml(formatPercent(score.cer_score))}</td>
      <td>${escapeHtml(formatPercent(score.confidence))}</td>
      <td>${escapeHtml(formatNumber(score.speaking_rate_wpm, 0))} <span class="history-unit">sł/min</span></td>
      <td>${escapeHtml(formatPercent(score.speaking_rate_score))}</td>
    </tr>`;
    })
    .join("");
}

async function loadScoresHistory(selectedId = null) {
  try {
    const history = await getScoresHistory();
    renderScoresHistory(history, selectedId ?? getAudioId());
  } catch (err) {
    els.historyTbody.innerHTML = "";
    els.historyTable.classList.add("hidden");
    els.historyEmpty.textContent =
      err.message || "Nie udało się załadować historii.";
    els.historyEmpty.classList.remove("hidden");
  }
}

async function selectHistoryAttempt(audioId) {
  if (!audioId) return;
  saveAudioId(audioId);
  renderScoresHistory(scoresHistory, audioId);
  await loadResults(audioId);
  els.resultsPanel.scrollIntoView({ behavior: "smooth", block: "start" });
}

function renderScores(score) {
  const accuracy = 1 - Number(score.cer_score);
  const cards = [
    { label: "Dokładność (1−CER)", value: formatPercent(accuracy) },
    { label: "CER", value: formatPercent(score.cer_score) },
    { label: "Pewność ASR", value: formatPercent(score.confidence) },
    { label: "Stabilność RMS", value: formatPercent(score.rms_stability) },
    { label: "ZCR", value: formatPercent(score.zcr_score) },
    {
      label: "Centroid widmowy",
      value: formatPercent(score.spectral_centroid_score),
    },
    {
      label: "Tempo mowy",
      value: `${formatNumber(score.speaking_rate_wpm, 0)} sł/min`,
    },
    {
      label: "Ocena tempa",
      value: formatPercent(score.speaking_rate_score),
    },
  ];

  els.scoresGrid.innerHTML = cards
    .map(
      (c) => `
    <div class="score-card">
      <span class="value">${escapeHtml(c.value)}</span>
      <span class="label">${escapeHtml(c.label)}</span>
    </div>`
    )
    .join("");
}

function clearPlayback() {
  if (playbackObjectUrl) {
    URL.revokeObjectURL(playbackObjectUrl);
    playbackObjectUrl = null;
  }
  els.playbackAudio.removeAttribute("src");
  els.playbackAudio.load();
  els.playbackMeta.classList.add("hidden");
  els.playbackMeta.textContent = "";
}

async function setupPlayback(audio) {
  clearPlayback();
  playbackObjectUrl = apiAudioToObjectUrl(audio);
  els.playbackAudio.src = playbackObjectUrl;
  const sr = audio.sample_rate ?? audio.sr;
  const channels = Array.isArray(audio.y?.[0]) ? audio.y.length : 1;
  const samples = channels === 1 ? audio.y.length : audio.y[0]?.length ?? 0;
  const durationSec = sr ? (samples / sr).toFixed(1) : "—";
  els.playbackMeta.textContent = `${sr} Hz · ${channels} kan. · ~${durationSec} s`;
  els.playbackMeta.classList.remove("hidden");
}

async function loadResults(audioId) {
  showLoading("Pobieranie wyników…");
  try {
    const [score, transcription, cerHtml] = await Promise.all([
      getScore(audioId),
      getTranscription(audioId),
      getCerVisualization(audioId),
    ]);

    renderScores(score);
    els.transcriptionRef.textContent = transcription.reference;
    els.transcriptionHyp.textContent = transcription.transcription;
    els.cerViz.innerHTML =
      typeof cerHtml === "string" ? cerHtml : String(cerHtml);

    try {
      const audio = await getAudio(audioId);
      setupPlayback(audio);
    } catch (audioErr) {
      clearPlayback();
      const msg = audioErr.message || "Nie udało się załadować nagrania.";
      const hint =
        msg.includes("404") || msg.toLowerCase().includes("nie znaleziono")
          ? " Nagranie mogło wygasnąć po restarcie API — nagraj i wyślij ponownie."
          : "";
      els.playbackMeta.textContent = msg + hint;
      els.playbackMeta.classList.remove("hidden");
    }

    els.resultsPanel.classList.remove("hidden");
    await loadScoresHistory(audioId);
    setStatus("Wyniki załadowane.", "success");
  } catch (err) {
    setStatus(
      err.message ||
        "Nie udało się pobrać wyników (sprawdź, czy API nadal działa).",
      "error"
    );
  } finally {
    hideLoading();
  }
}

async function tryRestoreResults() {
  const audioId = getAudioId();
  if (!audioId) return;
  setStatus(`Przywrócono sesję: ${audioId}`);
  await loadResults(audioId);
}

function bindEvents() {
  els.btnRefreshHistory.addEventListener("click", () =>
    loadScoresHistory(getAudioId())
  );

  els.historyTbody.addEventListener("click", (e) => {
    const row = e.target.closest(".history-row");
    if (row?.dataset.audioId) selectHistoryAttempt(row.dataset.audioId);
  });

  els.historyTbody.addEventListener("keydown", (e) => {
    if (e.key !== "Enter" && e.key !== " ") return;
    const row = e.target.closest(".history-row");
    if (row?.dataset.audioId) {
      e.preventDefault();
      selectHistoryAttempt(row.dataset.audioId);
    }
  });

  els.btnNewExercise.addEventListener("click", loadRandomExercise);
  els.btnRecord.addEventListener("click", onRecordStart);
  els.btnStop.addEventListener("click", onRecordStop);
  els.btnSubmit.addEventListener("click", onSubmit);
  els.btnReloadResults.addEventListener("click", async () => {
    const id = getAudioId();
    if (!id) {
      setStatus("Brak zapisanego audio_id.", "error");
      return;
    }
    await loadResults(id);
  });
  els.btnClearSession.addEventListener("click", () => {
    clearAudioId();
    clearPlayback();
    els.resultsPanel.classList.add("hidden");
    setStatus("Sesja wyczyszczona.", "success");
  });
}

async function init() {
  bindEvents();
  els.btnStop.disabled = true;
  els.btnSubmit.disabled = true;

  try {
    await healthCheck();
  } catch {
    setStatus(
      "API niedostępne. Uruchom backend i serwer deweloperski (patrz frontend/README.md).",
      "error"
    );
    return;
  }

  await loadScoresHistory();
  await loadRandomExercise();
  await tryRestoreResults();
}

init();
