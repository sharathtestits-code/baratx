import { useEffect, useRef, useState } from "react";
import { spacesApi } from "../api";

const ICE_SERVERS = [
  { urls: "stun:stun.l.google.com:19302" },
  { urls: "stun:stun1.l.google.com:19302" },
];

function iceConfig() {
  const servers = [...ICE_SERVERS];
  const turnUrl = (import.meta.env.VITE_TURN_URL || "").trim();
  const turnUser = (import.meta.env.VITE_TURN_USERNAME || "").trim();
  const turnPass = (import.meta.env.VITE_TURN_CREDENTIAL || "").trim();
  if (turnUrl) {
    servers.push({
      urls: turnUrl,
      username: turnUser || undefined,
      credential: turnPass || undefined,
    });
  }
  return { iceServers: servers };
}

function peerKey(id) {
  return id == null ? "" : String(id);
}

/**
 * WebRTC mesh for Live Talk — publishes local mic/cam and plays remote audio + video.
 * Signaling goes through REST (/talk/signals); no SFU required for small rooms.
 */
export function useLiveTalkRtc({
  spaceId,
  token,
  myUserId,
  inTalk,
  participants,
  localStream,
  myMuted,
}) {
  const peersRef = useRef(new Map()); // peerId -> { pc, audioEl, makingOffer, ignoreOffer }
  const streamRef = useRef(localStream);
  const mutedRef = useRef(myMuted);
  const myIdRef = useRef(myUserId);
  const audioRootRef = useRef(null);
  const [remoteStreams, setRemoteStreams] = useState({});
  const [remoteTick, setRemoteTick] = useState(0);

  streamRef.current = localStream;
  mutedRef.current = myMuted;
  myIdRef.current = myUserId;

  useEffect(() => {
    let root = document.getElementById("live-talk-remote-audio");
    if (!root) {
      root = document.createElement("div");
      root.id = "live-talk-remote-audio";
      root.setAttribute("aria-hidden", "true");
      root.style.cssText = "position:absolute;width:0;height:0;overflow:hidden;";
      document.body.appendChild(root);
    }
    audioRootRef.current = root;
  }, []);

  function ensureAudioEl(peerId) {
    const root = audioRootRef.current || document.body;
    const key = peerKey(peerId);
    let el = root.querySelector(`audio[data-peer="${key}"]`);
    if (!el) {
      el = document.createElement("audio");
      el.dataset.peer = key;
      el.autoplay = true;
      el.playsInline = true;
      el.setAttribute("playsinline", "true");
      el.muted = false;
      el.volume = 1;
      root.appendChild(el);
    }
    return el;
  }

  async function sendSignal(toUserId, kind, payloadObj) {
    if (!token || !spaceId) return;
    try {
      await spacesApi.talkSignal(token, spaceId, {
        to_user_id: toUserId,
        kind,
        payload: JSON.stringify(payloadObj),
      });
    } catch {
      // Peer may have left mid-handshake
    }
  }

  function setPeerStream(peerId, stream) {
    if (!stream) return;
    const key = peerKey(peerId);
    setRemoteStreams((prev) => ({ ...prev, [key]: stream }));
    // Force UI refresh when a video track is added to an existing stream
    setRemoteTick((n) => n + 1);
  }

  function clearPeerStream(peerId) {
    const key = peerKey(peerId);
    setRemoteStreams((prev) => {
      if (!prev[key]) return prev;
      const next = { ...prev };
      delete next[key];
      return next;
    });
    setRemoteTick((n) => n + 1);
  }

  /**
   * Prefer transceiver replaceTrack so mid-call camera on/off renegotiates cleanly.
   */
  function attachLocalTracks(pc) {
    const stream = streamRef.current;
    if (!stream) return false;
    let changed = false;

    const audioTrack = stream.getAudioTracks()[0] || null;
    const videoTrack = stream.getVideoTracks()[0] || null;

    let audioTc = pc.getTransceivers().find((t) => t.receiver?.track?.kind === "audio");
    let videoTc = pc.getTransceivers().find((t) => t.receiver?.track?.kind === "video");

    // Bootstrap sendrecv m-lines once so peers can receive video even before we have a cam
    if (!audioTc) {
      audioTc = pc.addTransceiver("audio", { direction: "sendrecv" });
      changed = true;
    }
    if (!videoTc) {
      videoTc = pc.addTransceiver("video", { direction: "sendrecv" });
      changed = true;
    }

    if (audioTrack) {
      audioTrack.enabled = !mutedRef.current;
      if (audioTc.sender.track !== audioTrack) {
        audioTc.sender.replaceTrack(audioTrack);
        changed = true;
      }
    }

    if (videoTrack) {
      if (videoTc.sender.track !== videoTrack) {
        videoTc.sender.replaceTrack(videoTrack);
        changed = true;
      }
      try {
        if (videoTc.direction !== "sendrecv") videoTc.direction = "sendrecv";
      } catch {
        /* ignore */
      }
    } else if (videoTc.sender.track) {
      videoTc.sender.replaceTrack(null);
      changed = true;
    }

    return changed;
  }

  function syncLocalMuteOnPeers() {
    const enabled = !mutedRef.current;
    peersRef.current.forEach(({ pc }) => {
      pc.getSenders().forEach((sender) => {
        if (sender.track && sender.track.kind === "audio") {
          sender.track.enabled = enabled;
        }
      });
    });
    if (streamRef.current) {
      streamRef.current.getAudioTracks().forEach((tr) => {
        tr.enabled = enabled;
      });
    }
  }

  async function renegotiate(peerId, entry) {
    const { pc } = entry;
    if (entry.makingOffer || pc.signalingState !== "stable") return;
    try {
      entry.makingOffer = true;
      attachLocalTracks(pc);
      const offer = await pc.createOffer();
      await pc.setLocalDescription(offer);
      await sendSignal(peerId, "offer", pc.localDescription);
    } catch {
      // ignore
    } finally {
      entry.makingOffer = false;
    }
  }

  async function createPeer(peerId) {
    const key = peerKey(peerId);
    if (peersRef.current.has(key)) return peersRef.current.get(key);
    const pc = new RTCPeerConnection(iceConfig());
    const audioEl = ensureAudioEl(key);
    const entry = { pc, audioEl, makingOffer: false, ignoreOffer: false, peerId };
    peersRef.current.set(key, entry);

    pc.onicecandidate = (ev) => {
      if (!ev.candidate) return;
      sendSignal(peerId, "ice", ev.candidate.toJSON());
    };

    pc.ontrack = (ev) => {
      let stream = ev.streams?.[0];
      if (!stream) {
        const existing = entry.remoteStream || new MediaStream();
        if (ev.track && !existing.getTracks().includes(ev.track)) {
          existing.addTrack(ev.track);
        }
        stream = existing;
      }
      entry.remoteStream = stream;
      setPeerStream(key, stream);
      audioEl.srcObject = stream;
      const play = () => {
        audioEl.play().catch(() => {});
      };
      play();
      audioEl.onloadedmetadata = play;
      // When video arrives later on same stream, bump UI
      ev.track?.addEventListener?.("unmute", () => setRemoteTick((n) => n + 1));
    };

    attachLocalTracks(pc);
    return entry;
  }

  async function ensureOffer(peerId) {
    const myId = myIdRef.current;
    if (!myId || myId >= peerId) return; // only lower id initiates first offer
    const entry = await createPeer(peerId);
    await renegotiate(peerId, entry);
  }

  async function handleSignal(signal) {
    const peerId = signal.from_user_id;
    let payload;
    try {
      payload = JSON.parse(signal.payload);
    } catch {
      return;
    }
    const entry = await createPeer(peerId);
    const { pc } = entry;
    const polite = (myIdRef.current || "") < peerId;

    try {
      if (signal.kind === "offer") {
        const offerCollision = entry.makingOffer || pc.signalingState !== "stable";
        entry.ignoreOffer = !polite && offerCollision;
        if (entry.ignoreOffer) return;
        await pc.setRemoteDescription(payload);
        attachLocalTracks(pc);
        const answer = await pc.createAnswer();
        await pc.setLocalDescription(answer);
        await sendSignal(peerId, "answer", pc.localDescription);
      } else if (signal.kind === "answer") {
        if (pc.signalingState === "have-local-offer") {
          await pc.setRemoteDescription(payload);
        }
      } else if (signal.kind === "ice") {
        try {
          await pc.addIceCandidate(payload);
        } catch {
          // candidate before remote description — usually recoverable
        }
      }
    } catch {
      // Bad SDP / race — next poll may renegotiate
    }
  }

  function closePeer(peerId) {
    const key = peerKey(peerId);
    const entry = peersRef.current.get(key);
    if (!entry) return;
    try {
      entry.pc.close();
    } catch {
      // ignore
    }
    if (entry.audioEl) {
      entry.audioEl.srcObject = null;
      entry.audioEl.remove();
    }
    peersRef.current.delete(key);
    clearPeerStream(key);
  }

  function closeAll() {
    Array.from(peersRef.current.keys()).forEach(closePeer);
    setRemoteStreams({});
    setRemoteTick((n) => n + 1);
  }

  useEffect(() => {
    if (!inTalk || !myUserId || !token || !spaceId) {
      closeAll();
      return undefined;
    }
    const others = (participants || [])
      .map((p) => p.user?.id)
      .filter((id) => id && id !== myUserId);

    Array.from(peersRef.current.keys()).forEach((id) => {
      if (!others.map(peerKey).includes(peerKey(id))) closePeer(id);
    });

    others.forEach((id) => {
      ensureOffer(id);
    });

    return undefined;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [inTalk, myUserId, token, spaceId, participants]);

  useEffect(() => {
    if (!inTalk) return;
    syncLocalMuteOnPeers();
  }, [inTalk, myMuted, localStream]);

  // Camera/mic stream changed → replace tracks + renegotiate with every peer
  useEffect(() => {
    if (!inTalk || !localStream || !myUserId) return;
    peersRef.current.forEach((entry, key) => {
      const changed = attachLocalTracks(entry.pc);
      if (changed || localStream.getVideoTracks().length > 0) {
        renegotiate(entry.peerId || key, entry);
      }
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [inTalk, localStream, myUserId]);

  useEffect(() => {
    if (!inTalk || !token || !spaceId) return undefined;
    let cancelled = false;

    async function poll() {
      try {
        const signals = await spacesApi.talkSignals(token, spaceId);
        if (cancelled || !Array.isArray(signals)) return;
        for (const signal of signals) {
          await handleSignal(signal);
        }
      } catch {
        // ignore transient
      }
    }

    poll();
    const t = setInterval(poll, 800);
    return () => {
      cancelled = true;
      clearInterval(t);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [inTalk, token, spaceId, myUserId]);

  useEffect(() => {
    if (!inTalk) closeAll();
    return () => closeAll();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [inTalk]);

  return {
    remoteStreams,
    remoteTick,
    resumeRemoteAudio: () => {
      peersRef.current.forEach(({ audioEl }) => {
        if (audioEl?.srcObject) audioEl.play().catch(() => {});
      });
    },
  };
}
